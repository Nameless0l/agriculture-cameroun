"""
Démonstration CLI - Agriculture Cameroun
========================================

Interface en ligne de commande simple pour tester les fonctionnalités
du système Agriculture Cameroun.
"""

import argparse
import sys
from typing import Optional


def simulate_weather_query(region: str, query: str) -> str:
    """Simule une consultation météo."""
    responses = {
        "yaoundé": f"🌤️ Météo {region}: Températures 22-28°C, averses l'après-midi. Idéal pour irrigation matinale.",
        "douala": f"🌤️ Météo {region}: Temps humide 25-30°C, forte humidité. Attention aux maladies fongiques.",
        "bafoussam": f"🌤️ Météo {region}: Climat frais 18-24°C, brouillards matinaux. Parfait pour café arabica."
    }
    return responses.get(region.lower(), f"🌤️ Météo {region}: Consultez les prévisions locales pour plus de détails.")


def simulate_crop_query(crop: str, region: str) -> str:
    """Simule une consultation cultures."""
    responses = {
        "maïs": f"🌱 Maïs ({region}): Variété recommandée ATP-Y, plantation mars-mai, rendement 4-6t/ha.",
        "café": f"🌱 Café ({region}): Arabica pour l'Ouest, Robusta pour le Centre/Sud. Plantation début pluies.",
        "cacao": f"🌱 Cacao ({region}): Variétés hybrides recommandées, ombrage nécessaire, récolte 2x/an.",
        "manioc": f"🌱 Manioc ({region}): Plantation toute année, variétés améliorées TMS, récolte 8-12 mois."
    }
    return responses.get(crop.lower(), f"🌱 {crop} ({region}): Consultez l'agent cultures pour des conseils spécifiques.")


def simulate_health_query(symptoms: str, crop: str) -> str:
    """Simule un diagnostic de santé."""
    if "jaune" in symptoms.lower() and "tache" in symptoms.lower():
        return f"🏥 Diagnostic {crop}: Probable maladie fongique. Traitement fongicide cuivrique recommandé."
    elif "flétrissement" in symptoms.lower():
        return f"🏥 Diagnostic {crop}: Possible stress hydrique ou maladie racinaire. Vérifiez irrigation."
    elif "insecte" in symptoms.lower() or "chenille" in symptoms.lower():
        return f"🏥 Diagnostic {crop}: Attaque parasitaire. Traitement bio Bacillus thuringiensis recommandé."
    else:
        return f"🏥 Diagnostic {crop}: Pour un diagnostic précis, contactez un phytopathologiste local."


def simulate_economic_query(crop: str, area: float) -> str:
    """Simule une analyse économique."""
    prices = {
        "café": {"price": 3000, "yield": 1.2},
        "cacao": {"price": 1500, "yield": 0.6},
        "maïs": {"price": 250, "yield": 4.0},
        "manioc": {"price": 150, "yield": 15.0}
    }
    
    if crop.lower() in prices:
        data = prices[crop.lower()]
        revenue = data["price"] * data["yield"] * area * 1000  # conversion en FCFA
        return f"💰 {crop} ({area}ha): Revenus estimés {revenue:,.0f} FCFA/an (prix {data['price']} FCFA/kg, rendement {data['yield']}t/ha)."
    else:
        return f"💰 {crop}: Consultez l'agent économique pour une analyse détaillée des prix et rentabilité."


def simulate_resources_query(topic: str, region: str) -> str:
    """Simule une recherche de ressources."""
    responses = {
        "formation": f"📚 Formations {region}: IRAD, FASA Dschang, centres agricoles régionaux disponibles.",
        "financement": f"📚 Financement {region}: PINA, PAJER-U, Banque Agricole offrent des solutions adaptées.",
        "expert": f"📚 Experts {region}: Contactez la délégation MINADER locale pour mise en relation.",
        "subvention": f"📚 Subventions {region}: Aides gouvernementales et ONG disponibles selon profil."
    }
    return responses.get(topic.lower(), f"📚 {topic} ({region}): Consultez l'agent ressources pour plus d'informations.")


def interactive_mode():
    """Mode interactif pour tester les fonctionnalités."""
    print("🌱 AGRICULTURE CAMEROUN - MODE INTERACTIF")
    print("=========================================")
    print("Tapez 'aide' pour voir les commandes disponibles")
    print("Tapez 'quit' pour quitter\n")
    
    while True:
        try:
            user_input = input("🔍 Votre question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'quitter']:
                print("Au revoir ! 🌱")
                break
            elif user_input.lower() in ['aide', 'help']:
                print_help()
            elif not user_input:
                continue
            else:
                response = process_query(user_input)
                print(f"💬 {response}\n")
                
        except KeyboardInterrupt:
            print("\nAu revoir ! 🌱")
            break
        except EOFError:
            break


def process_query(query: str) -> str:
    """Traite une requête utilisateur et retourne une réponse simulée."""
    query_lower = query.lower()
    
    # Détection du type de question
    if any(word in query_lower for word in ['météo', 'temps', 'pluie', 'température']):
        region = extract_region(query) or "Cameroun"
        return simulate_weather_query(region, query)
    
    elif any(word in query_lower for word in ['planter', 'culture', 'variété', 'semis']):
        crop = extract_crop(query) or "culture"
        region = extract_region(query) or "Cameroun"
        return simulate_crop_query(crop, region)
    
    elif any(word in query_lower for word in ['maladie', 'jaune', 'tache', 'flétrissement', 'parasite']):
        crop = extract_crop(query) or "plante"
        return simulate_health_query(query, crop)
    
    elif any(word in query_lower for word in ['prix', 'rentabilité', 'vendre', 'économique']):
        crop = extract_crop(query) or "culture"
        return simulate_economic_query(crop, 1.0)
    
    elif any(word in query_lower for word in ['formation', 'apprendre', 'expert', 'aide', 'subvention']):
        region = extract_region(query) or "Cameroun"
        topic = "formation" if "formation" in query_lower else "expert"
        return simulate_resources_query(topic, region)
    
    else:
        return "🤖 Question intéressante ! Pour une réponse précise, spécifiez le type de conseil souhaité (météo, culture, santé, économie, ressources)."


def extract_region(text: str) -> Optional[str]:
    """Extrait la région mentionnée dans le texte."""
    regions = [
        'centre', 'littoral', 'ouest', 'nord-ouest', 'sud-ouest',
        'est', 'sud', 'adamaoua', 'nord', 'extrême-nord',
        'yaoundé', 'douala', 'bafoussam', 'bamenda', 'garoua'
    ]
    
    text_lower = text.lower()
    for region in regions:
        if region in text_lower:
            return region.title()
    return None


def extract_crop(text: str) -> Optional[str]:
    """Extrait la culture mentionnée dans le texte."""
    crops = [
        'maïs', 'café', 'cacao', 'manioc', 'plantain', 'banane',
        'tomate', 'chou', 'carotte', 'haricot', 'arachide',
        'palmier', 'hevea', 'ananas', 'avocat'
    ]
    
    text_lower = text.lower()
    for crop in crops:
        if crop in text_lower:
            return crop
    return None


def print_help():
    """Affiche l'aide des commandes."""
    print("""
📖 COMMANDES DISPONIBLES:
=========================

Types de questions supportées:

🌤️ MÉTÉO:
   - "Quel temps à Yaoundé ?"
   - "Quand arroser mes tomates ?"

🌱 CULTURES:
   - "Quand planter le maïs ?"
   - "Quelle variété de café pour l'Ouest ?"

🏥 SANTÉ DES PLANTES:
   - "Mes feuilles de cacao jaunissent"
   - "Comment traiter les parasites ?"

💰 ÉCONOMIE:
   - "Prix du café actuellement ?"
   - "Rentabilité plantation cacao ?"

📚 RESSOURCES:
   - "Formations agriculture bio ?"
   - "Subventions jeunes agriculteurs ?"

Commandes spéciales:
   - aide/help : Affiche cette aide
   - quit/exit : Quitte le programme
""")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Démonstration CLI du système Agriculture Cameroun",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python demo_cli.py --interactive
  python demo_cli.py --query "Quand planter le maïs dans le Nord ?"
  python demo_cli.py --weather --region Yaoundé
  python demo_cli.py --crop maïs --region Centre
        """
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Mode interactif'
    )
    
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Question directe'
    )
    
    parser.add_argument(
        '--weather', '-w',
        action='store_true',
        help='Consultation météo'
    )
    
    parser.add_argument(
        '--crop', '-c',
        type=str,
        help='Consultation culture spécifique'
    )
    
    parser.add_argument(
        '--region', '-r',
        type=str,
        default='Cameroun',
        help='Région (défaut: Cameroun)'
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.query:
        response = process_query(args.query)
        print(f"💬 {response}")
    elif args.weather:
        response = simulate_weather_query(args.region, "prévisions")
        print(f"💬 {response}")
    elif args.crop:
        response = simulate_crop_query(args.crop, args.region)
        print(f"💬 {response}")
    else:
        print("🌱 Agriculture Cameroun - Démonstration CLI")
        print("Utilisez --help pour voir les options disponibles")
        print("Ou lancez --interactive pour le mode interactif")


if __name__ == "__main__":
    main()
