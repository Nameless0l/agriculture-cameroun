# Copyright 2025 Agriculture Cameroun

"""Agent de gestion des cultures."""

import os
from google.adk.agents import Agent
from google.genai import types

from .prompts import return_instructions_crops
from .tools import (
    get_planting_calendar,
    get_crop_rotation_advice,
    get_variety_recommendations,
    get_cultivation_techniques
)
from ...rag import retrieve_agricultural_knowledge
from ...observability import make_adk_callbacks

_obs = make_adk_callbacks()

crops_agent = Agent(
    model=os.getenv("CROPS_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="crops_agent",
    instruction=return_instructions_crops(),
    tools=[
        retrieve_agricultural_knowledge,
        get_planting_calendar,
        get_crop_rotation_advice,
        get_variety_recommendations,
        get_cultivation_techniques,
    ],
    before_agent_callback=_obs["before_agent"],
    after_agent_callback=_obs["after_agent"],
    before_tool_callback=_obs["before_tool"],
    after_tool_callback=_obs["after_tool"],
    generate_content_config=types.GenerateContentConfig(temperature=0.6),
)