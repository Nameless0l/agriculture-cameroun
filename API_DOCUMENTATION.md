# 🔌 API Documentation - Agriculture Cameroun

## Vue d'ensemble

L'API Agriculture Cameroun fournit un accès programmatique à tous les agents spécialisés du système. Cette documentation couvre les endpoints REST, les SDK, et les exemples d'intégration.

## Table des matières

1. [Authentification](#authentification)
2. [Endpoints principaux](#endpoints-principaux)
3. [Agents spécialisés](#agents-spécialisés)
4. [Modèles de données](#modèles-de-données)
5. [SDK et bibliothèques](#sdk-et-bibliothèques)
6. [Exemples d'utilisation](#exemples-dutilisation)
7. [Gestion des erreurs](#gestion-des-erreurs)
8. [Limites et quotas](#limites-et-quotas)

## Authentification

### Configuration des clés API

```bash
# Variables d'environnement requises
export AGRICULTURE_API_KEY="your_api_key"
export GOOGLE_API_KEY="your_google_ai_key"
export OPENWEATHER_API_KEY="your_openweather_key"
```

### Headers d'authentification

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
Accept: application/json
X-API-Version: v1
```

## Endpoints principaux

### Base URL

```
https://api.agriculture-cameroun.org/v1
```

### 1. Agent principal

#### POST /agent/ask

Consultation avec l'agent principal qui route vers les agents spécialisés.

**Request:**
```json
{
  "query": "Quand planter le maïs dans la région du Centre ?",
  "context": {
    "region": "Centre",
    "farmer_profile": "small_scale",
    "experience": "beginner",
    "preferred_language": "fr"
  },
  "options": {
    "include_explanations": true,
    "format": "detailed",
    "max_response_length": 1000
  }
}
```

**Response:**
```json
{
  "success": true,
  "timestamp": "2024-12-28T10:30:00Z",
  "response": {
    "answer": "Pour la région du Centre, la période optimale...",
    "confidence": 0.95,
    "sources": ["weather", "crops"],
    "agents_consulted": [
      {
        "agent": "weather",
        "contribution": "Analyse climatique et prévisions",
        "confidence": 0.92
      },
      {
        "agent": "crops",
        "contribution": "Calendrier de plantation pour maïs",
        "confidence": 0.98
      }
    ]
  },
  "metadata": {
    "processing_time": 2.3,
    "tokens_used": 150,
    "cache_hit": false
  }
}
```

### 2. Status et santé

#### GET /health

Vérification de l'état du système.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-28T10:30:00Z",
  "services": {
    "main_agent": "up",
    "weather_agent": "up",
    "crops_agent": "up",
    "health_agent": "up",
    "economic_agent": "up",
    "resources_agent": "up"
  },
  "external_apis": {
    "google_ai": "up",
    "openweather": "up"
  },
  "performance": {
    "avg_response_time": 1.8,
    "uptime": "99.9%",
    "requests_per_minute": 45
  }
}
```

## Agents spécialisés

### 1. Agent Météo

#### POST /agents/weather/forecast

**Request:**
```json
{
  "location": {
    "region": "Centre",
    "city": "Yaoundé",
    "coordinates": {
      "lat": 3.848,
      "lon": 11.502
    }
  },
  "timeframe": "7_days",
  "include": ["temperature", "rainfall", "humidity", "wind"]
}
```

**Response:**
```json
{
  "success": true,
  "forecast": {
    "current": {
      "temperature": 26.5,
      "humidity": 78,
      "rainfall": 0,
      "wind_speed": 12,
      "conditions": "Partly cloudy"
    },
    "daily": [
      {
        "date": "2024-12-28",
        "temp_min": 21,
        "temp_max": 29,
        "rainfall_mm": 15,
        "humidity": 82,
        "agricultural_advice": "Bon moment pour l'irrigation matinale"
      }
    ]
  },
  "alerts": [
    {
      "type": "heavy_rain",
      "severity": "moderate",
      "start_time": "2024-12-30T14:00:00Z",
      "message": "Fortes pluies attendues - protéger les cultures sensibles"
    }
  ]
}
```

#### POST /agents/weather/irrigation-advice

**Request:**
```json
{
  "crop": "tomato",
  "growth_stage": "flowering",
  "location": "Douala",
  "soil_type": "sandy_loam"
}
```

### 2. Agent Cultures

#### POST /agents/crops/recommend

**Request:**
```json
{
  "farmer_context": {
    "region": "Ouest",
    "farm_size": 2.5,
    "soil_type": "volcanic",
    "experience_level": "intermediate",
    "budget": "medium"
  },
  "preferences": {
    "market_focus": "local",
    "organic": true,
    "labor_intensity": "moderate"
  },
  "season": "dry_season"
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "crop": "irish_potato",
      "variety": "Cipira",
      "suitability_score": 0.91,
      "reasons": [
        "Adapté au climat de l'Ouest",
        "Résistant aux maladies",
        "Bon rendement économique"
      ],
      "planting_calendar": {
        "best_planting_period": "March-April",
        "harvest_period": "June-July",
        "growth_duration": 90
      },
      "requirements": {
        "water_needs": "moderate",
        "fertilizer": "NPK 20-10-10",
        "spacing": "30cm x 30cm"
      },
      "economics": {
        "estimated_yield": "15-20 tons/ha",
        "cost_per_hectare": 850000,
        "expected_revenue": 1500000,
        "profit_margin": 0.43
      }
    }
  ]
}
```

#### GET /agents/crops/varieties/{crop_name}

Obtenir les variétés disponibles pour une culture.

### 3. Agent Santé des plantes

#### POST /agents/health/diagnose

**Request:**
```json
{
  "crop": "cocoa",
  "symptoms": {
    "visual": [
      "yellow_leaves",
      "black_spots",
      "wilting"
    ],
    "affected_parts": ["leaves", "stems"],
    "progression": "rapid",
    "weather_conditions": "high_humidity"
  },
  "location": "Sud-Ouest",
  "photos": [
    "base64_encoded_image_1",
    "base64_encoded_image_2"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "diagnosis": {
    "primary_condition": {
      "name": "Black Pod Disease",
      "confidence": 0.87,
      "pathogen": "Phytophthora megakarya",
      "severity": "moderate"
    },
    "alternative_conditions": [
      {
        "name": "Witches Broom",
        "confidence": 0.23
      }
    ]
  },
  "treatment": {
    "immediate_actions": [
      "Remove affected pods immediately",
      "Improve drainage around trees",
      "Apply copper-based fungicide"
    ],
    "products": [
      {
        "name": "Copper oxychloride",
        "dosage": "3g/L water",
        "frequency": "Every 2 weeks",
        "safety_instructions": "Wear protective equipment"
      }
    ],
    "prevention": [
      "Regular pruning for air circulation",
      "Harvest ripe pods promptly",
      "Remove fallen leaves and pods"
    ]
  },
  "follow_up": {
    "monitoring_period": "2_weeks",
    "success_indicators": [
      "No new black spots appearing",
      "Existing spots not spreading"
    ]
  }
}
```

### 4. Agent Économique

#### POST /agents/economic/market-analysis

**Request:**
```json
{
  "crops": ["cocoa", "coffee", "palm_oil"],
  "region": "Centre",
  "analysis_type": "price_trends",
  "time_period": "6_months"
}
```

#### POST /agents/economic/profitability

**Request:**
```json
{
  "farm_plan": {
    "crops": [
      {
        "name": "maize",
        "area": 1.5,
        "variety": "local_yellow"
      }
    ],
    "location": "Nord",
    "farming_method": "conventional"
  },
  "costs": {
    "seeds": 50000,
    "fertilizer": 120000,
    "labor": 200000,
    "equipment": 80000
  }
}
```

### 5. Agent Ressources

#### GET /agents/resources/training

Obtenir les formations disponibles.

#### GET /agents/resources/subsidies

Obtenir les subventions et aides disponibles.

#### POST /agents/resources/expert-contact

Trouver un expert local.

## Modèles de données

### 1. Farmer Profile

```typescript
interface FarmerProfile {
  id: string;
  name: string;
  region: CameroonRegion;
  farm_size: number;
  experience_level: "beginner" | "intermediate" | "expert";
  farming_type: "subsistence" | "commercial" | "mixed";
  preferred_language: "fr" | "en" | string;
  crops_grown: string[];
  contact: {
    phone?: string;
    email?: string;
  };
}
```

### 2. Weather Data

```typescript
interface WeatherData {
  location: Location;
  timestamp: string;
  current: {
    temperature: number;
    humidity: number;
    rainfall: number;
    wind_speed: number;
    pressure: number;
    conditions: string;
  };
  forecast: DailyForecast[];
  alerts: WeatherAlert[];
}
```

### 3. Crop Information

```typescript
interface CropInfo {
  name: string;
  scientific_name: string;
  local_names: Record<string, string>;
  varieties: CropVariety[];
  growing_requirements: {
    climate: ClimateRequirements;
    soil: SoilRequirements;
    water: WaterRequirements;
  };
  calendar: PlantingCalendar;
  economics: EconomicData;
}
```

## SDK et bibliothèques

### Python SDK

```bash
pip install agriculture-cameroun-sdk
```

```python
from agriculture_cameroun import AgricultureAPI

# Initialisation
api = AgricultureAPI(api_key="your_key")

# Consultation simple
response = api.ask("Quand planter le maïs dans le Nord ?")
print(response.answer)

# Agent spécialisé
weather = api.weather()
forecast = weather.get_forecast(region="Centre", days=7)

# Diagnostic de maladie
health = api.health()
diagnosis = health.diagnose(
    crop="tomato",
    symptoms=["yellow_leaves", "black_spots"]
)
```

### JavaScript SDK

```bash
npm install agriculture-cameroun-js
```

```javascript
import { AgricultureAPI } from 'agriculture-cameroun-js';

const api = new AgricultureAPI({
  apiKey: 'your_key',
  baseUrl: 'https://api.agriculture-cameroun.org/v1'
});

// Async/await
const response = await api.ask({
  query: "Comment traiter la pourriture du cacao ?",
  context: { region: "Sud-Ouest" }
});

// Agents spécialisés
const economic = api.economic();
const analysis = await economic.getMarketAnalysis({
  crops: ["cocoa", "coffee"],
  region: "Centre"
});
```

### curl Examples

```bash
# Consultation générale
curl -X POST https://api.agriculture-cameroun.org/v1/agent/ask \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Meilleure période pour planter le manioc ?",
    "context": {"region": "Est"}
  }'

# Prévisions météo
curl -X POST https://api.agriculture-cameroun.org/v1/agents/weather/forecast \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"region": "Centre"},
    "timeframe": "7_days"
  }'
```

## Gestion des erreurs

### Codes d'erreur standard

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Paramètres invalides |
| 401 | Unauthorized | Clé API manquante/invalide |
| 403 | Forbidden | Quota dépassé |
| 404 | Not Found | Endpoint non trouvé |
| 429 | Too Many Requests | Limite de taux dépassée |
| 500 | Internal Server Error | Erreur serveur |
| 503 | Service Unavailable | Service temporairement indisponible |

### Format des réponses d'erreur

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REGION",
    "message": "La région spécifiée n'est pas supportée",
    "details": {
      "provided_region": "Invalid",
      "supported_regions": ["Centre", "Littoral", "Ouest", ...]
    }
  },
  "timestamp": "2024-12-28T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Gestion des erreurs dans le SDK

```python
from agriculture_cameroun import AgricultureAPI, APIError

api = AgricultureAPI(api_key="your_key")

try:
    response = api.ask("Question invalid")
except APIError as e:
    if e.code == "QUOTA_EXCEEDED":
        print("Quota API dépassé")
    elif e.code == "INVALID_REGION":
        print(f"Région invalide: {e.details['provided_region']}")
    else:
        print(f"Erreur API: {e.message}")
```

## Limites et quotas

### Quotas par défaut

| Plan | Requêtes/jour | Requêtes/minute | Agents simultanés |
|------|---------------|-----------------|-------------------|
| Gratuit | 1,000 | 10 | 1 |
| Basic | 10,000 | 100 | 3 |
| Pro | 100,000 | 1,000 | 10 |
| Enterprise | Illimité | 10,000 | 50 |

### Headers de quota

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1640700000
X-Quota-Used: 150
X-Quota-Limit: 1000
```

### Optimisation des performances

```python
# Utiliser le cache
response = api.ask(query, use_cache=True)

# Requêtes en lot
responses = api.batch_ask([
    "Question 1",
    "Question 2",
    "Question 3"
])

# Compression
api.config.enable_compression = True
```

## Webhooks et notifications

### Configuration des webhooks

```json
{
  "url": "https://your-app.com/webhooks/agriculture",
  "events": [
    "weather.alert",
    "disease.detected",
    "market.price_change"
  ],
  "secret": "your_webhook_secret"
}
```

### Exemples d'événements

```json
{
  "event": "weather.alert",
  "timestamp": "2024-12-28T10:30:00Z",
  "data": {
    "alert_type": "heavy_rain",
    "region": "Centre",
    "severity": "high",
    "message": "Fortes pluies attendues dans les prochaines 6 heures"
  }
}
```

---

**Cette documentation API est maintenue à jour automatiquement. Consultez la version en ligne pour les dernières modifications.**

*Généré automatiquement à partir du code source le $(date)*
