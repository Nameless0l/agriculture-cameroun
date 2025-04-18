# Copyright 2025 Agriculture Cameroun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Fonctions utilitaires pour le système multi-agents agriculture."""

import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from functools import wraps
import time

from agriculture_cameroun.config import AgricultureConfig, RegionType, CropType, SeasonType


def validate_cameroon_phone(phone: str) -> bool:
    """Valide un numéro de téléphone camerounais.
    
    Args:
        phone: Numéro de téléphone à valider
        
    Returns:
        True si le numéro est valide
    """
    # Formats acceptés: +237XXXXXXXX, 237XXXXXXXX, 6XXXXXXXX, 2XXXXXXXX
    patterns = [
        r'^\+237[26][0-9]{8}$',  # +237 suivi de 6 ou 2 et 8 chiffres
        r'^237[26][0-9]{8}$',    # 237 suivi de 6 ou 2 et 8 chiffres
        r'^[26][0-9]{8}$'        # 6 ou 2 suivi de 8 chiffres
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)


def format_currency(amount: float, currency: str = "FCFA") -> str:
    """Formate un montant avec la devise.
    
    Args:
        amount: Montant à formater
        currency: Devise (par défaut FCFA)
        
    Returns:
        Montant formaté avec séparateurs de milliers
    """
    return f"{amount:,.0f} {currency}".replace(",", " ")


def calculate_distance_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcule la distance entre deux points géographiques.
    
    Args:
        lat1, lon1: Coordonnées du premier point
        lat2, lon2: Coordonnées du second point
        
    Returns:
        Distance en kilomètres
    """
    import math
    
    # Rayon de la Terre en km
    R = 6371
    
    # Conversion en radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Différences
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Formule de Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def get_season_from_date(date: datetime, region: RegionType) -> SeasonType:
    """Détermine la saison agricole selon la date et la région.
    
    Args:
        date: Date à évaluer
        region: Région du Cameroun
        
    Returns:
        Saison agricole correspondante
    """
    month = date.month
    
    # Zones sahéliennes (Nord, Extrême-Nord)
    if region in [RegionType.NORD, RegionType.EXTREME_NORD]:
        if month in [6, 7, 8, 9]:
            return SeasonType.SAISON_PLUIES
        else:
            return SeasonType.SAISON_SECHE
    
    # Zones forestières (deux saisons des pluies)
    elif region in [RegionType.CENTRE, RegionType.SUD, RegionType.EST, RegionType.LITTORAL]:
        if month in [3, 4, 5]:
            return SeasonType.SAISON_PLUIES
        elif month in [6, 7]:
            return SeasonType.PETITE_SAISON_SECHE
        elif month in [8, 9, 10, 11]:
            return SeasonType.SAISON_PLUIES
        else:
            return SeasonType.GRANDE_SAISON_SECHE
    
    # Autres régions (pattern similaire aux zones forestières)
    else:
        if month in [3, 4, 5, 8, 9, 10]:
            return SeasonType.SAISON_PLUIES
        else:
            return SeasonType.SAISON_SECHE


def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """Convertit entre différentes unités agricoles.
    
    Args:
        value: Valeur à convertir
        from_unit: Unité d'origine
        to_unit: Unité de destination
        
    Returns:
        Valeur convertie
    """
    # Conversions de surface
    area_conversions = {
        ("ha", "m2"): 10000,
        ("ha", "acre"): 2.47105,
        ("m2", "ha"): 0.0001,
        ("acre", "ha"): 0.404686
    }
    
    # Conversions de poids
    weight_conversions = {
        ("kg", "t"): 0.001,
        ("t", "kg"): 1000,
        ("kg", "lb"): 2.20462,
        ("lb", "kg"): 0.453592
    }
    
    # Conversions de volume
    volume_conversions = {
        ("l", "m3"): 0.001,
        ("m3", "l"): 1000,
        ("gal", "l"): 3.78541
    }
    
    all_conversions = {**area_conversions, **weight_conversions, **volume_conversions}
    
    conversion_key = (from_unit.lower(), to_unit.lower())
    if conversion_key in all_conversions:
        return value * all_conversions[conversion_key]
    elif (to_unit.lower(), from_unit.lower()) in all_conversions:
        return value / all_conversions[(to_unit.lower(), from_unit.lower())]
    else:
        raise ValueError(f"Conversion non supportée: {from_unit} vers {to_unit}")


def calculate_growing_degree_days(temp_min: float, temp_max: float, base_temp: float = 10) -> float:
    """Calcule les degrés-jours de croissance.
    
    Args:
        temp_min: Température minimale
        temp_max: Température maximale
        base_temp: Température de base pour la culture
        
    Returns:
        Degrés-jours de croissance
    """
    temp_avg = (temp_min + temp_max) / 2
    return max(0, temp_avg - base_temp)


def estimate_crop_maturity(planting_date: datetime, crop: CropType, region: RegionType) -> datetime:
    """Estime la date de maturité d'une culture.
    
    Args:
        planting_date: Date de plantation
        crop: Type de culture
        region: Région de culture
        
    Returns:
        Date estimée de maturité
    """
    # Durées de cycle par culture (jours)
    cycle_durations = {
        CropType.MAIS: 120,
        CropType.ARACHIDE: 120,
        CropType.MANIOC: 300,
        CropType.PLANTAIN: 365,
        CropType.CACAO: 365,
        CropType.CAFE: 365
    }
    
    base_duration = cycle_durations.get(crop, 120)
    
    # Ajustements selon la région (températures)
    if region in [RegionType.NORD, RegionType.EXTREME_NORD]:
        # Températures plus élevées = cycle plus rapide
        adjusted_duration = base_duration * 0.9
    elif region in [RegionType.OUEST, RegionType.NORD_OUEST]:
        # Températures plus fraîches = cycle plus lent
        adjusted_duration = base_duration * 1.1
    else:
        adjusted_duration = base_duration
    
    return planting_date + timedelta(days=int(adjusted_duration))


def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """Décorateur pour réessayer une fonction en cas d'exception.
    
    Args:
        max_retries: Nombre maximum de tentatives
        delay: Délai entre les tentatives (secondes)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay * (2 ** attempt))  # Backoff exponentiel
                    continue
            
            raise last_exception
        return wrapper
    return decorator


def generate_cache_key(*args, **kwargs) -> str:
    """Génère une clé de cache basée sur les arguments.
    
    Args:
        *args: Arguments positionnels
        **kwargs: Arguments nommés
        
    Returns:
        Clé de cache unique
    """
    # Créer une chaîne représentant tous les arguments
    key_string = str(args) + str(sorted(kwargs.items()))
    
    # Générer un hash MD5
    return hashlib.md5(key_string.encode()).hexdigest()


def simple_cache(timeout: int = 300):
    """Cache simple en mémoire avec timeout.
    
    Args:
        timeout: Durée de vie du cache en secondes
    """
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer la clé de cache
            cache_key = generate_cache_key(func.__name__, *args, **kwargs)
            
            # Vérifier si la valeur est en cache et non expirée
            if cache_key in cache:
                value, timestamp = cache[cache_key]
                if time.time() - timestamp < timeout:
                    return value
            
            # Exécuter la fonction et mettre en cache
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        return wrapper
    return decorator


def sanitize_input(text: str) -> str:
    """Nettoie et valide une entrée de texte.
    
    Args:
        text: Texte à nettoyer
        
    Returns:
        Texte nettoyé
    """
    if not isinstance(text, str):
        return ""
    
    # Supprimer les caractères dangereux
    text = re.sub(r'[<>"\';]', '', text)
    
    # Limiter la longueur
    text = text[:1000]
    
    # Nettoyer les espaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def load_json_config(config_path: str) -> Dict[str, Any]:
    """Charge un fichier de configuration JSON.
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        Configuration sous forme de dictionnaire
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Erreur de format JSON dans {config_path}: {e}")


def save_json_config(config: Dict[str, Any], config_path: str) -> None:
    """Sauvegarde une configuration au format JSON.
    
    Args:
        config: Configuration à sauvegarder
        config_path: Chemin de destination
    """
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise IOError(f"Erreur lors de la sauvegarde de {config_path}: {e}")


def calculate_roi(investment: float, annual_return: float, years: int) -> Dict[str, float]:
    """Calcule le retour sur investissement.
    
    Args:
        investment: Montant de l'investissement initial
        annual_return: Retour annuel net
        years: Nombre d'années
        
    Returns:
        Métriques de ROI
    """
    total_return = annual_return * years
    roi_percent = (total_return / investment) * 100 if investment > 0 else 0
    payback_period = investment / annual_return if annual_return > 0 else float('inf')
    
    return {
        "total_return": total_return,
        "roi_percent": roi_percent,
        "payback_period_years": payback_period,
        "annual_roi_percent": roi_percent / years if years > 0 else 0
    }


def format_area(area_m2: float, preferred_unit: str = "ha") -> str:
    """Formate une superficie avec l'unité appropriée.
    
    Args:
        area_m2: Superficie en mètres carrés
        preferred_unit: Unité préférée (ha, m2, acre)
        
    Returns:
        Superficie formatée
    """
    if preferred_unit == "ha":
        if area_m2 >= 10000:
            return f"{area_m2/10000:.2f} ha"
        else:
            return f"{area_m2:.0f} m²"
    elif preferred_unit == "acre":
        return f"{area_m2/4047:.2f} acres"
    else:
        return f"{area_m2:.0f} m²"


def get_moon_phase(date: datetime) -> str:
    """Détermine la phase lunaire (approximation).
    
    Args:
        date: Date à évaluer
        
    Returns:
        Phase lunaire
    """
    # Calcul simplifié basé sur une approximation
    # Nouvelle lune de référence: 6 janvier 2000
    reference_date = datetime(2000, 1, 6)
    days_since_reference = (date - reference_date).days
    
    # Cycle lunaire moyen: 29.53 jours
    lunar_cycle = 29.53
    phase_position = (days_since_reference % lunar_cycle) / lunar_cycle
    
    if phase_position < 0.125:
        return "Nouvelle lune"
    elif phase_position < 0.375:
        return "Premier croissant"
    elif phase_position < 0.625:
        return "Pleine lune"
    elif phase_position < 0.875:
        return "Dernier croissant"
    else:
        return "Nouvelle lune"


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Valide si des coordonnées sont dans les limites du Cameroun.
    
    Args:
        latitude: Latitude à valider
        longitude: Longitude à valider
        
    Returns:
        True si les coordonnées sont au Cameroun
    """
    # Limites approximatives du Cameroun
    # Latitude: 1.7°N à 13.1°N
    # Longitude: 8.5°E à 16.2°E
    
    return (1.7 <= latitude <= 13.1) and (8.5 <= longitude <= 16.2)


def get_agricultural_zones(region: RegionType) -> List[str]:
    """Retourne les zones agricoles principales d'une région.
    
    Args:
        region: Région du Cameroun
        
    Returns:
        Liste des zones agricoles
    """
    zones = {
        RegionType.CENTRE: ["Yaoundé", "Mbalmayo", "Obala", "Mfou", "Soa"],
        RegionType.LITTORAL: ["Douala", "Edéa", "Nkongsamba", "Pouma", "Dizangué"],
        RegionType.OUEST: ["Bafoussam", "Dschang", "Mbouda", "Bangangté", "Foumban"],
        RegionType.NORD: ["Garoua", "Guider", "Figuil", "Pitoa", "Bibemi"],
        RegionType.SUD: ["Ebolowa", "Sangmélima", "Kribi", "Ambam", "Lolodorf"],
        RegionType.EST: ["Bertoua", "Batouri", "Yokadouma", "Abong-Mbang", "Kette"],
        RegionType.ADAMAOUA: ["Ngaoundéré", "Meiganga", "Banyo", "Tibati", "Tignère"],
        RegionType.EXTREME_NORD: ["Maroua", "Mokolo", "Kousseri", "Waza", "Mora"],
        RegionType.NORD_OUEST: ["Bamenda", "Kumbo", "Wum", "Nkambe", "Fundong"],
        RegionType.SUD_OUEST: ["Buea", "Limbe", "Kumba", "Mamfe", "Idenau"]
    }
    
    return zones.get(region, [])


class AgricultureLogger:
    """Logger simple pour les opérations agricoles."""
    
    def __init__(self, log_file: str = "agriculture.log"):
        self.log_file = log_file
    
    def log(self, level: str, message: str, context: Dict[str, Any] = None):
        """Enregistre un message de log.
        
        Args:
            level: Niveau de log (INFO, WARNING, ERROR)
            message: Message à enregistrer
            context: Contexte supplémentaire
        """
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}"
        
        if context:
            log_entry += f" | Context: {json.dumps(context, ensure_ascii=False)}"
        
        # Écrire dans le fichier de log
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception:
            pass  # Ignore les erreurs de log pour ne pas interrompre l'application
    
    def info(self, message: str, context: Dict[str, Any] = None):
        self.log("INFO", message, context)
    
    def warning(self, message: str, context: Dict[str, Any] = None):
        self.log("WARNING", message, context)
    
    def error(self, message: str, context: Dict[str, Any] = None):
        self.log("ERROR", message, context)


# Instance globale du logger
logger = AgricultureLogger()