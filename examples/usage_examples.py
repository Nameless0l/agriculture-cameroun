#!/usr/bin/env python3
"""
Exemples d'utilisation de l'Agriculture Cameroun API
====================================================

Ce script démontre comment utiliser les différents agents du système
Agriculture Cameroun pour obtenir des conseils agricoles personnalisés.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Simulation des imports (à remplacer par les vrais imports)
# from agriculture_cameroun import AgricultureAgent
# from agriculture_cameroun.sub_agents import WeatherAgent, CropsAgent, HealthAgent, EconomicAgent, ResourcesAgent


class ExampleRunner:
    """Gestionnaire d'exemples pour Agriculture Cameroun."""
    
    def __init__(self):
        """Initialise le gestionnaire d'exemples."""
        self.results = []
        
    def log_example(self, title: str, query: str, response: Dict[str, Any]):
        """Enregistre un exemple d'utilisation."""
        self.results.append({
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "query": query,
            "response": response
        })
        
        print(f"\n🌱 {title}")
        print("=" * (len(title) + 4))
        print(f"Question: {query}")
        print(f"Réponse: {response.get('answer', 'Pas de réponse')}")
        if response.get('confidence'):
            print(f"Confiance: {response['confidence']:.2%}")
        print("-" * 50)

    async def run_weather_examples(self):
        """Exemples d'utilisation de l'agent météo."""
        print("\n🌤️ EXEMPLES AGENT MÉTÉO")
        print("========================\n")
        
        # Simulation des réponses (à remplacer par de vrais appels API)
        examples = [
            {
                "title": "Prévisions météorologiques",
                "query": "Quel temps fera-t-il cette semaine à Yaoundé ?",
                "response": {
                    "answer": "Cette semaine à Yaoundé, attendez-vous à des températures entre 22°C et 28°C avec des averses l'après-midi mardi et jeudi. Humidité élevée (75-85%). Idéal pour l'irrigation matinale des cultures sensibles.",
                    "confidence": 0.91,
                    "weather_data": {
                        "avg_temp": 25,
                        "rainfall_days": 2,
                        "humidity": 80
                    }
                }
            },
            {
                "title": "Conseils d'irrigation",
                "query": "Quand arroser mes tomates à Douala en saison sèche ?",
                "response": {
                    "answer": "Pour vos tomates à Douala en saison sèche, arrosez tôt le matin (6h-8h) et en fin d'après-midi (17h-18h). Évitez l'arrosage en pleine journée. Quantité: 2-3L par plant tous les 2 jours selon l'humidité du sol.",
                    "confidence": 0.88,
                    "irrigation_schedule": {
                        "frequency": "every_2_days",
                        "quantity": "2-3L_per_plant",
                        "best_times": ["06:00-08:00", "17:00-18:00"]
                    }
                }
            },
            {
                "title": "Alerte climatique",
                "query": "Y a-t-il des risques climatiques pour mes cultures cette semaine ?",
                "response": {
                    "answer": "⚠️ ALERTE: Fortes pluies attendues mercredi-jeudi (30-50mm). Protégez vos cultures fragiles, vérifiez le drainage, et reportez les traitements phytosanitaires. Risque modéré d'érosion sur les terrains en pente.",
                    "confidence": 0.94,
                    "alerts": [
                        {
                            "type": "heavy_rain",
                            "severity": "moderate",
                            "days": ["mercredi", "jeudi"]
                        }
                    ]
                }
            }
        ]
        
        for example in examples:
            self.log_example(example["title"], example["query"], example["response"])
            await asyncio.sleep(0.5)  # Pause pour la démonstration

    async def run_crops_examples(self):
        """Exemples d'utilisation de l'agent cultures."""
        print("\n🌱 EXEMPLES AGENT CULTURES")
        print("==========================\n")
        
        examples = [
            {
                "title": "Recommandation de variété",
                "query": "Quelle variété de maïs planter dans la région du Nord en saison sèche ?",
                "response": {
                    "answer": "Pour la région du Nord en saison sèche, je recommande la variété TZPB-SR (résistante au Striga) ou ATP-Y (cycle court 85 jours). Ces variétés tolèrent bien la sécheresse et ont un bon rendement (4-6 t/ha).",
                    "confidence": 0.92,
                    "recommendations": [
                        {
                            "variety": "TZPB-SR",
                            "advantages": ["Résistant Striga", "Tolérant sécheresse"],
                            "yield": "4-6 t/ha"
                        }
                    ]
                }
            },
            {
                "title": "Calendrier de plantation",
                "query": "Quand planter le manioc dans la région de l'Est ?",
                "response": {
                    "answer": "Dans l'Est, plantez le manioc de mars à mai (début saison des pluies) ou septembre-octobre. Privilégiez avril-mai pour un meilleur enracinement. Récolte après 8-12 mois selon la variété.",
                    "confidence": 0.89,
                    "planting_calendar": {
                        "optimal_periods": ["mars-mai", "septembre-octobre"],
                        "best_month": "avril-mai",
                        "harvest_time": "8-12 mois"
                    }
                }
            },
            {
                "title": "Techniques culturales",
                "query": "Comment améliorer le rendement de mes plantains ?",
                "response": {
                    "answer": "Pour améliorer vos plantains: 1) Espacement 3m x 3m, 2) Fumure organique 10kg/pied, 3) Œilletonnage régulier, 4) Irrigation en saison sèche, 5) Traitement préventif nématodes. Rendement attendu: 20-30 t/ha.",
                    "confidence": 0.87,
                    "techniques": [
                        "Espacement optimal",
                        "Fumure organique",
                        "Œilletonnage",
                        "Gestion irrigation"
                    ]
                }
            }
        ]
        
        for example in examples:
            self.log_example(example["title"], example["query"], example["response"])
            await asyncio.sleep(0.5)

    async def run_health_examples(self):
        """Exemples d'utilisation de l'agent santé."""
        print("\n🏥 EXEMPLES AGENT SANTÉ")
        print("=======================\n")
        
        examples = [
            {
                "title": "Diagnostic de maladie",
                "query": "Mes feuilles de cacao ont des taches noires et jaunissent, que faire ?",
                "response": {
                    "answer": "Diagnostic probable: Pourriture brune (Phytophthora). Traitement immédiat: 1) Supprimez cabosses infectées, 2) Pulvérisez fongicide cuivrique, 3) Améliorez drainage, 4) Taillez pour aération. Répétez traitement tous les 15 jours.",
                    "confidence": 0.85,
                    "diagnosis": {
                        "disease": "Pourriture brune",
                        "pathogen": "Phytophthora",
                        "severity": "Modérée"
                    },
                    "treatment": [
                        "Suppression cabosses infectées",
                        "Fongicide cuivrique",
                        "Amélioration drainage"
                    ]
                }
            },
            {
                "title": "Prévention parasites",
                "query": "Comment prévenir les attaques de chenilles sur mes choux ?",
                "response": {
                    "answer": "Prévention chenilles sur choux: 1) Rotation avec légumineuses, 2) Filets anti-insectes, 3) Pulvérisation Bt (Bacillus thuringiensis) préventive, 4) Plantes répulsives (tagète), 5) Inspection hebdomadaire. Traitement bio efficace à 90%.",
                    "confidence": 0.91,
                    "prevention_methods": [
                        "Rotation culturale",
                        "Protection physique",
                        "Biocontrôle",
                        "Surveillance"
                    ]
                }
            },
            {
                "title": "Traitement biologique",
                "query": "Existe-t-il des traitements bio pour les pucerons sur tomates ?",
                "response": {
                    "answer": "Traitements bio anti-pucerons: 1) Savon noir 20g/L + huile neem, 2) Purins ortie/ail, 3) Coccinelles (auxiliaires), 4) Paillis réfléchissant, 5) Associations basilic/œillet d'Inde. Efficacité 85% en traitement précoce.",
                    "confidence": 0.88,
                    "bio_treatments": [
                        "Savon noir + neem",
                        "Purins végétaux",
                        "Auxiliaires",
                        "Associations végétales"
                    ]
                }
            }
        ]
        
        for example in examples:
            self.log_example(example["title"], example["query"], example["response"])
            await asyncio.sleep(0.5)

    async def run_economic_examples(self):
        """Exemples d'utilisation de l'agent économique."""
        print("\n💰 EXEMPLES AGENT ÉCONOMIQUE")
        print("=============================\n")
        
        examples = [
            {
                "title": "Analyse prix marché",
                "query": "Quel est le prix actuel du café arabica au Cameroun ?",
                "response": {
                    "answer": "Prix café arabica (décembre 2024): 2,800-3,200 FCFA/kg (producteur), 4,500-5,000 FCFA/kg (détail). Tendance haussière (+8% vs novembre). Meilleur prix à Bafoussam et Dschang. Exportation: 450-500 FCFA/kg parche.",
                    "confidence": 0.93,
                    "price_data": {
                        "producer_price": "2,800-3,200 FCFA/kg",
                        "retail_price": "4,500-5,000 FCFA/kg",
                        "trend": "+8%",
                        "best_markets": ["Bafoussam", "Dschang"]
                    }
                }
            },
            {
                "title": "Calcul rentabilité",
                "query": "Quelle est la rentabilité d'une plantation de cacao de 2 hectares ?",
                "response": {
                    "answer": "Plantation cacao 2ha - Rentabilité: Coûts/an: 1,200,000 FCFA (main-d'œuvre 60%, intrants 25%, équipement 15%). Revenus/an: 1,800,000 FCFA (600kg/ha × 1,500 FCFA/kg). Bénéfice net: 600,000 FCFA/an. ROI: 33%.",
                    "confidence": 0.86,
                    "profitability": {
                        "annual_costs": "1,200,000 FCFA",
                        "annual_revenue": "1,800,000 FCFA",
                        "net_profit": "600,000 FCFA",
                        "roi": "33%"
                    }
                }
            },
            {
                "title": "Optimisation revenus",
                "query": "Comment maximiser mes revenus avec 5 hectares dans l'Ouest ?",
                "response": {
                    "answer": "Optimisation 5ha Ouest: 1) Mix café arabica (3ha) + maraîchage (1ha) + aviculture (1ha). 2) Transformation locale (+30% valeur). 3) Vente directe coopérative. 4) Cultures intercalaires. Revenus potentiels: 3,500,000 FCFA/an vs 2,100,000 monoculture.",
                    "confidence": 0.89,
                    "optimization_plan": {
                        "crop_mix": "café 3ha + maraîchage 1ha + aviculture 1ha",
                        "value_addition": "Transformation locale +30%",
                        "potential_revenue": "3,500,000 FCFA/an"
                    }
                }
            }
        ]
        
        for example in examples:
            self.log_example(example["title"], example["query"], example["response"])
            await asyncio.sleep(0.5)

    async def run_resources_examples(self):
        """Exemples d'utilisation de l'agent ressources."""
        print("\n📚 EXEMPLES AGENT RESSOURCES")
        print("=============================\n")
        
        examples = [
            {
                "title": "Formations disponibles",
                "query": "Où puis-je apprendre l'agriculture biologique au Cameroun ?",
                "response": {
                    "answer": "Formations agriculture bio: 1) IRAD Bambui (programme certifiant 3 mois), 2) FASA Université de Dschang (cursus ingénieur), 3) ONG SAILD (formations pratiques), 4) Centres de formation agricole régionaux. Coût: 50,000-200,000 FCFA selon durée.",
                    "confidence": 0.90,
                    "training_options": [
                        "IRAD Bambui - 3 mois",
                        "FASA Dschang - cursus complet",
                        "ONG SAILD - formations pratiques",
                        "Centres régionaux"
                    ]
                }
            },
            {
                "title": "Subventions et aides",
                "query": "Quelles aides existent pour les jeunes agriculteurs ?",
                "response": {
                    "answer": "Aides jeunes agriculteurs: 1) PINA (50,000-500,000 FCFA subvention), 2) PAJER-U (microcrédits 25,000-2,000,000 FCFA), 3) MINADER (kits agricoles gratuits), 4) Banque Agricole (prêts bonifiés 5-8%). Conditions: 18-35 ans, projet viable.",
                    "confidence": 0.87,
                    "funding_options": [
                        "PINA - subventions directes",
                        "PAJER-U - microcrédits",
                        "MINADER - kits gratuits",
                        "Banque Agricole - prêts bonifiés"
                    ]
                }
            },
            {
                "title": "Contact experts",
                "query": "Comment contacter un agronome dans la région du Centre ?",
                "response": {
                    "answer": "Experts région Centre: 1) IRAD Nkolbisson: Dr. Marie MANGA (+237 650 XX XX XX), 2) Délégation MINADER Yaoundé: Ing. Paul ESSONO, 3) Consultants privés AGRI-CONSEIL: (+237 677 XX XX XX). Consultation: 15,000-50,000 FCFA/visite.",
                    "confidence": 0.92,
                    "expert_contacts": [
                        "IRAD Nkolbisson - Dr. Marie MANGA",
                        "MINADER Yaoundé - Ing. Paul ESSONO",
                        "AGRI-CONSEIL - Consultants privés"
                    ]
                }
            }
        ]
        
        for example in examples:
            self.log_example(example["title"], example["query"], example["response"])
            await asyncio.sleep(0.5)

    async def run_integrated_example(self):
        """Exemple d'utilisation intégrée de plusieurs agents."""
        print("\n🌍 EXEMPLE INTÉGRÉ MULTI-AGENTS")
        print("===============================\n")
        
        scenario = {
            "title": "Nouveau projet agricole complet",
            "query": "Je veux créer une ferme de 3 hectares dans l'Ouest. Que me conseillez-vous ?",
            "response": {
                "answer": """Projet ferme 3ha Ouest - Plan intégré:

🌱 CULTURES RECOMMANDÉES:
- Café arabica: 2ha (revenu principal)
- Maraîchage: 0.5ha (carottes, choux, tomates)
- Aviculture: 0.5ha (1000 poules pondeuses)

🌤️ CONSIDÉRATIONS CLIMATIQUES:
- Plantation café: Mars-Mai (début pluies)
- Maraîchage: Toute année avec irrigation
- Attention saison sèche: Nov-Feb

💰 RENTABILITÉ ESTIMÉE:
- Investissement initial: 2,500,000 FCFA
- Revenus annuels an 3: 4,200,000 FCFA
- Seuil rentabilité: 18 mois

📚 RESSOURCES ET FORMATION:
- Formation FASA Dschang recommandée
- Aide PINA: 500,000 FCFA possible
- Suivi technique IRAD Foumbot

🏥 RISQUES ET PRÉVENTION:
- Traitement préventif café (anthracnose)
- Vaccination volailles (Newcastle)
- Assurance récolte conseillée""",
                "confidence": 0.94,
                "agents_consulted": ["weather", "crops", "economic", "resources", "health"],
                "implementation_timeline": "36 mois",
                "success_probability": "85%"
            }
        }
        
        self.log_example(scenario["title"], scenario["query"], scenario["response"])

    def save_results(self, filename: str = "agriculture_examples_results.json"):
        """Sauvegarde les résultats des exemples."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Résultats sauvegardés dans {filename}")

    async def run_all_examples(self):
        """Lance tous les exemples d'utilisation."""
        print("🌱 DÉMONSTRATION AGRICULTURE CAMEROUN")
        print("=====================================")
        print("Simulation d'utilisation du système multi-agents")
        print("pour fournir des conseils agricoles personnalisés\n")
        
        await self.run_weather_examples()
        await self.run_crops_examples()
        await self.run_health_examples()
        await self.run_economic_examples()
        await self.run_resources_examples()
        await self.run_integrated_example()
        
        print("\n✅ DÉMONSTRATION TERMINÉE")
        print("=========================")
        print(f"Total d'exemples exécutés: {len(self.results)}")
        print("Ces exemples montrent les capacités du système Agriculture Cameroun")
        print("Pour utiliser le vrai système, configurez vos clés API et lancez:")
        print("  poetry run python -m agriculture_cameroun.agent")
        
        self.save_results()


async def main():
    """Fonction principale pour lancer les exemples."""
    runner = ExampleRunner()
    await runner.run_all_examples()


if __name__ == "__main__":
    # Lance les exemples
    asyncio.run(main())
