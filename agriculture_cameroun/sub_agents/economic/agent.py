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
from ...rag import retrieve_agricultural_knowledge
from ...observability import make_adk_callbacks

_obs = make_adk_callbacks()

economic_agent = Agent(
    model=os.getenv("ECONOMIC_AGENT_MODEL", "gemini-2.0-flash-001"),
    name="economic_agent",
    instruction=return_instructions_economic(),
    tools=[
        retrieve_agricultural_knowledge,
        get_market_prices,
        analyze_profitability,
        get_market_trends,
        recommend_sales_strategy,
        calculate_production_costs,
        analyze_market_opportunities,
    ],
    before_agent_callback=_obs["before_agent"],
    after_agent_callback=_obs["after_agent"],
    before_tool_callback=_obs["before_tool"],
    after_tool_callback=_obs["after_tool"],
    generate_content_config=types.GenerateContentConfig(temperature=0.3),
)