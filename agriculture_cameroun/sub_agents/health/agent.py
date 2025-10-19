# Copyright 2025 Agriculture Cameroun

"""Agent de santé des plantes."""

import os
from google.adk.agents import Agent
from google.genai import types

from .prompts import return_instructions_health
from .tools import (
    diagnose_plant_disease,
    get_treatment_recommendations,
    get_pest_identification,
    get_prevention_strategies
)
from ...rag import retrieve_agricultural_knowledge
from ...observability import make_adk_callbacks

_obs = make_adk_callbacks()

health_agent = Agent(
    model=os.getenv("HEALTH_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="health_agent",
    instruction=return_instructions_health(),
    tools=[
        retrieve_agricultural_knowledge,
        diagnose_plant_disease,
        get_treatment_recommendations,
        get_pest_identification,
        get_prevention_strategies,
    ],
    before_agent_callback=_obs["before_agent"],
    after_agent_callback=_obs["after_agent"],
    before_tool_callback=_obs["before_tool"],
    after_tool_callback=_obs["after_tool"],
    generate_content_config=types.GenerateContentConfig(temperature=0.5),
)