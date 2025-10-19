# Copyright 2025 Agriculture Cameroun

"""Outils météo — données réelles via Open-Meteo (gratuit, sans clé).

Fallback sur une simulation déterministe si l'API est indisponible, afin que
le système reste fonctionnel en environnement de démo/offline.
"""

from __future__ import annotations

import os
import random
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict

import google.generativeai as genai
import requests
from google.adk.tools import ToolContext

# Configuration de l'API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-001")


# Coordonnées des zones agricoles clés du Cameroun (lat, lon).
REGION_COORDS: dict[str, tuple[float, float]] = {
    "Centre": (3.87, 11.52),          # Yaoundé
    "Littoral": (4.06, 9.78),         # Douala
    "Ouest": (5.48, 10.42),           # Bafoussam
    "Nord-Ouest": (5.96, 10.15),      # Bamenda
    "Sud-Ouest": (4.15, 9.23),        # Buea
    "Sud": (2.93, 11.15),             # Ebolowa
    "Est": (4.58, 13.68),             # Bertoua
    "Nord": (9.30, 13.39),            # Garoua
    "Adamaoua": (7.32, 13.58),        # Ngaoundéré
    "Extrême-Nord": (10.60, 14.33),   # Maroua
    "Extreme-Nord": (10.60, 14.33),
}

_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"


def _fetch_open_meteo(lat: float, lon: float, days: int) -> dict[str, Any] | None:
    try:
        response = requests.get(
            _OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": ",".join(
                    [
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_sum",
                        "precipitation_probability_mean",
                        "windspeed_10m_max",
                        "relative_humidity_2m_mean",
                    ]
                ),
                "timezone": "Africa/Douala",
                "forecast_days": min(days, 14),
            },
            timeout=8,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def _simulate_forecast(region: str, days: int) -> list[dict[str, Any]]:
    base_temp = {
        "Nord": {"min": 22, "max": 38},
        "Centre": {"min": 19, "max": 28},
        "Littoral": {"min": 23, "max": 31},
        "Ouest": {"min": 15, "max": 25},
        "Sud": {"min": 22, "max": 29},
    }
    temps = base_temp.get(region, base_temp["Centre"])
    forecast = []
    for i in range(min(days, 14)):
        day = datetime.now() + timedelta(days=i)
        rain = (
            random.randint(40, 80)
            if day.month in [3, 4, 5, 9, 10, 11]
            else random.randint(10, 30)
        )
        forecast.append(
            {
                "date": day.strftime("%Y-%m-%d"),
                "temperature_min": temps["min"] + random.randint(-2, 2),
                "temperature_max": temps["max"] + random.randint(-2, 2),
                "humidity": random.randint(60, 85),
                "rain_probability": rain,
                "wind_speed": random.randint(5, 20),
                "conditions": "Pluvieux" if rain > 50 else "Partiellement nuageux",
                "source": "simulated",
            }
        )
    return forecast


def get_weather_forecast(
    region: str,
    tool_context: ToolContext,
    days: int = 7,
) -> Dict[str, Any]:
    """Prévisions météo réelles via Open-Meteo (fallback simulé).

    Args:
        region: Nom de la région au Cameroun.
        days: Nombre de jours (max 14).
        tool_context: Contexte ADK.

    Returns:
        Dict avec `region`, `forecast` (liste de jours), `summary`, `source`.
    """
    coords = REGION_COORDS.get(region, REGION_COORDS["Centre"])
    raw = _fetch_open_meteo(coords[0], coords[1], days)

    if raw and "daily" in raw:
        daily = raw["daily"]
        forecast: list[dict[str, Any]] = []
        for idx, date in enumerate(daily["time"]):
            forecast.append(
                {
                    "date": date,
                    "temperature_min": daily["temperature_2m_min"][idx],
                    "temperature_max": daily["temperature_2m_max"][idx],
                    "humidity": daily["relative_humidity_2m_mean"][idx],
                    "rain_probability": daily["precipitation_probability_mean"][idx],
                    "precipitation_mm": daily["precipitation_sum"][idx],
                    "wind_speed": daily["windspeed_10m_max"][idx],
                    "conditions": _describe(
                        daily["precipitation_probability_mean"][idx],
                        daily["precipitation_sum"][idx],
                    ),
                    "source": "open-meteo",
                }
            )
        source = "open-meteo"
    else:
        forecast = _simulate_forecast(region, days)
        source = "simulated"

    prompt = (
        f"Génère un résumé météo agricole pour la région {region} du Cameroun "
        f"à partir de ces données: {forecast}\n"
        "Inclus des conseils spécifiques pour les agriculteurs (semis, "
        "traitements, irrigation)."
    )
    response = model.generate_content(prompt)

    return {
        "region": region,
        "coordinates": {"lat": coords[0], "lon": coords[1]},
        "forecast": forecast,
        "summary": response.text,
        "source": source,
    }


def _describe(rain_prob: float | None, precipitation_mm: float | None) -> str:
    prob = rain_prob or 0
    mm = precipitation_mm or 0
    if mm > 20 or prob > 80:
        return "Pluies fortes"
    if mm > 5 or prob > 50:
        return "Pluvieux"
    if prob > 30:
        return "Averses possibles"
    return "Temps sec"


def get_irrigation_advice(
    crop: str,
    soil_type: str,
    current_conditions: Dict[str, Any],
    tool_context: ToolContext,
) -> str:
    """Conseils d'irrigation personnalisés (inchangé — basé sur Gemini)."""
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
    """Alertes climatiques dérivées des prévisions Open-Meteo.

    Génère des alertes réelles basées sur les seuils (pluies fortes >30 mm/jour,
    rafales >50 km/h, forte chaleur >38°C, humidité prolongée >90%).
    """
    coords = REGION_COORDS.get(region, REGION_COORDS["Centre"])
    raw = _fetch_open_meteo(coords[0], coords[1], 7)
    alerts: list[dict[str, Any]] = []

    if raw and "daily" in raw:
        daily = raw["daily"]
        for idx, date in enumerate(daily["time"]):
            precip = daily["precipitation_sum"][idx] or 0
            wind = daily["windspeed_10m_max"][idx] or 0
            tmax = daily["temperature_2m_max"][idx] or 0
            hum = daily["relative_humidity_2m_mean"][idx] or 0
            if precip > 30:
                alerts.append(
                    {
                        "date": date,
                        "type": "Fortes pluies",
                        "severity": "Élevée" if precip > 50 else "Modérée",
                        "value": f"{precip} mm",
                        "recommendations": "Drainer les parcelles, protéger semis et récoltes.",
                    }
                )
            if wind > 50:
                alerts.append(
                    {
                        "date": date,
                        "type": "Vents violents",
                        "severity": "Modérée",
                        "value": f"{wind} km/h",
                        "recommendations": "Tuteurer les cultures hautes, sécuriser les serres.",
                    }
                )
            if tmax > 38:
                alerts.append(
                    {
                        "date": date,
                        "type": "Forte chaleur",
                        "severity": "Modérée",
                        "value": f"{tmax}°C",
                        "recommendations": "Paillage, arrosage aux heures fraîches.",
                    }
                )
            if hum > 90:
                alerts.append(
                    {
                        "date": date,
                        "type": "Humidité élevée prolongée",
                        "severity": "Faible",
                        "value": f"{hum}%",
                        "recommendations": "Surveiller cercosporiose/mildiou, aérer la parcelle.",
                    }
                )
        source = "open-meteo"
    else:
        source = "no-data"

    return {
        "region": region,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "alerts": alerts,
        "general_status": "Vigilance requise" if alerts else "Conditions normales",
        "source": source,
    }


def analyze_rainfall_patterns(
    region: str,
    tool_context: ToolContext,
    period_months: int = 6,
) -> Dict[str, Any]:
    """Analyse des précipitations sur les N derniers mois via Open-Meteo Archive."""
    coords = REGION_COORDS.get(region, REGION_COORDS["Centre"])
    end = datetime.now().date()
    start = end - timedelta(days=period_months * 30)

    try:
        response = requests.get(
            _OPEN_METEO_ARCHIVE,
            params={
                "latitude": coords[0],
                "longitude": coords[1],
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "daily": "precipitation_sum",
                "timezone": "Africa/Douala",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        data = None

    monthly_data: list[dict[str, Any]] = []
    if data and "daily" in data:
        buckets: dict[str, list[float]] = {}
        for date_str, value in zip(
            data["daily"]["time"], data["daily"]["precipitation_sum"]
        ):
            month = date_str[:7]
            buckets.setdefault(month, []).append(value or 0.0)
        for month, values in sorted(buckets.items()):
            monthly_data.append(
                {
                    "month": month,
                    "rainfall_mm": round(sum(values), 1),
                    "days_with_rain": sum(1 for v in values if v > 1.0),
                    "max_day_mm": round(max(values), 1) if values else 0.0,
                    "mean_day_mm": round(statistics.mean(values), 1) if values else 0.0,
                }
            )
        source = "open-meteo-archive"
    else:
        source = "simulated"
        for i in range(period_months):
            month_date = datetime.now() - timedelta(days=i * 30)
            avg = (
                random.randint(150, 300)
                if month_date.month in [3, 4, 5, 9, 10, 11]
                else random.randint(20, 80)
            )
            monthly_data.append(
                {
                    "month": month_date.strftime("%Y-%m"),
                    "rainfall_mm": avg,
                    "days_with_rain": random.randint(5, 20),
                }
            )

    prompt = (
        f"Analyse ces données pluviométriques pour {region}, Cameroun: "
        f"{monthly_data}\n"
        "Fournis: tendance générale, comparaison moyennes historiques, "
        "impact agricole, prévisions prochains mois, recommandations."
    )
    analysis = model.generate_content(prompt).text

    return {
        "region": region,
        "period": f"{period_months} derniers mois",
        "data": monthly_data,
        "analysis": analysis,
        "source": source,
    }
