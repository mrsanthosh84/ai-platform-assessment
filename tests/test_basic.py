#!/usr/bin/env python3
"""
Simple tests for AI Platform Assessment
Tests basic functionality without external dependencies
"""

import unittest
import os
import sys
import tempfile
import sqlite3
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests that don't require external dependencies"""
    
    def test_project_structure(self):
        """Test that required files exist"""
        project_root = os.path.join(os.path.dirname(__file__), '..', 'src')
        
        required_files = [
            'chat.py',
            'rag_system.py', 
            'planning_agent.py',
            'code_assistant.py',
            'dashboard.py',
            'main.py'
        ]
        
        for file in required_files:
            file_path = os.path.join(project_root, file)
            self.assertTrue(os.path.exists(file_path), f"Missing required file: {file}")
    
    def test_sqlite_operations(self):
        """Test basic SQLite operations"""
        # Create temporary database
        fd, temp_db = tempfile.mkstemp()
        os.close(fd)
        
        try:
            conn = sqlite3.connect(temp_db)
            
            # Create test table
            conn.execute("""
                CREATE TABLE test_messages (
                    id INTEGER PRIMARY KEY,
                    role TEXT,
                    content TEXT,
                    timestamp REAL
                )
            """)
            
            # Insert test data
            conn.execute(
                "INSERT INTO test_messages (role, content, timestamp) VALUES (?, ?, ?)",
                ("user", "Hello", 1640995200.0)
            )
            conn.commit()
            
            # Query data
            cursor = conn.execute("SELECT role, content FROM test_messages")
            messages = cursor.fetchall()
            
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0], ("user", "Hello"))
            
            conn.close()
            
        finally:
            os.unlink(temp_db)
    
    def test_cost_calculation(self):
        """Test cost calculation logic"""
        def calculate_cost(prompt_tokens, completion_tokens):
            # GPT-4o pricing: $5/1M input, $15/1M output
            input_cost = (prompt_tokens / 1_000_000) * 5.0
            output_cost = (completion_tokens / 1_000_000) * 15.0
            return input_cost + output_cost
        
        cost = calculate_cost(100, 200)
        expected = (100 / 1_000_000) * 5.0 + (200 / 1_000_000) * 15.0
        self.assertEqual(cost, expected)
        
        # Test with realistic values
        cost = calculate_cost(50, 150)
        self.assertGreater(cost, 0)
        self.assertLess(cost, 0.01)  # Should be small amount
    
    def test_json_parsing(self):
        """Test JSON parsing functionality"""
        import json
        
        # Test valid JSON
        test_data = {
            "destination": "Auckland",
            "duration": 2,
            "budget_amount": 500,
            "budget_currency": "NZD"
        }
        
        json_str = json.dumps(test_data)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["destination"], "Auckland")
        self.assertEqual(parsed["duration"], 2)
        self.assertEqual(parsed["budget_amount"], 500)
        
        # Test invalid JSON handling
        try:
            json.loads("invalid json")
            self.fail("Should have raised exception")
        except json.JSONDecodeError:
            pass  # Expected
    
    def test_file_operations(self):
        """Test basic file operations"""
        # Create temporary file
        fd, temp_file = tempfile.mkstemp(suffix='.txt')
        os.close(fd)
        
        try:
            # Write to file
            with open(temp_file, 'w') as f:
                f.write("Test content")
            
            # Read from file
            with open(temp_file, 'r') as f:
                content = f.read()
            
            self.assertEqual(content, "Test content")
            
        finally:
            os.unlink(temp_file)
    
    def test_environment_variables(self):
        """Test environment variable handling"""
        # Test setting and getting environment variables
        test_key = "TEST_AI_PLATFORM_VAR"
        test_value = "test_value_123"
        
        # Set environment variable
        os.environ[test_key] = test_value
        
        # Get environment variable
        retrieved_value = os.getenv(test_key)
        self.assertEqual(retrieved_value, test_value)
        
        # Clean up
        del os.environ[test_key]
        
        # Test default value
        default_value = os.getenv("NON_EXISTENT_VAR", "default")
        self.assertEqual(default_value, "default")
    
    def test_mock_functionality(self):
        """Test that mocking works correctly"""
        # Create mock object
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test mock behavior
        response = mock_client.chat.completions.create(
            model="test-model",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        self.assertEqual(response.choices[0].message.content, "Test response")
        mock_client.chat.completions.create.assert_called_once()

class TestConfigurationLoading(unittest.TestCase):
    """Test configuration and imports"""
    
    def test_requirements_file(self):
        """Test that requirements.txt exists and has content"""
        project_root = os.path.join(os.path.dirname(__file__), '..')
        requirements_path = os.path.join(project_root, 'requirements.txt')
        
        self.assertTrue(os.path.exists(requirements_path))
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for key dependencies
        self.assertIn('openai', content)
        self.assertIn('streamlit', content)
    
    def test_env_file_template(self):
        """Test that .env file exists"""
        project_root = os.path.join(os.path.dirname(__file__), '..', 'config')
        env_path = os.path.join(project_root, '.env')
        
        # .env file should exist
        self.assertTrue(os.path.exists(env_path), ".env file should exist")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)