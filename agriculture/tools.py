# Copyright 2025 Agriculture Cameroun

"""Outils pour l'agent principal."""

from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool

from .sub_agents import (
    weather_agent,
    crops_agent,
    health_agent,
    economic_agent,
    resources_agent
)


async def call_weather_agent(
    question: str,
    region: str = None,
    tool_context: ToolContext,
):
    """Appelle l'agent météo pour les questions climatiques.
    
    Args:
        question: Question sur la météo ou le climat
        region: Région spécifique (optionnel)
        tool_context: Contexte de l'outil
    
    Returns:
        Réponse de l'agent météo
    """
    if region is None:
        region = tool_context.state["agriculture_settings"]["default_region"]
    
    agent_tool = AgentTool(agent=weather_agent)
    
    weather_input = {
        "request": question,
        "region": region
    }
    
    response = await agent_tool.run_async(
        args=weather_input,
        tool_context=tool_context
    )
    
    tool_context.state["weather_response"] = response
    return response


async def call_crops_agent(
    question: str,
    crop: str = None,
    region: str = None,
    tool_context: ToolContext,
):
    """Appelle l'agent cultures pour les questions de plantation et récolte.
    
    Args:
        question: Question sur les cultures
        crop: Culture spécifique (optionnel)
        region: Région spécifique (optionnel)
        tool_context: Contexte de l'outil
    
    Returns:
        Réponse de l'agent cultures
    """
    if region is None:
        region = tool_context.state["agriculture_settings"]["default_region"]
    
    agent_tool = AgentTool(agent=crops_agent)
    
    crops_input = {
        "request": question,
        "crop": crop,
        "region": region
    }
    
    response = await agent_tool.run_async(
        args=crops_input,
        tool_context=tool_context
    )
    
    tool_context.state["crops_response"] = response
    return response


async def call_health_agent(
    question: str,
    symptoms: str = None,
    crop: str = None,
    tool_context: ToolContext,
):
    """Appelle l'agent santé des plantes pour diagnostics et traitements.
    
    Args:
        question: Question sur la santé des plantes
        symptoms: Description des symptômes (optionnel)
        crop: Culture affectée (optionnel)
        tool_context: Contexte de l'outil
    
    Returns:
        Réponse de l'agent santé
    """
    agent_tool = AgentTool(agent=health_agent)
    
    health_input = {
        "request": question,
        "symptoms": symptoms,
        "crop": crop
    }
    
    response = await agent_tool.run_async(
        args=health_input,
        tool_context=tool_context
    )
    
    tool_context.state["health_response"] = response
    return response


async def call_economic_agent(
    question: str,
    crop: str = None,
    quantity: float = None,
    tool_context: ToolContext,
):
    """Appelle l'agent économique pour analyses de marché et rentabilité.
    
    Args:
        question: Question économique
        crop: Culture concernée (optionnel)
        quantity: Quantité en kg (optionnel)
        tool_context: Contexte de l'outil
    
    Returns:
        Réponse de l'agent économique
    """
    agent_tool = AgentTool(agent=economic_agent)
    
    economic_input = {
        "request": question,
        "crop": crop,
        "quantity": quantity
    }
    
    response = await agent_tool.run_async(
        args=economic_input,
        tool_context=tool_context
    )
    
    tool_context.state["economic_response"] = response
    return response


async def call_resources_agent(
    question: str,
    resource_type: str = None,
    crop: str = None,
    tool_context: ToolContext,
):
    """Appelle l'agent ressources pour gestion sol, eau et engrais.
    
    Args:
        question: Question sur les ressources
        resource_type: Type de ressource (sol, eau, engrais)
        crop: Culture concernée (optionnel)
        tool_context: Contexte de l'outil
    
    Returns:
        Réponse de l'agent ressources
    """
    agent_tool = AgentTool(agent=resources_agent)
    
    resources_input = {
        "request": question,
        "resource_type": resource_type,
        "crop": crop
    }
    
    response = await agent_tool.run_async(
        args=resources_input,
        tool_context=tool_context
    )
    
    tool_context.state["resources_response"] = response
    return response