# Copyright 2025 Agriculture Cameroun

"""Outils pour l'agent de santé des plantes."""

import os
import random
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from google.adk.tools import ToolContext
from typing import Optional
from ...utils.data import COMMON_DISEASES

# Configuration de l'API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-001')


def diagnose_plant_disease(
    crop: str,
    symptoms: List[str],
    tool_context: ToolContext,
    affected_parts: Optional[List[str]] = None,
    environmental_conditions: Optional[str] = None,
) -> Dict[str, Any]:
    """Diagnostique une maladie des plantes basée sur les symptômes.
    
    Args:
        crop: Type de culture affectée
        symptoms: Liste des symptômes observés
        affected_parts: Parties de la plante affectées (optionnel)
        environmental_conditions: Conditions environnementales (optionnel)
        tool_context: Contexte de l'outil
        
    Returns:
        Diagnostic détaillé avec probabilités
    """
    # Base de données des maladies étendues
    disease_database = {
        "cacao": [
            {
                "name": "Pourriture brune",
                "agent": "Phytophthora palmivora",
                "symptoms": ["taches brunes", "pourriture fruits", "brunissement cabosses", "exsudat"],
                "affected_parts": ["fruits", "cabosses", "branches"],
                "conditions": ["humidité élevée", "température 25-30°C", "blessures"],
                "severity": "élevée",
                "treatments": ["fongicides cupriques", "taille sanitaire", "amélioration drainage"]
            },
            {
                "name": "Mirides",
                "agent": "Sahlbergella singularis",
                "symptoms": ["taches noires", "dessèchement branches", "écoulement sève", "chancres"],
                "affected_parts": ["branches", "tronc", "rameaux"],
                "conditions": ["saison sèche", "stress hydrique", "mauvais entretien"],
                "severity": "très élevée",
                "treatments": ["insecticides", "taille parties atteintes", "amélioration ombrage"]
            },
            {
                "name": "Chancre du cacaoyer",
                "agent": "Phytophthora megakarya",
                "symptoms": ["chancres bruns", "exsudat noir", "flétrissement", "défoliation"],
                "affected_parts": ["tronc", "branches", "fruits"],
                "conditions": ["blessures", "humidité", "mauvaise ventilation"],
                "severity": "critique",
                "treatments": ["fongicides systémiques", "curettage chancres", "mastication"]
            }
        ],
        "maïs": [
            {
                "name": "Charbon du maïs",
                "agent": "Ustilago maydis",
                "symptoms": ["galles blanches", "galles noires", "déformation épis", "spores noires"],
                "affected_parts": ["épis", "feuilles", "tiges"],
                "conditions": ["humidité", "blessures", "variété sensible"],
                "severity": "modérée",
                "treatments": ["variétés résistantes", "rotation culturale", "élimination galles"]
            },
            {
                "name": "Striure du maïs",
                "agent": "Maize streak virus",
                "symptoms": ["striures jaunes", "nanisme", "déformation feuilles", "rendement réduit"],
                "affected_parts": ["feuilles", "plant entier"],
                "conditions": ["cicadelles vectrices", "saison des pluies"],
                "severity": "élevée",
                "treatments": ["variétés résistantes", "lutte contre cicadelles", "dates plantation"]
            }
        ],
        "manioc": [
            {
                "name": "Mosaïque du manioc",
                "agent": "Cassava mosaic virus",
                "symptoms": ["mosaïque feuilles", "jaunissement", "déformation", "nanisme"],
                "affected_parts": ["feuilles", "plant entier"],
                "conditions": ["boutures infectées", "aleurodes vectrices"],
                "severity": "élevée",
                "treatments": ["boutures saines", "lutte contre aleurodes", "variétés résistantes"]
            }
        ]
    }
    
    # Calcul des scores de correspondance
    crop_diseases = disease_database.get(crop, [])
    disease_scores = []
    
    for disease in crop_diseases:
        score = 0
        total_criteria = 0
        
        # Score basé sur les symptômes
        if symptoms:
            symptom_matches = sum(1 for symptom in symptoms 
                                if any(s in symptom.lower() for s in disease["symptoms"]))
            score += (symptom_matches / len(disease["symptoms"])) * 40
            total_criteria += 40
        
        # Score basé sur les parties affectées
        if affected_parts:
            part_matches = sum(1 for part in affected_parts 
                             if part.lower() in disease["affected_parts"])
            score += (part_matches / len(disease["affected_parts"])) * 30
            total_criteria += 30
        
        # Score basé sur les conditions
        if environmental_conditions:
            condition_matches = sum(1 for condition in disease["conditions"]
                                  if condition.lower() in environmental_conditions.lower())
            score += (condition_matches / len(disease["conditions"])) * 30
            total_criteria += 30
        
        # Calcul du pourcentage de probabilité
        probability = (score / total_criteria * 100) if total_criteria > 0 else 0
        
        disease_scores.append({
            "disease": disease["name"],
            "agent": disease["agent"],
            "probability": probability,
            "severity": disease["severity"],
            "treatments": disease["treatments"],
            "matching_symptoms": [s for s in symptoms if any(ds in s.lower() for ds in disease["symptoms"])]
        })
    
    # Tri par probabilité décroissante
    disease_scores.sort(key=lambda x: x["probability"], reverse=True)
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Diagnostic phytosanitaire pour {crop} au Cameroun:
    
    Symptômes observés: {', '.join(symptoms)}
    Parties affectées: {', '.join(affected_parts) if affected_parts else 'Non spécifié'}
    Conditions: {environmental_conditions or 'Non spécifiées'}
    
    Analyses possibles: {disease_scores[:3]}
    
    Fournis un diagnostic détaillé incluant:
    1. Diagnostic le plus probable avec justification
    2. Diagnostics différentiels à considérer
    3. Examens complémentaires recommandés
    4. Urgence d'intervention
    5. Risques d'évolution si non traité
    6. Impact potentiel sur le rendement
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "symptoms": symptoms,
        "affected_parts": affected_parts,
        "environmental_conditions": environmental_conditions,
        "diagnostic_results": disease_scores,
        "most_likely_diagnosis": disease_scores[0] if disease_scores else None,
        "diagnostic_analysis": response.text,
        "confidence_level": disease_scores[0]["probability"] if disease_scores else 0
    }


def get_treatment_recommendations(
    diagnosis: str,
    crop: str,
    tool_context: ToolContext,
    severity: str = "modérée",
    budget_constraints: str = "limité",
) -> Dict[str, Any]:
    """Fournit des recommandations de traitement spécifiques.
    
    Args:
        diagnosis: Diagnostic de la maladie/parasite
        crop: Culture affectée
        severity: Gravité du problème
        budget_constraints: Contraintes budgétaires
        tool_context: Contexte de l'outil
        
    Returns:
        Plan de traitement détaillé
    """
    # Traitements par type et budget
    treatment_options = {
        "biologique": {
            "cost_level": "faible",
            "products": [
                {"name": "Trichoderma", "price_fcfa": 5000, "dose": "5g/L", "efficacy": 70},
                {"name": "Bacillus thuringiensis", "price_fcfa": 8000, "dose": "2g/L", "efficacy": 65},
                {"name": "Extrait de neem", "price_fcfa": 3000, "dose": "10ml/L", "efficacy": 60},
                {"name": "Savon noir", "price_fcfa": 1000, "dose": "20g/L", "efficacy": 50}
            ]
        },
        "traditionnel": {
            "cost_level": "très faible",
            "products": [
                {"name": "Cendre de bois", "price_fcfa": 500, "dose": "100g/L", "efficacy": 45},
                {"name": "Extrait ail-piment", "price_fcfa": 800, "dose": "50ml/L", "efficacy": 55},
                {"name": "Urine fermentée", "price_fcfa": 0, "dose": "1:10", "efficacy": 40},
                {"name": "Infusion feuilles papayer", "price_fcfa": 200, "dose": "100g/L", "efficacy": 35}
            ]
        },
        "chimique": {
            "cost_level": "élevé",
            "products": [
                {"name": "Mancozèbe", "price_fcfa": 15000, "dose": "2.5g/L", "efficacy": 85},
                {"name": "Lambda-cyhalothrine", "price_fcfa": 12000, "dose": "1ml/L", "efficacy": 90},
                {"name": "Oxychlorure de cuivre", "price_fcfa": 8000, "dose": "3g/L", "efficacy": 80},
                {"name": "Profénofos", "price_fcfa": 18000, "dose": "2ml/L", "efficacy": 88}
            ]
        }
    }
    
    # Sélection selon les contraintes budgétaires
    if budget_constraints == "limité":
        recommended_categories = ["traditionnel", "biologique"]
    elif budget_constraints == "modéré":
        recommended_categories = ["biologique", "chimique"]
    else:
        recommended_categories = ["chimique", "biologique"]
    
    # Sélection selon la gravité
    if severity == "critique":
        recommended_categories = ["chimique"] + recommended_categories
    elif severity == "faible":
        recommended_categories = ["traditionnel", "biologique"]
    
    # Création du plan de traitement
    treatment_plan = []
    for category in recommended_categories[:2]:  # Limiter à 2 catégories
        if category in treatment_options:
            best_products = sorted(treatment_options[category]["products"], 
                                 key=lambda x: x["efficacy"], reverse=True)[:2]
            treatment_plan.extend(best_products)
    
    # Calendrier de traitement
    treatment_schedule = {
        "immédiat": ["Nettoyage zone affectée", "Application première dose"],
        "7_jours": ["Évaluation évolution", "Deuxième application si nécessaire"],
        "14_jours": ["Contrôle efficacité", "Troisième application si persistance"],
        "21_jours": ["Bilan traitement", "Mesures préventives"]
    }
    
    # Utiliser Gemini pour les recommandations
    prompt = f"""
    Plan de traitement pour {diagnosis} sur {crop} au Cameroun:
    
    Gravité: {severity}
    Budget: {budget_constraints}
    Produits recommandés: {treatment_plan}
    Calendrier: {treatment_schedule}
    
    Élabore un plan détaillé incluant:
    1. Stratégie de traitement prioritaire
    2. Protocole d'application précis
    3. Calendrier d'intervention
    4. Mesures d'accompagnement (cultural, préventif)
    5. Évaluation de l'efficacité
    6. Plan B en cas d'échec
    7. Coût total estimé
    8. Précautions d'usage et sécurité
    """
    
    response = model.generate_content(prompt)
    
    # Calcul du coût total
    total_cost = sum(product["price_fcfa"] for product in treatment_plan)
    
    return {
        "diagnosis": diagnosis,
        "crop": crop,
        "severity": severity,
        "budget_constraints": budget_constraints,
        "treatment_plan": treatment_plan,
        "treatment_schedule": treatment_schedule,
        "estimated_cost": total_cost,
        "treatment_recommendations": response.text,
        "expected_efficacy": sum(p["efficacy"] for p in treatment_plan) / len(treatment_plan) if treatment_plan else 0
    }


def get_pest_identification(
    crop: str,
    pest_description: str,
    tool_context: ToolContext,
    damage_type: Optional[str] = None,
    location_on_plant: Optional[str] = None,
) -> Dict[str, Any]:
    """Identifie les parasites et ravageurs.
    
    Args:
        crop: Culture affectée
        pest_description: Description du parasite observé
        damage_type: Type de dégâts observés
        location_on_plant: Localisation sur la plante
        tool_context: Contexte de l'outil
        
    Returns:
        Identification du parasite avec informations détaillées
    """
    # Base de données des parasites
    pest_database = {
        "cacao": [
            {
                "name": "Mirides",
                "scientific_name": "Sahlbergella singularis",
                "description": "Insecte brun-noir, 10-12mm, antennes longues",
                "damage": ["taches noires branches", "dessèchement", "écoulement sève"],
                "location": ["branches", "tronc", "rameaux"],
                "lifecycle": "45-60 jours",
                "peak_season": ["saison sèche"],
                "economic_impact": "très élevé"
            },
            {
                "name": "Punaises des cabosses",
                "scientific_name": "Bathycoelia thalassina",
                "description": "Punaise verte, 8-10mm, forme ovale",
                "damage": ["piqûres cabosses", "déformation fruits", "coulure"],
                "location": ["cabosses", "fruits"],
                "lifecycle": "30-40 jours",
                "peak_season": ["saison des pluies"],
                "economic_impact": "élevé"
            }
        ],
        "maïs": [
            {
                "name": "Foreur de tige",
                "scientific_name": "Sesamia calamistis",
                "description": "Chenille rosâtre, 25-40mm, tête brune",
                "damage": ["trous dans tiges", "brisure plants", "flétrissement"],
                "location": ["tiges", "épis"],
                "lifecycle": "35-45 jours",
                "peak_season": ["début saison pluies"],
                "economic_impact": "élevé"
            },
            {
                "name": "Légionnaire d'automne",
                "scientific_name": "Spodoptera frugiperda",
                "description": "Chenille gris-brun, 30-40mm, rayures longitudinales",
                "damage": ["défoliation", "consommation grains", "trous feuilles"],
                "location": ["feuilles", "épis", "grains"],
                "lifecycle": "30-35 jours",
                "peak_season": ["toute l'année"],
                "economic_impact": "très élevé"
            }
        ],
        "manioc": [
            {
                "name": "Cochenille farineuse",
                "scientific_name": "Phenacoccus manihoti",
                "description": "Insecte blanc farineux, 2-4mm, colonies denses",
                "damage": ["jaunissement feuilles", "déformation", "fumagine"],
                "location": ["feuilles", "tiges", "bourgeons"],
                "lifecycle": "20-30 jours",
                "peak_season": ["saison sèche"],
                "economic_impact": "élevé"
            }
        ]
    }
    
    # Identification par correspondance
    crop_pests = pest_database.get(crop, [])
    identification_scores = []
    
    for pest in crop_pests:
        score = 0
        
        # Score basé sur la description
        if pest_description:
            desc_words = pest_description.lower().split()
            pest_words = pest["description"].lower().split()
            matches = sum(1 for word in desc_words if any(pw in word for pw in pest_words))
            score += (matches / len(desc_words)) * 30
        
        # Score basé sur les dégâts
        if damage_type:
            damage_matches = sum(1 for damage in pest["damage"]
                               if damage.lower() in damage_type.lower())
            score += (damage_matches / len(pest["damage"])) * 40
        
        # Score basé sur la localisation
        if location_on_plant:
            location_matches = sum(1 for loc in pest["location"]
                                 if loc.lower() in location_on_plant.lower())
            score += (location_matches / len(pest["location"])) * 30
        
        identification_scores.append({
            "pest": pest["name"],
            "scientific_name": pest["scientific_name"],
            "probability": score,
            "description": pest["description"],
            "damage_patterns": pest["damage"],
            "preferred_location": pest["location"],
            "lifecycle": pest["lifecycle"],
            "peak_season": pest["peak_season"],
            "economic_impact": pest["economic_impact"]
        })
    
    # Tri par probabilité
    identification_scores.sort(key=lambda x: x["probability"], reverse=True)
    
    # Utiliser Gemini pour l'analyse
    prompt = f"""
    Identification de parasite sur {crop} au Cameroun:
    
    Description observée: {pest_description}
    Type de dégâts: {damage_type or 'Non spécifié'}
    Localisation: {location_on_plant or 'Non spécifiée'}
    
    Identifications possibles: {identification_scores[:3]}
    
    Fournis une analyse détaillée incluant:
    1. Identification la plus probable avec justification
    2. Stade de développement probable
    3. Niveau d'infestation estimé
    4. Urgence d'intervention
    5. Méthodes de confirmation d'identification
    6. Prédiction évolution sans traitement
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "pest_description": pest_description,
        "damage_type": damage_type,
        "location_on_plant": location_on_plant,
        "identification_results": identification_scores,
        "most_likely_pest": identification_scores[0] if identification_scores else None,
        "identification_analysis": response.text,
        "confidence_level": identification_scores[0]["probability"] if identification_scores else 0
    }


def get_prevention_strategies(
    crop: str,
    tool_context: ToolContext,
    region: Optional[str] = None,
    main_threats: Optional[List[str]] = None,
    farming_system: str = "traditionnel",
) -> Dict[str, Any]:
    """Fournit des stratégies de prévention personnalisées.
    
    Args:
        crop: Culture à protéger
        region: Région de culture
        main_threats: Menaces principales identifiées
        farming_system: Système de culture
        tool_context: Contexte de l'outil
        
    Returns:
        Stratégies de prévention complètes
    """
    # Stratégies préventives par catégorie
    prevention_strategies = {
        "culturales": [
            {"strategy": "Rotation des cultures", "cost": 0, "efficacy": 70, "description": "Briser le cycle des parasites"},
            {"strategy": "Densité optimale", "cost": 5000, "efficacy": 60, "description": "Réduire humidité et compétition"},
            {"strategy": "Associations culturales", "cost": 2000, "efficacy": 65, "description": "Plantes répulsives ou attractives"},
            {"strategy": "Dates de semis", "cost": 0, "efficacy": 55, "description": "Éviter les pics d'infestation"}
        ],
        "biologiques": [
            {"strategy": "Auxiliaires naturels", "cost": 10000, "efficacy": 75, "description": "Prédateurs et parasitoïdes"},
            {"strategy": "Plantes pièges", "cost": 3000, "efficacy": 60, "description": "Concentrer les parasites"},
            {"strategy": "Biodiversité fonctionnelle", "cost": 5000, "efficacy": 70, "description": "Haies, bandes fleuries"},
            {"strategy": "Micro-organismes bénéfiques", "cost": 8000, "efficacy": 65, "description": "Mycorhizes, rhizobactéries"}
        ],
        "physiques": [
            {"strategy": "Paillage", "cost": 15000, "efficacy": 50, "description": "Limiter mauvaises herbes et maladies sol"},
            {"strategy": "Filets anti-insectes", "cost": 25000, "efficacy": 85, "description": "Barrière physique"},
            {"strategy": "Pièges colorés", "cost": 8000, "efficacy": 60, "description": "Capture des adultes volants"},
            {"strategy": "Barrières végétales", "cost": 12000, "efficacy": 55, "description": "Haies répulsives"}
        ],
        "sanitaires": [
            {"strategy": "Assainissement", "cost": 2000, "efficacy": 80, "description": "Élimination résidus infectés"},
            {"strategy": "Désinfection outils", "cost": 1000, "efficacy": 70, "description": "Éviter propagation"},
            {"strategy": "Quarantaine nouvelles plants", "cost": 500, "efficacy": 90, "description": "Contrôle introduction"},
            {"strategy": "Surveillance régulière", "cost": 3000, "efficacy": 85, "description": "Détection précoce"}
        ],
        "nutritionnelles": [
            {"strategy": "Équilibre NPK", "cost": 20000, "efficacy": 65, "description": "Plantes plus résistantes"},
            {"strategy": "Amendements organiques", "cost": 15000, "efficacy": 70, "description": "Amélioration sol et résistance"},
            {"strategy": "Oligoéléments", "cost": 8000, "efficacy": 60, "description": "Stimulation défenses naturelles"},
            {"strategy": "Compost de qualité", "cost": 10000, "efficacy": 68, "description": "Nutrition équilibrée"}
        ]
    }
    
    # Sélection selon le système de culture
    if farming_system == "traditionnel":
        priority_categories = ["culturales", "sanitaires", "nutritionnelles"]
    elif farming_system == "biologique":
        priority_categories = ["biologiques", "culturales", "physiques"]
    else:  # intensif
        priority_categories = ["physiques", "biologiques", "nutritionnelles"]
    
    # Sélection des meilleures stratégies
    selected_strategies = {}
    for category in priority_categories:
        if category in prevention_strategies:
            # Trier par efficacité et sélectionner les 3 meilleures
            best_strategies = sorted(prevention_strategies[category], 
                                   key=lambda x: x["efficacy"], reverse=True)[:3]
            selected_strategies[category] = best_strategies
    
    # Calcul du coût total et efficacité moyenne
    total_cost = 0
    total_efficacy = 0
    strategy_count = 0
    
    for strategies in selected_strategies.values():
        for strategy in strategies:
            total_cost += strategy["cost"]
            total_efficacy += strategy["efficacy"]
            strategy_count += 1
    
    average_efficacy = total_efficacy / strategy_count if strategy_count > 0 else 0
    
    # Utiliser Gemini pour les recommandations
    prompt = f"""
    Stratégies de prévention pour {crop} au Cameroun:
    
    Région: {region or 'Non spécifiée'}
    Système de culture: {farming_system}
    Menaces principales: {', '.join(main_threats) if main_threats else 'Génériques'}
    
    Stratégies sélectionnées: {selected_strategies}
    Coût total estimé: {total_cost} FCFA
    Efficacité moyenne: {average_efficacy:.1f}%
    
    Élabore un plan préventif incluant:
    1. Priorités d'action selon les menaces
    2. Calendrier de mise en œuvre
    3. Combinaisons synergiques de stratégies
    4. Adaptations selon les conditions locales
    5. Indicateurs de suivi et évaluation
    6. Plan d'urgence si prévention insuffisante
    7. Formation nécessaire pour l'agriculteur
    """
    
    response = model.generate_content(prompt)
    
    return {
        "crop": crop,
        "region": region,
        "main_threats": main_threats,
        "farming_system": farming_system,
        "prevention_strategies": selected_strategies,
        "implementation_cost": total_cost,
        "expected_efficacy": average_efficacy,
        "prevention_plan": response.text,
        "priority_actions": [
            strategy["strategy"] for strategies in selected_strategies.values()
            for strategy in sorted(strategies, key=lambda x: x["efficacy"], reverse=True)[:2]
        ]
    }