# 📦 Guide d'Installation - Agriculture Cameroun

Ce guide vous accompagne étape par étape pour installer et configurer le système multi-agents Agriculture Cameroun.

## 📋 Prérequis

### Système d'exploitation
- Windows 10/11, macOS 10.15+, ou Linux (Ubuntu 18.04+)
- 4 GB de RAM minimum (8 GB recommandé)
- 2 GB d'espace disque libre
- Connexion Internet pour les API

### Logiciels requis
- **Python 3.12+** : Langage de programmation principal
- **Poetry** : Gestionnaire de dépendances et d'environnements virtuels
- **Git** : Système de contrôle de version
- **VS Code** : Éditeur recommandé (optionnel mais conseillé)

## 🛠️ Installation des outils

### 1. Installation de Python

#### Windows
```powershell
# Option 1: Via Microsoft Store
# Rechercher "Python 3.12" dans le Microsoft Store

# Option 2: Via winget
winget install Python.Python.3.12

# Option 3: Téléchargement direct
# Aller sur https://python.org/downloads/ et télécharger Python 3.12+
```

#### macOS
```bash
# Option 1: Via Homebrew (recommandé)
brew install python@3.12

# Option 2: Via pyenv
brew install pyenv
pyenv install 3.12.0
pyenv global 3.12.0

# Option 3: Téléchargement direct depuis python.org
```

#### Linux (Ubuntu/Debian)
```bash
# Mettre à jour les packages
sudo apt update && sudo apt upgrade -y

# Installer Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip

# Vérifier l'installation
python3.12 --version
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# Pour Fedora
sudo dnf install python3.12 python3.12-devel python3.12-pip

# Pour CentOS/RHEL (avec EPEL)
sudo yum install epel-release
sudo yum install python312 python312-devel python312-pip
```

### 2. Installation de Poetry

#### Méthode universelle (recommandée)
```bash
# Installation via le script officiel
curl -sSL https://install.python-poetry.org | python3 -

# Ou sur Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### Méthode alternative avec pip
```bash
pip install poetry
```

#### Configuration de Poetry
```bash
# Configurer Poetry pour créer les environnements virtuels dans le projet
poetry config virtualenvs.in-project true

# Vérifier la configuration
poetry --version
poetry config --list
```

### 3. Installation de Git

#### Windows
```powershell
# Via winget
winget install Git.Git

# Ou télécharger depuis https://git-scm.com/download/win
```

#### macOS
```bash
# Via Homebrew
brew install git

# Git est aussi installé avec Xcode Command Line Tools
xcode-select --install
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL/Fedora
sudo yum install git  # ou dnf install git
```

### 4. Configuration de Git (optionnel mais recommandé)
```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
git config --global init.defaultBranch main
```

## 🚀 Installation du projet

### 1. Cloner le repository

#### Option A: HTTPS (recommandé pour les utilisateurs)
```bash
git clone https://github.com/Nameless0l/agriculture-cameroun.git
cd agriculture-cameroun
```

#### Option B: SSH (pour les contributeurs)
```bash
git clone git@github.com:Nameless0l/agriculture-cameroun.git
cd agriculture-cameroun
```

#### Option C: Téléchargement direct
1. Aller sur la page GitHub du projet
2. Cliquer sur "Code" → "Download ZIP"
3. Extraire l'archive
4. Ouvrir un terminal dans le dossier extrait

### 2. Installation des dépendances

```bash
# Installer toutes les dépendances (développement + production)
poetry install

# Ou installer uniquement les dépendances de production
poetry install --without dev

# Vérifier l'installation
poetry check
```

### 3. Activation de l'environnement virtuel

```bash
# Activer l'environnement Poetry
poetry shell

# Vérifier que l'environnement est actif
which python  # Doit pointer vers l'environnement Poetry
python --version  # Doit afficher Python 3.12+
```

## 🔐 Configuration des API

### 1. Créer le fichier de configuration

```bash
# Copier le template de configuration
cp .env.example .env

# Ou créer manuellement le fichier .env
touch .env
```

### 2. Obtenir une clé API Google Gemini

1. **Aller sur Google AI Studio**
   - Visiter: https://aistudio.google.com/
   - Se connecter avec un compte Google

2. **Créer une clé API**
   - Cliquer sur "Get API key"
   - Cliquer sur "Create API key"
   - Choisir un projet Google Cloud ou en créer un nouveau
   - Copier la clé générée

3. **Sécuriser la clé API**
   - Ne jamais partager la clé publiquement
   - Ne pas la commiter dans Git
   - La stocker uniquement dans le fichier `.env`

### 3. Configuration du fichier .env

Éditer le fichier `.env` et ajouter vos configurations :

```env
# ================================
# CONFIGURATION OBLIGATOIRE
# ================================

# Clé API Google Gemini (OBLIGATOIRE)
GEMINI_API_KEY=votre_cle_api_gemini_ici

# ================================
# CONFIGURATION RÉGIONALE
# ================================

# Région par défaut (optionnel)
DEFAULT_REGION=Centre

# Langue par défaut (optionnel)
DEFAULT_LANGUAGE=fr

# ================================
# CONFIGURATION DES MODÈLES
# ================================

# Modèle pour l'agent principal
ROOT_AGENT_MODEL=gemini-2.0-flash-001

# Modèles pour les agents spécialisés
WEATHER_AGENT_MODEL=gemini-2.0-flash-001
CROPS_AGENT_MODEL=gemini-2.0-flash-001
HEALTH_AGENT_MODEL=gemini-2.0-flash-001
ECONOMIC_AGENT_MODEL=gemini-2.0-flash-001
RESOURCES_AGENT_MODEL=gemini-2.0-flash-001

# ================================
# CONFIGURATION DÉVELOPPEMENT
# ================================

# Mode debug (true/false)
DEBUG=false

# Niveau de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Port pour le serveur web (optionnel)
PORT=8080

# ================================
# API EXTERNES (OPTIONNEL)
# ================================

# Clé API OpenWeather pour météo temps réel
OPENWEATHER_API_KEY=votre_cle_openweather

# Clé API pour données de marché
MARKET_API_KEY=votre_cle_marche
```

## ✅ Vérification de l'installation

### 1. Test de base

```bash
# Vérifier que toutes les dépendances sont installées
poetry run python -c "import agriculture_cameroun; print('✅ Import réussi')"

# Vérifier la configuration
poetry run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print('✅ Clé API Gemini configurée')
else:
    print('❌ Clé API Gemini manquante')
"
```

### 2. Test des agents

```bash
# Lancer les tests unitaires
poetry run pytest tests/ -v

# Test spécifique des agents
poetry run pytest tests/test_agents.py -v
```

### 3. Test d'intégration

```bash
# Lancer le système en mode test
poetry run python -m agriculture_cameroun.agent --test

# Ou tester avec une question simple
poetry run adk run . --input "Bonjour, pouvez-vous me présenter le système ?"
```

## 🌐 Premier lancement

### 1. Mode interface web (recommandé pour débuter)

```bash
# Lancer l'interface web
poetry run adk serve . --port 8080

# Ouvrir le navigateur sur: http://localhost:8080
```

### 2. Mode ligne de commande

```bash
# Lancer en mode interactif
poetry run adk run .

# Poser une question de test
# Exemple: "Quand planter le maïs dans la région Centre ?"
```

### 3. Mode API REST

```bash
# Lancer le serveur API
poetry run adk serve . --port 8080 --api-only

# Tester avec curl
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Comment traiter la pourriture brune du cacao ?", "session_id": "test123"}'
```

## 🐛 Résolution des problèmes courants

### Problème: Poetry n'est pas reconnu

```bash
# Ajouter Poetry au PATH
export PATH="$HOME/.local/bin:$PATH"

# Sur Windows, ajouter à la variable PATH système:
# %APPDATA%\Python\Scripts
```

### Problème: Python 3.12 introuvable

```bash
# Vérifier les versions installées
python --version
python3 --version
python3.12 --version

# Utiliser pyenv pour gérer les versions
pyenv versions
pyenv install 3.12.0
pyenv local 3.12.0
```

### Problème: Erreur lors de l'installation de dépendances

```bash
# Nettoyer le cache Poetry
poetry cache clear pypi --all

# Réinstaller les dépendances
poetry install --verbose

# En cas de problème de réseau, configurer un proxy
poetry config http-basic.pypi username password
```

### Problème: Clé API invalide

```bash
# Vérifier que la clé est bien dans .env
cat .env | grep GEMINI_API_KEY

# Tester la clé directement
poetry run python -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-001')
response = model.generate_content('Hello')
print('✅ API fonctionne:', response.text[:50])
"
```

### Problème: Erreurs d'importation

```bash
# Vérifier la structure du projet
ls -la agriculture_cameroun/

# Réinstaller en mode développement
poetry install --with dev

# Vérifier les chemins Python
poetry run python -c "import sys; print('\n'.join(sys.path))"
```

## 🔧 Configuration avancée

### 1. Configuration pour le développement

```bash
# Installer les outils de développement
poetry install --with dev

# Configurer pre-commit hooks
poetry run pre-commit install

# Configurer les outils de formatage
poetry run black --check agriculture_cameroun/
poetry run isort --check-only agriculture_cameroun/
poetry run flake8 agriculture_cameroun/
```

### 2. Configuration pour la production

```bash
# Installation optimisée pour la production
poetry install --without dev --no-root

# Configuration des variables d'environnement
export POETRY_VENV_IN_PROJECT=true
export POETRY_CACHE_DIR=/tmp/poetry_cache
```

### 3. Configuration Docker (optionnel)

```bash
# Construire l'image Docker
docker build -t agriculture-cameroun .

# Lancer le conteneur
docker run -p 8080:8080 --env-file .env agriculture-cameroun

# Ou utiliser docker-compose
docker-compose up -d
```

## 🎓 Prochaines étapes

Maintenant que l'installation est terminée :

1. **Lire la documentation utilisateur** : `docs/user-guide.md`
2. **Essayer les exemples** : `examples/`
3. **Explorer les fonctionnalités** via l'interface web
4. **Rejoindre la communauté** pour poser des questions
5. **Contribuer au projet** si vous le souhaitez

## 📞 Support

Si vous rencontrez des problèmes lors de l'installation :

1. **Vérifier les issues GitHub** : https://github.com/Nameless0l/agriculture-cameroun/issues
2. **Consulter la FAQ** : `docs/faq.md`
3. **Demander de l'aide** : Créer une nouvelle issue avec les détails de votre problème
4. **Contact direct** : team@agriculture-cm.com

---

**Installation réussie ? Parfait ! 🎉 Vous êtes maintenant prêt à utiliser le système Agriculture Cameroun !**
