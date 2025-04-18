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

crops_agent = Agent(
    model=os.getenv("CROPS_AGENT_MODEL"),
    name="crops_agent",
    instruction=return_instructions_crops(),
    tools=[
        get_planting_calendar,
        get_crop_rotation_advice,
        get_variety_recommendations,
        get_cultivation_techniques
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.6),
)