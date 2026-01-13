import pytest
import json
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from planning_agent import PlanningAgent

class TestPlanningAgent:
    
    @pytest.fixture
    def agent(self):
        """Create PlanningAgent instance"""
        with patch('planning_agent.OpenAI'):
            return PlanningAgent()
    
    def test_log_reasoning(self, agent):
        """Test reasoning logging"""
        with patch('builtins.print') as mock_print:
            agent.log_reasoning("Test thought")
            
            assert len(agent.scratchpad) == 1
            assert "[REASONING] Test thought" in agent.scratchpad[0]
            mock_print.assert_called_with("Test thought")
    
    def test_get_flight_prices(self, agent):
        """Test flight price retrieval"""
        result = agent.get_flight_prices("Wellington", "Auckland", "2024-01-15")
        
        assert "flights" in result
        assert "currency" in result
        assert len(result["flights"]) > 0
        assert all("price" in flight for flight in result["flights"])
    
    def test_get_weather(self, agent):
        """Test weather retrieval"""
        result = agent.get_weather("Auckland", "2024-01-15")
        
        assert "temperature" in result
        assert "condition" in result
        assert "precipitation" in result
        assert "recommendation" in result
    
    def test_get_attractions(self, agent):
        """Test attractions retrieval"""
        result = agent.get_attractions("Auckland")
        
        assert "attractions" in result
        assert len(result["attractions"]) > 0
        
        for attraction in result["attractions"]:
            assert "name" in attraction
            assert "price" in attraction
            assert "duration" in attraction
            assert "category" in attraction
    
    def test_get_accommodation(self, agent):
        """Test accommodation retrieval"""
        result = agent.get_accommodation("Auckland", 100)
        
        assert "accommodations" in result
        # Should filter by budget
        for acc in result["accommodations"]:
            assert acc["price"] <= 100
    
    @patch('planning_agent.OpenAI')
    def test_plan_trip_success(self, mock_openai, agent):
        """Test successful trip planning"""
        # Mock OpenAI response for parsing
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "destination": "Auckland",
            "duration": 2,
            "budget_amount": 500,
            "budget_currency": "NZD",
            "preferences": []
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent.client = mock_client
        
        result = agent.plan_trip("Plan a 2-day trip to Auckland for under NZ$500")
        
        assert "destination" in result
        assert "duration" in result
        assert "total_budget" in result
        assert "estimated_cost" in result
        assert "accommodation" in result
        assert "flights" in result
        assert "activities" in result
        assert "daily_schedule" in result
        
        # Budget constraint check
        assert result["estimated_cost"] <= result["total_budget"]
    
    @patch('planning_agent.OpenAI')
    def test_plan_trip_json_parse_error(self, mock_openai, agent):
        """Test trip planning with JSON parse error (fallback)"""
        # Mock OpenAI response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        agent.client = mock_client
        
        result = agent.plan_trip("Plan a trip")
        
        # Should use fallback parameters
        assert result["destination"] == "Auckland"
        assert result["total_budget"] == 500
    
    def test_budget_allocation(self, agent):
        """Test budget allocation logic"""
        with patch.object(agent, 'client'):
            with patch.object(agent, 'get_weather'):
                with patch.object(agent, 'get_attractions'):
                    with patch.object(agent, 'get_accommodation'):
                        with patch.object(agent, 'get_flight_prices'):
                            
                            # Mock all API calls to return minimal data
                            agent.get_weather.return_value = {"temperature": "20°C", "condition": "sunny", "precipitation": "0%", "recommendation": "Perfect weather"}
                            agent.get_attractions.return_value = {"attractions": [{"name": "Test", "price": 50, "duration": "2h", "category": "test"}]}
                            agent.get_accommodation.return_value = {"accommodations": [{"name": "Test Hotel", "price": 100, "rating": 4.0, "type": "hotel"}]}
                            agent.get_flight_prices.return_value = {"flights": [{"airline": "Test Air", "price": 100, "departure": "10:00", "arrival": "12:00"}]}
                            
                            # Mock OpenAI for parsing
                            mock_response = Mock()
                            mock_response.choices = [Mock()]
                            mock_response.choices[0].message.content = json.dumps({
                                "destination": "Auckland",
                                "duration": 2,
                                "budget_amount": 1000,
                                "budget_currency": "NZD",
                                "preferences": []
                            })
                            agent.client.chat.completions.create.return_value = mock_response
                            
                            result = agent.plan_trip("Plan a trip")
                            
                            # Verify budget allocation makes sense
                            total_cost = result["estimated_cost"]
                            assert total_cost > 0
                            assert total_cost <= result["total_budget"]
    
    def test_daily_schedule_creation(self, agent):
        """Test daily schedule creation"""
        with patch.object(agent, 'client'):
            # Mock all dependencies
            agent.get_weather = Mock(return_value={"temperature": "20°C", "condition": "sunny", "precipitation": "0%", "recommendation": "Great weather"})
            agent.get_attractions = Mock(return_value={"attractions": [
                {"name": "Attraction 1", "price": 30, "duration": "2h", "category": "museum"},
                {"name": "Attraction 2", "price": 40, "duration": "3h", "category": "nature"}
            ]})
            agent.get_accommodation = Mock(return_value={"accommodations": [{"name": "Hotel", "price": 80, "rating": 4.0, "type": "hotel"}]})
            agent.get_flight_prices = Mock(return_value={"flights": [{"airline": "Air", "price": 120, "departure": "09:00", "arrival": "11:00"}]})
            
            # Mock OpenAI
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "destination": "Auckland",
                "duration": 3,
                "budget_amount": 800,
                "budget_currency": "NZD",
                "preferences": []
            })
            agent.client.chat.completions.create.return_value = mock_response
            
            result = agent.plan_trip("Plan a 3-day trip")
            
            assert len(result["daily_schedule"]) == 3
            for day_plan in result["daily_schedule"]:
                assert "day" in day_plan
                assert "activities" in day_plan
                assert "meals" in day_plan
                assert "notes" in day_plan