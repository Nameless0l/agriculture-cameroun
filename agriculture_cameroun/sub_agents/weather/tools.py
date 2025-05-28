# Copyright 2025 Agriculture Cameroun

"""Outils pour l'agent météorologique."""

import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any
import google.generativeai as genai
from google.adk.tools import ToolContext

# Configuration de l'API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-001')


def get_weather_forecast(
    region: str,
    tool_context: ToolContext,
    days: int = 7,
) -> Dict[str, Any]:
    """Obtient les prévisions météo pour une région.
    
    Args:
        region: Nom de la région
        days: Nombre de jours de prévision (max 14)
        tool_context: Contexte de l'outil
        
    Returns:
        Prévisions météorologiques détaillées
    """
    # Simulation de données météo réalistes pour le Cameroun
    base_temp = {
        "Nord": {"min": 22, "max": 38},
        "Centre": {"min": 19, "max": 28},
        "Littoral": {"min": 23, "max": 31},
        "Ouest": {"min": 15, "max": 25},
        "Sud": {"min": 22, "max": 29}
    }
    
    # Obtenir les températures de base pour la région
    temps = base_temp.get(region, base_temp["Centre"])
    
    # Générer les prévisions
    forecast = []
    for i in range(min(days, 14)):
        date = datetime.now() + timedelta(days=i)
        
        # Variations aléatoires réalistes
        temp_min = temps["min"] + random.randint(-2, 2)
        temp_max = temps["max"] + random.randint(-2, 2)
        
        # Probabilité de pluie selon la saison (simulée)
        month = date.month
        if month in [3, 4, 5, 9, 10, 11]:  # Saisons des pluies
            rain_chance = random.randint(40, 80)
        else:
            rain_chance = random.randint(10, 30)
        
        daily_forecast = {
            "date": date.strftime("%Y-%m-%d"),
            "temperature_min": temp_min,
            "temperature_max": temp_max,
            "humidity": random.randint(60, 85),
            "rain_probability": rain_chance,
            "wind_speed": random.randint(5, 20),
            "conditions": "Pluvieux" if rain_chance > 50 else "Partiellement nuageux"
        }
        
        forecast.append(daily_forecast)
    
    # Utiliser Gemini pour générer un résumé
    prompt = f"""
    Génère un résumé météo agricole pour la région {region} du Cameroun basé sur ces données:
    {forecast}
    
    Inclus des conseils spécifiques pour les agriculteurs.
    """
    
    response = model.generate_content(prompt)
    
    return {
        "region": region,
        "forecast": forecast,
        "summary": response.text
    }


def get_irrigation_advice(
    crop: str,
    soil_type: str,
    current_conditions: Dict[str, Any],
    tool_context: ToolContext,
) -> str:
    """Fournit des conseils d'irrigation personnalisés.
    
    Args:
        crop: Type de culture
        soil_type: Type de sol
        current_conditions: Conditions météo actuelles
        tool_context: Contexte de l'outil
        
    Returns:
        Conseils d'irrigation détaillés
    """
    prompt = f"""
    En tant qu'expert en irrigation agricole au Cameroun, fournis des conseils pour:
    - Culture: {crop}
    - Type de sol: {soil_type}
    - Conditions actuelles: {current_conditions}
    
    Inclus:
    1. Fréquence d'irrigation recommandée
    2. Quantité d'eau par irrigation
    3. Meilleur moment de la journée
    4. Techniques d'économie d'eau
    5. Signes de sur/sous-irrigation
    """
    
    response = model.generate_content(prompt)
    return response.text


def get_climate_alerts(
    region: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Vérifie les alertes climatiques pour une région.
    
    Args:
        region: Nom de la région
        tool_context: Contexte de l'outil
        
    Returns:
        Alertes météo actives
    """
    # Simulation d'alertes possibles
    possible_alerts = [
        {
            "type": "Fortes pluies",
            "severity": "Modérée",
            "description": "Risque d'inondations dans les zones basses",
            "recommendations": "Drainer les champs, protéger les récoltes"
        },
        {
            "type": "Sécheresse",
            "severity": "Élevée", 
            "description": "Période de sécheresse prolongée prévue",
            "recommendations": "Conserver l'eau, irrigation goutte-à-goutte"
        },
        {
            "type": "Vents violents",
            "severity": "Faible",
            "description": "Rafales jusqu'à 60 km/h possibles",
            "recommendations": "Tutorer les plantes hautes, sécuriser les serres"
        }
    ]
    
    # Sélectionner aléatoirement des alertes (ou aucune)
    active_alerts = []
    if random.random() > 0.7:  # 30% de chance d'avoir des alertes
        num_alerts = random.randint(1, 2)
        active_alerts = random.sample(possible_alerts, num_alerts)
    
    return {
        "region": region,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "alerts": active_alerts,
        "general_status": "Vigilance requise" if active_alerts else "Conditions normales"
    }


def analyze_rainfall_patterns(
    region: str,
    tool_context: ToolContext,
    period_months: int = 6,
) -> Dict[str, Any]:
    """Analyse les tendances pluviométriques d'une région.
    
    Args:
        region: Nom de la région
        period_months: Période d'analyse en mois
        tool_context: Contexte de l'outil
        
    Returns:
        Analyse des précipitations
    """
    # Génération de données historiques simulées
    monthly_data = []
    for i in range(period_months):
        month_date = datetime.now() - timedelta(days=i*30)
        
        # Précipitations moyennes selon la saison
        if month_date.month in [3, 4, 5, 9, 10, 11]:
            avg_rainfall = random.randint(150, 300)
        else:
            avg_rainfall = random.randint(20, 80)
        
        monthly_data.append({
            "month": month_date.strftime("%B %Y"),
            "rainfall_mm": avg_rainfall,
            "days_with_rain": random.randint(5, 20)
        })
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Analyse ces données pluviométriques pour {region}, Cameroun:
    {monthly_data}
    
    Fournis:
    1. Tendance générale (augmentation/diminution)
    2. Comparaison avec les moyennes historiques
    3. Impact sur l'agriculture
    4. Prévisions pour les prochains mois
    5. Recommandations pour les agriculteurs
    """
    
    response = model.generate_content(prompt)
    
    return {
        "region": region,
        "period": f"{period_months} derniers mois",
        "data": monthly_data,
        "analysis": response.text
    }