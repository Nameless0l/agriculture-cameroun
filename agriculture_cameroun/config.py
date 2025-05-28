# Copyright 2025 Agriculture Cameroun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Configuration module for Agriculture Cameroun multi-agent system."""

import os
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgricultureBaseModel(BaseModel):
    """Base model for all Agriculture Cameroun data structures."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='forbid',
        validate_assignment=True,
        str_strip_whitespace=True,
        frozen=False
    )


class RegionType(str, Enum):
    """Types de régions du Cameroun."""
    CENTRE = "Centre"
    LITTORAL = "Littoral"
    OUEST = "Ouest"
    SUD = "Sud"
    EST = "Est"
    NORD = "Nord"
    ADAMAOUA = "Adamaoua"
    EXTREME_NORD = "Extrême-Nord"
    NORD_OUEST = "Nord-Ouest"
    SUD_OUEST = "Sud-Ouest"


class CropType(str, Enum):
    """Types principaux de cultures."""
    CACAO = "cacao"
    CAFE = "café"
    MANIOC = "manioc"
    MAIS = "maïs"
    PLANTAIN = "plantain"
    ARACHIDE = "arachide"
    IGNAME = "igname"
    COTON = "coton"
    PALMIER_HUILE = "palmier_à_huile"
    TOMATE = "tomate"
    GOMBO = "gombo"
    PIMENT = "piment"


class SoilType(str, Enum):
    """Types de sol."""
    ARGILEUX = "argileux"
    SABLEUX = "sableux"
    LIMONEUX = "limoneux"
    LATERITIQUE = "latéritique"
    VOLCANIQUE = "volcanique"
    HUMIFERE = "humifère"


class SeasonType(str, Enum):
    """Saisons agricoles."""
    SAISON_SECHE = "saison_sèche"
    SAISON_PLUIES = "saison_des_pluies"
    PETITE_SAISON_SECHE = "petite_saison_sèche"
    GRANDE_SAISON_SECHE = "grande_saison_sèche"


class AgricultureConfig(AgricultureBaseModel):
    """Configuration principale du système agricole."""
    
    default_region: RegionType = RegionType.CENTRE
    default_language: str = "fr"
    currency: str = "FCFA"
    temperature_unit: str = "celsius"
    distance_unit: str = "km"
    area_unit: str = "hectare"
    weight_unit: str = "kg"
    
    # Modèles d'IA
    root_agent_model: str = Field(default="gemini-2.0-flash-001")
    weather_agent_model: str = Field(default="gemini-2.0-flash-001")
    crops_agent_model: str = Field(default="gemini-2.0-flash-001")
    health_agent_model: str = Field(default="gemini-2.0-flash-001")
    economic_agent_model: str = Field(default="gemini-2.0-flash-001")
    resources_agent_model: str = Field(default="gemini-2.0-flash-001")
    
    # Configuration API
    gemini_api_key: Optional[str] = Field(default=None)
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # Configuration base de données
    enable_data_persistence: bool = False
    data_storage_path: str = "./data"
    
    @field_validator('gemini_api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v:
            v = os.getenv("GEMINI_API_KEY")
        if not v:
            raise ValueError("GEMINI_API_KEY est requis")
        return v


class WeatherData(AgricultureBaseModel):
    """Structure des données météorologiques."""
    
    date: str
    region: RegionType
    temperature_min: float
    temperature_max: float
    humidity: float = Field(ge=0, le=100)
    rain_probability: float = Field(ge=0, le=100)
    rainfall_mm: Optional[float] = Field(default=None, ge=0)
    wind_speed: float = Field(ge=0)
    conditions: str


class CropInfo(AgricultureBaseModel):
    """Informations sur une culture."""
    
    name: CropType
    scientific_name: Optional[str] = None
    local_names: List[str] = Field(default_factory=list)
    growth_cycle_days: int = Field(gt=0)
    optimal_temperature_min: float
    optimal_temperature_max: float
    water_requirements: str  # "low", "medium", "high"
    soil_preferences: List[SoilType] = Field(default_factory=list)
    suitable_regions: List[RegionType] = Field(default_factory=list)
    planting_seasons: List[SeasonType] = Field(default_factory=list)
    expected_yield_per_hectare: float = Field(gt=0)


class MarketPrice(AgricultureBaseModel):
    """Prix du marché pour une culture."""
    
    crop: CropType
    region: RegionType
    price_per_kg: float = Field(gt=0)
    currency: str = "FCFA"
    date: str
    market_location: str
    quality_grade: str = "standard"  # "premium", "standard", "low"


class FarmingAdvice(AgricultureBaseModel):
    """Conseil agricole."""
    
    title: str
    category: str  # "planting", "irrigation", "fertilization", "pest_control", etc.
    crop: Optional[CropType] = None
    region: Optional[RegionType] = None
    season: Optional[SeasonType] = None
    advice_text: str
    estimated_cost_fcfa: Optional[float] = None
    urgency_level: str = "medium"  # "low", "medium", "high", "urgent"
    source: str = "agriculture_agent"


class HealthIssue(AgricultureBaseModel):
    """Problème de santé des plantes."""
    
    issue_type: str  # "disease", "pest", "nutrient_deficiency", "environmental"
    name: str
    symptoms: List[str]
    affected_crops: List[CropType]
    severity_level: str = "medium"  # "low", "medium", "high", "critical"
    treatment_options: List[str] = Field(default_factory=list)
    prevention_measures: List[str] = Field(default_factory=list)
    estimated_treatment_cost: Optional[float] = None


class ResourceRecommendation(AgricultureBaseModel):
    """Recommandation de ressources."""
    
    resource_type: str  # "fertilizer", "pesticide", "irrigation", "equipment"
    name: str
    description: str
    crop: Optional[CropType] = None
    application_rate: Optional[str] = None
    application_timing: Optional[str] = None
    estimated_cost_per_hectare: Optional[float] = None
    availability: str = "available"  # "available", "seasonal", "limited", "unavailable"
    local_suppliers: List[str] = Field(default_factory=list)


# Configuration globale par défaut
DEFAULT_CONFIG = AgricultureConfig()


def get_config() -> AgricultureConfig:
    """Retourne la configuration actuelle."""
    return DEFAULT_CONFIG


def update_config(**kwargs) -> None:
    """Met à jour la configuration globale."""
    global DEFAULT_CONFIG
    for key, value in kwargs.items():
        if hasattr(DEFAULT_CONFIG, key):
            setattr(DEFAULT_CONFIG, key, value)


# Validation des variables d'environnement requises
def validate_environment():
    """Valide que toutes les variables d'environnement requises sont définies."""
    required_vars = ["GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(
            f"Variables d'environnement manquantes: {', '.join(missing_vars)}"
        )


# Classes utilitaires pour les réponses des agents
class AgentResponse(AgricultureBaseModel):
    """Réponse standard d'un agent."""
    
    agent_name: str
    response_text: str
    confidence_score: float = Field(ge=0, le=1)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_seconds: Optional[float] = None


class MultiAgentResponse(AgricultureBaseModel):
    """Réponse combinée de plusieurs agents."""
    
    primary_agent: str
    agent_responses: List[AgentResponse]
    final_recommendation: str
    total_processing_time: float
    correlation_score: float = Field(ge=0, le=1)  # Cohérence entre les réponses