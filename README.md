# 🔬 AgentLab — Day-to-Day Testing Workbench

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.37%2B-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A **chain-first, multi-agent testing workbench** for day-to-day API testing, LLM evaluation, and multi-agent orchestration. Built on [Streamlit](https://streamlit.io/) with:

- **Context Chunking** — large API/LLM responses are automatically split into overlapping chunks before being passed to the next agent in a chain
- **MCP (Model Context Protocol)** — LLM-driven tool selection and orchestration
- **LangChain + RAG** — retrieval-augmented agents with vector store memory
- **Playwright Agents** — AI-powered browser automation (Planner / Generator / Healer)
- **Marketplace** — pre-built agent manifests deployable to AWS or Azure

---

## ⚡ Quick Start

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run framework/agentlab.py --server.port 8503
```

**Linux / macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run framework/agentlab.py --server.port 8503
```

Open [http://localhost:8503](http://localhost:8503) in your browser.

> **Note:** [Ollama](https://ollama.ai/) must be running locally for LLM-based features. See [`docs/ollama-guide.md`](docs/ollama-guide.md) for setup instructions.

---

## 🗂️ Project Layout

```
AgentLab/
├── framework/
│   ├── agentlab.py                  # Main Streamlit entrypoint
│   ├── agent_registry.py            # Central agent registry
│   ├── agentFactory.py              # Agent instantiation factory
│   │
│   ├── # Core agents
│   ├── api_test_agent.py            # REST API testing
│   ├── ui_test_agent.py             # Browser / UI testing
│   ├── validation_agent.py          # Data & schema validation
│   ├── report_agent.py              # Report generation
│   ├── healing_agent.py             # Auto-healing / self-repair
│   ├── advanced_agents.py           # Security, perf, GraphQL, chaos, ML, mobile
│   │
│   ├── # LLM & evaluation
│   ├── llm_eval_agent.py            # LLM evaluation framework
│   ├── llm_model_tester.py          # Ollama model benchmarking
│   ├── ollama_helper.py             # Ollama client utilities
│   ├── ollama_demo.py               # Ollama demo scripts
│   │
│   ├── # LangChain / RAG / VectorDB
│   ├── langchain_agent.py           # LangChain integration agent
│   ├── rag_agent.py                 # Retrieval-Augmented Generation agent
│   ├── vectordb_agent.py            # Vector DB evaluation (FAISS / Chroma)
│   │
│   ├── # MCP (Model Context Protocol)
│   ├── mcp_tool_protocol.py         # MCP tool registry & base classes
│   ├── mcp_orchestrator.py          # LLM-driven MCP orchestrator
│   ├── mcp_api_agent.py             # MCP-compliant API test agent
│   ├── mcp_ui_agent.py              # MCP-compliant UI test agent
│   ├── mcp_config.py                # MCP server configuration
│   │
│   ├── # Playwright AI agents
│   ├── playwright_agents.py         # Planner / Generator / Healer agents
│   ├── playwright_agents_config.py  # Environment-based Playwright config
│   ├── playwright_agents_ui.py      # Streamlit UI for Playwright agents
│   ├── playwright_agents_examples.py# Usage examples
│   ├── PLAYWRIGHT_AGENTS_README.md  # Playwright agents documentation
│   │
│   ├── # Orchestration
│   ├── orchestrator_agent.py        # High-level orchestration agent
│   ├── orchestration_examples.py    # Orchestration usage examples
│   │
│   ├── # Utilities & verification
│   ├── marketplace_deployer.py      # Marketplace agent deployer
│   ├── examples.py                  # General usage examples
│   ├── verify_agents.py             # Quick agent verification checks
│   ├── verify_framework.py          # Framework integrity checks
│   └── START_HERE.py                # Getting-started entry point
│
├── marketplace/                     # Pre-built agent packages
│   ├── accessibility_checker/       # WCAG accessibility testing
│   ├── api_contract_validator/      # OpenAPI contract validation
│   ├── browser_automation/          # Headless browser automation
│   ├── chaos_engineer/              # Chaos / fault injection testing
│   ├── compliance_checker/          # GDPR / SOC2 / HIPAA compliance
│   ├── graphql_tester/              # GraphQL API testing
│   ├── ml_model_tester/             # ML model quality evaluation
│   ├── mobile_app_tester/           # Mobile UI testing
│   ├── performance_tester/          # Load & stress testing
│   ├── security_scanner/            # OWASP security scanning
│   └── visual_regression_tester/    # Screenshot diff testing
│
├── scripts/
│   ├── run_dashboard.ps1            # Windows quick-launch script
│   ├── run_dashboard.sh             # Linux/macOS quick-launch script
│   ├── run_playwright_agents.ps1    # Launch Playwright agent suite
│   └── setup_venv.ps1               # Virtual environment setup
│
├── docs/                            # Full documentation
│   ├── INDEX.md                     # Documentation index
│   ├── ollama-guide.md              # Ollama setup & usage
│   ├── multi-agent-orchestration-guide.md
│   ├── playwright-agents-guide.md
│   ├── langchain-vectordb-rag.md
│   ├── configuration-guide.md
│   └── ...                          # Additional guides
│
├── requirements.txt
├── pyproject.toml
└── conftest.py
```

---

## ✨ Key Features

### 🔗 Chain Builder
Wire agents sequentially into a pipeline. The output of each step is automatically chunked (configurable size & overlap) and injected as context into the next step's input.

### ✂️ Context Chunking
Large API responses or LLM outputs are split into overlapping chunks before being forwarded, preventing token-limit overflow in downstream agents.

### 📚 Agent Catalog
Browse, search, and run any of the 20+ registered agents directly from the UI with full parameter configuration.

### 🧪 Test Lab
Interactive single-agent tester with full configuration: authentication (Basic, Bearer, API Key, OAuth 2.0, Form Login), custom HTTP headers, request body, and timeout settings.

### 💬 Natural Language Tests
Describe a test scenario in plain English — the app parses your intent and dispatches the right agent automatically.

### 🤖 LLM Playground
Benchmark and compare Ollama models side-by-side with custom prompts. Supports all locally available Ollama models.

### 🎯 Multi-Agent Orchestration (MCP)
Build and execute parallel or sequential test suites with dependency tracking, priority ordering, and auto-healing on failure. Uses the **Model Context Protocol (MCP)** for LLM-driven tool selection.

### 🎭 Playwright AI Agents
Three specialized agents powered by Ollama LLM:
- **Planner** — analyses the target application and generates a structured test plan
- **Generator** — converts the plan into executable Playwright test scripts
- **Healer** — detects and auto-fixes broken selectors and flaky assertions

### 🔍 RAG / VectorDB Evaluation
Evaluate Retrieval-Augmented Generation pipelines and vector store performance (FAISS, Chroma) with configurable embedding models.

### 🏪 Marketplace Agents
11 pre-built, deployment-ready agent packages with OpenAPI specs and AWS/Azure deployment manifests.

---

## 🛠️ Dependencies

| Category | Packages |
|---|---|
| UI | `streamlit`, `nest_asyncio` |
| HTTP | `httpx` |
| Agents | `autogen-agentchat`, `autogen-core`, `autogen-ext` |
| LangChain | `langchain`, `langchain-community`, `langchain-ollama`, `langchain-text-splitters` |
| Vector DB | `chromadb` |
| Browser | `playwright` |
| Data | `pandas`, `numpy`, `openpyxl`, `reportlab` |
| Testing | `pytest`, `pytest-asyncio`, `pytest-playwright`, `pytest-html` |

Install all dependencies:

```bash
pip install -r requirements.txt
playwright install chromium  # install browser binaries
```

---

## 🧪 Running Tests

```bash
# MCP system tests (tool registry, orchestrator, tool execution)
pytest framework/test_mcp_system.py -v

# LangChain integration tests
pytest framework/test_langchain_integration.py -v

# All tests
pytest -v
```

---

## 📝 Configuration

All agent behaviour is configurable via the sidebar in the UI:

- **Authentication** — none / Basic / Bearer / API Key / OAuth 2.0 / Form Login
- **API Config** — method, headers, body, content type, timeout, num requests
- **UI Config** — browser engine, headless mode, viewport, wait timeout
- **Database Config** — host, port, credentials, database name, engine type
- **Chunk Config** — chunk size, overlap, max chunks per step
- **LangChain / VectorDB / RAG** — per-agent evaluation parameters

See [`docs/configuration-guide.md`](docs/configuration-guide.md) for full details.

---

## 🤖 Ollama Setup

AgentLab uses [Ollama](https://ollama.ai/) as its local LLM backend (no API key required).

```bash
# Install and start Ollama
ollama serve

# Pull a model
ollama pull llama3.2:latest
```

See [`docs/ollama-guide.md`](docs/ollama-guide.md) for more models and configuration options.

---

## 📖 Documentation

Full documentation is in [`docs/`](docs/):

| Guide | Description |
|---|---|
| [`INDEX.md`](docs/INDEX.md) | Documentation index |
| [`configuration-guide.md`](docs/configuration-guide.md) | Full configuration reference |
| [`multi-agent-orchestration-guide.md`](docs/multi-agent-orchestration-guide.md) | Orchestration and MCP |
| [`playwright-agents-guide.md`](docs/playwright-agents-guide.md) | Playwright AI agents |
| [`langchain-vectordb-rag.md`](docs/langchain-vectordb-rag.md) | LangChain, RAG, and VectorDB |
| [`ollama-guide.md`](docs/ollama-guide.md) | Ollama setup and models |
| [`deployment-guide.md`](docs/deployment-guide.md) | Marketplace deployment |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
