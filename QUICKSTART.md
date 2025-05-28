# ⚡ Démarrage Rapide - Agriculture Cameroun

Ce guide vous permet de démarrer rapidement avec le système Agriculture Cameroun en moins de 10 minutes.

## 🚀 Installation Express (5 minutes)

### Prérequis

- Python 3.12+ installé
- Connexion Internet

### 1. Installation automatique

```bash
# Cloner et installer d'un coup
git clone https://github.com/votre-organisation/agriculture-cameroun.git
cd agriculture-cameroun
pip install poetry
poetry install
```

### 2. Configuration minimale

```bash
# Copier la configuration
cp .env.example .env

# Éditer le fichier .env et ajouter votre clé API Gemini
# GEMINI_API_KEY=votre_cle_ici
```

### 3. Premier lancement

```bash
# Activer l'environnement et lancer
poetry shell
adk serve . --port 8080
```

Ouvrir http://localhost:8080 dans votre navigateur.

## 🎯 Premières Questions

Testez le système avec ces questions typiques :

### Agriculture générale

- "Comment optimiser ma production de maïs ?"
- "Quand planter le manioc dans la région Centre ?"
- "Quelles sont les meilleures variétés de cacao pour l'Ouest ?"

### Problèmes de santé des plantes

- "Mon cacao a des taches brunes sur les feuilles"
- "Comment traiter les chenilles sur le maïs ?"
- "Prévention de la pourriture du manioc"

### Questions économiques

- "Prix actuel de l'arachide au marché"
- "Rentabilité d'1 hectare de palmier à huile"
- "Coût de production du café arabica"

### Gestion des ressources

- "Comment améliorer un sol argileux ?"
- "Techniques d'irrigation pour le maraîchage"
- "Engrais organiques disponibles localement"

### Météorologie

- "Prévisions météo pour les plantations"
- "Meilleure période pour récolter le cacao"
- "Impact de la saison sèche sur le maïs"

## 🔧 Interface Web

### Navigation principale

- **Chat** : Interface conversationnelle principale
- **Agents** : Accès direct aux agents spécialisés
- **Données** : Informations sur les cultures et régions
- **Aide** : Documentation et support

### Fonctionnalités clés

- **Multi-langues** : Français/Anglais
- **Géolocalisation** : Conseils par région
- **Historique** : Conversations sauvegardées
- **Export** : Télécharger les recommandations

## 📱 Utilisation Mobile

L'interface web est responsive et fonctionne sur mobile :

1. Ouvrir http://votre-ip:8080 sur mobile
2. Ajouter à l'écran d'accueil pour un accès rapide
3. Utiliser la reconnaissance vocale pour poser des questions

## 🎓 Cas d'Usage Typiques

### Pour un petit agriculteur

```
"Je suis agriculteur dans la région du Littoral. 
J'ai 2 hectares et je veux diversifier mes cultures. 
Que me conseillez-vous ?"
```

### Pour un problème urgent

```
"URGENT: Mes plants de tomates flétrissent rapidement. 
Feuilles jaunes avec taches noires. 
Que faire immédiatement ?"
```

### Pour une planification

```
"Je veux créer un calendrier agricole pour l'année prochaine 
dans la région Nord. Cultures: maïs, sorgho, arachide."
```

### Pour l'analyse économique

```
"Analyse comparative: cacao vs café arabica vs palmier à huile 
pour 10 hectares dans l'Ouest. ROI sur 5 ans."
```

## 🛠️ Personnalisation Rapide

### Changer la région par défaut

```bash
# Dans .env
DEFAULT_REGION=Littoral
```

### Modifier les modèles IA

```bash
# Utiliser des modèles plus rapides
WEATHER_AGENT_MODEL=gemini-1.5-flash
CROPS_AGENT_MODEL=gemini-1.5-flash
```

### Ajouter des données locales

```python
# Dans agriculture_cameroun/utils/data.py
REGIONS["Nouvelle_Region"] = {
    "climate": "tropical",
    "soil_types": ["argilo-sableux"],
    "main_crops": ["manioc", "plantain"]
}
```

## 🔍 Diagnostics Rapides

### Vérifier que tout fonctionne

```bash
# Test des composants
poetry run pytest tests/test_quick.py -v

# Test de l'API
curl http://localhost:8080/health
```

### Problèmes courants

#### Erreur "API Key not found"

```bash
# Vérifier le fichier .env
cat .env | grep GEMINI_API_KEY
```

#### Port déjà utilisé

```bash
# Utiliser un autre port
adk serve . --port 8081
```

#### Lenteur des réponses

```bash
# Utiliser des modèles plus rapides
export HEALTH_AGENT_MODEL=gemini-1.5-flash
```

## 🚀 Fonctionnalités Avancées (Optionnel)

### Mode développeur

```bash
# Lancer avec debug
adk serve . --debug --reload

# Accéder aux logs détaillés
tail -f logs/agriculture.log
```

### API REST

```python
import requests

response = requests.post("http://localhost:8080/api/chat", json={
    "message": "Prix du cacao aujourd'hui",
    "context": {"region": "Centre", "user_type": "farmer"}
})
```

### Intégration WhatsApp/Telegram

```python
# Webhook pour recevoir des messages
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(message: dict):
    response = await root_agent.generate_content(message["text"])
    return {"reply": response.text}
```

## 📊 Métriques et Monitoring

### Statistiques d'usage

- Accéder à http://localhost:8080/stats
- Voir les questions les plus fréquentes
- Analyser les performances par agent

### Logs structurés

```bash
# Suivre les logs en temps réel
tail -f logs/agriculture.log | grep ERROR
```

## 🌍 Déploiement Public

### Hébergement gratuit sur Railway

```bash
# Installation Railway CLI
npm install -g @railway/cli

# Déploiement
railway login
railway deploy
```

### Configuration domaine personnalisé

1. Acheter un domaine (ex: agriculture-cm.com)
2. Configurer les DNS vers votre serveur
3. Activer HTTPS avec Let's Encrypt

## 📞 Support Express

### Discord communautaire

Rejoindre : https://discord.gg/agriculture-cameroun

### FAQ rapide

- **Q**: Comment ajouter une nouvelle culture ?
- **R**: Modifier `agriculture_cameroun/utils/data.py`
- **Q**: Le système fonctionne-t-il hors ligne ?
- **R**: Partiellement, mais l'IA nécessite Internet
- **Q**: Puis-je l'utiliser commercialement ?
- **R**: Oui, sous licence Apache 2.0

## 🎉 Prochaines Étapes

1. **Explorer** : Tester différents types de questions
2. **Personnaliser** : Ajouter vos données locales
3. **Partager** : Inviter d'autres agriculteurs
4. **Contribuer** : Améliorer le système
5. **Déployer** : Mettre en production

---

**🌱 Bon agriculture avec l'IA ! Le Cameroun agricole du futur commence aujourd'hui.**
