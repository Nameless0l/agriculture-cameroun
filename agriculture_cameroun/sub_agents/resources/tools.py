# Copyright 2025 Agriculture Cameroun

"""Outils pour l'agent de gestion des ressources."""

import os
import random
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from google.adk.tools import ToolContext
from typing import Optional
from agriculture_cameroun.config import CropType, RegionType, SoilType
from ...utils.data import LOCAL_FERTILIZERS, get_crop_info, get_region_info

# Configuration de l'API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-001')


def analyze_soil_requirements(
    crop: str,
    region: str,
    tool_context: ToolContext,
    soil_type: Optional[str] = None,
    current_ph: Optional[float] = None,
) -> Dict[str, Any]:
    """Analyse les exigences du sol pour une culture donnée.
    
    Args:
        crop: Type de culture
        region: Région de culture
        soil_type: Type de sol (optionnel)
        current_ph: pH actuel du sol (optionnel)
        tool_context: Contexte de l'outil
        
    Returns:
        Analyse complète des exigences du sol
    """
    # Exigences par culture
    crop_requirements = {
        "cacao": {
            "ph_optimal": {"min": 6.0, "max": 7.0},
            "depth_cm": 150,
            "drainage": "bien drainé",
            "organic_matter_percent": {"min": 3.0, "optimal": 5.0},
            "texture_preferred": ["argileux", "argilo-limoneux"],
            "nutrients": {"N": "élevé", "P": "modéré", "K": "élevé", "Ca": "élevé", "Mg": "modéré"}
        },
        "café": {
            "ph_optimal": {"min": 6.0, "max": 6.8},
            "depth_cm": 120,
            "drainage": "bien drainé",
            "organic_matter_percent": {"min": 4.0, "optimal": 6.0},
            "texture_preferred": ["volcanique", "argilo-limoneux"],
            "nutrients": {"N": "élevé", "P": "modéré", "K": "élevé", "Ca": "élevé", "Mg": "élevé"}
        },
        "maïs": {
            "ph_optimal": {"min": 5.8, "max": 7.0},
            "depth_cm": 80,
            "drainage": "bien drainé à modéré",
            "organic_matter_percent": {"min": 2.0, "optimal": 4.0},
            "texture_preferred": ["limoneux", "argilo-limoneux"],
            "nutrients": {"N": "très élevé", "P": "élevé", "K": "élevé", "Ca": "modéré", "Mg": "modéré"}
        },
        "manioc": {
            "ph_optimal": {"min": 5.5, "max": 6.5},
            "depth_cm": 60,
            "drainage": "bien drainé",
            "organic_matter_percent": {"min": 1.5, "optimal": 3.0},
            "texture_preferred": ["sableux", "sablo-limoneux"],
            "nutrients": {"N": "modéré", "P": "modéré", "K": "élevé", "Ca": "modéré", "Mg": "faible"}
        },
        "plantain": {
            "ph_optimal": {"min": 6.0, "max": 7.5},
            "depth_cm": 100,
            "drainage": "modéré à humide",
            "organic_matter_percent": {"min": 3.0, "optimal": 5.0},
            "texture_preferred": ["argileux", "argilo-limoneux"],
            "nutrients": {"N": "très élevé", "P": "élevé", "K": "très élevé", "Ca": "élevé", "Mg": "élevé"}
        },
        "arachide": {
            "ph_optimal": {"min": 6.0, "max": 7.0},
            "depth_cm": 50,
            "drainage": "bien drainé",
            "organic_matter_percent": {"min": 2.0, "optimal": 3.5},
            "texture_preferred": ["sableux", "sablo-limoneux"],
            "nutrients": {"N": "faible", "P": "élevé", "K": "modéré", "Ca": "élevé", "Mg": "modéré"}
        }
    }
    
    # Caractéristiques des sols par région
    regional_soils = {
        "Centre": {
            "dominant_type": "ferrallitique",
            "average_ph": 4.8,
            "organic_matter": 2.5,
            "main_constraints": ["acidité", "pauvreté en bases", "lixiviation"],
            "advantages": ["profondeur", "pas de toxicité aluminique sévère"]
        },
        "Ouest": {
            "dominant_type": "volcanique", 
            "average_ph": 5.8,
            "organic_matter": 4.2,
            "main_constraints": ["pentes", "érosion potentielle"],
            "advantages": ["fertilité naturelle", "rétention eau", "structure"]
        },
        "Nord": {
            "dominant_type": "ferrugineux",
            "average_ph": 6.2,
            "organic_matter": 1.8,
            "main_constraints": ["faible MO", "carence P", "battance"],
            "advantages": ["pas d'acidité", "bonne base"]
        }
    }
    
    # Obtenir les exigences de la culture
    requirements = crop_requirements.get(crop, crop_requirements["maïs"])
    regional_data = regional_soils.get(region, regional_soils["Centre"])
    
    # Évaluation de l'adéquation
    ph_current = current_ph if current_ph else regional_data["average_ph"]
    ph_optimal = requirements["ph_optimal"]
    
    ph_adequacy = "optimal" if ph_optimal["min"] <= ph_current <= ph_optimal["max"] else (
        "trop acide" if ph_current < ph_optimal["min"] else "trop alcalin"
    )
    
    # Recommandations d'amélioration
    improvements = []
    if ph_adequacy == "trop acide":
        lime_needed = (ph_optimal["min"] - ph_current) * 2  # Estimation simplifiée
        improvements.append({
            "action": "Chaulage",
            "quantity": f"{lime_needed:.1f} tonnes/ha de chaux agricole",
            "cost_fcfa": lime_needed * 50000,
            "priority": "élevée"
        })
    
    if regional_data["organic_matter"] < requirements["organic_matter_percent"]["min"]:
        organic_deficit = requirements["organic_matter_percent"]["optimal"] - regional_data["organic_matter"]
        compost_needed = organic_deficit * 20  # Estimation
        improvements.append({
            "action": "Apport matière organique",
            "quantity": f"{compost_needed:.0f} tonnes/ha de compost",
            "cost_fcfa": compost_needed * 10000,
            "priority": "élevée"
        })
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Analyse des exigences du sol pour {crop} en région {region} du Cameroun:
    
    Exigences de la culture: {requirements}
    Caractéristiques sol régional: {regional_data}
    pH actuel: {ph_current}
    Adéquation pH: {ph_adequacy}
    Type de sol: {soil_type or regional_data['dominant_type']}
    
    Améliorations identifiées: {improvements}
    
    Fournis une analyse complète incluant:
    1. Évaluation de l'adéquation sol-culture
    2. Facteurs limitants identifiés
    3. Plan d'amélioration détaillé avec chronologie
    4. Techniques d'amendement appropriées
    5. Coûts estimés et retour sur investissement
    6. Suivi et indicateurs de réussite
    7. Alternatives si contraintes trop importantes
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "region": region,
        "soil_type": soil_type or regional_data["dominant_type"],
        "requirements": requirements,
        "current_conditions": {
            "ph": ph_current,
            "organic_matter": regional_data["organic_matter"],
            "main_constraints": regional_data["main_constraints"]
        },
        "adequacy_assessment": {
            "ph_status": ph_adequacy,
            "overall_suitability": "moyenne" if improvements else "bonne"
        },
        "improvement_plan": improvements,
        "total_improvement_cost": sum(imp["cost_fcfa"] for imp in improvements),
        "soil_analysis": response.text
    }


def recommend_fertilizers(
    crop: str,
    area_hectares: float,
    tool_context: ToolContext,
    soil_fertility: str = "moyenne",
    budget_level: str = "modéré",
) -> Dict[str, Any]:
    """Recommande un plan de fertilisation adapté.
    
    Args:
        crop: Type de culture
        area_hectares: Superficie à fertiliser
        soil_fertility: Niveau de fertilité du sol
        budget_level: Niveau de budget disponible
        tool_context: Contexte de l'outil
        
    Returns:
        Plan de fertilisation détaillé
    """
    # Besoins nutritifs par culture (kg/ha)
    nutrient_needs = {
        "cacao": {"N": 120, "P2O5": 40, "K2O": 150, "Ca": 80, "Mg": 30},
        "café": {"N": 150, "P2O5": 50, "K2O": 180, "Ca": 100, "Mg": 40},
        "maïs": {"N": 200, "P2O5": 80, "K2O": 160, "Ca": 50, "Mg": 25},
        "manioc": {"N": 80, "P2O5": 40, "K2O": 120, "Ca": 30, "Mg": 15},
        "plantain": {"N": 250, "P2O5": 100, "K2O": 300, "Ca": 120, "Mg": 50},
        "arachide": {"N": 30, "P2O5": 60, "K2O": 80, "Ca": 80, "Mg": 20}
    }
    
    # Facteurs de correction selon fertilité
    fertility_factors = {
        "faible": 1.3,
        "moyenne": 1.0,
        "bonne": 0.8,
        "élevée": 0.6
    }
    
    # Obtenir les besoins ajustés
    base_needs = nutrient_needs.get(crop, nutrient_needs["maïs"])
    fertility_factor = fertility_factors.get(soil_fertility, 1.0)
    adjusted_needs = {k: v * fertility_factor for k, v in base_needs.items()}
    
    # Sélection d'engrais selon budget
    if budget_level == "limité":
        fertilizer_priority = ["fumier_bovin", "compost", "cendres_bois"]
        max_chemical_percent = 20
    elif budget_level == "modéré":
        fertilizer_priority = ["compost", "npk_1520", "fumier_bovin"]
        max_chemical_percent = 50
    else:  # élevé
        fertilizer_priority = ["npk_1520", "urée", "compost"]
        max_chemical_percent = 80
    
    # Plan de fertilisation
    fertilization_plan = []
    remaining_needs = adjusted_needs.copy()
    total_cost = 0
    
    # Engrais organiques de base (toujours recommandés)
    organic_base = {
        "product": "compost",
        "quantity_per_ha": 5,  # tonnes
        "total_quantity": 5 * area_hectares,
        "nutrient_supply": {"N": 75, "P2O5": 50, "K2O": 75},
        "cost_per_unit": 10000,  # FCFA/tonne
        "application_timing": "avant plantation",
        "benefits": ["améliore structure sol", "stimule vie microbienne", "libération lente"]
    }
    
    fertilization_plan.append(organic_base)
    total_cost += organic_base["total_quantity"] * organic_base["cost_per_unit"]
    
    # Réduction des besoins par apport organique
    for nutrient, supply in organic_base["nutrient_supply"].items():
        if nutrient in remaining_needs:
            remaining_needs[nutrient] = max(0, remaining_needs[nutrient] - supply)
    
    # Compléments minéraux si nécessaire
    if any(need > 20 for need in remaining_needs.values()):
        if remaining_needs["N"] > 20:
            n_fertilizer = {
                "product": "urée (46% N)",
                "quantity_per_ha": remaining_needs["N"] / 0.46,
                "total_quantity": (remaining_needs["N"] / 0.46) * area_hectares,
                "nutrient_supply": {"N": remaining_needs["N"]},
                "cost_per_unit": 450,  # FCFA/kg
                "application_timing": "fractionnée (plantation + 45j + 90j)",
                "precautions": ["appliquer avant pluie", "ne pas mettre sur feuilles"]
            }
            fertilization_plan.append(n_fertilizer)
            total_cost += n_fertilizer["total_quantity"] * n_fertilizer["cost_per_unit"]
        
        if remaining_needs["P2O5"] > 20:
            p_fertilizer = {
                "product": "phosphate naturel",
                "quantity_per_ha": remaining_needs["P2O5"] / 0.28,
                "total_quantity": (remaining_needs["P2O5"] / 0.28) * area_hectares,
                "nutrient_supply": {"P2O5": remaining_needs["P2O5"]},
                "cost_per_unit": 300,  # FCFA/kg
                "application_timing": "à la plantation",
                "benefits": ["effet résiduel long", "améliore enracinement"]
            }
            fertilization_plan.append(p_fertilizer)
            total_cost += p_fertilizer["total_quantity"] * p_fertilizer["cost_per_unit"]
    
    # Utiliser Gemini pour les recommandations
    prompt = f"""
    Plan de fertilisation pour {crop} au Cameroun:
    
    Superficie: {area_hectares} ha
    Fertilité sol: {soil_fertility}
    Budget: {budget_level}
    Besoins nutritifs ajustés: {adjusted_needs}
    
    Plan proposé: {fertilization_plan}
    Coût total: {total_cost:,.0f} FCFA
    
    Optimise le plan en considérant:
    1. Efficacité agronomique des apports
    2. Fractionnement et timing d'application
    3. Compatibilités et synergies entre engrais
    4. Alternatives locales moins coûteuses
    5. Méthodes d'application recommandées
    6. Précautions d'usage et stockage
    7. Indicateurs de suivi d'efficacité
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "area_hectares": area_hectares,
        "soil_fertility": soil_fertility,
        "budget_level": budget_level,
        "nutrient_needs": adjusted_needs,
        "fertilization_plan": fertilization_plan,
        "total_cost": total_cost,
        "cost_per_hectare": total_cost / area_hectares,
        "recommendations": response.text,
        "application_calendar": {
            "avant_plantation": ["compost", "phosphate"],
            "plantation": ["engrais starter"],
            "45_jours": ["urée fraction 1"],
            "90_jours": ["urée fraction 2", "potasse"]
        }
    }


def optimize_irrigation(
    crop: str,
    region: str,
    area_hectares: float,
    tool_context: ToolContext,
    water_source: str = "pluie",
) -> Dict[str, Any]:
    """Optimise la gestion de l'irrigation.
    
    Args:
        crop: Type de culture
        region: Région de culture
        area_hectares: Superficie à irriguer
        water_source: Source d'eau disponible
        tool_context: Contexte de l'outil
        
    Returns:
        Plan d'irrigation optimisé
    """
    # Besoins en eau par culture (mm/cycle)
    water_requirements = {
        "cacao": {"min": 1200, "optimal": 1800, "critical_periods": ["floraison", "développement fruits"]},
        "café": {"min": 1000, "optimal": 1500, "critical_periods": ["floraison", "grossissement grains"]},
        "maïs": {"min": 450, "optimal": 600, "critical_periods": ["floraison", "remplissage grains"]},
        "manioc": {"min": 600, "optimal": 1000, "critical_periods": ["établissement", "tubérisation"]},
        "plantain": {"min": 1200, "optimal": 1800, "critical_periods": ["toute l'année"]},
        "arachide": {"min": 400, "optimal": 550, "critical_periods": ["floraison", "formation gousses"]}
    }
    
    # Précipitations moyennes par région (mm/an)
    regional_rainfall = {
        "Centre": 1400,
        "Littoral": 2800,
        "Ouest": 1800,
        "Sud": 1600,
        "Est": 1500,
        "Nord": 1000,
        "Adamaoua": 1300,
        "Extrême-Nord": 600,
        "Nord-Ouest": 1600,
        "Sud-Ouest": 3000
    }
    
    crop_needs = water_requirements.get(crop, water_requirements["maïs"])
    annual_rainfall = regional_rainfall.get(region, 1200)
    
    # Calcul du déficit hydrique
    water_deficit = max(0, crop_needs["optimal"] - annual_rainfall)
    irrigation_needed = water_deficit > 100  # Si déficit > 100mm
    
    # Systèmes d'irrigation recommandés
    irrigation_systems = {
        "goutte_à_goutte": {
            "efficiency": 0.9,
            "cost_per_ha": 800000,
            "water_saving": 0.5,
            "suitable_crops": ["maraîchage", "arbres fruitiers"],
            "maintenance": "modérée"
        },
        "aspersion": {
            "efficiency": 0.75,
            "cost_per_ha": 400000,
            "water_saving": 0.3,
            "suitable_crops": ["céréales", "légumineuses"],
            "maintenance": "élevée"
        },
        "gravitaire": {
            "efficiency": 0.6,
            "cost_per_ha": 150000,
            "water_saving": 0.1,
            "suitable_crops": ["riz", "maraîchage"],
            "maintenance": "faible"
        },
        "micro_aspersion": {
            "efficiency": 0.8,
            "cost_per_ha": 600000,
            "water_saving": 0.4,
            "suitable_crops": ["plantain", "agrumes"],
            "maintenance": "modérée"
        }
    }
    
    # Recommandation système selon culture et budget
    if crop in ["cacao", "café", "plantain"]:
        recommended_system = "micro_aspersion"
    elif crop in ["maïs", "arachide"]:
        recommended_system = "aspersion"
    else:
        recommended_system = "goutte_à_goutte"
    
    system_data = irrigation_systems[recommended_system]
    total_cost = system_data["cost_per_ha"] * area_hectares
    
    # Calendrier d'irrigation
    irrigation_schedule = {
        "fréquence": "tous les 3-5 jours selon saison",
        "durée_application": "2-4 heures/application",
        "période_critique": crop_needs["critical_periods"],
        "ajustements_saisonniers": {
            "saison_sèche": "irrigation quotidienne si nécessaire",
            "saison_pluies": "irrigation d'appoint seulement",
            "début_pluies": "réduction progressive"
        }
    }
    
    # Techniques de conservation de l'eau
    water_conservation = [
        {"technique": "Paillage", "water_saving": 30, "cost_fcfa": 20000, "implementation": "facile"},
        {"technique": "Brise-vent", "water_saving": 15, "cost_fcfa": 50000, "implementation": "moyenne"},
        {"technique": "Récupération eau pluie", "water_saving": 0, "cost_fcfa": 100000, "implementation": "complexe"},
        {"technique": "Amélioration sol", "water_saving": 25, "cost_fcfa": 30000, "implementation": "facile"}
    ]
    
    # Utiliser Gemini pour l'optimisation
    prompt = f"""
    Optimisation irrigation pour {crop} en région {region} du Cameroun:
    
    Besoins en eau: {crop_needs}
    Précipitations région: {annual_rainfall} mm/an
    Déficit hydrique: {water_deficit} mm
    Superficie: {area_hectares} ha
    Source d'eau: {water_source}
    
    Système recommandé: {recommended_system}
    Coût installation: {total_cost:,.0f} FCFA
    Techniques conservation: {water_conservation}
    
    Propose un plan complet incluant:
    1. Stratégie d'irrigation adaptée à la région
    2. Dimensionnement du système (débit, réservoirs)
    3. Calendrier d'irrigation précis
    4. Techniques complémentaires d'économie d'eau
    5. Coûts d'exploitation annuels
    6. Retour sur investissement estimé
    7. Maintenance préventive requise
    8. Alternatives en cas de pénurie d'eau
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "region": region,
        "area_hectares": area_hectares,
        "water_source": water_source,
        "water_analysis": {
            "annual_rainfall": annual_rainfall,
            "crop_needs": crop_needs,
            "deficit": water_deficit,
            "irrigation_required": irrigation_needed
        },
        "recommended_system": {
            "type": recommended_system,
            "specifications": system_data,
            "total_cost": total_cost
        },
        "irrigation_schedule": irrigation_schedule,
        "conservation_techniques": water_conservation,
        "optimization_plan": response.text
    }


def assess_land_suitability(
    crop: str,
    region: str,
    terrain_characteristics: Dict[str, Any],
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Évalue l'aptitude d'un terrain pour une culture.
    
    Args:
        crop: Culture envisagée
        region: Région du terrain
        terrain_characteristics: Caractéristiques du terrain (pente, drainage, etc.)
        tool_context: Contexte de l'outil
        
    Returns:
        Évaluation complète de l'aptitude du terrain
    """
    # Critères d'aptitude par culture
    suitability_criteria = {
        "cacao": {
            "altitude": {"min": 0, "max": 800},
            "pente": {"max": 30},
            "drainage": ["bien drainé", "modérément drainé"],
            "exposition": ["ombragé", "mi-ombre"],
            "ph": {"min": 5.5, "max": 7.0}
        },
        "café": {
            "altitude": {"min": 500, "max": 2000},
            "pente": {"max": 45},
            "drainage": ["bien drainé"],
            "exposition": ["mi-ombre", "ombragé"],
            "ph": {"min": 6.0, "max": 7.0}
        },
        "maïs": {
            "altitude": {"min": 0, "max": 1500},
            "pente": {"max": 15},
            "drainage": ["bien drainé", "modérément drainé"],
            "exposition": ["plein soleil"],
            "ph": {"min": 5.8, "max": 7.2}
        }
    }
    
    # Évaluation par critère
    criteria = suitability_criteria.get(crop, suitability_criteria["maïs"])
    evaluation = {}
    overall_score = 0
    max_score = 0
    
    for criterion, requirements in criteria.items():
        if criterion in terrain_characteristics:
            value = terrain_characteristics[criterion]
            
            if criterion == "altitude":
                if requirements["min"] <= value <= requirements["max"]:
                    score = 3  # Excellent
                elif abs(value - requirements["min"]) <= 200 or abs(value - requirements["max"]) <= 200:
                    score = 2  # Bon
                else:
                    score = 1  # Marginal
                    
            elif criterion == "pente":
                if value <= requirements["max"]/2:
                    score = 3
                elif value <= requirements["max"]:
                    score = 2
                else:
                    score = 1
                    
            elif criterion == "drainage":
                score = 3 if value in requirements else 1
                
            elif criterion == "ph":
                if requirements["min"] <= value <= requirements["max"]:
                    score = 3
                elif abs(value - requirements["min"]) <= 0.5 or abs(value - requirements["max"]) <= 0.5:
                    score = 2
                else:
                    score = 1
            else:
                score = 2  # Score par défaut
            
            evaluation[criterion] = {
                "value": value,
                "score": score,
                "status": ["inadéquat", "marginal", "bon", "excellent"][score]
            }
            
            overall_score += score
            max_score += 3
    
    # Calcul aptitude globale
    suitability_percent = (overall_score / max_score) * 100 if max_score > 0 else 0
    
    if suitability_percent >= 80:
        suitability_class = "Très apte (S1)"
    elif suitability_percent >= 60:
        suitability_class = "Apte (S2)"
    elif suitability_percent >= 40:
        suitability_class = "Marginalement apte (S3)"
    else:
        suitability_class = "Inapte (N)"
    
    # Recommandations d'amélioration
    improvements = []
    for criterion, eval_data in evaluation.items():
        if eval_data["score"] < 2:
            if criterion == "drainage":
                improvements.append({
                    "issue": "Drainage insuffisant",
                    "solution": "Installation drains, billonnage",
                    "cost": 100000,
                    "feasibility": "moyenne"
                })
            elif criterion == "ph":
                if eval_data["value"] < criteria[criterion]["min"]:
                    improvements.append({
                        "issue": "Sol trop acide",
                        "solution": "Chaulage (2-3 t/ha)",
                        "cost": 150000,
                        "feasibility": "élevée"
                    })
    
    # Utiliser Gemini pour l'évaluation
    prompt = f"""
    Évaluation aptitude terrain pour {crop} en région {region} du Cameroun:
    
    Caractéristiques terrain: {terrain_characteristics}
    Critères culture: {criteria}
    Évaluation par critère: {evaluation}
    
    Aptitude globale: {suitability_class} ({suitability_percent:.1f}%)
    Améliorations identifiées: {improvements}
    
    Fournis une évaluation détaillée incluant:
    1. Analyse de l'aptitude par critère
    2. Facteurs limitants principaux
    3. Potentiel de production estimé
    4. Plan d'amélioration si nécessaire
    5. Alternatives culturales mieux adaptées
    6. Risques et contraintes à surveiller
    7. Investissements requis pour optimisation
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "region": region,
        "terrain_characteristics": terrain_characteristics,
        "suitability_evaluation": evaluation,
        "overall_suitability": {
            "class": suitability_class,
            "score_percent": suitability_percent,
            "production_potential": "élevé" if suitability_percent >= 70 else ("moyen" if suitability_percent >= 50 else "faible")
        },
        "improvement_recommendations": improvements,
        "suitability_analysis": response.text
    }


def calculate_nutrient_needs(
    crop: str,
    target_yield: float,
    tool_context: ToolContext,
    soil_analysis: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Calcule les besoins nutritifs précis d'une culture.
    
    Args:
        crop: Type de culture
        target_yield: Rendement cible (kg/ha ou tonnes/ha)
        soil_analysis: Résultats d'analyse de sol (optionnel)
        tool_context: Contexte de l'outil
        
    Returns:
        Calcul détaillé des besoins nutritifs
    """
    # Besoins unitaires par kg de produit (g/kg produit)
    nutrient_uptake = {
        "cacao": {"N": 25, "P": 3, "K": 35, "Ca": 8, "Mg": 4, "S": 2},
        "café": {"N": 20, "P": 2, "K": 25, "Ca": 5, "Mg": 3, "S": 1.5},
        "maïs": {"N": 15, "P": 3, "K": 8, "Ca": 2, "Mg": 2, "S": 1},
        "manioc": {"N": 5, "P": 1, "K": 8, "Ca": 3, "Mg": 1, "S": 0.5},
        "plantain": {"N": 12, "P": 1.5, "K": 20, "Ca": 4, "Mg": 2, "S": 1},
        "arachide": {"N": 40, "P": 4, "K": 12, "Ca": 8, "Mg": 3, "S": 2}
    }
    
    # Coefficients d'efficacité des engrais
    fertilizer_efficiency = {
        "N": 0.6,  # 60% du N appliqué utilisé
        "P": 0.2,  # 20% du P appliqué utilisé
        "K": 0.8,  # 80% du K appliqué utilisé
        "Ca": 0.7,
        "Mg": 0.6,
        "S": 0.5
    }
    
    # Calcul besoins bruts
    uptake_data = nutrient_uptake.get(crop, nutrient_uptake["maïs"])
    gross_needs = {}
    
    for nutrient, uptake_per_kg in uptake_data.items():
        gross_need = (target_yield * uptake_per_kg) / 1000  # kg/ha
        # Ajustement pour efficacité engrais
        net_need = gross_need / fertilizer_efficiency.get(nutrient, 0.6)
        gross_needs[nutrient] = {
            "uptake_kg": gross_need,
            "fertilizer_needed_kg": net_need
        }
    
    # Ajustements selon analyse de sol
    soil_corrections = {}
    if soil_analysis:
        # Niveaux critiques de référence
        critical_levels = {
            "ph": 6.0,
            "organic_matter": 3.0,
            "available_P": 15,  # ppm
            "exchangeable_K": 120,  # ppm
            "exchangeable_Ca": 2000,  # ppm
            "exchangeable_Mg": 240   # ppm
        }
        
        for nutrient, critical in critical_levels.items():
            if nutrient in soil_analysis:
                current = soil_analysis[nutrient]
                if current < critical:
                    deficit_ratio = (critical - current) / critical
                    if nutrient == "available_P":
                        soil_corrections["P"] = gross_needs["P"]["fertilizer_needed_kg"] * (1 + deficit_ratio)
                    elif nutrient == "exchangeable_K":
                        soil_corrections["K"] = gross_needs["K"]["fertilizer_needed_kg"] * (1 + deficit_ratio)
    
    # Plan de fertilisation
    fertilization_schedule = {
        "basal": {},  # À la plantation
        "side_dress_1": {},  # Premier apport de couverture
        "side_dress_2": {},  # Deuxième apport de couverture
        "foliar": {}  # Applications foliaires
    }
    
    # Répartition des apports
    for nutrient, needs in gross_needs.items():
        total_need = soil_corrections.get(nutrient, needs["fertilizer_needed_kg"])
        
        if nutrient == "N":
            fertilization_schedule["basal"]["N"] = total_need * 0.3
            fertilization_schedule["side_dress_1"]["N"] = total_need * 0.4
            fertilization_schedule["side_dress_2"]["N"] = total_need * 0.3
        elif nutrient == "P":
            fertilization_schedule["basal"]["P"] = total_need
        elif nutrient == "K":
            fertilization_schedule["basal"]["K"] = total_need * 0.5
            fertilization_schedule["side_dress_1"]["K"] = total_need * 0.3
            fertilization_schedule["side_dress_2"]["K"] = total_need * 0.2
        else:
            fertilization_schedule["basal"][nutrient] = total_need
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Calcul besoins nutritifs pour {crop} au Cameroun:
    
    Rendement cible: {target_yield} kg/ha
    Besoins bruts calculés: {gross_needs}
    Analyse de sol: {soil_analysis or 'Non disponible'}
    Corrections sol: {soil_corrections}
    
    Programme fertilisation: {fertilization_schedule}
    
    Optimise le calcul en considérant:
    1. Précision des besoins selon le rendement cible
    2. Ajustements selon fertilité du sol
    3. Fractionnement optimal des apports
    4. Formes d'engrais les plus appropriées
    5. Interactions entre nutriments
    6. Facteurs climatiques et saisonniers
    7. Coût du programme et alternatives
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "target_yield": target_yield,
        "soil_analysis": soil_analysis,
        "nutrient_requirements": gross_needs,
        "soil_corrections": soil_corrections,
        "fertilization_schedule": fertilization_schedule,
        "total_nutrients_needed": {
            nutrient: sum(schedule.get(nutrient, 0) for schedule in fertilization_schedule.values())
            for nutrient in gross_needs.keys()
        },
        "nutrient_analysis": response.text
    }


def suggest_soil_amendments(
    soil_ph: float,
    organic_matter: float,
    main_constraints: List[str],
    tool_context: ToolContext,
    budget_fcfa: Optional[float] = None,
) -> Dict[str, Any]:
    """Suggère des amendements du sol appropriés.
    
    Args:
        soil_ph: pH actuel du sol
        organic_matter: Taux de matière organique (%)
        main_constraints: Principales contraintes du sol
        budget_fcfa: Budget disponible (optionnel)
        tool_context: Contexte de l'outil
        
    Returns:
        Plan d'amendement du sol
    """
    # Amendements disponibles
    amendments = {
        "chaux_agricole": {
            "purpose": "correction acidité",
            "ph_range": {"min": 4.0, "max": 6.0},
            "application_rate": "2-4 t/ha",
            "cost_per_tonne": 50000,
            "effect_duration": "2-3 ans",
            "benefits": ["augmente pH", "apporte Ca", "améliore structure"]
        },
        "dolomie": {
            "purpose": "correction acidité + Mg",
            "ph_range": {"min": 4.0, "max": 6.0},
            "application_rate": "1.5-3 t/ha",
            "cost_per_tonne": 55000,
            "effect_duration": "3-4 ans",
            "benefits": ["augmente pH", "apporte Ca et Mg", "action plus douce"]
        },
        "compost": {
            "purpose": "matière organique",
            "mo_threshold": 3.0,
            "application_rate": "10-20 t/ha",
            "cost_per_tonne": 10000,
            "effect_duration": "1-2 ans",
            "benefits": ["améliore structure", "fertilité", "rétention eau", "vie microbienne"]
        },
        "fumier_décomposé": {
            "purpose": "matière organique + nutriments",
            "mo_threshold": 2.5,
            "application_rate": "15-25 t/ha",
            "cost_per_tonne": 12000,
            "effect_duration": "1-2 ans",
            "benefits": ["nutrition", "structure", "activité biologique"]
        },
        "gypse": {
            "purpose": "amélioration sols sodiques",
            "constraints": ["excès sodium", "compaction"],
            "application_rate": "2-5 t/ha",
            "cost_per_tonne": 30000,
            "effect_duration": "2-3 ans",
            "benefits": ["améliore infiltration", "réduit compaction"]
        },
        "biochar": {
            "purpose": "amélioration physico-chimique",
            "universal": True,
            "application_rate": "2-5 t/ha",
            "cost_per_tonne": 80000,
            "effect_duration": "10+ ans",
            "benefits": ["séquestration carbone", "rétention nutriments", "structure"]
        }
    }
    
    # Sélection selon contraintes
    recommended_amendments = []
    total_cost = 0
    
    # Correction acidité
    if soil_ph < 5.5:
        lime_needed = (6.0 - soil_ph) * 2  # Estimation simplifiée
        if "carence magnésium" in main_constraints:
            amendment = amendments["dolomie"].copy()
            amendment["quantity_needed"] = min(3.0, lime_needed)
        else:
            amendment = amendments["chaux_agricole"].copy()
            amendment["quantity_needed"] = min(4.0, lime_needed)
        
        cost = amendment["quantity_needed"] * amendment["cost_per_tonne"]
        amendment["total_cost"] = cost
        total_cost += cost
        recommended_amendments.append(amendment)
    
    # Amélioration matière organique
    if organic_matter < 3.0:
        mo_deficit = 3.0 - organic_matter
        compost_needed = mo_deficit * 10  # Estimation
        
        amendment = amendments["compost"].copy()
        amendment["quantity_needed"] = min(20, compost_needed)
        cost = amendment["quantity_needed"] * amendment["cost_per_tonne"]
        amendment["total_cost"] = cost
        total_cost += cost
        recommended_amendments.append(amendment)
    
    # Contraintes spécifiques
    if "compaction" in main_constraints:
        if total_cost < (budget_fcfa or float('inf')):
            amendment = amendments["gypse"].copy()
            amendment["quantity_needed"] = 3.0
            cost = amendment["quantity_needed"] * amendment["cost_per_tonne"]
            amendment["total_cost"] = cost
            total_cost += cost
            recommended_amendments.append(amendment)
    
    # Filtrage selon budget
    if budget_fcfa and total_cost > budget_fcfa:
        # Prioriser les amendements les plus critiques
        recommended_amendments.sort(key=lambda x: x["total_cost"])
        filtered_amendments = []
        running_cost = 0
        
        for amendment in recommended_amendments:
            if running_cost + amendment["total_cost"] <= budget_fcfa:
                filtered_amendments.append(amendment)
                running_cost += amendment["total_cost"]
        
        recommended_amendments = filtered_amendments
        total_cost = running_cost
    
    # Calendrier d'application
    application_schedule = {
        "début_saison_sèche": [],
        "avant_plantation": [],
        "entretien_annuel": []
    }
    
    for amendment in recommended_amendments:
        if amendment["purpose"] == "correction acidité":
            application_schedule["début_saison_sèche"].append(amendment)
        elif amendment["purpose"] == "matière organique":
            application_schedule["avant_plantation"].append(amendment)
        else:
            application_schedule["entretien_annuel"].append(amendment)
    
    # Utiliser Gemini pour les recommandations
    prompt = f"""
    Plan d'amendement du sol au Cameroun:
    
    État actuel:
    - pH: {soil_ph}
    - Matière organique: {organic_matter}%
    - Contraintes: {', '.join(main_constraints)}
    - Budget: {budget_fcfa or 'Non limité'} FCFA
    
    Amendements recommandés: {recommended_amendments}
    Coût total: {total_cost:,.0f} FCFA
    Calendrier: {application_schedule}
    
    Optimise le plan en considérant:
    1. Priorités d'intervention selon l'urgence
    2. Synergies entre amendements
    3. Méthodes d'application optimales
    4. Suivi et évaluation des résultats
    5. Alternatives moins coûteuses
    6. Planning pluriannuel d'amélioration
    7. Indicateurs de réussite du programme
    """
    
    response = model.generate_content(prompt)
    
    return {
        "soil_status": {
            "ph": soil_ph,
            "organic_matter": organic_matter,
            "main_constraints": main_constraints
        },
        "recommended_amendments": recommended_amendments,
        "total_cost": total_cost,
        "budget_fcfa": budget_fcfa,
        "cost_per_hectare": total_cost,  # Assumant 1 ha
        "application_schedule": application_schedule,
        "amendment_plan": response.text,
        "expected_improvements": {
            "ph_target": min(6.5, soil_ph + 1.0) if soil_ph < 6.0 else soil_ph,
            "organic_matter_target": min(4.0, organic_matter + 1.0),
            "timeline_months": "6-12 mois pour effets visibles"
        }
    }