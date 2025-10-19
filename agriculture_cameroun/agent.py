# Copyright 2025 Agriculture Cameroun
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Agent principal pour le système multi-agents agriculture camerounaise."""

import os

from dotenv import load_dotenv

load_dotenv(override=True)
if os.getenv("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

from datetime import date
from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_artifacts

from .sub_agents import (
    weather_agent,
    crops_agent,
    health_agent,
    economic_agent,
    resources_agent,
)
from .prompts import return_instructions_root
from .tools import (
    call_weather_agent,
    call_crops_agent,
    call_health_agent,
    call_economic_agent,
    call_resources_agent,
)
from .utils.data import REGIONS, CROPS, SEASONS
from .observability import make_adk_callbacks

date_today = date.today()
_obs = make_adk_callbacks()


def setup_before_agent_call(callback_context: CallbackContext):
    """Initialise l'état de session + démarre le span Langfuse."""
    if "agriculture_settings" not in callback_context.state:
        callback_context.state["agriculture_settings"] = {
            "regions": {k.value: k.value for k in REGIONS},
            "crops": {k.value: k.value for k in CROPS},
            "current_date": str(date_today),
            "default_region": os.getenv("DEFAULT_REGION", "Centre"),
            "language": os.getenv("DEFAULT_LANGUAGE", "fr"),
        }
    context = callback_context.state["agriculture_settings"]
    callback_context._invocation_context.agent.instruction = (
        return_instructions_root()
        + f"""

        Contexte actuel:
        - Date: {context['current_date']}
        - Région par défaut: {context['default_region']}
        - Cultures principales: {', '.join(context['crops'].keys())}
        - Régions disponibles: {', '.join(context['regions'].keys())}
        """
    )
    _obs["before_agent"](callback_context)


def teardown_after_agent_call(callback_context: CallbackContext):
    """Ferme le span Langfuse après la réponse de l'agent."""
    _obs["after_agent"](callback_context)


root_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="agriculture_multiagent",
    instruction=return_instructions_root(),
    global_instruction=(
        f"Tu es un Système Multi-Agents pour l'Agriculture Camerounaise.\n"
        f"Date actuelle: {date_today}\nLangue: Français"
    ),
    sub_agents=[
        weather_agent,
        crops_agent,
        health_agent,
        economic_agent,
        resources_agent,
    ],
    tools=[
        call_weather_agent,
        call_crops_agent,
        call_health_agent,
        call_economic_agent,
        call_resources_agent,
        load_artifacts,
    ],
    before_agent_callback=setup_before_agent_call,
    after_agent_callback=teardown_after_agent_call,
    before_tool_callback=_obs["before_tool"],
    after_tool_callback=_obs["after_tool"],
    generate_content_config=types.GenerateContentConfig(temperature=0.7),
)