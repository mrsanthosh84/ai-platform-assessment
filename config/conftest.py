import pytest
import os
import tempfile
import sqlite3
from unittest.mock import Mock, patch
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables"""
    original_env = {}
    test_env = {
        'OPENAI_BASE_URL': 'https://test.api.com',
        'OPENAI_API_KEY': 'test-key-12345',
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

@pytest.fixture
def temp_sqlite_db():
    """Create temporary SQLite database"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    conn = sqlite3.connect(path)
    yield conn, path
    
    conn.close()
    os.unlink(path)

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client with standard responses"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test response"
    
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client

@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB client"""
    mock_collection = Mock()
    mock_collection.count.return_value = 0
    mock_collection.query.return_value = {
        'documents': [['Test document']],
        'metadatas': [[{'chunk_id': 'test_chunk'}]],
        'distances': [[0.1]]
    }
    
    mock_client = Mock()
    mock_client.get_or_create_collection.return_value = mock_collection
    
    return mock_client, mock_collection