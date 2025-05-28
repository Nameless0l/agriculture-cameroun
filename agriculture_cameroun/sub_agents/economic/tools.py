# Copyright 2025 Agriculture Cameroun

"""Outils pour l'agent économique."""

import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from google.adk.tools import ToolContext
from agriculture_cameroun.config import CropType, RegionType, get_config
from ...utils.data import MARKET_PRICES, LOCAL_FERTILIZERS, AGRICULTURAL_TOOLS

# Configuration de l'API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-001')


def get_market_prices(
    crop: str,
    tool_context: ToolContext,
    market_type: str = "gros",
    region: Optional[str] = None,
) -> Dict[str, Any]:
    """Obtient les prix actuels du marché pour une culture.
    
    Args:
        crop: Type de culture
        region: Région (optionnel)
        market_type: Type de marché (gros, détail, export)
        tool_context: Contexte de l'outil
        
    Returns:
        Prix du marché avec tendances
    """
    config = get_config()
    
    # Obtenir les prix de base
    base_prices = MARKET_PRICES.get(CropType(crop), {"min": 100, "max": 500, "average": 300})
    
    # Simulation de variations selon le type de marché
    market_multipliers = {
        "producteur": 0.7,  # Prix au producteur plus bas
        "gros": 1.0,        # Prix de référence
        "détail": 1.4,      # Prix au détail plus élevé
        "export": 1.2       # Prix export variable
    }
    
    multiplier = market_multipliers.get(market_type, 1.0)
    
    # Variations saisonnières simulées
    current_month = datetime.now().month
    seasonal_factor = 1.0
    
    # Exemple: prix plus élevés en période de soudure
    if current_month in [6, 7, 8]:  # Période de soudure
        seasonal_factor = 1.2
    elif current_month in [11, 12, 1]:  # Période de récolte
        seasonal_factor = 0.9
    
    # Prix avec variations
    current_price = int(base_prices["average"] * multiplier * seasonal_factor)
    min_price = int(base_prices["min"] * multiplier * seasonal_factor)
    max_price = int(base_prices["max"] * multiplier * seasonal_factor)
    
    # Génération de données historiques simulées
    price_history = []
    for i in range(12):  # 12 derniers mois
        month_date = datetime.now() - timedelta(days=i*30)
        month_price = int(base_prices["average"] * (0.8 + random.random() * 0.4))
        price_history.append({
            "month": month_date.strftime("%B %Y"),
            "price": month_price,
            "volume_estimation": random.randint(100, 1000)
        })
    
    # Utiliser Gemini pour générer une analyse
    prompt = f"""
    Analyse économique des prix pour {crop} au Cameroun en {region or "toutes régions"}:
    
    Prix actuel: {current_price} FCFA/kg
    Fourchette: {min_price} - {max_price} FCFA/kg
    Type de marché: {market_type}
    Historique: {price_history[:3]}
    
    Fournis une analyse incluant:
    1. Évaluation du niveau de prix actuel
    2. Facteurs influençant les prix
    3. Prévisions à court terme
    4. Conseils pour optimiser les ventes
    5. Comparaison avec les autres cultures
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "region": region,
        "market_type": market_type,
        "current_price": current_price,
        "price_range": {"min": min_price, "max": max_price},
        "currency": config.currency,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "price_history": price_history,
        "analysis": response.text,
        "trend": "stable" if seasonal_factor == 1.0 else ("hausse" if seasonal_factor > 1.0 else "baisse")
    }


def analyze_profitability(
    crop: str,
    area_hectares: float,
    tool_context: ToolContext,
    production_system: str = "traditionnel",
) -> Dict[str, Any]:
    """Analyse la rentabilité d'une culture.
    
    Args:
        crop: Type de culture
        area_hectares: Superficie en hectares
        production_system: Système de production (traditionnel, amélioré, intensif)
        tool_context: Contexte de l'outil
        
    Returns:
        Analyse de rentabilité détaillée
    """
    # Rendements selon le système
    yield_factors = {
        "traditionnel": 0.7,
        "amélioré": 1.0,
        "intensif": 1.4
    }
    
    # Coûts de base par hectare (FCFA)
    base_costs = {
        "semences": 25000,
        "engrais": 45000,
        "pesticides": 20000,
        "main_oeuvre": 80000,
        "transport": 15000,
        "divers": 10000
    }
    
    factor = yield_factors.get(production_system, 1.0)
    
    # Ajustement des coûts selon le système
    if production_system == "intensif":
        base_costs["engrais"] *= 1.5
        base_costs["pesticides"] *= 1.3
    elif production_system == "traditionnel":
        base_costs["engrais"] *= 0.5
        base_costs["pesticides"] *= 0.3
    
    # Calcul du coût total par hectare
    total_cost_per_ha = sum(base_costs.values())
    total_cost = total_cost_per_ha * area_hectares
    
    # Estimation du rendement
    from ...utils.data import get_crop_info
    crop_info = get_crop_info(CropType(crop))
    if crop_info:
        expected_yield_ha = crop_info.expected_yield_per_hectare * factor
        total_yield = expected_yield_ha * area_hectares
    else:
        expected_yield_ha = 1000 * factor
        total_yield = expected_yield_ha * area_hectares
    
    # Prix de vente estimé
    market_price = MARKET_PRICES.get(CropType(crop), {"average": 300})["average"]
    
    # Calcul des revenus
    gross_revenue = total_yield * market_price
    net_revenue = gross_revenue - total_cost
    profit_margin = (net_revenue / gross_revenue * 100) if gross_revenue > 0 else 0
    roi = (net_revenue / total_cost * 100) if total_cost > 0 else 0
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Analyse de rentabilité pour {crop} au Cameroun:
    
    Superficie: {area_hectares} ha
    Système: {production_system}
    Coûts totaux: {total_cost:,.0f} FCFA
    Rendement estimé: {total_yield:,.0f} kg
    Revenus bruts: {gross_revenue:,.0f} FCFA
    Bénéfice net: {net_revenue:,.0f} FCFA
    Marge: {profit_margin:.1f}%
    ROI: {roi:.1f}%
    
    Fournis une analyse incluant:
    1. Évaluation de la rentabilité
    2. Points d'amélioration possibles
    3. Risques économiques
    4. Recommandations concrètes
    5. Comparaison avec d'autres cultures
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "area_hectares": area_hectares,
        "production_system": production_system,
        "costs": {
            "breakdown": base_costs,
            "total_per_hectare": total_cost_per_ha,
            "total": total_cost
        },
        "yield": {
            "per_hectare": expected_yield_ha,
            "total": total_yield,
            "unit": "kg"
        },
        "revenue": {
            "price_per_kg": market_price,
            "gross": gross_revenue,
            "net": net_revenue,
            "currency": "FCFA"
        },
        "profitability": {
            "profit_margin_percent": profit_margin,
            "roi_percent": roi,
            "break_even_kg": total_cost / market_price if market_price > 0 else 0
        },
        "analysis": response.text
    }


def get_market_trends(
    tool_context: ToolContext,
    crop: Optional[str] = None,
    period_months: int = 12,
) -> Dict[str, Any]:
    """Analyse les tendances du marché.
    
    Args:
        crop: Culture spécifique (optionnel)
        period_months: Période d'analyse en mois
        tool_context: Contexte de l'outil
        
    Returns:
        Analyse des tendances du marché
    """
    # Génération de données de tendance simulées
    trends_data = {}
    
    if crop:
        crops_to_analyze = [crop]
    else:
        crops_to_analyze = ["cacao", "café", "manioc", "maïs", "plantain"]
    
    for crop_name in crops_to_analyze:
        # Simulation de tendances
        trend_direction = random.choice(["hausse", "baisse", "stable"])
        trend_percentage = random.randint(-15, 25)
        
        market_factors = [
            "Conditions climatiques",
            "Demande d'exportation", 
            "Politique gouvernementale",
            "Coûts de transport",
            "Concurrence régionale"
        ]
        
        selected_factors = random.sample(market_factors, 3)
        
        trends_data[crop_name] = {
            "trend": trend_direction,
            "variation_percent": trend_percentage,
            "key_factors": selected_factors,
            "demand_level": random.choice(["faible", "modérée", "forte", "très forte"]),
            "supply_situation": random.choice(["déficit", "équilibre", "excédent"])
        }
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Analyse des tendances du marché agricole camerounais sur {period_months} mois:
    
    Données: {trends_data}
    
    Fournis une analyse complète incluant:
    1. Tendances générales du marché
    2. Cultures les plus prometteuses
    3. Facteurs de risque identifiés
    4. Opportunités émergentes
    5. Recommandations stratégiques pour les agriculteurs
    6. Prévisions pour les 6 prochains mois
    """
    
    response = model.generate_content(prompt)
    
    return {
        "period_months": period_months,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "trends_data": trends_data,
        "market_analysis": response.text,
        "recommended_crops": [crop for crop, data in trends_data.items() if data["variation_percent"] > 10]
    }


def recommend_sales_strategy(
    crop: str,
    quantity_kg: float,
    tool_context: ToolContext,
    urgency: str = "normal",
) -> Dict[str, Any]:
    """Recommande une stratégie de vente optimale.
    
    Args:
        crop: Type de culture
        quantity_kg: Quantité à vendre en kg
        urgency: Urgence de vente (urgent, normal, patient)
        tool_context: Contexte de l'outil
        
    Returns:
        Stratégie de vente recommandée
    """
    # Canaux de commercialisation possibles
    sales_channels = {
        "marché_local": {
            "prix_relatif": 0.8,
            "délai_jours": 1,
            "coût_transport": 0.02,
            "avantages": ["Paiement immédiat", "Pas d'intermédiaire"],
            "inconvénients": ["Prix plus bas", "Quantités limitées"]
        },
        "coopérative": {
            "prix_relatif": 0.9,
            "délai_jours": 7,
            "coût_transport": 0.01,
            "avantages": ["Prix négocié", "Soutien technique"],
            "inconvénients": ["Délai de paiement", "Conditions qualité"]
        },
        "grossiste": {
            "prix_relatif": 0.85,
            "délai_jours": 3,
            "coût_transport": 0.03,
            "avantages": ["Gros volumes", "Régularité"],
            "inconvénients": ["Négociation difficile", "Dépendance"]
        },
        "export": {
            "prix_relatif": 1.2,
            "délai_jours": 30,
            "coût_transport": 0.08,
            "avantages": ["Prix élevé", "Devise"],
            "inconvénients": ["Exigences qualité", "Procédures complexes"]
        }
    }
    
    # Prix de base
    base_price = MARKET_PRICES.get(CropType(crop), {"average": 300})["average"]
    
    # Recommandations selon l'urgence
    if urgency == "urgent":
        recommended_channels = ["marché_local", "grossiste"]
    elif urgency == "patient":
        recommended_channels = ["export", "coopérative"] if quantity_kg > 1000 else ["coopérative", "grossiste"]
    else:
        recommended_channels = ["coopérative", "grossiste"]
    
    # Calcul des revenus potentiels par canal
    revenue_scenarios = {}
    for channel in recommended_channels:
        channel_data = sales_channels[channel]
        price_per_kg = base_price * channel_data["prix_relatif"]
        transport_cost = quantity_kg * channel_data["coût_transport"] * base_price
        net_revenue = (quantity_kg * price_per_kg) - transport_cost
        
        revenue_scenarios[channel] = {
            "price_per_kg": price_per_kg,
            "gross_revenue": quantity_kg * price_per_kg,
            "transport_cost": transport_cost,
            "net_revenue": net_revenue,
            "delivery_days": channel_data["délai_jours"],
            "advantages": channel_data["avantages"],
            "disadvantages": channel_data["inconvénients"]
        }
    
    # Utiliser Gemini pour la recommandation
    prompt = f"""
    Stratégie de vente pour {crop} au Cameroun:
    
    Quantité: {quantity_kg} kg
    Urgence: {urgency}
    Scénarios de revenus: {revenue_scenarios}
    
    Recommande la meilleure stratégie en considérant:
    1. Canal de vente optimal
    2. Timing de vente
    3. Préparation nécessaire (qualité, conditionnement)
    4. Négociation des prix
    5. Diversification des canaux
    6. Alternatives en cas de difficulté
    """
    
    response = model.generate_content(prompt)
    
    # Meilleur canal par revenu net
    best_channel = max(revenue_scenarios.keys(), key=lambda x: revenue_scenarios[x]["net_revenue"])
    
    return {
        "crop": crop,
        "quantity_kg": quantity_kg,
        "urgency": urgency,
        "recommended_channel": best_channel,
        "revenue_scenarios": revenue_scenarios,
        "strategy_analysis": response.text,
        "estimated_best_revenue": revenue_scenarios[best_channel]["net_revenue"]
    }


def calculate_production_costs(
    crop: str,
    area_hectares: float,
    tool_context: ToolContext,
    input_level: str = "standard",
) -> Dict[str, Any]:
    """Calcule les coûts de production détaillés.
    
    Args:
        crop: Type de culture
        area_hectares: Superficie en hectares
        input_level: Niveau d'intrants (minimal, standard, intensif)
        tool_context: Contexte de l'outil
        
    Returns:
        Analyse détaillée des coûts de production
    """
    # Coûts de base par poste (FCFA/ha)
    base_costs = {
        "préparation_sol": {
            "labour": 30000,
            "hersage": 15000,
            "billonnage": 10000
        },
        "semences_plants": {
            "semences": 25000,
            "transport_semences": 2000
        },
        "fertilisation": {
            "engrais_organique": 20000,
            "engrais_minéral": 35000,
            "amendements": 8000
        },
        "protection_cultures": {
            "herbicides": 15000,
            "insecticides": 12000,
            "fongicides": 8000
        },
        "main_oeuvre": {
            "plantation": 25000,
            "entretien": 40000,
            "récolte": 35000
        },
        "autres": {
            "transport_intrants": 8000,
            "stockage": 5000,
            "divers": 7000
        }
    }
    
    # Facteurs selon le niveau d'intrants
    input_factors = {
        "minimal": 0.6,
        "standard": 1.0,
        "intensif": 1.5
    }
    
    factor = input_factors.get(input_level, 1.0)
    
    # Calcul des coûts ajustés
    adjusted_costs = {}
    total_cost_per_ha = 0
    
    for category, items in base_costs.items():
        adjusted_costs[category] = {}
        category_total = 0
        
        for item, cost in items.items():
            adjusted_cost = cost * factor
            adjusted_costs[category][item] = adjusted_cost
            category_total += adjusted_cost
        
        adjusted_costs[category]["total"] = category_total
        total_cost_per_ha += category_total
    
    total_cost = total_cost_per_ha * area_hectares
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Analyse des coûts de production pour {crop} au Cameroun:
    
    Superficie: {area_hectares} ha
    Niveau d'intrants: {input_level}
    Coût total par hectare: {total_cost_per_ha:,.0f} FCFA
    Coût total: {total_cost:,.0f} FCFA
    
    Détail des coûts: {adjusted_costs}
    
    Fournis une analyse incluant:
    1. Répartition des coûts par poste
    2. Postes les plus coûteux
    3. Opportunités de réduction des coûts
    4. Alternatives économiques locales
    5. Impact du niveau d'intrants sur la rentabilité
    6. Conseils pour l'optimisation financière
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "area_hectares": area_hectares,
        "input_level": input_level,
        "cost_breakdown": adjusted_costs,
        "totals": {
            "per_hectare": total_cost_per_ha,
            "total": total_cost,
            "currency": "FCFA"
        },
        "cost_analysis": response.text,
        "major_cost_drivers": sorted(
            [(cat, data["total"]) for cat, data in adjusted_costs.items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
    }


def analyze_market_opportunities(
    tool_context: ToolContext,
    region: Optional[str] = None,
    investment_budget: Optional[float] = None,
) -> Dict[str, Any]:
    """Identifie les opportunités de marché.
    
    Args:
        region: Région d'intérêt (optionnel)
        investment_budget: Budget d'investissement disponible (optionnel)
        tool_context: Contexte de l'outil
        
    Returns:
        Analyse des opportunités de marché
    """
    # Opportunités par secteur
    opportunities = {
        "cultures_émergentes": {
            "moringa": {
                "potentiel": "très élevé",
                "investissement_min": 200000,
                "roi_estimé": "200-300%",
                "marché_cible": "export, nutrition"
            },
            "avocat": {
                "potentiel": "élevé", 
                "investissement_min": 500000,
                "roi_estimé": "150-200%",
                "marché_cible": "urbain, export"
            },
            "spiruline": {
                "potentiel": "élevé",
                "investissement_min": 1000000,
                "roi_estimé": "300-400%",
                "marché_cible": "santé, export"
            }
        },
        "transformation": {
            "farine_manioc": {
                "potentiel": "très élevé",
                "investissement_min": 300000,
                "roi_estimé": "100-150%",
                "marché_cible": "boulangerie, export"
            },
            "huile_palme_artisanale": {
                "potentiel": "élevé",
                "investissement_min": 150000,
                "roi_estimé": "80-120%",
                "marché_cible": "local, régional"
            }
        },
        "services": {
            "location_équipement": {
                "potentiel": "élevé",
                "investissement_min": 800000,
                "roi_estimé": "60-100%",
                "marché_cible": "petits agriculteurs"
            },
            "formation_conseil": {
                "potentiel": "modéré",
                "investissement_min": 50000,
                "roi_estimé": "50-80%",
                "marché_cible": "agriculteurs, coopératives"
            }
        }
    }
    
    # Filtrage selon le budget si fourni
    if investment_budget:
        filtered_opportunities = {}
        for sector, items in opportunities.items():
            filtered_items = {k: v for k, v in items.items() 
                            if v["investissement_min"] <= investment_budget}
            if filtered_items:
                filtered_opportunities[sector] = filtered_items
        opportunities = filtered_opportunities
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Analyse des opportunités de marché agricole au Cameroun:
    
    Région: {region or "Toutes régions"}
    Budget disponible: {investment_budget or "Non spécifié"} FCFA
    
    Opportunités identifiées: {opportunities}
    
    Fournis une analyse détaillée incluant:
    1. Top 3 des meilleures opportunités
    2. Facteurs de succès pour chaque opportunité
    3. Risques et défis à considérer
    4. Étapes de mise en œuvre
    5. Partenaires potentiels
    6. Sources de financement disponibles
    7. Timeline recommandé
    """
    
    response = model.generate_content(prompt)
    
    # Calcul du score d'opportunité
    scored_opportunities = []
    for sector, items in opportunities.items():
        for item, data in items.items():
            roi_score = int(data["roi_estimé"].split("-")[0].replace("%", ""))
            potentiel_score = {"très élevé": 5, "élevé": 4, "modéré": 3, "faible": 2}.get(data["potentiel"], 3)
            
            total_score = roi_score / 20 + potentiel_score
            scored_opportunities.append({
                "name": item,
                "sector": sector,
                "score": total_score,
                "data": data
            })
    
    # Tri par score décroissant
    scored_opportunities.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "region": region,
        "investment_budget": investment_budget,
        "opportunities": opportunities,
        "top_opportunities": scored_opportunities[:5],
        "market_analysis": response.text,
        "analysis_date": datetime.now().strftime("%Y-%m-%d")
    }