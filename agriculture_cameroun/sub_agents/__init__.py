# Copyright 2025 Agriculture Cameroun

"""Module des sous-agents spécialisés."""

from .weather.agent import weather_agent
from .crops.agent import crops_agent
from .health.agent import health_agent
from .economic.agent import economic_agent
from .resources.agent import resources_agent

__all__ = [
    "weather_agent",
    "crops_agent", 
    "health_agent",
    "economic_agent",
    "resources_agent"
]