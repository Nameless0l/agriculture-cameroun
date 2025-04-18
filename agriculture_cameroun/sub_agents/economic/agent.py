# Copyright 2025 Agriculture Cameroun

"""Agent économique pour l'analyse des marchés et de la rentabilité."""

import os
from google.adk.agents import Agent
from google.genai import types

from .prompts import return_instructions_economic
from .tools import (
    get_market_prices,
    analyze_profitability,
    get_market_trends,
    recommend_sales_strategy,
    calculate_production_costs,
    analyze_market_opportunities
)

economic_agent = Agent(
    model=os.getenv("ECONOMIC_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="economic_agent",
    instruction=return_instructions_economic(),
    tools=[
        get_market_prices,
        analyze_profitability,
        get_market_trends,
        recommend_sales_strategy,
        calculate_production_costs,
        analyze_market_opportunities
    ],
    generate_content_config=types.GenerateContentConfig(temperature=0.3),
)