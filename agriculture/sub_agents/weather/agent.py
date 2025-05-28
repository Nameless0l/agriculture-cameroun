# Copyright 2025 Agriculture Cameroun

"""Agent météorologique pour les prévisions et conseils climatiques."""

import os
from google.adk.agents import Agent
from google.genai import types

from .prompts import return_instructions_weather
from .tools import (
    get_weather_forecast,
    get_irrigation_advice,
    get_climate_alerts,
    analyze_rainfall_patterns
)

weather_agent = Agent(
    model=os.getenv("WEATHER_AGENT_MODEL"),
    name="weather_agent",
    instruction=return_instructions_weather(),
    tools=[
        get_weather_forecast,
        get_irrigation_advice,
        get_climate_alerts,
        analyze_rainfall_patterns
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.5),
)