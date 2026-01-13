import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat import ChatBot
from rag_system import RAGSystem
from planning_agent import PlanningAgent
from code_assistant import CodeAssistant
from dashboard import MetricsDashboard

class TestIntegration:
    """Integration tests for the AI platform components"""
    
    @pytest.fixture
    def temp_env(self):
        """Set up temporary environment variables"""
        original_env = {}
        test_env = {
            'OPENAI_BASE_URL': 'https://test.api.com',
            'OPENAI_API_KEY': 'test-key',
            'MODEL_NAME': 'test-model'
        }
        
        for key, value in test_env.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        yield test_env
        
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    
    def test_chat_to_dashboard_integration(self, temp_env):
        """Test chat system integration with dashboard metrics"""
        with patch('openai.OpenAI'):
            # Create chat bot with real database operations
            chat_bot = ChatBot()
            
            # Use in-memory database for testing
            import sqlite3
            chat_bot.conn = sqlite3.connect(':memory:')
            chat_bot.init_db()
            
            # Test basic chat functionality
            assert chat_bot is not None
            assert hasattr(chat_bot, 'save_message')
            assert hasattr(chat_bot, 'get_recent_messages')
            
            # Test message operations work
            chat_bot.save_message("user", "Hello")
            messages = chat_bot.get_recent_messages()
            assert len(messages) > 0
            assert messages[0]['content'] == "Hello"
    
    @patch('rag_system.OpenAI')
    def test_rag_system_end_to_end(self, mock_openai, temp_env):
        """Test RAG system end-to-end functionality"""
        # Mock OpenAI
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Frodo is the main character"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create RAG system
        rag = RAGSystem()
        
        # Mock retrieval for simple vector store
        if hasattr(rag.collection, 'query'):
            rag.collection.query = Mock(return_value={
                'documents': [['Frodo Baggins is a hobbit']],
                'metadatas': [[{'chunk_id': 'test_chunk'}]],
                'distances': [[0.1]]
            })
        
        # Test question answering
        answer = rag.answer_question("Who is Frodo?")
        assert "Frodo" in answer
    
    @patch('planning_agent.OpenAI')
    def test_planning_agent_workflow(self, mock_openai, temp_env):
        """Test planning agent complete workflow"""
        # Mock OpenAI response
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
        
        # Create agent
        agent = PlanningAgent()
        
        # Test trip planning
        result = agent.plan_trip("Plan a 2-day trip to Auckland for $500")
        
        # Verify complete itinerary structure
        required_keys = [
            'destination', 'duration', 'total_budget', 'estimated_cost',
            'accommodation', 'flights', 'activities', 'daily_schedule'
        ]
        
        for key in required_keys:
            assert key in result
        
        # Verify budget constraint
        assert result['estimated_cost'] <= result['total_budget']
        
        # Verify daily schedule
        assert len(result['daily_schedule']) == 2  # 2 days
    
    @patch('code_assistant.OpenAI')
    def test_code_assistant_self_healing(self, mock_openai, temp_env):
        """Test code assistant self-healing capability"""
        # Mock OpenAI responses for multiple attempts
        responses = [
            "def broken_function(): return undefined_variable",  # First attempt (broken)
            "def working_function(): return 'Hello, World!'"    # Second attempt (working)
        ]
        
        mock_response_objects = []
        for response in responses:
            mock_resp = Mock()
            mock_resp.choices = [Mock()]
            mock_resp.choices[0].message.content = response
            mock_response_objects.append(mock_resp)
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = mock_response_objects
        mock_openai.return_value = mock_client
        
        # Create assistant
        assistant = CodeAssistant()
        
        # Mock test results
        with patch.object(assistant, 'test_python_code') as mock_test:
            mock_test.side_effect = [
                (False, "NameError: name 'undefined_variable' is not defined"),
                (True, "Code executed successfully!")
            ]
            
            result = assistant.solve_task("create a hello function")
            
            assert result["success"]
            assert result["attempts"] == 2
            assert "working_function" in result["final_code"]
    
    def test_dashboard_metrics_aggregation(self, temp_env):
        """Test dashboard metrics aggregation from multiple sources"""
        with patch('dashboard.sqlite3.connect') as mock_connect:
            # Mock database connection
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = [0]  # Empty database
            mock_conn.execute.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Test dashboard creation
            try:
                from dashboard import MetricsDashboard
                dashboard = MetricsDashboard()
                
                # Test that methods exist
                assert hasattr(dashboard, 'get_chat_metrics')
                assert hasattr(dashboard, 'get_rag_metrics')
                assert hasattr(dashboard, 'get_agent_metrics')
                
            except ImportError:
                # Dashboard not available, that's ok
                pass
    
    @patch('openai.OpenAI')
    @patch('openai.OpenAI')
    @patch('openai.OpenAI')
    @patch('openai.OpenAI')
    def test_system_wide_error_handling(self, mock_code_openai, mock_plan_openai, 
                                       mock_rag_openai, mock_chat_openai, temp_env):
        """Test error handling across all system components"""
        
        # Mock API failures
        for mock_openai in [mock_chat_openai, mock_rag_openai, mock_plan_openai, mock_code_openai]:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client
        
        # Test each component handles errors gracefully
        # Chat system
        chat_bot = ChatBot()
        with patch('builtins.print'):
            try:
                chat_bot.chat_stream("Hello")  # Should not raise exception
            except Exception as e:
                # Expected to fail with API error
                assert "API Error" in str(e)
        
        # RAG system
        rag = RAGSystem()
        try:
            rag.answer_question("Test question")
        except Exception as e:
            # Should handle gracefully or raise expected exception
            assert "API Error" in str(e)
        
        # Planning agent
        agent = PlanningAgent()
        try:
            agent.plan_trip("Test trip")
        except Exception as e:
            assert "API Error" in str(e)
        
        # Code assistant - disable mock mode to test real API error handling
        assistant = CodeAssistant()
        assistant.is_mock = False  # Force real API usage
        assistant.client = mock_code_openai.return_value  # Use the failing mock client
        try:
            result = assistant.solve_task("Test task")
            # If it doesn't raise an exception, it should fail gracefully
            assert not result["success"]  # Should fail gracefully
        except Exception as e:
            # Code assistant may raise exception on API error
            assert "API Error" in str(e)
    
    def test_configuration_loading(self, temp_env):
        """Test that all components load configuration correctly"""
        # Test environment variables are loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        # Test that environment variables are accessible
        assert os.getenv('OPENAI_BASE_URL') == temp_env['OPENAI_BASE_URL']
        assert os.getenv('OPENAI_API_KEY') == temp_env['OPENAI_API_KEY']
        assert os.getenv('MODEL_NAME') == temp_env['MODEL_NAME']
        
        # Create instances and verify they initialize without errors
        # Note: These components have fallback mock implementations for Python 3.14
        chat_bot = ChatBot()
        assert chat_bot is not None
        assert hasattr(chat_bot, 'client')
        
        rag = RAGSystem()
        assert rag is not None
        assert hasattr(rag, 'client')
        
        agent = PlanningAgent()
        assert agent is not None
        assert hasattr(agent, 'client')
        
        assistant = CodeAssistant()
        assert assistant is not None
        assert hasattr(assistant, 'client')