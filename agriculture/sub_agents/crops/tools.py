# Copyright 2025 Agriculture Cameroun

"""Outils pour l'agent de gestion des cultures."""

import os
from typing import Dict, List, Any
import google.generativeai as genai
from google.adk.tools import ToolContext

# Configuration de l'API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-001')


def get_planting_calendar(
    crop: str,
    region: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Génère un calendrier de plantation détaillé.
    
    Args:
        crop: Type de culture
        region: Région du Cameroun
        tool_context: Contexte de l'outil
        
    Returns:
        Calendrier de plantation avec dates et activités
    """
    prompt = f"""
    En tant qu'agronome expert au Cameroun, crée un calendrier de plantation détaillé pour:
    - Culture: {crop}
    - Région: {region}
    
    Le calendrier doit inclure:
    1. Période optimale de semis/plantation
    2. Préparation du sol (timing et méthodes)
    3. Étapes de croissance avec durées
    4. Périodes d'entretien (sarclage, buttage)
    5. Application d'engrais (timing et types)
    6. Période de récolte optimale
    7. Activités post-récolte
    
    Adapte selon le climat local et les pratiques traditionnelles efficaces.
    Format: structure JSON avec mois et activités.
    """
    
    response = model.generate_content(prompt)
    
    # Parser la réponse pour extraire le calendrier
    calendar_data = {
        "crop": crop,
        "region": region,
        "calendar": response.text,
        "cycle_duration": "Variable selon la variété"
    }
    
    return calendar_data


def get_crop_rotation_advice(
    current_crop: str,
    soil_type: str,
    field_history: List[str] = None,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Recommande un plan de rotation des cultures.
    
    Args:
        current_crop: Culture actuelle
        soil_type: Type de sol
        field_history: Historique des cultures (optionnel)
        tool_context: Contexte de l'outil
        
    Returns:
        Plan de rotation recommandé
    """
    history_str = ", ".join(field_history) if field_history else "Non spécifié"
    
    prompt = f"""
    Expert en rotation des cultures au Cameroun, recommande un plan de rotation pour:
    - Culture actuelle: {current_crop}
    - Type de sol: {soil_type}
    - Historique du champ: {history_str}
    
    Fournis:
    1. Prochaine culture recommandée (avec justification)
    2. Plan de rotation sur 3-4 ans
    3. Cultures de couverture/engrais verts à intégrer
    4. Bénéfices attendus (fertilité, contrôle parasites)
    5. Associations culturales bénéfiques
    6. Estimation des rendements
    
    Considère les pratiques locales et la rentabilité économique.
    """
    
    response = model.generate_content(prompt)
    
    return {
        "current_crop": current_crop,
        "soil_type": soil_type,
        "rotation_plan": response.text
    }


def get_variety_recommendations(
    crop: str,
    region: str,
    priorities: List[str] = None,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Recommande les meilleures variétés pour une culture.
    
    Args:
        crop: Type de culture
        region: Région du Cameroun
        priorities: Priorités (rendement, résistance, précocité)
        tool_context: Contexte de l'outil
        
    Returns:
        Variétés recommandées avec caractéristiques
    """
    priorities_str = ", ".join(priorities) if priorities else "Rendement et adaptation locale"
    
    prompt = f"""
    En tant qu'expert en sélection variétale au Cameroun, recommande les meilleures variétés pour:
    - Culture: {crop}
    - Région: {region}
    - Priorités: {priorities_str}
    
    Pour chaque variété recommandée, fournis:
    1. Nom de la variété (local et scientifique si applicable)
    2. Caractéristiques principales
    3. Rendement potentiel
    4. Cycle de croissance
    5. Résistance aux maladies/parasites
    6. Exigences spécifiques
    7. Disponibilité des semences
    8. Coût approximatif
    
    Inclus les variétés locales performantes et les variétés améliorées disponibles.
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "region": region,
        "priorities": priorities_str,
        "recommendations": response.text
    }


def get_cultivation_techniques(
    crop: str,
    farming_system: str = "Traditionnel",
    constraints: List[str] = None,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Fournit des techniques de culture adaptées.
    
    Args:
        crop: Type de culture
        farming_system: Système agricole (traditionnel, moderne, mixte)
        constraints: Contraintes (budget, main d'œuvre, équipement)
        tool_context: Contexte de l'outil
        
    Returns:
        Techniques de culture recommandées
    """
    constraints_str = ", ".join(constraints) if constraints else "Budget limité"
    
    prompt = f"""
    Expert en techniques culturales au Cameroun, fournis un guide pour:
    - Culture: {crop}
    - Système: {farming_system}
    - Contraintes: {constraints_str}
    
    Détaille:
    1. Préparation du sol (méthodes adaptées)
    2. Techniques de semis/plantation
    3. Espacement et densité optimaux
    4. Gestion de l'eau (irrigation si nécessaire)
    5. Fertilisation (organique et minérale)
    6. Contrôle des adventices
    7. Protection des cultures (méthodes intégrées)
    8. Techniques de récolte
    9. Innovations simples applicables
    10. Estimation des coûts
    
    Privilégie les solutions économiques et durables.
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "system": farming_system,
        "techniques": response.text
    }