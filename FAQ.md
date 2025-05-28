# ❓ Foire Aux Questions (FAQ) - Agriculture Cameroun

## Questions générales

### 🤖 Qu'est-ce qu'Agriculture Cameroun ?

**Agriculture Cameroun** est un système d'intelligence artificielle multi-agents conçu spécifiquement pour les agriculteurs camerounais. Il combine cinq agents spécialisés (météo, cultures, santé des plantes, économie, ressources) pour fournir des conseils agricoles personnalisés et contextualés.

### 🆓 Le système est-il gratuit ?

Oui, Agriculture Cameroun est un projet open source gratuit. Cependant, certaines fonctionnalités nécessitent des clés API tierces (Google AI, OpenWeather) qui peuvent avoir leurs propres conditions tarifaires.

### 🌍 Dans quelles régions du Cameroun fonctionne-t-il ?

Le système couvre toutes les 10 régions du Cameroun :
- Centre, Littoral, Ouest, Nord-Ouest, Sud-Ouest
- Est, Sud, Adamaoua, Nord, Extrême-Nord

Les conseils sont adaptés aux spécificités climatiques et agricoles de chaque région.

### 🗣️ Quelles langues sont supportées ?

- **Français** (principal)
- **Anglais** (support complet)
- **Langues locales** (support partiel) : Ewondo, Duala, Bamiléké, Fulfulde

## Installation et configuration

### 💻 Quels sont les prérequis système ?

**Configuration minimale :**
- Python 3.8+
- 4 GB RAM
- 1 GB espace disque
- Connexion internet (pour les API)

**Configuration recommandée :**
- Python 3.10+
- 8 GB RAM
- 2 GB espace disque
- Connexion internet stable

### 🔑 Comment obtenir les clés API nécessaires ?

**Google AI (Gemini) :**
1. Visitez [Google AI Studio](https://makersuite.google.com/)
2. Créez un compte ou connectez-vous
3. Générez une nouvelle clé API
4. Ajoutez la clé dans votre fichier `.env`

**OpenWeather :**
1. Créez un compte sur [OpenWeatherMap](https://openweathermap.org/api)
2. Souscrivez au plan gratuit (1000 appels/jour)
3. Récupérez votre clé API
4. Ajoutez la clé dans votre fichier `.env`

### ⚠️ L'installation échoue avec une erreur Poetry

**Problèmes courants :**

```bash
# Erreur : Poetry command not found
# Solution : Ajouter Poetry au PATH
export PATH="$HOME/.local/bin:$PATH"

# Erreur : Python version incompatible
# Solution : Installer Python 3.8+
pyenv install 3.10.12
pyenv local 3.10.12

# Erreur : Dépendances conflictuelles
# Solution : Nettoyer et réinstaller
poetry env remove python
poetry install
```

### 🐳 Puis-je utiliser Docker ?

Oui ! Un Dockerfile sera bientôt disponible. En attendant :

```bash
# Construction manuelle
docker build -t agriculture-cameroun .
docker run -p 8000:8000 agriculture-cameroun
```

## Utilisation

### 📝 Comment poser une bonne question ?

**Structure recommandée :**
```
[Contexte] + [Question spécifique] + [Localisation]

Exemples :
✅ "Je cultive du maïs dans la région du Centre, quand dois-je planter pour la saison des pluies ?"
✅ "Mes plants de tomates à Douala ont des feuilles jaunes avec des taches noires, que faire ?"
❌ "Aidez-moi avec mes plantes"
❌ "Comment faire de l'agriculture ?"
```

**Informations utiles à inclure :**
- Type de culture
- Région/ville
- Saison en cours
- Problème observé (avec détails)
- Superficie cultivée
- Expérience agricole

### 🎯 Quel agent utiliser pour ma question ?

| Type de question | Agent recommandé | Exemples |
|------------------|------------------|----------|
| Météo, irrigation, saisons | 🌤️ Weather | "Quand va pleuvoir ?", "Risque de sécheresse ?" |
| Variétés, plantation, techniques | 🌱 Crops | "Quelle variété choisir ?", "Comment planter ?" |
| Maladies, parasites, traitement | 🏥 Health | "Feuilles malades", "Insectes nuisibles" |
| Prix, rentabilité, vente | 💰 Economic | "Prix du marché", "Calculer profit" |
| Formation, aide, contacts | 📚 Resources | "Où apprendre ?", "Subventions disponibles ?" |

### 🔄 L'agent donne des réponses incorrectes

**Solutions :**

1. **Soyez plus précis :**
   - Ajoutez le contexte géographique
   - Spécifiez la culture et la variété
   - Décrivez précisément le problème

2. **Utilisez l'agent spécialisé :**
   ```bash
   # Au lieu de l'agent général
   python -m agriculture_cameroun.sub_agents.health.agent --query "votre question"
   ```

3. **Vérifiez vos données :**
   - Informations à jour ?
   - Localisation correcte ?
   - Saison appropriée ?

4. **Signalez le problème :**
   ```bash
   python -m agriculture_cameroun.feedback --incorrect "description de l'erreur"
   ```

### 📱 Existe-t-il une application mobile ?

Pas encore, mais c'est dans la roadmap ! En attendant :
- Interface web responsive
- API REST pour développeurs
- Intégration WhatsApp prévue

## Fonctionnalités avancées

### 🔒 Mode hors ligne disponible ?

**Oui, partiellement :**
- Base de données locale des cultures
- Calendriers agricoles pré-calculés
- Conseils généraux stockés localement

**Limitations hors ligne :**
- Pas de prévisions météo en temps réel
- Pas d'analyse IA contextuelle
- Données de prix non actualisées

**Activation :**
```bash
python -m agriculture_cameroun.sync --download-offline
python -m agriculture_cameroun.agent --offline
```

### 📊 Export des données et rapports

**Formats supportés :**
- PDF (conseils personnalisés)
- Excel (analyses économiques)
- JSON (données brutes)
- CSV (export données)

**Commandes :**
```bash
# Rapport mensuel
python -m agriculture_cameroun.export --monthly-report --format pdf

# Analyse économique
python -m agriculture_cameroun.export --economic-analysis --crop maïs --format xlsx
```

### 🔔 Notifications et alertes

**Types d'alertes :**
- Alertes météorologiques urgentes
- Détection précoce de maladies
- Opportunités de marché
- Rappels de tâches agricoles

**Configuration :**
```env
ENABLE_ALERTS=true
SMS_PROVIDER=twilio
EMAIL_NOTIFICATIONS=true
ALERT_FREQUENCY=daily
```

### 🤝 Intégration avec d'autres systèmes

**APIs disponibles :**
- REST API complète
- Webhooks pour notifications
- SDK Python pour développeurs

**Exemples d'intégration :**
```python
from agriculture_cameroun import AgricultureAgent

agent = AgricultureAgent()
response = agent.ask("Conseil pour plantation maïs")
print(response.advice)
```

## Dépannage

### 🐛 Problèmes de performance

**Système lent :**
- Activez le cache : `ENABLE_CACHING=true`
- Réduisez la complexité des requêtes
- Utilisez des agents spécialisés

**Consommation mémoire élevée :**
- Limitez la taille du cache : `CACHE_SIZE_LIMIT=50MB`
- Fermez les sessions inutilisées
- Redémarrez le système régulièrement

### 🌐 Problèmes de connectivité

**Erreurs d'API :**
```bash
# Test de connectivité
python -m agriculture_cameroun.tools --test-connectivity

# Diagnostic des APIs
python -m agriculture_cameroun.tools --diagnose-apis
```

**Solutions :**
- Vérifiez les clés API
- Contrôlez les quotas
- Configurez les proxies si nécessaire

### 📝 Logs et débogage

**Activer les logs détaillés :**
```bash
export LOG_LEVEL=DEBUG
export LOG_FILE=agriculture.log
python -m agriculture_cameroun.agent --debug
```

**Localisation des logs :**
- Linux : `~/.cache/agriculture_cameroun/logs/`
- Windows : `%APPDATA%\agriculture_cameroun\logs\`
- macOS : `~/Library/Caches/agriculture_cameroun/logs/`

## Contribution et développement

### 👨‍💻 Comment contribuer au projet ?

1. **Fork le repository**
2. **Créez une branche feature**
3. **Implémentez votre amélioration**
4. **Testez exhaustivement**
5. **Soumettez une pull request**

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails.

### 🧪 Comment ajouter de nouvelles cultures ?

```python
# Dans agriculture_cameroun/data/crops.py
CAMEROON_CROPS["nouvelle_culture"] = {
    "name": "Nouvelle Culture",
    "varieties": ["variété1", "variété2"],
    "planting_seasons": ["mars-mai", "septembre-novembre"],
    "regions": ["Centre", "Ouest"],
    "growth_duration": 90,  # jours
    "soil_requirements": "Well-drained, fertile",
    "water_needs": "moderate"
}
```

### 🌍 Ajouter support d'une nouvelle langue

1. **Créez les fichiers de traduction :**
```bash
mkdir agriculture_cameroun/i18n/nouvelle_langue/
touch agriculture_cameroun/i18n/nouvelle_langue/messages.po
```

2. **Implémentez les traductions**
3. **Testez avec différents scénarios**
4. **Soumettez la contribution**

## Support et communauté

### 📞 Comment obtenir de l'aide ?

**Ordre de priorité :**
1. **Cette FAQ** - Solutions aux problèmes courants
2. **Documentation** - Guides détaillés
3. **GitHub Issues** - Signalement de bugs
4. **Discussions** - Questions communautaires
5. **Email support** - Cas complexes

### 🏆 Roadmap du projet

**Version 2.0 (Q2 2025) :**
- Application mobile (Android/iOS)
- Support vocal en langues locales
- IA vision pour diagnostic par photo
- Marketplace intégré

**Version 3.0 (Q4 2025) :**
- IoT sensors integration
- Blockchain pour traçabilité
- Machine learning prédictif
- Réalité augmentée

### 🎯 Comment signaler un bug ?

**Template de bug report :**
```markdown
**Description :** Description claire du bug
**Reproduction :** Étapes pour reproduire
**Environnement :** OS, Python version, etc.
**Logs :** Logs d'erreur pertinents
**Comportement attendu :** Ce qui devrait se passer
```

### 💡 Comment suggérer une fonctionnalité ?

**Template de feature request :**
```markdown
**Problème :** Quel problème cela résoudrait-il ?
**Solution :** Description de la fonctionnalité souhaitée
**Alternatives :** Autres solutions considérées
**Impact :** Qui bénéficierait de cette fonctionnalité ?
```

---

**Cette FAQ est maintenue par la communauté. N'hésitez pas à proposer des améliorations !**

*Dernière mise à jour : $(date)*
