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

health_agent = Agent(
    model=os.getenv("HEALTH_AGENT_MODEL"),
    name="health_agent",
    instruction=return_instructions_health(),
    tools=[
        diagnose_plant_disease,
        get_treatment_recommendations,
        get_pest_identification,
        get_prevention_strategies
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.5),
)