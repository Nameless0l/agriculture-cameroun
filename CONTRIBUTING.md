# 🤝 Guide de Contribution - Agriculture Cameroun

Merci de votre intérêt pour contribuer au projet Agriculture Cameroun ! Ce guide vous explique comment participer efficacement au développement.

## 🎯 Types de Contributions

### 🐛 Signaler des bugs
- Utiliser les [GitHub Issues](https://github.com/Nameless0l/agriculture-cameroun/issues)
- Fournir une description détaillée
- Inclure les étapes de reproduction
- Préciser l'environnement (OS, Python, etc.)

### 💡 Proposer des fonctionnalités
- Ouvrir une [Discussion GitHub](https://github.com/Nameless0l/agriculture-cameroun/discussions)
- Expliquer le cas d'usage
- Proposer une solution technique
- Évaluer l'impact sur les utilisateurs

### 📝 Améliorer la documentation
- Corriger les fautes de frappe
- Ajouter des exemples
- Traduire en langues locales
- Créer des tutoriels

### 🌱 Ajouter des données agricoles
- Nouvelles cultures
- Régions supplémentaires
- Maladies et traitements
- Prix de marché locaux

### 🔧 Développer du code
- Corriger des bugs
- Implémenter de nouvelles fonctionnalités
- Optimiser les performances
- Améliorer les tests

## 🛠️ Configuration Développeur

### 1. Fork et Clone

```bash
# Fork le projet sur GitHub, puis :
git clone https://github.com/votre-username/agriculture-cameroun.git
cd agriculture-cameroun

# Ajouter le repository original comme remote
git remote add upstream https://github.com/Nameless0l/agriculture-cameroun.git
```

### 2. Installation Développeur

```bash
# Installer avec les dépendances de développement
poetry install --with dev

# Activer l'environnement
poetry shell

# Installer les pre-commit hooks
pre-commit install
```

### 3. Configuration IDE

#### VS Code (recommandé)
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### Extensions recommandées
- Python
- Pylance
- Black Formatter
- isort
- GitLens
- French Language Pack

### 4. Vérification de l'environnement

```bash
# Tester l'installation
poetry run pytest tests/test_setup.py -v

# Vérifier le formatage
poetry run black --check agriculture_cameroun/
poetry run isort --check-only agriculture_cameroun/
poetry run flake8 agriculture_cameroun/

# Vérifier les types
poetry run mypy agriculture_cameroun/
```

## 📝 Standards de Code

### Style Python
- **PEP 8** : Standard de style Python
- **Black** : Formatage automatique
- **isort** : Tri des imports
- **Type hints** : Obligatoires pour les nouvelles fonctions

### Conventions de nommage
```python
# Modules et packages
agriculture_cameroun/sub_agents/weather/

# Classes (PascalCase)
class WeatherAgent:

# Fonctions et variables (snake_case)
def get_weather_forecast():
    crop_name = "cacao"

# Constantes (UPPER_CASE)
REGIONS = {"Centre": {...}}

# Fichiers (snake_case)
weather_tools.py
```

### Documentation
```python
def diagnose_plant_disease(
    crop: str,
    symptoms: List[str],
    tool_context: ToolContext,
    affected_parts: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Diagnostique une maladie des plantes basée sur les symptômes.
    
    Cette fonction analyse les symptômes observés sur une culture
    et propose un diagnostic avec des recommandations de traitement.
    
    Args:
        crop: Type de culture affectée (ex: "cacao", "maïs")
        symptoms: Liste des symptômes observés
        tool_context: Contexte de l'outil ADK
        affected_parts: Parties de la plante affectées (optionnel)
        
    Returns:
        Dictionnaire contenant:
        - diagnostic_results: Liste des diagnostics possibles
        - most_likely_diagnosis: Diagnostic le plus probable
        - confidence_level: Niveau de confiance (0-100)
        
    Example:
        >>> result = diagnose_plant_disease(
        ...     crop="cacao",
        ...     symptoms=["taches brunes", "pourriture"],
        ...     tool_context=context
        ... )
        >>> print(result["most_likely_diagnosis"]["disease"])
        "Pourriture brune"
    """
```

### Tests
```python
import pytest
from agriculture_cameroun.sub_agents.health.tools import diagnose_plant_disease

def test_diagnose_cacao_brown_rot():
    """Test du diagnostic de pourriture brune du cacao."""
    # Arrange
    crop = "cacao"
    symptoms = ["taches brunes", "pourriture fruits"]
    
    # Act
    result = diagnose_plant_disease(
        crop=crop,
        symptoms=symptoms,
        tool_context=mock_tool_context()
    )
    
    # Assert
    assert result["crop"] == crop
    assert "pourriture brune" in result["most_likely_diagnosis"]["disease"].lower()
    assert result["confidence_level"] > 70
```

## 🔄 Workflow de Contribution

### 1. Créer une branche

```bash
# Mettre à jour main
git checkout main
git pull upstream main

# Créer une branche feature
git checkout -b feature/nouvelle-fonctionnalite

# Ou pour un bugfix
git checkout -b fix/correction-bug-xyz
```

### 2. Développer

```bash
# Faire vos modifications
# Tester régulièrement
poetry run pytest tests/ -v

# Committer par petites étapes
git add agriculture_cameroun/sub_agents/health/tools.py
git commit -m "feat(health): ajouter diagnostic mosaïque manioc"
```

### 3. Tests et qualité

```bash
# Tests complets
poetry run pytest tests/ -v --cov=agriculture_cameroun

# Formatage
poetry run black agriculture_cameroun/
poetry run isort agriculture_cameroun/

# Linting
poetry run flake8 agriculture_cameroun/
poetry run mypy agriculture_cameroun/

# Pre-commit (automatique)
git commit -m "feat: nouvelle fonctionnalité"
```

### 4. Pull Request

```bash
# Pousser la branche
git push origin feature/nouvelle-fonctionnalite

# Créer une PR sur GitHub avec :
# - Titre descriptif
# - Description détaillée
# - Captures d'écran si UI
# - Liens vers les issues
```

## 📋 Template de Pull Request

```markdown
## 🎯 Description

Brève description de ce que fait cette PR.

## 🔗 Issues Liées

Fixes #123
Closes #456

## 🧪 Types de Changements

- [ ] Bug fix (changement non-breaking qui corrige un problème)
- [ ] New feature (changement non-breaking qui ajoute une fonctionnalité)
- [ ] Breaking change (fix ou feature qui casserait la fonctionnalité existante)
- [ ] Documentation (changement dans la documentation uniquement)

## ✅ Checklist

- [ ] Mon code suit les standards du projet
- [ ] J'ai effectué une auto-revue de mon code
- [ ] J'ai commenté mon code, particulièrement les parties complexes
- [ ] J'ai ajouté des tests qui prouvent que mon fix/feature fonctionne
- [ ] Les tests nouveaux et existants passent
- [ ] J'ai mis à jour la documentation si nécessaire

## 🧪 Tests

Décrivez les tests effectués :

```bash
poetry run pytest tests/test_nouvelle_fonctionnalite.py -v
```

## 📸 Captures d'écran

Si applicable, ajoutez des captures d'écran.

## 📝 Notes Supplémentaires

Tout autre contexte ou information utile.
```

## 🌍 Contribution Données Locales

### Ajouter une nouvelle région

1. **Modifier `agriculture_cameroun/config.py`**
```python
class RegionType(str, Enum):
    # ... existing regions ...
    NOUVELLE_REGION = "Nouvelle-Region"
```

2. **Mettre à jour `agriculture_cameroun/utils/data.py`**
```python
REGIONS = {
    # ... existing regions ...
    "Nouvelle-Region": {
        "climate": "tropical_humide",
        "soil_types": ["argilo-sableux", "latéritique"],
        "main_crops": ["manioc", "plantain", "cacao"],
        "rainfall_mm": 1500,
        "temperature_range": {"min": 22, "max": 30},
        "dry_season": {"start": "décembre", "end": "février"},
        "wet_season": {"start": "mars", "end": "novembre"}
    }
}
```

3. **Ajouter des tests**
```python
def test_nouvelle_region_data():
    """Test des données de la nouvelle région."""
    region_data = REGIONS["Nouvelle-Region"]
    assert "climate" in region_data
    assert len(region_data["main_crops"]) > 0
```

### Ajouter une nouvelle culture

1. **Configuration**
```python
class CropType(str, Enum):
    NOUVELLE_CULTURE = "nouvelle-culture"
```

2. **Données de base**
```python
CROPS = {
    "nouvelle-culture": {
        "name_fr": "Nouvelle Culture",
        "name_en": "New Crop",
        "family": "Famille Botanique",
        "planting_months": ["mars", "avril", "mai"],
        "harvest_months": ["octobre", "novembre"],
        "growth_period_days": 120,
        "water_needs": "modérées",
        "soil_ph": {"min": 6.0, "max": 7.5},
        "temperature_range": {"min": 20, "max": 35}
    }
}
```

3. **Maladies communes**
```python
# Dans sub_agents/health/tools.py
disease_database = {
    "nouvelle-culture": [
        {
            "name": "Maladie Commune",
            "agent": "Agent Pathogène",
            "symptoms": ["symptôme 1", "symptôme 2"],
            "affected_parts": ["feuilles", "fruits"],
            "conditions": ["humidité élevée"],
            "severity": "modérée",
            "treatments": ["traitement 1", "traitement 2"]
        }
    ]
}
```

4. **Prix de marché**
```python
MARKET_PRICES = {
    CropType.NOUVELLE_CULTURE: {
        "min": 200,
        "max": 800,
        "average": 500,
        "currency": "FCFA",
        "unit": "kg"
    }
}
```

## 🔍 Review Process

### Critères d'acceptance
1. **Fonctionnalité** : La fonctionnalité fonctionne comme attendu
2. **Tests** : Couverture de test suffisante (>80%)
3. **Documentation** : Code documenté et README mis à jour
4. **Performance** : Pas de régression de performance
5. **Sécurité** : Pas de vulnérabilité introduite

### Process de review
1. **Auto-review** : Revue par l'auteur
2. **Peer review** : Revue par un autre développeur
3. **Tests automatiques** : CI/CD doit passer
4. **Review maintainer** : Validation finale

## 🏆 Reconnaissance

### Hall of Fame
Les contributeurs majeurs sont reconnus dans :
- README.md
- Site web du projet
- Releases notes
- Conférences et présentations

### Types de contributions reconnues
- **Code** : Nouvelles fonctionnalités, corrections de bugs
- **Documentation** : Guides, tutoriels, traductions
- **Données** : Informations agricoles locales
- **Tests** : Amélioration de la couverture de test
- **Design** : Interface utilisateur, expérience utilisateur
- **Community** : Support utilisateurs, organisation d'événements

## 📞 Support Développeur

### Channels de communication
- **GitHub Discussions** : Questions générales
- **GitHub Issues** : Bugs et fonctionnalités
- **Discord** : Chat en temps réel
- **Email** : dev@agriculture-cm.com

### Ressources utiles
- [Documentation ADK](https://docs.anthropic.com/claude/docs/agent-computer-use)
- [Guide Google Gemini](https://ai.google.dev/docs)
- [Bonnes pratiques Python](https://realpython.com/python-pep8/)
- [Agriculture au Cameroun](https://www.minader.cm/)

## 📅 Calendrier des Releases

- **Releases mineures** : Chaque mois
- **Releases majeures** : Chaque trimestre
- **Hotfixes** : Selon les besoins

### Processus de release
1. Feature freeze
2. Tests complets
3. Documentation update
4. Release candidate
5. Release finale

---

**Merci de contribuer à l'amélioration de l'agriculture camerounaise ! 🌱**
