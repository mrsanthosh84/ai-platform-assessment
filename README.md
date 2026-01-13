# AI Platform Assessment

A comprehensive AI platform implementation featuring conversational AI, retrieval-augmented generation, autonomous planning agents, and self-healing code assistance.

## Architecture

```
ai-platform-assessment/
├── chat.py              # Task 3.1: Conversational Core
├── rag_system.py        # Task 3.2: RAG QA System  
├── planning_agent.py    # Task 3.3: Planning Agent
├── code_assistant.py    # Task 3.4: Code Assistant
├── dashboard.py         # Stretch: Evaluation Dashboard
├── main.py             # Main runner script
├── requirements.txt    # Python dependencies
├── .env               # Environment configuration
├── Dockerfile         # Container configuration
├── docker-compose.yml # Docker orchestration
└── README.md          # This file
```

## Quick Start

### Option 1: Docker (Recommended)
```bash
docker-compose up --build
```
Access dashboard at http://localhost:8501

### Option 2: Local Setup
```bash
# Install dependencies
pip3 install -r requirements.txt
# OR if pip3 not available:
python3 -m pip install -r requirements.txt

# Run all tasks interactively
python3 main.py

# Or run individual components
python3 chat.py
python3 rag_system.py
python3 planning_agent.py
python3 code_assistant.py
python3 dashboard.py
```

## Task Implementation

### Task 3.1: Conversational Core
**File:** `chat.py`

Features:
- Token-level streaming responses
- SQLite persistence (last 10 messages)
- Cost telemetry (prompt/completion tokens, USD cost, latency)
- Real-time metrics display

**Usage:**
```bash
python3 chat.py
# Type "Hello" to see streaming response with metrics
```

**Expected Output:**
```
[stats] prompt=8 completion=23 cost=$0.000146 latency=623ms
```

### Task 3.2: High-Performance RAG QA
**File:** `rag_system.py`

Features:
- PDF ingestion (50MB+ corpus)
- ChromaDB vector storage
- Sub-300ms retrieval performance
- Inline citations in answers
- Automated accuracy evaluation (20+ test questions)

**Usage:**
```bash
python3 rag_system.py
# Automatically downloads and processes Lord of the Rings PDF
# Runs retrieval evaluation
# Interactive QA session
```

### Task 3.3: Autonomous Planning Agent
**File:** `planning_agent.py`

Features:
- Multi-tool integration (flights, weather, attractions, accommodation)
- Visible scratch-pad reasoning
- Budget constraint satisfaction
- Structured JSON output

**Usage:**
```bash
python3 planning_agent.py
# Example: "Plan a 2-day trip to Auckland for under NZ$500"
```

### Task 3.4: Self-Healing Code Assistant
**File:** `code_assistant.py`

Features:
- Natural language to code generation
- Automatic compilation/testing (Rust & Python)
- Error feedback and retry logic (max 3 attempts)
- Progress streaming to console

**Usage:**
```bash
python3 code_assistant.py
# Example: "write quicksort in Rust"
```

### Stretch Goal: Evaluation Dashboard
**File:** `dashboard.py`

Features:
- Real-time metrics visualization
- Latency and cost tracking over time
- Retrieval accuracy curves
- Agent success/failure breakdown
- Auto-refresh capabilities

**Access:** http://localhost:8501 (after running `streamlit run dashboard.py`)

## 🔧 Configuration

Environment variables in `.env`:
```
OPENAI_BASE_URL=https://aiunifier.wonderfulrock-83cb33fd.australiaeast.azurecontainerapps.io
OPENAI_API_KEY=sk-zM2MxgXhXnusmExHx1sKyw
MODEL_NAME=Gpt4o
```

## Performance Targets

- **Chat Latency:** < 2000ms typical
- **RAG Retrieval:** < 300ms median
- **Agent Planning:** < 30s end-to-end
- **Code Generation:** < 3 attempts for success

## Testing

Comprehensive test suite with 85+ test cases:

# Run all tests
python3 -m pytest tests/ -v

# Use convenience script
python3 run_pytest.py

# Run specific tests
python3 -m pytest tests/test_chat.py -v

# Run with short traceback
python3 run_pytest.py --tb=short


```bash
# test runners
python3 validate_tests.py  # Validate test structure
python3 run_tests.py       # Run with unittest
```

Test coverage:
- **Unit Tests:** Individual component testing
- **Integration Tests:** Cross-component workflows  
- **Error Handling:** Failure scenario validation
- **Performance:** Latency and accuracy targets

## Monitoring

The dashboard provides real-time monitoring of:
- Token usage and costs
- Response latencies
- Retrieval performance
- Agent success rates
- System health metrics

## Docker Deployment

```bash
# Build and run
docker-compose up --build

# Background mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Key Features

1. **Streaming Responses:** Real-time token-by-token output
2. **Cost Tracking:** Precise token counting and USD cost calculation
3. **High-Performance Retrieval:** Sub-300ms vector search
4. **Autonomous Planning:** Multi-tool orchestration with reasoning
5. **Self-Healing Code:** Automatic error detection and retry
6. **Real-time Dashboard:** Live metrics and performance visualization

## Dependencies

- **OpenAI:** GPT-4o integration
- **ChromaDB:** Vector database for RAG
- **Streamlit:** Dashboard framework
- **SQLite:** Message persistence
- **PyPDF2:** Document processing
- **Requests:** HTTP client for APIs

## Notes

- All components use the provided Azure OpenAI endpoint
- Token usage is tracked and reported for cost monitoring
- The system is designed for production-scale deployment
- Error handling and retry logic ensure robust operation
- Metrics are persisted for historical analysis