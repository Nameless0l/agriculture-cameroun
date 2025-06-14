# 📖 User Guide - Agriculture Cameroun

## Table des matières

1. [Vue d&#39;ensemble](#vue-densemble)
2. [Configuration initiale](#configuration-initiale)
3. [Utilisation des agents](#utilisation-des-agents)
4. [Types de consultations](#types-de-consultations)
5. [Exemples pratiques](#exemples-pratiques)
6. [Dépannage](#dépannage)
7. [Conseils avancés](#conseils-avancés)

## Vue d'ensemble

Agriculture Cameroun est un système multi-agents IA conçu pour fournir des conseils agricoles personnalisés aux agriculteurs camerounais. Le système utilise cinq agents spécialisés :

- **🌤️ Agent Météo** : Prévisions et alertes climatiques
- **🌱 Agent Cultures** : Conseils sur les variétés et pratiques culturales
- **🏥 Agent Santé** : Diagnostic et traitement des maladies des plantes
- **💰 Agent Économique** : Analyse des prix et optimisation des revenus
- **📚 Agent Ressources** : Accès aux ressources et formations

## Configuration initiale

### 1. Variables d'environnement

Après l'installation, configurez votre fichier `.env` avec vos informations :

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos clés API
nano .env  # ou votre éditeur préféré
```

#### Configuration minimale

```env
# Clés API (obligatoires)
GOOGLE_API_KEY=votre_clé_gemini
OPENWEATHER_API_KEY=votre_clé_openweather

# Localisation (recommandée)
DEFAULT_REGION=Centre
DEFAULT_LANGUAGE=fr
```



### 2. Test de la configuration

```bash
# Vérifier la configuration
poetry run python -m agriculture_cameroun.config --validate

# Test des API
poetry run python -m agriculture_cameroun.tools --test-apis
```

## Utilisation des agents

### Démarrage du système

```bash
# Activation de l'environnement
poetry shell

# Lancement du système principal
python -m agriculture_cameroun.agent

# Ou utilisation directe d'un agent spécifique
python -m agriculture_cameroun.sub_agents.weather.agent
```

### Interface en ligne de commande

```bash
# Consultation interactive
python -m agriculture_cameroun.agent --interactive

# Consultation directe
python -m agriculture_cameroun.agent --query "Quand planter le maïs dans la région du Centre ?"

# Agent spécifique
python -m agriculture_cameroun.sub_agents.crops.agent --crop=maïs --region=Centre
```

## Types de consultations

### 1. Consultations météorologiques

**Questions supportées :**

- Prévisions météorologiques
- Alertes climatiques
- Conseils d'irrigation
- Optimisation des périodes de plantation

**Exemples :**

```
🌤️ "Quel temps fera-t-il cette semaine à Yaoundé ?"
🌤️ "Y a-t-il des risques de sécheresse ce mois-ci ?"
🌤️ "Quand commencer l'irrigation pour mes tomates ?"
```

### 2. Consultations sur les cultures

**Questions supportées :**

- Sélection de variétés
- Calendriers de plantation
- Techniques de culture
- Optimisation des rendements

**Exemples :**

```
🌱 "Quelle variété de manioc est adaptée au sol argileux ?"
🌱 "Comment améliorer le rendement de mes cacaoyers ?"
🌱 "Quel espacement pour planter les bananiers ?"
```

### 3. Consultations de santé des plantes

**Questions supportées :**

- Diagnostic de maladies
- Identification de parasites
- Traitements recommandés
- Prévention

**Exemples :**

```
🏥 "Mes feuilles de café jaunissent, que faire ?"
🏥 "Comment traiter la pourriture brune du cacao ?"
🏥 "Prévention contre les attaques d'insectes sur maïs"
```

### 4. Consultations économiques

**Questions supportées :**

- Analyse des prix de marché
- Optimisation des revenus
- Calcul de rentabilité
- Stratégies de commercialisation

**Exemples :**

```
💰 "Quel est le prix actuel du café arabica ?"
💰 "Comment calculer la rentabilité de ma plantation ?"
💰 "Meilleur moment pour vendre mes tomates ?"
```

### 5. Accès aux ressources

**Questions supportées :**

- Formations disponibles
- Subventions et aides
- Contacts d'experts
- Documentation technique

**Exemples :**

```
📚 "Où trouver des formations sur l'agriculture biologique ?"
📚 "Quelles sont les aides disponibles pour les jeunes agriculteurs ?"
📚 "Contact d'un vétérinaire à Douala"
```

## Exemples pratiques

### Scénario 1 : Nouveau agriculteur

```bash
# Consultation complète pour débuter
python -m agriculture_cameroun.agent --query "Je suis nouveau dans l'agriculture, que planter dans la région de l'Ouest en saison sèche ?"
```

**Réponse attendue :**

- Recommandations de cultures adaptées
- Calendrier de plantation
- Prévisions météorologiques
- Ressources de formation
- Estimation économique

### Scénario 2 : Problème de maladie

```bash
# Diagnostic et traitement
python -m agriculture_cameroun.sub_agents.health.agent --symptoms "feuilles jaunes, taches noires, flétrissement" --crop "tomate"
```

**Processus :**

1. Analyse des symptômes
2. Diagnostic probable
3. Traitements recommandés
4. Mesures préventives
5. Suivi suggéré

### Scénario 3 : Optimisation économique

```bash
# Analyse de rentabilité
python -m agriculture_cameroun.sub_agents.economic.agent --analysis "rentabilité plantation cacao 2 hectares"
```

**Éléments fournis :**

- Coûts de production
- Revenus estimés
- Seuil de rentabilité
- Recommandations d'optimisation

## Dépannage

### Problèmes fréquents

#### 1. Erreur de clé API

```
Erreur : Invalid API key
```

**Solutions :**

- Vérifier la clé dans le fichier `.env`
- S'assurer que la clé est valide et active
- Vérifier les quotas de l'API

#### 2. Problème de connexion

```
Erreur : Connection timeout
```

**Solutions :**

- Vérifier la connexion internet
- Configurer le proxy si nécessaire
- Utiliser le mode hors ligne (limité)

#### 3. Réponse incohérente

```
L'agent donne des réponses inappropriées
```

**Solutions :**

- Reformuler la question plus précisément
- Spécifier la région et le contexte
- Utiliser l'agent spécialisé directement

### Mode debug

```bash
# Activer les logs détaillés
export LOG_LEVEL=DEBUG
python -m agriculture_cameroun.agent --debug --query "votre question"

# Traçage des appels API
export TRACE_APIS=true
python -m agriculture_cameroun.agent --query "votre question"
```

### Réinitialisation

```bash
# Nettoyer le cache
poetry run python -m agriculture_cameroun.utils --clear-cache

# Réinitialiser la configuration
rm .env
cp .env.example .env

# Réinstaller les dépendances
poetry install --sync
```


**Requêtes groupées :**

```bash
# Traiter plusieurs questions en lot
python -m agriculture_cameroun.agent --batch questions.txt
```

### 2. Personnalisation

**Profil agriculteur :**

```env
FARMER_PROFILE=small_scale  # small_scale, medium_scale, large_scale
DEFAULT_CROPS=maïs,manioc,plantain
EXPERIENCE_LEVEL=beginner   # beginner, intermediate, expert
```

**Préférences linguistiques :**

```env
DEFAULT_LANGUAGE=fr
ENABLE_LOCAL_DIALECTS=true
DIALECT_PREFERENCE=ewondo
```






## Support et communauté

- **Documentation :** [GitHub Repository](https://github.com/Nameless0l/agriculture-cameroun)
- **Issues :** Signalez les bugs sur GitHub Issues
- **Email :** wwwmbassiloic@gmail.com

---
