# Copyright 2025 Agriculture Cameroun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Données de base pour l'agriculture camerounaise."""

from typing import Dict, List, Any
from agriculture_cameroun.config import RegionType, CropType, SoilType, SeasonType, CropInfo

# Régions du Cameroun avec leurs caractéristiques
REGIONS = {
    RegionType.CENTRE: {
        "name": "Centre",
        "climate": "Équatorial de transition",
        "rainfall_mm": "1000-1600",
        "temperature_range": "22-28°C",
        "main_crops": ["manioc", "maïs", "plantain", "arachide"],
        "soil_types": ["argileux", "lateritique"],
        "agricultural_zones": ["Yaoundé", "Mbalmayo", "Obala"]
    },
    RegionType.LITTORAL: {
        "name": "Littoral",
        "climate": "Équatorial humide",
        "rainfall_mm": "1500-4000",
        "temperature_range": "24-30°C",
        "main_crops": ["cacao", "palmier_à_huile", "plantain", "manioc"],
        "soil_types": ["argileux", "sableux"],
        "agricultural_zones": ["Douala", "Edéa", "Nkongsamba"]
    },
    RegionType.OUEST: {
        "name": "Ouest",
        "climate": "Tropical d'altitude",
        "rainfall_mm": "1500-2000",
        "temperature_range": "18-25°C",
        "main_crops": ["café", "maraîchage", "pomme_de_terre", "haricot"],
        "soil_types": ["volcanique", "humifère"],
        "agricultural_zones": ["Bafoussam", "Dschang", "Mbouda"]
    },
    RegionType.SUD: {
        "name": "Sud",
        "climate": "Équatorial humide",
        "rainfall_mm": "1500-2000",
        "temperature_range": "23-28°C",
        "main_crops": ["cacao", "café", "plantain", "manioc"],
        "soil_types": ["argileux", "lateritique"],
        "agricultural_zones": ["Ebolowa", "Sangmélima", "Kribi"]
    },
    RegionType.EST: {
        "name": "Est",
        "climate": "Équatorial humide",
        "rainfall_mm": "1500-1800",
        "temperature_range": "23-28°C",
        "main_crops": ["manioc", "plantain", "café", "cacao"],
        "soil_types": ["lateritique", "argileux"],
        "agricultural_zones": ["Bertoua", "Batouri", "Yokadouma"]
    },
    RegionType.NORD: {
        "name": "Nord",
        "climate": "Tropical sec",
        "rainfall_mm": "900-1200",
        "temperature_range": "25-35°C",
        "main_crops": ["coton", "arachide", "mil", "sorgho"],
        "soil_types": ["sableux", "argileux"],
        "agricultural_zones": ["Garoua", "Guider", "Figuil"]
    },
    RegionType.ADAMAOUA: {
        "name": "Adamaoua",
        "climate": "Tropical d'altitude",
        "rainfall_mm": "1200-1500",
        "temperature_range": "20-28°C",
        "main_crops": ["maïs", "arachide", "igname", "élevage"],
        "soil_types": ["lateritique", "volcanique"],
        "agricultural_zones": ["Ngaoundéré", "Meiganga", "Banyo"]
    },
    RegionType.EXTREME_NORD: {
        "name": "Extrême-Nord",
        "climate": "Sahélien",
        "rainfall_mm": "400-800",
        "temperature_range": "28-40°C",
        "main_crops": ["mil", "sorgho", "niébé", "arachide"],
        "soil_types": ["sableux", "argileux"],
        "agricultural_zones": ["Maroua", "Mokolo", "Kousseri"]
    },
    RegionType.NORD_OUEST: {
        "name": "Nord-Ouest",
        "climate": "Tropical d'altitude",
        "rainfall_mm": "1200-2000",
        "temperature_range": "18-26°C",
        "main_crops": ["café", "maraîchage", "igname", "maïs"],
        "soil_types": ["volcanique", "humifère"],
        "agricultural_zones": ["Bamenda", "Kumbo", "Wum"]
    },
    RegionType.SUD_OUEST: {
        "name": "Sud-Ouest",
        "climate": "Équatorial humide",
        "rainfall_mm": "2000-4000",
        "temperature_range": "22-28°C",
        "main_crops": ["palmier_à_huile", "cacao", "café", "plantain"],
        "soil_types": ["volcanique", "argileux"],
        "agricultural_zones": ["Buea", "Limbe", "Kumba"]
    }
}

# Cultures principales avec informations détaillées
CROPS = {
    CropType.CACAO: CropInfo(
        name=CropType.CACAO,
        scientific_name="Theobroma cacao",
        local_names=["Cacao", "Cocoa"],
        growth_cycle_days=365,
        optimal_temperature_min=21,
        optimal_temperature_max=32,
        water_requirements="high",
        soil_preferences=[SoilType.ARGILEUX, SoilType.HUMIFERE],
        suitable_regions=[RegionType.CENTRE, RegionType.SUD, RegionType.LITTORAL, RegionType.SUD_OUEST],
        planting_seasons=[SeasonType.SAISON_PLUIES],
        expected_yield_per_hectare=600
    ),
    CropType.CAFE: CropInfo(
        name=CropType.CAFE,
        scientific_name="Coffea arabica/robusta",
        local_names=["Café", "Coffee"],
        growth_cycle_days=365,
        optimal_temperature_min=15,
        optimal_temperature_max=24,
        water_requirements="medium",
        soil_preferences=[SoilType.VOLCANIQUE, SoilType.HUMIFERE],
        suitable_regions=[RegionType.OUEST, RegionType.NORD_OUEST, RegionType.SUD],
        planting_seasons=[SeasonType.SAISON_PLUIES],
        expected_yield_per_hectare=800
    ),
    CropType.MANIOC: CropInfo(
        name=CropType.MANIOC,
        scientific_name="Manihot esculenta",
        local_names=["Manioc", "Cassava", "Mianga"],
        growth_cycle_days=300,
        optimal_temperature_min=20,
        optimal_temperature_max=30,
        water_requirements="medium",
        soil_preferences=[SoilType.SABLEUX, SoilType.ARGILEUX, SoilType.LATERITIQUE],
        suitable_regions=list(RegionType),
        planting_seasons=[SeasonType.SAISON_PLUIES, SeasonType.PETITE_SAISON_SECHE],
        expected_yield_per_hectare=15000
    ),
    CropType.MAIS: CropInfo(
        name=CropType.MAIS,
        scientific_name="Zea mays",
        local_names=["Maïs", "Corn", "Mbong"],
        growth_cycle_days=120,
        optimal_temperature_min=18,
        optimal_temperature_max=32,
        water_requirements="medium",
        soil_preferences=[SoilType.ARGILEUX, SoilType.LIMONEUX],
        suitable_regions=[RegionType.CENTRE, RegionType.OUEST, RegionType.ADAMAOUA, RegionType.NORD],
        planting_seasons=[SeasonType.SAISON_PLUIES],
        expected_yield_per_hectare=2500
    ),
    CropType.PLANTAIN: CropInfo(
        name=CropType.PLANTAIN,
        scientific_name="Musa paradisiaca",
        local_names=["Plantain", "Kondré"],
        growth_cycle_days=365,
        optimal_temperature_min=22,
        optimal_temperature_max=30,
        water_requirements="high",
        soil_preferences=[SoilType.HUMIFERE, SoilType.ARGILEUX],
        suitable_regions=[RegionType.CENTRE, RegionType.SUD, RegionType.LITTORAL, RegionType.EST],
        planting_seasons=[SeasonType.SAISON_PLUIES],
        expected_yield_per_hectare=20000
    ),
    CropType.ARACHIDE: CropInfo(
        name=CropType.ARACHIDE,
        scientific_name="Arachis hypogaea",
        local_names=["Arachide", "Peanut", "Nkassi"],
        growth_cycle_days=120,
        optimal_temperature_min=20,
        optimal_temperature_max=30,
        water_requirements="medium",
        soil_preferences=[SoilType.SABLEUX, SoilType.LIMONEUX],
        suitable_regions=[RegionType.CENTRE, RegionType.NORD, RegionType.ADAMAOUA, RegionType.EXTREME_NORD],
        planting_seasons=[SeasonType.SAISON_PLUIES],
        expected_yield_per_hectare=1200
    )
}

# Saisons agricoles par région
SEASONS = {
    RegionType.CENTRE: {
        SeasonType.GRANDE_SAISON_SECHE: {"mois": ["décembre", "janvier", "février"], "cultures": ["préparation"]},
        SeasonType.SAISON_PLUIES: {"mois": ["mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre"], "cultures": ["plantation", "entretien"]},
    },
    RegionType.NORD: {
        SeasonType.SAISON_SECHE: {"mois": ["octobre", "novembre", "décembre", "janvier", "février", "mars", "avril", "mai"], "cultures": ["récolte", "préparation"]},
        SeasonType.SAISON_PLUIES: {"mois": ["juin", "juillet", "août", "septembre"], "cultures": ["plantation", "croissance"]},
    },
    RegionType.EXTREME_NORD: {
        SeasonType.SAISON_SECHE: {"mois": ["octobre", "novembre", "décembre", "janvier", "février", "mars", "avril", "mai"], "cultures": ["récolte", "préparation"]},
        SeasonType.SAISON_PLUIES: {"mois": ["juin", "juillet", "août", "septembre"], "cultures": ["plantation", "croissance"]},
    }
}

# Maladies et parasites communs
COMMON_DISEASES = {
    "cacao": [
        {
            "name": "Pourriture brune",
            "agent": "Phytophthora palmivora",
            "symptoms": ["Taches brunes sur fruits", "Pourriture des cabosses"],
            "treatment": ["Fongicides cupriques", "Taille sanitaire"],
            "prevention": ["Drainage", "Espacement des plants"]
        },
        {
            "name": "Mirides",
            "agent": "Sahlbergella singularis",
            "symptoms": ["Taches noires sur branches", "Dessèchement"],
            "treatment": ["Insecticides", "Taille des parties atteintes"],
            "prevention": ["Ombrage modéré", "Surveillance régulière"]
        }
    ],
    "maïs": [
        {
            "name": "Charbon du maïs",
            "agent": "Ustilago maydis",
            "symptoms": ["Galles blanches puis noires", "Déformation des épis"],
            "treatment": ["Variétés résistantes", "Rotation culturale"],
            "prevention": ["Semences saines", "Éviter l'humidité excessive"]
        }
    ]
}

# Prix moyens du marché (FCFA/kg)
MARKET_PRICES = {
    CropType.CACAO: {"min": 1000, "max": 1500, "average": 1200},
    CropType.CAFE: {"min": 1500, "max": 2500, "average": 2000},
    CropType.MANIOC: {"min": 150, "max": 300, "average": 200},
    CropType.MAIS: {"min": 200, "max": 400, "average": 300},
    CropType.PLANTAIN: {"min": 100, "max": 200, "average": 150},
    CropType.ARACHIDE: {"min": 600, "max": 1000, "average": 800}
}

# Techniques traditionnelles efficaces
TRADITIONAL_TECHNIQUES = {
    "association_culturale": {
        "description": "Culture simultanée de plusieurs espèces",
        "exemples": {
            "maïs_haricot": "Le haricot fixe l'azote pour le maïs",
            "cacao_plantain": "Le plantain fournit l'ombrage au cacao",
            "manioc_arachide": "Optimisation de l'utilisation du sol"
        }
    },
    "jachère_améliorée": {
        "description": "Rotation avec légumineuses",
        "avantages": ["Restauration fertilité", "Contrôle adventices"],
        "durée": "2-3 ans"
    },
    "compostage": {
        "description": "Valorisation des déchets organiques",
        "ingrédients": ["Résidus de récolte", "Fumier animal", "Cendres"],
        "durée_fermentation": "3-6 mois"
    }
}

# Engrais et amendements locaux
LOCAL_FERTILIZERS = {
    "fumier_bovin": {
        "type": "organique",
        "npk": "1-0.5-1",
        "dose_ha": "10-15 tonnes",
        "prix_tonne": 15000
    },
    "compost": {
        "type": "organique",
        "npk": "1.5-1-1.5",
        "dose_ha": "5-10 tonnes",
        "prix_tonne": 10000
    },
    "cendres_bois": {
        "type": "minéral",
        "elements": "K, Ca, Mg",
        "dose_ha": "500 kg",
        "prix_kg": 50
    },
    "npk_1520": {
        "type": "chimique",
        "npk": "15-20-15",
        "dose_ha": "200-300 kg",
        "prix_kg": 400
    }
}

# Outils et équipements agricoles
AGRICULTURAL_TOOLS = {
    "manuel": {
        "machette": {"prix": 2500, "usage": "Défrichage, récolte"},
        "houe": {"prix": 3000, "usage": "Travail du sol"},
        "serfouette": {"prix": 2000, "usage": "Sarclage"},
        "pulvérisateur_dos": {"prix": 25000, "usage": "Traitement phytosanitaire"}
    },
    "mécanisé": {
        "motoculteur": {"prix": 500000, "usage": "Labour, hersage"},
        "tronçonneuse": {"prix": 150000, "usage": "Abattage, élagage"},
        "motopompe": {"prix": 100000, "usage": "Irrigation"}
    }
}

# Calendrier cultural général (mois optimaux)
PLANTING_CALENDAR = {
    "zone_forestière": {
        "première_saison": {"mois": [3, 4, 5], "cultures": ["maïs", "arachide", "haricot"]},
        "deuxième_saison": {"mois": [8, 9], "cultures": ["maïs", "légumes"]},
        "toute_année": {"cultures": ["manioc", "plantain", "légumes_feuilles"]}
    },
    "zone_savane": {
        "saison_pluies": {"mois": [5, 6, 7], "cultures": ["maïs", "sorgho", "mil", "arachide", "coton"]},
        "contre_saison": {"mois": [10, 11, 12], "cultures": ["maraîchage", "riz_irrigué"]}
    }
}

def get_region_info(region: RegionType) -> Dict[str, Any]:
    """Retourne les informations d'une région."""
    return REGIONS.get(region, {})

def get_crop_info(crop: CropType) -> CropInfo:
    """Retourne les informations d'une culture."""
    return CROPS.get(crop)

def get_suitable_crops(region: RegionType) -> List[CropType]:
    """Retourne les cultures adaptées à une région."""
    suitable_crops = []
    for crop_type, crop_info in CROPS.items():
        if region in crop_info.suitable_regions:
            suitable_crops.append(crop_type)
    return suitable_crops

def get_seasonal_activities(region: RegionType, month: int) -> List[str]:
    """Retourne les activités agricoles recommandées pour un mois donné."""
    # Implémentation simplifiée
    if region in [RegionType.NORD, RegionType.EXTREME_NORD]:
        if month in [6, 7, 8, 9]:
            return ["plantation", "sarclage", "fertilisation"]
        else:
            return ["récolte", "préparation_sol", "commercialisation"]
    else:
        if month in [3, 4, 5, 8, 9]:
            return ["plantation", "entretien_cultures"]
        elif month in [12, 1, 2]:
            return ["préparation_sol", "récolte_cultures_pérennes"]
        else:
            return ["entretien_général", "surveillance_sanitaire"]

def get_market_price_range(crop: CropType) -> Dict[str, float]:
    """Retourne la fourchette de prix pour une culture."""
    return MARKET_PRICES.get(crop, {"min": 0, "max": 0, "average": 0})