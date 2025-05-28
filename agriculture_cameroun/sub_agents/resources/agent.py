# Copyright 2025 Agriculture Cameroun

"""Agent de gestion des ressources (sol, eau, engrais)."""

import os
from google.adk.agents import Agent
from google.genai import types

from .prompts import return_instructions_resources
from .tools import (
    analyze_soil_requirements,
    recommend_fertilizers,
    optimize_irrigation,
    assess_land_suitability,
    calculate_nutrient_needs,
    suggest_soil_amendments
)

resources_agent = Agent(
    model=os.getenv("RESOURCES_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="resources_agent",
    instruction=return_instructions_resources(),
    tools=[
        analyze_soil_requirements,
        recommend_fertilizers,
        optimize_irrigation,
        assess_land_suitability,
        calculate_nutrient_needs,
        suggest_soil_amendments
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.4),
)