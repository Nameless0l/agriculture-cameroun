# Copyright 2025 Agriculture Cameroun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""Tests pour les agents du système multi-agents agriculture."""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Configuration pour les tests
os.environ["GEMINI_API_KEY"] = "test-api-key"

from agriculture_cameroun.agent import root_agent
from agriculture_cameroun.sub_agents.weather.agent import weather_agent
from agriculture_cameroun.sub_agents.crops.agent import crops_agent
from agriculture_cameroun.sub_agents.health.agent import health_agent
from agriculture_cameroun.sub_agents.economic.agent import economic_agent
from agriculture_cameroun.sub_agents.resources.agent import resources_agent
from agriculture_cameroun.config import AgricultureConfig, CropType, RegionType
from agriculture_cameroun.utils.data import get_crop_info, get_region_info


class TestAgentConfiguration:
    """Tests de configuration des agents."""
    
    def test_root_agent_initialization(self):
        """Test l'initialisation de l'agent principal."""
        assert root_agent.name == "agriculture_multiagent"
        assert root_agent.model is not None
        assert len(root_agent.sub_agents) == 5
        assert len(root_agent.tools) >= 6
    
    def test_sub_agents_initialization(self):
        """Test l'initialisation des sous-agents."""
        agents = [
            (weather_agent, "weather_agent"),
            (crops_agent, "crops_agent"),
            (health_agent, "health_agent"),
            (economic_agent, "economic_agent"),
            (resources_agent, "resources_agent")
        ]
        
        for agent, expected_name in agents:
            assert agent.name == expected_name
            assert agent.model is not None
            assert len(agent.tools) > 0
    
    def test_configuration_loading(self):
        """Test le chargement de la configuration."""
        config = AgricultureConfig()
        assert config.default_region == RegionType.CENTRE
        assert config.default_language == "fr"
        assert config.currency == "FCFA"


class TestWeatherAgent:
    """Tests pour l'agent météorologique."""
    
    @pytest.fixture
    def mock_weather_context(self):
        """Mock du contexte pour les outils météo."""
        context = Mock()
        context.state = {"agriculture_settings": {"default_region": "Centre"}}
        return context
    
    @patch('agriculture.sub_agents.weather.tools.model.generate_content')
    def test_weather_forecast_tool(self, mock_generate, mock_weather_context):
        """Test l'outil de prévisions météo."""
        from agriculture_cameroun.sub_agents.weather.tools import get_weather_forecast
        
        # Mock de la réponse Gemini
        mock_response = Mock()
        mock_response.text = "Prévisions météo favorables pour l'agriculture"
        mock_generate.return_value = mock_response
        
        result = get_weather_forecast(
            region="Centre",
            days=7,
            tool_context=mock_weather_context
        )
        
        assert "region" in result
        assert "forecast" in result
        assert "summary" in result
        assert result["region"] == "Centre"
        assert len(result["forecast"]) == 7
    
    @patch('agriculture.sub_agents.weather.tools.model.generate_content')
    def test_irrigation_advice_tool(self, mock_generate, mock_weather_context):
        """Test l'outil de conseils d'irrigation."""
        from agriculture_cameroun.sub_agents.weather.tools import get_irrigation_advice
        
        mock_response = Mock()
        mock_response.text = "Irrigation recommandée le matin"
        mock_generate.return_value = mock_response
        
        result = get_irrigation_advice(
            crop="maïs",
            soil_type="argileux",
            current_conditions={"humidity": 70, "temperature": 28},
            tool_context=mock_weather_context
        )
        
        assert isinstance(result, str)
        assert "irrigation" in result.lower()


class TestCropsAgent:
    """Tests pour l'agent de gestion des cultures."""
    
    @pytest.fixture
    def mock_crops_context(self):
        """Mock du contexte pour les outils cultures."""
        context = Mock()
        context.state = {"agriculture_settings": {"default_region": "Centre"}}
        return context
    
    @patch('agriculture.sub_agents.crops.tools.model.generate_content')
    def test_planting_calendar_tool(self, mock_generate, mock_crops_context):
        """Test l'outil de calendrier de plantation."""
        from agriculture_cameroun.sub_agents.crops.tools import get_planting_calendar
        
        mock_response = Mock()
        mock_response.text = '{"plantation": "mars-avril", "récolte": "juillet"}'
        mock_generate.return_value = mock_response
        
        result = get_planting_calendar(
            crop="maïs",
            region="Centre",
            tool_context=mock_crops_context
        )
        
        assert "crop" in result
        assert "region" in result
        assert "calendar" in result
        assert result["crop"] == "maïs"
        assert result["region"] == "Centre"
    
    @patch('agriculture.sub_agents.crops.tools.model.generate_content')
    def test_variety_recommendations_tool(self, mock_generate, mock_crops_context):
        """Test l'outil de recommandations de variétés."""
        from agriculture_cameroun.sub_agents.crops.tools import get_variety_recommendations
        
        mock_response = Mock()
        mock_response.text = "Variétés recommandées: ATP Y2000, CMS 8704"
        mock_generate.return_value = mock_response
        
        result = get_variety_recommendations(
            crop="maïs",
            region="Centre",
            priorities=["rendement", "résistance"],
            tool_context=mock_crops_context
        )
        
        assert "crop" in result
        assert "recommendations" in result
        assert result["priorities"] == "rendement, résistance"


class TestHealthAgent:
    """Tests pour l'agent de santé des plantes."""
    
    @pytest.fixture
    def mock_health_context(self):
        """Mock du contexte pour les outils santé."""
        context = Mock()
        return context
    
    @patch('agriculture.sub_agents.health.tools.model.generate_content')
    def test_disease_diagnosis_tool(self, mock_generate, mock_health_context):
        """Test l'outil de diagnostic des maladies."""
        from agriculture_cameroun.sub_agents.health.tools import diagnose_plant_disease
        
        mock_response = Mock()
        mock_response.text = "Diagnostic: Pourriture brune probable"
        mock_generate.return_value = mock_response
        
        result = diagnose_plant_disease(
            crop="cacao",
            symptoms=["taches brunes", "pourriture fruits"],
            affected_parts=["fruits"],
            tool_context=mock_health_context
        )
        
        assert "crop" in result
        assert "symptoms" in result
        assert "diagnostic_results" in result
        assert len(result["diagnostic_results"]) > 0
    
    @patch('agriculture.sub_agents.health.tools.model.generate_content')
    def test_treatment_recommendations_tool(self, mock_generate, mock_health_context):
        """Test l'outil de recommandations de traitement."""
        from agriculture_cameroun.sub_agents.health.tools import get_treatment_recommendations
        
        mock_response = Mock()
        mock_response.text = "Traitement: Application de fongicide cuprique"
        mock_generate.return_value = mock_response
        
        result = get_treatment_recommendations(
            diagnosis="Pourriture brune",
            crop="cacao",
            severity="élevée",
            tool_context=mock_health_context
        )
        
        assert "diagnosis" in result
        assert "treatment_plan" in result
        assert "estimated_cost" in result
        assert result["severity"] == "élevée"


class TestEconomicAgent:
    """Tests pour l'agent économique."""
    
    @pytest.fixture
    def mock_economic_context(self):
        """Mock du contexte pour les outils économiques."""
        context = Mock()
        return context
    
    @patch('agriculture.sub_agents.economic.tools.model.generate_content')
    def test_market_prices_tool(self, mock_generate, mock_economic_context):
        """Test l'outil de prix du marché."""
        from agriculture_cameroun.sub_agents.economic.tools import get_market_prices
        
        mock_response = Mock()
        mock_response.text = "Analyse des prix du marché"
        mock_generate.return_value = mock_response
        
        result = get_market_prices(
            crop="cacao",
            region="Centre",
            market_type="gros",
            tool_context=mock_economic_context
        )
        
        assert "crop" in result
        assert "current_price" in result
        assert "price_range" in result
        assert "analysis" in result
        assert result["crop"] == "cacao"
    
    @patch('agriculture.sub_agents.economic.tools.model.generate_content')
    def test_profitability_analysis_tool(self, mock_generate, mock_economic_context):
        """Test l'outil d'analyse de rentabilité."""
        from agriculture_cameroun.sub_agents.economic.tools import analyze_profitability
        
        mock_response = Mock()
        mock_response.text = "Analyse de rentabilité détaillée"
        mock_generate.return_value = mock_response
        
        result = analyze_profitability(
            crop="maïs",
            area_hectares=2.0,
            production_system="amélioré",
            tool_context=mock_economic_context
        )
        
        assert "crop" in result
        assert "area_hectares" in result
        assert "costs" in result
        assert "revenue" in result
        assert "profitability" in result
        assert result["area_hectares"] == 2.0


class TestResourcesAgent:
    """Tests pour l'agent de gestion des ressources."""
    
    @pytest.fixture
    def mock_resources_context(self):
        """Mock du contexte pour les outils ressources."""
        context = Mock()
        return context
    
    @patch('agriculture.sub_agents.resources.tools.model.generate_content')
    def test_soil_analysis_tool(self, mock_generate, mock_resources_context):
        """Test l'outil d'analyse du sol."""
        from agriculture_cameroun.sub_agents.resources.tools import analyze_soil_requirements
        
        mock_response = Mock()
        mock_response.text = "Analyse des exigences du sol"
        mock_generate.return_value = mock_response
        
        result = analyze_soil_requirements(
            crop="cacao",
            region="Centre",
            soil_type="argileux",
            current_ph=5.2,
            tool_context=mock_resources_context
        )
        
        assert "crop" in result
        assert "region" in result
        assert "requirements" in result
        assert "current_conditions" in result
        assert "improvement_plan" in result
    
    @patch('agriculture.sub_agents.resources.tools.model.generate_content')
    def test_fertilizer_recommendations_tool(self, mock_generate, mock_resources_context):
        """Test l'outil de recommandations d'engrais."""
        from agriculture_cameroun.sub_agents.resources.tools import recommend_fertilizers
        
        mock_response = Mock()
        mock_response.text = "Plan de fertilisation recommandé"
        mock_generate.return_value = mock_response
        
        result = recommend_fertilizers(
            crop="maïs",
            area_hectares=1.0,
            soil_fertility="moyenne",
            budget_level="modéré",
            tool_context=mock_resources_context
        )
        
        assert "crop" in result
        assert "fertilization_plan" in result
        assert "total_cost" in result
        assert "application_calendar" in result


class TestDataUtilities:
    """Tests pour les utilitaires de données."""
    
    def test_crop_info_retrieval(self):
        """Test la récupération d'informations sur les cultures."""
        cacao_info = get_crop_info(CropType.CACAO)
        assert cacao_info is not None
        assert cacao_info.name == CropType.CACAO
        assert cacao_info.growth_cycle_days > 0
        assert len(cacao_info.suitable_regions) > 0
    
    def test_region_info_retrieval(self):
        """Test la récupération d'informations sur les régions."""
        centre_info = get_region_info(RegionType.CENTRE)
        assert centre_info is not None
        assert "name" in centre_info
        assert "climate" in centre_info
        assert "main_crops" in centre_info
    
    def test_crop_region_compatibility(self):
        """Test la compatibilité culture-région."""
        from agriculture_cameroun.utils.data import get_suitable_crops
        
        centre_crops = get_suitable_crops(RegionType.CENTRE)
        assert isinstance(centre_crops, list)
        assert len(centre_crops) > 0
        assert CropType.MANIOC in centre_crops


class TestIntegration:
    """Tests d'intégration des agents."""
    
    @pytest.mark.asyncio
    async def test_agent_communication_mock(self):
        """Test mock de la communication entre agents."""
        # Mock des outils d'agent
        with patch('agriculture.tools.AgentTool') as mock_agent_tool:
            mock_instance = AsyncMock()
            mock_instance.run_async.return_value = "Réponse de l'agent météo"
            mock_agent_tool.return_value = mock_instance
            
            from agriculture_cameroun.tools import call_weather_agent
            
            mock_context = Mock()
            mock_context.state = {"agriculture_settings": {"default_region": "Centre"}}
            
            result = await call_weather_agent(
                question="Quelles sont les prévisions pour cette semaine?",
                region="Centre",
                tool_context=mock_context
            )
            
            assert result == "Réponse de l'agent météo"
            mock_instance.run_async.assert_called_once()
    
    def test_config_validation(self):
        """Test la validation de la configuration."""
        from agriculture_cameroun.config import validate_environment
        
        # Test avec variable d'environnement manquante
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Variables d'environnement manquantes"):
                validate_environment()
    
    def test_data_consistency(self):
        """Test la cohérence des données."""
        from agriculture_cameroun.utils.data import CROPS, REGIONS, MARKET_PRICES
        
        # Vérifier que toutes les cultures ont des prix
        for crop_type in CROPS.keys():
            assert crop_type in MARKET_PRICES, f"Prix manquant pour {crop_type}"
        
        # Vérifier que les régions ont des cultures compatibles
        # for region_type in REGIONS.keys():
        #     region_crops = get_suitable_crops(region_type)
        #     assert len(region_crops) > 0, f"Aucune culture compatible pour {region_type}"


class TestErrorHandling:
    """Tests de gestion d'erreurs."""
    
    def test_invalid_crop_type(self):
        """Test la gestion des types de culture invalides."""
        from agriculture_cameroun.utils.data import get_crop_info
        
        result = get_crop_info("culture_inexistante")
        assert result is None
    
    def test_invalid_region_type(self):
        """Test la gestion des types de région invalides."""
        from agriculture_cameroun.utils.data import get_region_info
        
        result = get_region_info("région_inexistante")
        assert result == {}
    
    @patch('agriculture.sub_agents.weather.tools.model.generate_content')
    def test_api_error_handling(self, mock_generate):
        """Test la gestion des erreurs d'API."""
        from agriculture_cameroun.sub_agents.weather.tools import get_weather_forecast
        
        # Simuler une erreur d'API
        mock_generate.side_effect = Exception("Erreur API")
        
        mock_context = Mock()
        mock_context.state = {"agriculture_settings": {"default_region": "Centre"}}
        
        with pytest.raises(Exception):
            get_weather_forecast(
                region="Centre",
                days=7,
                tool_context=mock_context
            )


@pytest.fixture(scope="session")
def event_loop():
    """Crée une boucle d'événements pour les tests async."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])