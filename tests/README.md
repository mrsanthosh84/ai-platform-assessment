# AI Platform Assessment - Test Suite

Comprehensive test suite for the AI platform with unit and integration tests.

## 📁 Test Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Shared fixtures
├── test_chat.py             # Chat system unit tests
├── test_rag_system.py       # RAG system unit tests
├── test_planning_agent.py   # Planning agent unit tests
├── test_code_assistant.py   # Code assistant unit tests
├── test_dashboard.py        # Dashboard unit tests
└── test_integration.py      # Integration tests
```

## 🧪 Test Coverage

### Unit Tests (85+ test cases)

**Chat System (`test_chat.py`)**
- Database initialization and schema
- Message saving and retrieval
- Cost calculation accuracy
- Streaming response handling
- Error handling and recovery

**RAG System (`test_rag_system.py`)**
- PDF processing and chunking
- Vector storage operations
- Document retrieval performance
- Question answering accuracy
- Evaluation metrics

**Planning Agent (`test_planning_agent.py`)**
- API integration (flights, weather, attractions)
- Budget constraint satisfaction
- Itinerary generation
- JSON parsing and fallback handling
- Daily schedule creation

**Code Assistant (`test_code_assistant.py`)**
- Code generation for Rust/Python
- Compilation and testing
- Self-healing retry logic
- Error feedback processing
- Language detection

**Dashboard (`test_dashboard.py`)**
- Metrics database operations
- Data type conversions
- Aggregation calculations
- Sample data generation
- Error handling

### Integration Tests (`test_integration.py`)
- Cross-component data flow
- End-to-end workflows
- System-wide error handling
- Configuration loading
- Metrics aggregation

## 🚀 Running Tests

### Option 1: With pytest (Recommended)
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run all tests
pytest -q

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_chat.py -v

# Run with coverage
pytest --cov=. tests/
```

### Option 2: Alternative Test Runner
```bash
# If pytest is not available
python3 validate_tests.py  # Validate test structure
python3 run_tests.py       # Run tests with unittest
```

## 📊 Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Mock Tests**: Use mocks for external dependencies (OpenAI, ChromaDB)
- **Database Tests**: Test SQLite operations with temporary databases
- **Error Handling**: Test graceful failure scenarios

## 🔧 Test Configuration

**pytest.ini**
- Test discovery patterns
- Output formatting
- Warning filters
- Markers for test categorization

**conftest.py**
- Shared fixtures for database setup
- Mock OpenAI clients
- Environment variable management
- Temporary file handling

## 📈 Key Test Features

1. **Isolated Testing**: Each test uses temporary databases/files
2. **Mock External APIs**: No real API calls during testing
3. **Error Simulation**: Tests failure scenarios and recovery
4. **Performance Validation**: Checks latency and accuracy targets
5. **Data Integrity**: Validates database operations and data types
6. **Configuration Testing**: Ensures proper environment setup

## 🎯 Performance Targets Tested

- Chat latency < 2000ms (mocked)
- RAG retrieval < 300ms (mocked)
- Agent planning < 30s (mocked)
- Code generation success within 3 attempts
- Database operations complete without errors

## 🛠️ Dependencies

Test-specific dependencies in `requirements.txt`:
- `pytest==7.4.4` - Test framework
- `pytest-mock==3.12.0` - Mocking utilities

## 📝 CI/CD Integration

Tests are designed to run in CI environments:

```bash
# CI command
pytest -q --tb=short --disable-warnings
```

Exit codes:
- `0`: All tests passed
- `1`: Test failures or errors

## 🔍 Test Examples

**Unit Test Example:**
```python
def test_calculate_cost(self, chat_bot):
    cost = chat_bot.calculate_cost(100, 200)
    expected = (100 / 1_000_000) * 5.0 + (200 / 1_000_000) * 15.0
    assert cost == expected
```

**Integration Test Example:**
```python
def test_chat_to_dashboard_integration(self, temp_env):
    chat_bot = ChatBot()
    dashboard = MetricsDashboard()
    # Test data flow between components
```

**Mock Test Example:**
```python
@patch('chat.OpenAI')
def test_chat_stream_success(self, mock_openai, chat_bot):
    # Mock API response and test functionality
```

## 🚨 Common Issues

1. **Missing Dependencies**: Install with `pip install -r requirements.txt`
2. **Import Errors**: Ensure project root is in Python path
3. **Database Locks**: Tests use temporary databases to avoid conflicts
4. **Mock Failures**: Check mock setup in conftest.py

## 📋 Test Checklist

- ✅ All components have unit tests
- ✅ Integration tests cover cross-component workflows
- ✅ Error handling is thoroughly tested
- ✅ Database operations are validated
- ✅ Performance targets are checked
- ✅ Configuration loading is tested
- ✅ Mock external dependencies
- ✅ CI/CD ready with proper exit codes