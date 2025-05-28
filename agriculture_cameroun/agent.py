# Copyright 2025 Agriculture Cameroun
#
# Licensed under the Apache License, Version 2.0 (the "License");

"""Agent principal pour le système multi-agents agriculture camerounaise."""

import os
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
    resources_agent
)
from .prompts import return_instructions_root
from .tools import call_weather_agent, call_crops_agent, call_health_agent, call_economic_agent, call_resources_agent
from .utils.data import REGIONS, CROPS, SEASONS

date_today = date.today()


def setup_before_agent_call(callback_context: CallbackContext):
    """Configuration avant l'appel de l'agent."""
    
    # Configuration de l'état de session
    if "agriculture_settings" not in callback_context.state:
        agriculture_settings = {
            "regions": REGIONS,
            "crops": CROPS,
            "seasons": SEASONS,
            "current_date": date_today,
            "default_region": os.getenv("DEFAULT_REGION", "Centre"),
            "language": os.getenv("DEFAULT_LANGUAGE", "fr")
        }
        callback_context.state["agriculture_settings"] = agriculture_settings
    
    # Mise à jour des instructions avec le contexte
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


root_agent = Agent(
    model=os.getenv("ROOT_AGENT_MODEL"),
    name="agriculture_multiagent",
    instruction=return_instructions_root(),
    global_instruction=(
        f"""
        Tu es un Système Multi-Agents pour l'Agriculture Camerounaise.
        Date actuelle: {date_today}
        Langue: Français
        """
    ),
    sub_agents=[
        weather_agent,
        crops_agent,
        health_agent,
        economic_agent,
        resources_agent
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
    generate_content_config=types.GenerateContentConfig(temperature=0.7),
)