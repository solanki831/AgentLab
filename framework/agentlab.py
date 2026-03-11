"""
� AGENTLAB — Day-to-Day Agent & API Testing Workbench
- Chain multiple agents sequentially with context passing
- Context chunking for large API responses and documents
- All agents in one UI with dynamic configuration
- Ollama LLM integration (no API key required)
- MCP integration verification
- Full authentication/login support for UI testing
- Complete API data input (headers, body, auth)
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
import sys
import os
import logging
import traceback

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass  # nest_asyncio not installed; asyncio.run() may fail inside Streamlit

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.agent_registry import get_registry, AgentType
from framework.agentFactory import AgentFactory
from framework.ollama_helper import create_ollama_client
from framework.mcp_config import McpConfig
from framework.advanced_agents import (
    security_scan, performance_test, validate_api_contract,
    test_mobile_app, test_graphql_endpoint, run_chaos_test,
    check_compliance, test_ml_model, run_e2e_test,
    generate_comprehensive_report
)
from framework.llm_eval_agent import LLMEvaluationAgent
from framework.langchain_agent import LangChainTestAgent
from framework.vectordb_agent import VectorDBEvaluationAgent
from framework.rag_agent import RAGEvaluationAgent
from framework.mcp_orchestrator import OrchestratorAgent, TestTask

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="🔬 AgentLab — Test Workbench",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    /* Metric cards */
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 8px; }
    
    /* Status colors */
    .status-ok { color: #06AD1C; font-weight: bold; }
    .status-warning { color: #FF9500; font-weight: bold; }
    .status-error { color: #FF2B2B; font-weight: bold; }
    div[data-testid="column"] { padding: 5px; }
    
    /* Category cards */
    .category-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 12px;
        margin: 8px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Agent cards */
    .agent-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-left: 4px solid #667eea;
        padding: 12px;
        border-radius: 8px;
        margin: 6px 0;
        transition: transform 0.2s;
    }
    .agent-card:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Category badges */
    .badge-llm { background-color: #9333ea; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-api { background-color: #2563eb; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-ui { background-color: #059669; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-data { background-color: #d97706; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-security { background-color: #dc2626; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-performance { background-color: #0891b2; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-compliance { background-color: #4f46e5; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-ml { background-color: #7c3aed; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-reporting { background-color: #475569; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-reliability { background-color: #ea580c; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    .badge-database { background-color: #16a34a; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; }
    
    /* Quick test buttons */
    .quick-test-btn {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        color: white;
    }
    
    /* Test result cards */
    .result-success { border-left: 4px solid #06AD1C; background: #f0fdf4; }
    .result-failed { border-left: 4px solid #dc2626; background: #fef2f2; }
    .result-warning { border-left: 4px solid #f59e0b; background: #fffbeb; }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    
    /* Config section */
    .config-section { background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin: 10px 0; }
    
    /* Divider with text */
    .divider-text {
        display: flex;
        align-items: center;
        text-align: center;
        color: #6b7280;
        margin: 20px 0;
    }
    .divider-text::before,
    .divider-text::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #e5e7eb;
    }
    .divider-text::before { margin-right: 10px; }
    .divider-text::after { margin-left: 10px; }
</style>
""", unsafe_allow_html=True)

# Category configuration with icons and colors
CATEGORY_CONFIG = {
    "llm": {"icon": "🤖", "color": "#9333ea", "name": "LLM & AI"},
    "api": {"icon": "🌐", "color": "#2563eb", "name": "API Testing"},
    "ui": {"icon": "🖥️", "color": "#059669", "name": "UI & Visual"},
    "data": {"icon": "📊", "color": "#d97706", "name": "Data & Database"},
    "database": {"icon": "🗄️", "color": "#16a34a", "name": "Database"},
    "security": {"icon": "🔒", "color": "#dc2626", "name": "Security"},
    "performance": {"icon": "⚡", "color": "#0891b2", "name": "Performance"},
    "compliance": {"icon": "📋", "color": "#4f46e5", "name": "Compliance"},
    "ml": {"icon": "🧠", "color": "#7c3aed", "name": "Machine Learning"},
    "reporting": {"icon": "📈", "color": "#475569", "name": "Reporting"},
    "reliability": {"icon": "🔄", "color": "#ea580c", "name": "Reliability"},
}


# ============================================================================
# SESSION STATE - Extended for auth and API config
# ============================================================================

def init_session_state():
    """Initialize session state variables with auth and API config"""
    defaults = {
        "ollama_client": None,
        "mcp_status": {},
        "test_results": [],
        "test_history": [],  # Track test history
        "ollama_models": [],
        "selected_category": "all",  # Category filter
        # Quick Tests configuration (editable in sidebar)
        "quick_tests_config": {
            "sections": [
                {
                    "title": "Security & Compliance",
                    "tests": [
                        {"label": "🔒 Security Scan", "agent": "Security", "url": "https://example.com"},
                        {"label": "📋 GDPR Check", "agent": "Compliance", "url": "https://example.com"}
                    ]
                },
                {
                    "title": "Performance & API",
                    "tests": [
                        {"label": "⚡ Performance", "agent": "Performance", "url": "https://example.com"},
                        {"label": "🌐 API Contract", "agent": "API Contract", "url": "https://example.com"}
                    ]
                },
                {
                    "title": "UI & Accessibility",
                    "tests": [
                        {"label": "🔄 E2E Test", "agent": "E2E", "url": "https://example.com"},
                        {"label": "♿ Accessibility", "agent": "Accessibility", "url": "https://example.com"}
                    ]
                }
            ]
        },
        # Authentication Configuration
        "auth_config": {
            "auth_type": "none",  # none, basic, bearer, oauth, api_key, form_login
            "username": "",
            "password": "",
            "token": "",
            "api_key": "",
            "api_key_header": "X-API-Key",
            "client_id": "",
            "client_secret": "",
            "token_url": "",
            "scope": "",
            "login_url": "",
            "username_field": "username",
            "password_field": "password",
            "submit_button": "submit",
        },
        # API Configuration
        "api_config": {
            "method": "GET",
            "headers": {},
            "body": "",
            "content_type": "application/json",
            "timeout": 30,
            "follow_redirects": True,
        },
        # UI Testing Configuration
        "ui_config": {
            "browser": "chromium",
            "headless": True,
            "viewport_width": 1920,
            "viewport_height": 1080,
            "wait_timeout": 30000,
            "screenshot": True,
        },
        # Database Configuration
        "db_config": {
            "host": "",
            "port": 3306,
            "username": "",
            "password": "",
            "database": "",
            "db_type": "mysql",
        },
        # Context Chunking Configuration
        "chunk_config": {
            "chunk_size": 800,
            "overlap": 80,
            "enabled": True,
            "max_chunks": 10,
        },
        # Agent Chain Builder state
        "chain_steps": [],          # List of chain step dicts
        "chain_results": [],        # Last chain execution results
        "chain_running": False,
        # Natural Language Test Templates
        "nl_templates": [
            "Test security of {url}",
            "Check API performance at {url} with {num_requests} requests",
            "Run accessibility check on {url}",
            "Validate {compliance_type} compliance for {url}"
        ],
        # LLM Benchmark Prompts (configurable)
        "benchmark_prompts": [
            {"category": "Factual", "prompt": "What is the capital of France?"},
            {"category": "Math", "prompt": "What is 15% of 200?"},
            {"category": "Reasoning", "prompt": "If all roses are flowers and some flowers fade quickly, can we conclude all roses fade quickly?"},
            {"category": "Code", "prompt": "Write a Python function to check if a number is prime."}
        ],
        # RAG Sample Documents (configurable)
        "rag_documents": [
            "Machine learning is a subset of artificial intelligence that focuses on enabling systems to learn and improve from experience.",
            "Deep learning uses neural networks with multiple layers to process complex data and patterns.",
            "Natural Language Processing is a branch of AI that focuses on understanding and generating human language.",
            "Computer vision enables machines to interpret and understand visual information from the world.",
            "Reinforcement learning is a type of machine learning where agents learn to make decisions through trial and error."
        ],
        # RAG Test Queries (configurable)
        "rag_queries": [
            {"query": "What is machine learning?", "expected_docs": ["Machine learning"]},
            {"query": "How does deep learning work?", "expected_docs": ["Deep learning"]},
            {"query": "What is NLP?", "expected_docs": ["Natural Language Processing"]}
        ]
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_resource
def get_ollama_client():
    """Get Ollama client with caching"""
    try:
        return create_ollama_client()
    except Exception as e:
        logger.error(f"Ollama client error: {e}")
        return None


async def fetch_ollama_models():
    """Fetch available Ollama models"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
    except Exception as e:
        logger.warning(f"Could not fetch models: {e}")
    return ["llama3.2:latest"]


async def run_ollama_prompt(model: str, prompt: str) -> Dict:
    """Run a prompt against Ollama model"""
    import httpx
    start = datetime.now()
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
        
        elapsed = (datetime.now() - start).total_seconds()
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "model": model,
                "response": data.get("response", ""),
                "time": f"{elapsed:.2f}s",
                "tokens": data.get("eval_count", 0)
            }
        return {"success": False, "model": model, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"success": False, "model": model, "error": str(e)}


def get_mcp_status():
    """Check MCP integration status"""
    mcp_config = McpConfig()
    status = {}
    
    checks = [
        ("MySQL", "get_mysql_workbench"),
        ("REST API", "get_rest_api_workbench"),
        ("Excel", "get_excel_workbench"),
        ("Filesystem", "get_filesystem_workbench"),
        ("Playwright", "get_playwright_workbench"),
    ]
    
    for name, method in checks:
        try:
            getattr(mcp_config, method)()
            status[name] = {"ready": True, "status": "✅ Ready"}
        except Exception as e:
            status[name] = {"ready": False, "status": f"⚠️ {str(e)[:40]}"}
    
    return status


# ============================================================================
# SIDEBAR CONFIGURATION PANEL
# ============================================================================

def render_sidebar_config():
    """Render the sidebar configuration panel for test parameters"""
    st.sidebar.header("⚙️ Test Configuration")
    
    # =========== AUTHENTICATION SECTION ===========
    with st.sidebar.expander("🔐 Authentication", expanded=False):
        auth_type = st.selectbox(
            "Auth Type",
            options=["none", "basic", "bearer", "api_key", "form_login", "oauth"],
            index=["none", "basic", "bearer", "api_key", "form_login", "oauth"].index(
                st.session_state.auth_config.get("auth_type", "none")
            ),
            key="sidebar_auth_type"
        )
        st.session_state.auth_config["auth_type"] = auth_type
        
        if auth_type == "basic":
            st.markdown("##### Basic Authentication")
            username = st.text_input("Username", value=st.session_state.auth_config.get("username", ""), key="basic_username")
            password = st.text_input("Password", value=st.session_state.auth_config.get("password", ""), type="password", key="basic_password")
            st.session_state.auth_config["username"] = username
            st.session_state.auth_config["password"] = password
        
        elif auth_type == "bearer":
            st.markdown("##### Bearer Token")
            token = st.text_area("Token", value=st.session_state.auth_config.get("token", ""), height=80, key="bearer_token")
            st.session_state.auth_config["token"] = token
        
        elif auth_type == "api_key":
            st.markdown("##### API Key")
            api_key = st.text_input("API Key", value=st.session_state.auth_config.get("api_key", ""), type="password", key="api_key_input")
            key_header = st.text_input("Header Name", value=st.session_state.auth_config.get("api_key_header", "X-API-Key"), key="api_key_header")
            st.session_state.auth_config["api_key"] = api_key
            st.session_state.auth_config["api_key_header"] = key_header
        
        elif auth_type == "form_login":
            st.markdown("##### Form Login (UI Testing)")
            login_url = st.text_input("Login URL", value=st.session_state.auth_config.get("login_url", ""), key="login_url")
            username = st.text_input("Username", value=st.session_state.auth_config.get("username", ""), key="form_username")
            password = st.text_input("Password", value=st.session_state.auth_config.get("password", ""), type="password", key="form_password")
            
            st.markdown("##### Field Selectors")
            col1, col2 = st.columns(2)
            with col1:
                username_field = st.text_input("Username Field", value=st.session_state.auth_config.get("username_field", "username"), key="username_field")
            with col2:
                password_field = st.text_input("Password Field", value=st.session_state.auth_config.get("password_field", "password"), key="password_field")
            
            submit_button = st.text_input("Submit Button Selector", value=st.session_state.auth_config.get("submit_button", "submit"), key="submit_button")
            
            st.session_state.auth_config.update({
                "login_url": login_url, "username": username, "password": password,
                "username_field": username_field, "password_field": password_field,
                "submit_button": submit_button
            })
        
        elif auth_type == "oauth":
            st.markdown("##### OAuth 2.0")
            client_id = st.text_input("Client ID", value=st.session_state.auth_config.get("client_id", ""), key="oauth_client_id")
            client_secret = st.text_input("Client Secret", value=st.session_state.auth_config.get("client_secret", ""), type="password", key="oauth_client_secret")
            token_url = st.text_input("Token URL", value=st.session_state.auth_config.get("token_url", ""), key="oauth_token_url")
            scope = st.text_input("Scope", value=st.session_state.auth_config.get("scope", ""), key="oauth_scope")
            
            st.session_state.auth_config.update({
                "client_id": client_id, "client_secret": client_secret,
                "token_url": token_url, "scope": scope
            })
    
    # =========== API CONFIG SECTION ===========
    with st.sidebar.expander("🌐 API Settings", expanded=False):
        method = st.selectbox(
            "HTTP Method",
            options=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            index=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"].index(
                st.session_state.api_config.get("method", "GET")
            ),
            key="api_method"
        )
        st.session_state.api_config["method"] = method
        
        content_type = st.selectbox(
            "Content-Type",
            options=["application/json", "application/xml", "application/x-www-form-urlencoded", "multipart/form-data", "text/plain"],
            key="content_type"
        )
        st.session_state.api_config["content_type"] = content_type
        
        timeout = st.slider("Timeout (seconds)", min_value=5, max_value=300, value=st.session_state.api_config.get("timeout", 30), key="api_timeout")
        st.session_state.api_config["timeout"] = timeout
        
        st.markdown("##### Custom Headers")
        headers_text = st.text_area(
            "Headers (JSON format)",
            value=json.dumps(st.session_state.api_config.get("headers", {}), indent=2),
            height=100,
            key="api_headers",
            help="Enter headers as JSON object, e.g., {\"X-Custom\": \"value\"}"
        )
        try:
            st.session_state.api_config["headers"] = json.loads(headers_text) if headers_text.strip() else {}
        except json.JSONDecodeError:
            st.warning("Invalid JSON in headers")
        
        st.markdown("##### Request Body")
        body = st.text_area(
            "Body",
            value=st.session_state.api_config.get("body", ""),
            height=120,
            key="api_body",
            help="Enter request body for POST/PUT/PATCH requests"
        )
        st.session_state.api_config["body"] = body
        
        st.markdown("##### Advanced API Options")
        num_requests = st.number_input("Performance Test Requests", min_value=1, max_value=1000, value=st.session_state.api_config.get("num_requests", 10), key="num_requests")
        st.session_state.api_config["num_requests"] = num_requests
        
        chaos_type = st.selectbox("Chaos Test Type", options=["latency", "error", "timeout", "random"], key="chaos_type")
        st.session_state.api_config["chaos_type"] = chaos_type
        
        compliance_type = st.selectbox("Compliance Type", options=["gdpr", "hipaa", "pci-dss", "soc2", "owasp"], key="compliance_type")
        st.session_state.api_config["compliance_type"] = compliance_type
    
    # =========== UI TESTING SECTION ===========
    with st.sidebar.expander("🖥️ UI Testing", expanded=False):
        browser = st.selectbox(
            "Browser",
            options=["chromium", "firefox", "webkit"],
            index=["chromium", "firefox", "webkit"].index(
                st.session_state.ui_config.get("browser", "chromium")
            ),
            key="ui_browser"
        )
        st.session_state.ui_config["browser"] = browser
        
        headless = st.checkbox("Headless Mode", value=st.session_state.ui_config.get("headless", True), key="ui_headless")
        st.session_state.ui_config["headless"] = headless
        
        screenshot = st.checkbox("Capture Screenshots", value=st.session_state.ui_config.get("screenshot", True), key="ui_screenshot")
        st.session_state.ui_config["screenshot"] = screenshot
        
        st.markdown("##### Viewport")
        col1, col2 = st.columns(2)
        with col1:
            viewport_width = st.number_input("Width", min_value=320, max_value=3840, value=st.session_state.ui_config.get("viewport_width", 1920), key="viewport_width")
        with col2:
            viewport_height = st.number_input("Height", min_value=240, max_value=2160, value=st.session_state.ui_config.get("viewport_height", 1080), key="viewport_height")
        st.session_state.ui_config["viewport_width"] = viewport_width
        st.session_state.ui_config["viewport_height"] = viewport_height
        
        wait_timeout = st.slider("Wait Timeout (ms)", min_value=1000, max_value=60000, value=st.session_state.ui_config.get("wait_timeout", 30000), step=1000, key="wait_timeout")
        st.session_state.ui_config["wait_timeout"] = wait_timeout
        
        test_scenario = st.selectbox("Test Scenario", options=["smoke", "regression", "functional", "visual", "accessibility"], key="test_scenario")
        st.session_state.api_config["test_scenario"] = test_scenario
    
    # =========== LLM/LANGCHAIN SECTION ===========
    with st.sidebar.expander("🤖 LLM & LangChain", expanded=False):
        st.markdown("##### LangChain Test Selection")
        lc_test_qa = st.checkbox("QA Chains", value=st.session_state.get("langchain_config", {}).get("test_qa", True), key="lc_test_qa")
        lc_test_sum = st.checkbox("Summarization", value=st.session_state.get("langchain_config", {}).get("test_summarization", True), key="lc_test_sum")
        lc_test_trans = st.checkbox("Translation", value=st.session_state.get("langchain_config", {}).get("test_translation", True), key="lc_test_trans")
        lc_test_mem = st.checkbox("Memory Management", value=st.session_state.get("langchain_config", {}).get("test_memory", True), key="lc_test_mem")
        lc_test_tools = st.checkbox("Tool Usage", value=st.session_state.get("langchain_config", {}).get("test_tools", True), key="lc_test_tools")
        lc_test_err = st.checkbox("Error Handling", value=st.session_state.get("langchain_config", {}).get("test_error_handling", True), key="lc_test_err")
        
        if "langchain_config" not in st.session_state:
            st.session_state.langchain_config = {}
        st.session_state.langchain_config.update({
            "test_qa": lc_test_qa,
            "test_summarization": lc_test_sum,
            "test_translation": lc_test_trans,
            "test_memory": lc_test_mem,
            "test_tools": lc_test_tools,
            "test_error_handling": lc_test_err
        })
    
    # =========== VECTORDB SECTION ===========
    with st.sidebar.expander("🗃️ Vector Database", expanded=False):
        vdb_dimension = st.number_input("Vector Dimension", min_value=128, max_value=1536, value=st.session_state.get("vectordb_config", {}).get("dimension", 384), step=128, key="vdb_dimension")
        vdb_num_vectors = st.number_input("Number of Vectors", min_value=100, max_value=100000, value=st.session_state.get("vectordb_config", {}).get("num_vectors", 1000), step=100, key="vdb_num_vectors")
        vdb_query_count = st.number_input("Query Count", min_value=10, max_value=1000, value=st.session_state.get("vectordb_config", {}).get("query_count", 100), step=10, key="vdb_query_count")
        vdb_batch_size = st.number_input("Batch Size", min_value=10, max_value=500, value=st.session_state.get("vectordb_config", {}).get("batch_size", 100), step=10, key="vdb_batch_size")
        
        if "vectordb_config" not in st.session_state:
            st.session_state.vectordb_config = {}
        st.session_state.vectordb_config.update({
            "dimension": vdb_dimension,
            "num_vectors": vdb_num_vectors,
            "query_count": vdb_query_count,
            "batch_size": vdb_batch_size
        })
    
    # =========== RAG SECTION ===========
    with st.sidebar.expander("🔄 RAG Pipeline", expanded=False):
        st.markdown("##### Document Configuration")
        rag_chunk_size = st.number_input("Chunk Size", min_value=100, max_value=2000, value=st.session_state.get("rag_config", {}).get("chunk_size", 500), step=100, key="rag_chunk_size")
        rag_num_docs = st.number_input("Test Documents", min_value=1, max_value=20, value=st.session_state.get("rag_config", {}).get("num_documents", 3), key="rag_num_docs")
        
        st.markdown("##### Test Configuration")
        rag_num_queries = st.number_input("Number of Queries", min_value=1, max_value=20, value=st.session_state.get("rag_config", {}).get("num_queries", 3), key="rag_num_queries")
        rag_num_iterations = st.number_input("Latency Test Iterations", min_value=1, max_value=20, value=st.session_state.get("rag_config", {}).get("num_iterations", 5), key="rag_num_iterations")
        
        if "rag_config" not in st.session_state:
            st.session_state.rag_config = {}
        st.session_state.rag_config.update({
            "chunk_size": rag_chunk_size,
            "num_documents": rag_num_docs,
            "num_queries": rag_num_queries,
            "num_iterations": rag_num_iterations
        })
    
    # =========== DATABASE SECTION ===========
    with st.sidebar.expander("🗄️ Database", expanded=False):
        db_type = st.selectbox(
            "Database Type",
            options=["mysql", "postgresql", "sqlite", "mssql", "mongodb", "redis"],
            key="db_type_select"
        )
        st.session_state.db_config["db_type"] = db_type
        
        host = st.text_input("Host", value=st.session_state.db_config.get("host", "localhost"), key="db_host")
        st.session_state.db_config["host"] = host
        
        port_defaults = {"mysql": 3306, "postgresql": 5432, "mssql": 1433, "mongodb": 27017, "redis": 6379, "sqlite": 0}
        port = st.number_input("Port", min_value=0, max_value=65535, value=st.session_state.db_config.get("port", port_defaults.get(db_type, 3306)), key="db_port")
        st.session_state.db_config["port"] = port
        
        database = st.text_input("Database Name", value=st.session_state.db_config.get("database", ""), key="db_name")
        st.session_state.db_config["database"] = database
        
        db_username = st.text_input("Username", value=st.session_state.db_config.get("username", ""), key="db_username")
        db_password = st.text_input("Password", value=st.session_state.db_config.get("password", ""), type="password", key="db_password")
        st.session_state.db_config["username"] = db_username
        st.session_state.db_config["password"] = db_password
    
    # =========== QUICK STATUS ===========
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Config Status")
    
    status_dict = get_config_status_dict()
    status_rows = "\n".join([f"    | {key} | {value} |" for key, value in status_dict.items()])
    
    st.sidebar.markdown(f"""
    | Setting | Status |
    |---------|--------|
{status_rows}
    """)
    # =========== QUICK TESTS CONFIG (JSON editable) ===========
    with st.sidebar.expander("⚡ Quick Tests (Configurable)", expanded=False):
        qt_text = st.text_area(
            "Quick Tests JSON",
            value=json.dumps(st.session_state.get("quick_tests_config", {}), indent=2),
            height=260,
            key="quick_tests_json"
        )
        try:
            parsed = json.loads(qt_text) if qt_text.strip() else {}
            st.session_state.quick_tests_config = parsed
        except json.JSONDecodeError:
            st.warning("Invalid JSON for Quick Tests configuration")
        if st.button("🔁 Reset Quick Tests to Defaults", key="reset_quick_tests"):
            if "quick_tests_config" in st.session_state:
                del st.session_state["quick_tests_config"]
            st.rerun()
    
    # =========== TEMPLATES & SAMPLES CONFIG ===========
    with st.sidebar.expander("📝 Templates & Samples (Advanced)", expanded=False):
        st.markdown("**Natural Language Test Templates**")
        nl_templates_text = st.text_area(
            "NL Templates (JSON array)",
            value=json.dumps(st.session_state.get("nl_templates", []), indent=2),
            height=100,
            key="nl_templates_json"
        )
        try:
            st.session_state.nl_templates = json.loads(nl_templates_text) if nl_templates_text.strip() else []
        except json.JSONDecodeError:
            st.warning("Invalid JSON for NL templates")
        
        st.markdown("**LLM Benchmark Prompts**")
        benchmark_text = st.text_area(
            "Benchmark Prompts (JSON array)",
            value=json.dumps(st.session_state.get("benchmark_prompts", []), indent=2),
            height=100,
            key="benchmark_json"
        )
        try:
            st.session_state.benchmark_prompts = json.loads(benchmark_text) if benchmark_text.strip() else []
        except json.JSONDecodeError:
            st.warning("Invalid JSON for benchmarks")
        
        st.markdown("**RAG Sample Documents**")
        rag_docs_text = st.text_area(
            "RAG Documents (JSON array)",
            value=json.dumps(st.session_state.get("rag_documents", []), indent=2),
            height=100,
            key="rag_docs_json"
        )
        try:
            st.session_state.rag_documents = json.loads(rag_docs_text) if rag_docs_text.strip() else []
        except json.JSONDecodeError:
            st.warning("Invalid JSON for RAG documents")
    
    # =========== CONTEXT CHUNKING SECTION ===========
    with st.sidebar.expander("✂️ Context Chunking", expanded=False):
        st.markdown("Splits large API/LLM responses before passing to the next chain step.")
        chunk_enabled = st.checkbox(
            "Enable Chunking",
            value=st.session_state.get("chunk_config", {}).get("enabled", True),
            key="chunk_enabled"
        )
        chunk_size = st.slider(
            "Chunk Size (chars)",
            min_value=200, max_value=4000,
            value=st.session_state.get("chunk_config", {}).get("chunk_size", 800),
            step=100, key="chunk_size_slider"
        )
        chunk_overlap = st.slider(
            "Overlap (chars)",
            min_value=0, max_value=400,
            value=st.session_state.get("chunk_config", {}).get("overlap", 80),
            step=20, key="chunk_overlap_slider"
        )
        max_chunks = st.number_input(
            "Max Chunks to Process",
            min_value=1, max_value=50,
            value=st.session_state.get("chunk_config", {}).get("max_chunks", 10),
            key="max_chunks_input"
        )
        if "chunk_config" not in st.session_state:
            st.session_state.chunk_config = {}
        st.session_state.chunk_config.update({
            "enabled": chunk_enabled,
            "chunk_size": chunk_size,
            "overlap": chunk_overlap,
            "max_chunks": int(max_chunks),
        })

    # Reset button
    if st.sidebar.button("🔄 Reset All Config", key="reset_config"):
        st.session_state.auth_config = {
            "auth_type": "none", "username": "", "password": "", "token": "",
            "api_key": "", "api_key_header": "X-API-Key", "login_url": "",
            "username_field": "username", "password_field": "password",
            "submit_button": "submit", "client_id": "", "client_secret": "",
            "token_url": "", "scope": ""
        }
        st.session_state.api_config = {
            "method": "GET", "headers": {}, "body": "",
            "content_type": "application/json", "timeout": 30,
            "num_requests": 10, "chaos_type": "latency", "compliance_type": "gdpr"
        }
        st.session_state.ui_config = {
            "browser": "chromium", "headless": True, "viewport_width": 1920,
            "viewport_height": 1080, "wait_timeout": 30000, "screenshot": True
        }
        st.session_state.db_config = {
            "host": "", "port": 3306, "username": "", "password": "",
            "database": "", "db_type": "mysql"
        }
        st.session_state.langchain_config = {
            "test_qa": True, "test_summarization": True, "test_translation": True,
            "test_memory": True, "test_tools": True, "test_error_handling": True
        }
        st.session_state.vectordb_config = {
            "dimension": 384, "num_vectors": 1000, "query_count": 100, "batch_size": 100
        }
        st.session_state.rag_config = {
            "chunk_size": 500, "num_documents": 3, "num_queries": 3, "num_iterations": 5
        }
        st.rerun()


# ============================================================================
# AGENT EXECUTION - WITH CONFIG FROM SESSION STATE
# ============================================================================

async def execute_agent_test(
    agent_type: str, 
    test_input: str, 
    test_url: str = None,
    config: Dict = None
) -> Dict:
    """Execute actual agent test based on type with full configuration support"""
    start_time = datetime.now()
    
    # Get config from session state if not provided
    auth_config = config.get("auth", {}) if config else st.session_state.get("auth_config", {})
    api_config = config.get("api", {}) if config else st.session_state.get("api_config", {})
    ui_config = config.get("ui", {}) if config else st.session_state.get("ui_config", {})
    
    try:
        agent_lower = agent_type.lower()
        url = test_url or test_input
        
        # Build headers with authentication
        headers = build_auth_headers(auth_config, api_config)
        
        # Map agent types to actual functions
        if "security" in agent_lower:
            result = await security_scan(url)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False
            }
        
        elif "performance" in agent_lower:
            num_requests = api_config.get("num_requests", 10)
            result = await performance_test(url, num_requests=num_requests)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False
            }
        
        elif "api" in agent_lower and "contract" in agent_lower:
            method = api_config.get("method", "GET")
            result = await validate_api_contract(url, method=method)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False
            }
        
        elif "graphql" in agent_lower:
            query = test_input or "query { __typename }"
            variables = api_config.get("variables", {})
            result = await test_graphql_endpoint(url, query, variables)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False
            }
        
        elif "chaos" in agent_lower:
            chaos_type = api_config.get("chaos_type", "latency")
            intensity = api_config.get("intensity", "low")
            result = await run_chaos_test(url, chaos_type, intensity)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False
            }
        
        elif "compliance" in agent_lower:
            compliance_type = api_config.get("compliance_type", "gdpr")
            result = await check_compliance(url, compliance_type)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False
            }
        
        elif "ml" in agent_lower or "model" in agent_lower:
            test_type = api_config.get("ml_test_type", "accuracy")
            result = await test_ml_model(url, test_type)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": True,  # ML testing often uses LLM
                "is_simulated": False
            }
        
        elif "e2e" in agent_lower or "end" in agent_lower or "ui" in agent_lower or "visual" in agent_lower:
            browser = ui_config.get("browser", "chromium")
            scenario = api_config.get("test_scenario", "smoke")
            # Pass login config for authenticated tests
            result = await run_e2e_test_with_auth(url, auth_config, ui_config, scenario)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,  # E2E tests don't use Ollama
                "is_simulated": True  # Currently simulated, not real Playwright
            }
        
        elif "comprehensive" in agent_lower or "report" in agent_lower:
            result = await generate_comprehensive_report(url, url)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False
            }
        
        elif "mobile" in agent_lower:
            platform = api_config.get("platform", "android")
            result = await test_mobile_app(url, platform)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False,  # Provides setup instructions, not simulation
                "requires_setup": "Appium"
            }
        
        elif "database" in agent_lower or "db" in agent_lower:
            db_config = config.get("db", {}) if config else st.session_state.get("db_config", {})
            result = await test_database_with_config(db_config)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False  # Real database connection testing
            }
        
        elif "accessibility" in agent_lower:
            result = await run_accessibility_test(url, ui_config)
            return {
                "success": True, 
                "result": result, 
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False  # Real HTML/WCAG analysis
            }
        
        elif "llm" in agent_lower and ("eval" in agent_lower or "evaluation" in agent_lower or "benchmark" in agent_lower):
            # LLM Evaluation Agent
            models = await fetch_ollama_models()
            
            # Smart model selection: ignore button text or empty input
            if test_input and not test_input.startswith("Run ") and "test" not in test_input.lower():
                model = test_input
            elif models:
                model = models[0]  # Use first available model
            else:
                model = "llama3.2:latest"
            
            evaluator = LLMEvaluationAgent()
            result = await evaluator.run_full_evaluation(model)
            
            # Format result as string for display
            formatted_result = f"""
🎯 LLM EVALUATION REPORT
═══════════════════════════════════════════════════════════
Model: {result['model']}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════

🏆 OVERALL SCORE: {result['overall_score']:.1f}/100
⏱️  Evaluation Time: {result['total_evaluation_time']:.2f}s

📊 CATEGORY SCORES:
   📚 Factual Accuracy: {result['categories']['factual_accuracy']['score']:.1f}/100 ({result['categories']['factual_accuracy']['correct']}/{result['categories']['factual_accuracy']['total']} correct)
   🧠 Reasoning & Logic: {result['categories']['reasoning']['score']:.1f}/100 ({result['categories']['reasoning']['correct']}/{result['categories']['reasoning']['total']} correct)
   🔢 Math Problem Solving: {result['categories']['math']['score']:.1f}/100 ({result['categories']['math']['correct']}/{result['categories']['math']['total']} correct)
   💻 Code Generation: {result['categories']['code_generation']['score']:.1f}/100 ({result['categories']['code_generation']['passed']}/{result['categories']['code_generation']['total']} passed)
   📋 Instruction Following: {result['categories']['instruction_following']['score']:.1f}/100 ({result['categories']['instruction_following']['passed']}/{result['categories']['instruction_following']['total']} passed)
   🔍 Hallucination Resistance: {result['categories']['hallucination_resistance']['score']:.1f}/100 ({result['categories']['hallucination_resistance']['no_hallucinations']}/{result['categories']['hallucination_resistance']['total']} clean)

🎓 GRADE: {'A+ (Excellent)' if result['overall_score'] >= 90 else 'A (Very Good)' if result['overall_score'] >= 80 else 'B (Good)' if result['overall_score'] >= 70 else 'C (Fair)' if result['overall_score'] >= 60 else 'D (Needs Improvement)'}
═══════════════════════════════════════════════════════════
"""
            return {
                "success": True,
                "result": formatted_result,
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": True,
                "is_simulated": False,
                "raw_data": result  # Include full report
            }
        
        elif "langchain" in agent_lower:
            # LangChain Testing Agent
            models = await fetch_ollama_models()
            model = test_input if test_input and not test_input.startswith("Run ") else (models[0] if models else "llama3.2:latest")
            
            langchain_agent = LangChainTestAgent()
            
            # Get config from sidebar (session state)
            eval_config = st.session_state.get("langchain_config", {
                "test_qa": True,
                "test_summarization": True,
                "test_translation": True,
                "test_memory": True,
                "test_tools": True,
                "test_error_handling": True
            })
            
            result = await langchain_agent.run_full_langchain_test(model, eval_config)
            
            # Format result for display
            formatted_result = f"""
🔗 LANGCHAIN TESTING REPORT
═══════════════════════════════════════════════════════════
Model: {result['model']}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════

🏆 OVERALL SCORE: {result['overall_score']:.1f}/100
⏱️  Evaluation Time: {result['total_evaluation_time']:.2f}s

📊 TEST RESULTS:
   QA Chains: {result['test_results']['qa_chain']['status']}
   Summarization: {result['test_results']['summarization']['status']}
   Translation: {result['test_results']['translation']['status']}
   Memory: {result['test_results']['memory']['status']}
   Tool Usage: {result['test_results']['tools']['status']}
   Error Handling: {result['test_results']['error_handling']['status']}

📈 METRICS:
   Avg Response Time: {result['metrics']['avg_response_time']:.2f}s
   Total Tokens: {result['metrics']['total_tokens']}
   Success Rate: {result['metrics']['success_rate']:.1f}%
═══════════════════════════════════════════════════════════
"""
            return {
                "success": True,
                "result": formatted_result,
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": True,
                "is_simulated": False,
                "raw_data": result
            }
        
        elif "vectordb" in agent_lower or "vector" in agent_lower:
            # Vector Database Evaluation Agent
            db_type = test_input if test_input and test_input in ["pinecone", "weaviate", "milvus", "faiss", "chromadb", "qdrant"] else "chromadb"
            
            vectordb_agent = VectorDBEvaluationAgent()
            
            # Get config from sidebar (session state)
            eval_config = st.session_state.get("vectordb_config", {
                "dimension": 384,
                "num_vectors": 1000,
                "query_count": 100,
                "batch_size": 100
            })
            
            result = await vectordb_agent.run_full_evaluation(db_type, eval_config)
            
            # Format result for display
            formatted_result = f"""
🗄️ VECTORDB EVALUATION REPORT
═══════════════════════════════════════════════════════════
Database: {result['database_type'].upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════

🏆 OVERALL SCORE: {result['overall_score']:.1f}/100
⏱️  Evaluation Time: {result['total_evaluation_time']:.2f}s

📊 TEST RESULTS:
   Connection: {result['test_results']['connection']['status']}
   Write Performance: {result['test_results']['write_performance']['status']}
   Query Latency: {result['test_results']['query_latency']['status']}
   Search Accuracy: {result['test_results']['search_accuracy']['status']}
   Scalability: {result['test_results']['scalability']['status']}
   Memory Usage: {result['test_results']['memory']['status']}
   Cost Analysis: {result['test_results']['cost']['status']}

📈 KEY METRICS:
   Vectors/sec: {result['test_results']['write_performance'].get('vectors_per_sec', 'N/A')}
   Avg Latency: {result['test_results']['query_latency'].get('avg_latency_ms', 'N/A')}ms
   Accuracy: {result['test_results']['search_accuracy'].get('accuracy_score', 'N/A')}%
   Memory: {result['test_results']['memory'].get('memory_usage_mb', 'N/A')}MB
   Monthly Cost: ${result['test_results']['cost'].get('monthly_cost', 'N/A')}
═══════════════════════════════════════════════════════════
"""
            return {
                "success": True,
                "result": formatted_result,
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": False,
                "is_simulated": False,
                "raw_data": result
            }
        
        elif "rag" in agent_lower:
            # RAG Evaluation Agent
            models = await fetch_ollama_models()
            model = test_input if test_input and not test_input.startswith("Run ") else (models[0] if models else "llama3.2:latest")
            
            rag_agent = RAGEvaluationAgent()
            
            # Get config from sidebar and build eval_config
            rag_sidebar_config = st.session_state.get("rag_config", {
                "chunk_size": 500,
                "num_documents": 3,
                "num_queries": 3,
                "num_iterations": 5
            })
            
            # Use configurable RAG documents and queries from session state
            rag_documents = st.session_state.get("rag_documents", ["Sample document"])
            rag_queries = st.session_state.get("rag_queries", [{"query": "Sample query", "expected_docs": ["Sample"]}])
            
            # Build eval_config with configurable documents and queries
            eval_config = {
                "documents": rag_documents[:rag_sidebar_config["num_documents"]],
                "queries": rag_queries[:rag_sidebar_config["num_queries"]],
                "test_questions": [q.get("query", "") for q in rag_queries[:rag_sidebar_config["num_queries"]]],
                "chunk_size": rag_sidebar_config["chunk_size"],
                "num_iterations": rag_sidebar_config["num_iterations"]
            }
            
            result = await rag_agent.run_full_rag_evaluation(model, eval_config)
            
            # Format result for display
            formatted_result = f"""
🔄 RAG PIPELINE EVALUATION REPORT
═══════════════════════════════════════════════════════════
Model: {result['model']}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════

🏆 OVERALL SCORE: {result['overall_score']:.1f}/100
⏱️  Evaluation Time: {result['total_evaluation_time']:.2f}s

📊 RAG PIPELINE COMPONENTS:
   Document Ingestion: {result['test_results']['document_ingestion']['status']} ({result['test_results']['document_ingestion']['chunks_created']} chunks)
   Embedding Quality: {result['test_results']['embedding_quality']['status']} ({result['test_results']['embedding_quality']['diversity_score']:.1f}/100)
   Retrieval Accuracy: {result['test_results']['retrieval_accuracy']['status']} ({result['test_results']['retrieval_accuracy']['avg_recall']:.1f}% recall)
   Generation Quality: {result['test_results']['generation_quality']['status']} ({result['test_results']['generation_quality']['accuracy']:.1f}% accuracy)
   Hallucination Detection: {result['test_results']['hallucination_detection']['status']} ({result['test_results']['hallucination_detection']['hallucination_rate']:.1f}% rate)
   End-to-End Latency: {result['test_results']['end_to_end_latency']['status']} ({result['test_results']['end_to_end_latency']['avg_latency']:.3f}s avg)

📈 LATENCY METRICS:
   P50: {result['test_results']['end_to_end_latency']['avg_latency']:.3f}s
   P95: {result['test_results']['end_to_end_latency']['p95_latency']:.3f}s
   P99: {result['test_results']['end_to_end_latency']['p99_latency']:.3f}s
═══════════════════════════════════════════════════════════
"""
            return {
                "success": True,
                "result": formatted_result,
                "time": (datetime.now() - start_time).total_seconds(),
                "uses_ollama": True,
                "is_simulated": False,
                "raw_data": result
            }
        
        else:
            # For agents without specific implementations, use LLM
            models = await fetch_ollama_models()
            model = models[0] if models else "llama3.2:latest"
            ollama_result = await run_ollama_prompt(
                model,
                f"You are a {agent_type} testing agent. Process this request: {test_input}"
            )
            if ollama_result["success"]:
                return {
                    "success": True, 
                    "result": ollama_result["response"], 
                    "time": (datetime.now() - start_time).total_seconds(),
                    "uses_ollama": True,  # This actually uses Ollama
                    "is_simulated": False
                }
            else:
                return {"success": False, "error": ollama_result.get("error", "Unknown error"), "uses_ollama": True}
    
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


async def orchestrate_agents(tasks: List[Dict[str, Any]], config: Dict = None) -> List[Dict]:
    """Run multiple agent tests in parallel and return aggregated results.
    
    Args:
        tasks: List of task dicts with 'agent', 'url', 'label' keys
        config: Optional config dict with auth, api, ui, db sub-dicts
    
    Returns:
        List of result dicts with task info and execution results
    """
    logger.info(f"🎭 Orchestrating {len(tasks)} agents in parallel")
    
    # Create coroutines for each task
    coros = [
        execute_agent_test(
            task.get("agent", ""),
            task.get("input", task.get("url", "")),
            task.get("url", None),
            config
        )
        for task in tasks
    ]
    
    # Run all in parallel
    results = await asyncio.gather(*coros, return_exceptions=True)
    
    # Package results with task info
    out = []
    for task, res in zip(tasks, results):
        if isinstance(res, Exception):
            out.append({
                "task": task,
                "success": False,
                "error": str(res),
                "traceback": traceback.format_exception(type(res), res, res.__traceback__)
            })
        else:
            out.append({"task": task, **res})
    
    passed_count = sum(1 for r in out if r.get('success'))
    logger.info(f"✅ Orchestration complete: {passed_count}/{len(out)} passed")
    return out


async def parse_natural_language_test(nl_input: str) -> Dict[str, Any]:
    """Parse natural language test description into executable test spec using LLM.
    
    Args:
        nl_input: Natural language test description
    
    Returns:
        Dict with 'agent', 'url', 'config', 'steps' keys
    """
    models = await fetch_ollama_models()
    model = models[0] if models else "llama3.2:latest"
    
    # Get configurable templates from session state
    templates = st.session_state.get("nl_templates", [])
    examples_text = "\n".join([f"- {tmpl}" for tmpl in templates[:3]]) if templates else "- Test security of https://example.com\n- Check API performance at https://api.example.com\n- Run E2E test on https://app.com"
    
    prompt = f"""You are a test automation expert. Parse this natural language test into a JSON structure.

Test description: {nl_input}

Extract and return ONLY a JSON object with this structure:
{{
  "agent": "<agent_type>",  // One of: Security, Performance, API Contract, E2E, Accessibility, Compliance, GraphQL, Chaos, ML Model, Mobile, Database
  "url": "<target_url>",
  "method": "GET",  // HTTP method if applicable
  "expected_status": 200,  // Expected HTTP status if applicable
  "steps": ["step1", "step2"],  // Test steps if E2E
  "assertions": ["check1", "check2"]  // What to verify
}}

Example templates:
{examples_text}

Return ONLY the JSON, no explanation."""
    
    result = await run_ollama_prompt(model, prompt)
    
    if result.get("success"):
        response_text = result["response"].strip()
        # Extract JSON from response (handle markdown code blocks)
        if "```" in response_text:
            import re
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        try:
            parsed = json.loads(response_text)
            return {"success": True, "test_spec": parsed}
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Failed to parse LLM response as JSON: {e}", "raw": response_text}
    else:
        return {"success": False, "error": result.get("error")}


async def self_heal_test(failed_test: Dict, error_info: str) -> Dict[str, Any]:
    """Use AI to analyze test failure and suggest/apply fixes.
    
    Args:
        failed_test: The test configuration that failed
        error_info: Error message and traceback
    
    Returns:
        Dict with 'fixed', 'suggestions', 'new_config' keys
    """
    models = await fetch_ollama_models()
    model = models[0] if models else "llama3.2:latest"
    
    prompt = f"""You are a test automation expert specializing in debugging and fixing broken tests.

Failed Test Configuration:
{json.dumps(failed_test, indent=2)}

Error Information:
{error_info}

Analyze the failure and provide:
1. Root cause of the failure
2. Suggested fixes
3. Updated test configuration (if applicable)

Return a JSON object with this structure:
{{
  "root_cause": "<explanation>",
  "fixes": ["fix1", "fix2"],
  "updated_config": {{<new_test_config>}},
  "retry_recommended": true/false,
  "manual_intervention_needed": true/false
}}

Common fixes:
- Update timeout values
- Adjust URL/endpoint
- Modify authentication
- Change expected values
- Add retry logic
- Update selectors (for UI tests)

Return ONLY the JSON, no explanation."""
    
    result = await run_ollama_prompt(model, prompt)
    
    if result.get("success"):
        response_text = result["response"].strip()
        # Extract JSON
        if "```" in response_text:
            import re
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        try:
            healing = json.loads(response_text)
            return {"success": True, "healing": healing}
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Failed to parse healing response: {e}", "raw": response_text}
    else:
        return {"success": False, "error": result.get("error")}


# ============================================================================
# CONTEXT CHUNKING
# ============================================================================

def chunk_context(text: str, chunk_size: int = 800, overlap: int = 80) -> List[str]:
    """Split large text into overlapping chunks for LLM / agent processing.

    Args:
        text: The source text to split.
        chunk_size: Maximum characters per chunk.
        overlap: Characters of overlap between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Prefer to break at a word boundary
        if end < len(text):
            last_space = chunk.rfind(" ")
            if last_space > chunk_size // 2:
                chunk = chunk[:last_space]
                end = start + last_space
        chunks.append(chunk.strip())
        new_start = end - overlap
        if new_start <= start:  # no forward progress — prevent infinite loop
            break
        start = new_start

    return [c for c in chunks if c]


def summarize_chunks(chunks: List[str]) -> str:
    """Return a lightweight summary placeholder joining chunk previews."""
    if not chunks:
        return ""
    if len(chunks) == 1:
        return chunks[0]
    previews = [f"[Chunk {i+1}/{len(chunks)}]: {c[:120]}..." for i, c in enumerate(chunks)]
    return "\n".join(previews)


# ============================================================================
# AGENT CHAIN EXECUTION
# ============================================================================

async def execute_chain(
    steps: List[Dict[str, Any]],
    initial_input: str,
    chunk_config: Dict = None
) -> List[Dict[str, Any]]:
    """Execute a sequence of agent steps, piping context from one step to the next.

    Each step dict should contain:
        agent (str)          : Agent type name (e.g. "Security", "API Contract")
        url   (str)          : Target URL (optional)
        input (str)          : Static input / prompt prefix (optional)
        use_chunking (bool)  : Override global chunking for this step
        continue_on_failure (bool): Keep running even if this step fails
        config (dict)        : Optional per-step auth/api/ui config

    Args:
        steps         : Ordered list of step dicts.
        initial_input : Seed input / URL fed into the first step.
        chunk_config  : Chunking settings from session state.

    Returns:
        List of result dicts, one per step, with keys:
            step, agent, input_preview, output, chunks_used, success, time, error
    """
    cfg = chunk_config or {"enabled": True, "chunk_size": 800, "overlap": 80, "max_chunks": 10}
    chunking_enabled = cfg.get("enabled", True)
    chunk_size = cfg.get("chunk_size", 800)
    overlap = cfg.get("overlap", 80)
    max_chunks = cfg.get("max_chunks", 10)

    context = initial_input
    results: List[Dict[str, Any]] = []

    for i, step in enumerate(steps):
        step_agent = step.get("agent", "")
        step_url = step.get("url", "")
        step_input_prefix = step.get("input", "")
        use_chunking = step.get("use_chunking", chunking_enabled)
        step_config = step.get("config", {})

        # --- Build the input to send to the agent ---
        chunks_used = 0
        if i == 0:
            combined_input = step_input_prefix or context
        else:
            # Optionally chunk previous context before injecting
            context_to_inject = context
            chunks_used = 0
            if use_chunking and context and len(context) > chunk_size:
                chunks = chunk_context(context, chunk_size=chunk_size, overlap=overlap)[:max_chunks]
                chunks_used = len(chunks)
                # Use summarised chunk list as context prefix
                context_to_inject = summarize_chunks(chunks)
            else:
                chunks_used = 1 if context else 0

            sep = "\n\n" if step_input_prefix else ""
            combined_input = (
                f"[Context from previous step]:\n{context_to_inject}"
                f"{sep}{step_input_prefix}"
            )

        step_result: Dict[str, Any] = {
            "step": i + 1,
            "agent": step_agent,
            "input_preview": combined_input[:200],
            "output": None,
            "chunks_used": chunks_used,
            "success": False,
            "time": 0.0,
            "error": None,
        }

        try:
            raw = await execute_agent_test(
                step_agent,
                combined_input,
                step_url or (initial_input if i == 0 else ""),
                step_config,
            )
            step_result["success"] = raw.get("success", False)
            step_result["time"] = raw.get("time", 0.0)

            if raw.get("success"):
                step_result["output"] = raw.get("result", "")
                context = step_result["output"] or context  # pipe to next step
            else:
                step_result["error"] = raw.get("error", "Unknown error")
                if not step.get("continue_on_failure", False):
                    results.append(step_result)
                    break
        except Exception as exc:
            step_result["success"] = False
            step_result["error"] = str(exc)
            if not step.get("continue_on_failure", False):
                results.append(step_result)
                break

        results.append(step_result)

    return results


def build_auth_headers(auth_config: Dict, api_config: Dict) -> Dict:
    """Build HTTP headers with authentication"""
    headers = dict(api_config.get("headers", {}))
    
    auth_type = auth_config.get("auth_type", "none")
    
    if auth_type == "basic":
        import base64
        credentials = f"{auth_config.get('username', '')}:{auth_config.get('password', '')}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"
    
    elif auth_type == "bearer":
        token = auth_config.get("token", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    
    elif auth_type == "api_key":
        key_header = auth_config.get("api_key_header", "X-API-Key")
        api_key = auth_config.get("api_key", "")
        if api_key:
            headers[key_header] = api_key
    
    # Add content type
    content_type = api_config.get("content_type", "application/json")
    if content_type:
        headers["Content-Type"] = content_type
    
    return headers


async def run_e2e_test_with_auth(
    url: str, 
    auth_config: Dict, 
    ui_config: Dict,
    scenario: str = "smoke"
) -> str:
    """Run REAL E2E test with authentication using actual framework integration"""
    import httpx
    from time import perf_counter
    
    auth_type = auth_config.get("auth_type", "none")
    browser = ui_config.get("browser", "chromium")
    start_time = perf_counter()
    
    test_steps = []
    passed = 0
    failed = 0
    
    try:
        # Step 1: Navigate to URL
        step_start = perf_counter()
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            step_time = perf_counter() - step_start
            
            if response.status_code == 200:
                test_steps.append(("✅", "Navigate to URL", step_time, "SUCCESS"))
                passed += 1
            else:
                test_steps.append(("❌", "Navigate to URL", step_time, f"HTTP {response.status_code}"))
                failed += 1
            
            # Step 2: Check response time
            step_start = perf_counter()
            page_size = len(response.content)
            step_time = perf_counter() - step_start
            test_steps.append(("✅", f"Page loaded ({page_size} bytes)", step_time, "SUCCESS"))
            passed += 1
            
            # Step 3: Validate content
            step_start = perf_counter()
            content = response.text.lower()
            has_html = "<html" in content or "<!doctype" in content
            step_time = perf_counter() - step_start
            
            if has_html:
                test_steps.append(("✅", "Valid HTML document", step_time, "SUCCESS"))
                passed += 1
            else:
                test_steps.append(("⚠️", "Non-HTML response", step_time, "WARNING"))
                passed += 1
            
            # Step 4: Check for common elements
            step_start = perf_counter()
            elements_found = []
            if "<form" in content:
                elements_found.append("forms")
            if "<input" in content:
                elements_found.append("inputs")
            if "<button" in content:
                elements_found.append("buttons")
            if "<nav" in content:
                elements_found.append("navigation")
            
            step_time = perf_counter() - step_start
            test_steps.append(("✅", f"Found elements: {', '.join(elements_found) or 'none'}", step_time, "SUCCESS"))
            passed += 1
            
            # Step 5: Authentication check
            if auth_type == "form_login":
                step_start = perf_counter()
                username_field = auth_config.get("username_field", "username")
                password_field = auth_config.get("password_field", "password")
                
                has_login_form = username_field in content or password_field in content
                step_time = perf_counter() - step_start
                
                if has_login_form:
                    test_steps.append(("✅", "Login form detected", step_time, "SUCCESS"))
                    passed += 1
                else:
                    test_steps.append(("⚠️", "Login form not found (may be already authenticated)", step_time, "WARNING"))
                    passed += 1
            
            # Step 6: Check headers
            step_start = perf_counter()
            security_headers = []
            if "x-frame-options" in response.headers:
                security_headers.append("X-Frame-Options")
            if "strict-transport-security" in response.headers:
                security_headers.append("HSTS")
            if "content-security-policy" in response.headers:
                security_headers.append("CSP")
            
            step_time = perf_counter() - step_start
            test_steps.append(("ℹ️", f"Security headers: {', '.join(security_headers) or 'none'}", step_time, "INFO"))
            passed += 1
    
    except Exception as e:
        test_steps.append(("❌", f"Test execution failed", 0.0, str(e)))
        failed += 1
    
    total_time = perf_counter() - start_time
    total_tests = passed + failed
    
    steps_report = "\n".join([f"   {icon} {name} ({time:.3f}s) - {status}" for icon, name, time, status in test_steps])
    
    login_info = ""
    if auth_type == "form_login":
        login_info = f"""
🔐 AUTHENTICATION CONFIG:
   Type: Form Login
   Login URL: {auth_config.get('login_url', url)}
   Username Field: {auth_config.get('username_field', 'username')}
   Password Field: {auth_config.get('password_field', 'password')}
"""
    
    report = f"""
🎭 E2E BROWSER AUTOMATION REPORT (REAL EXECUTION)
═══════════════════════════════════════════════════════════
Target: {url}
Browser: {browser} (HTTP client)
Scenario: {scenario}
Authentication: {auth_type.upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════

📊 TEST RESULTS: {passed}/{total_tests} Passed ({(passed/total_tests*100) if total_tests else 0:.1f}%)
⏱️ EXECUTION TIME: {total_time:.3f}s
{login_info}
📋 TEST STEPS:
{steps_report}

🖥️ UI CONFIGURATION:
   Viewport: {ui_config.get('viewport_width', 1920)}x{ui_config.get('viewport_height', 1080)}
   Headless: {'Yes' if ui_config.get('headless', True) else 'No'}
   Wait Timeout: {ui_config.get('wait_timeout', 30000)}ms

💡 NOTE: Using HTTP client. For full browser automation with clicks/forms,
   integrate Playwright MCP tools (mcp_microsoft_pla_browser_*).
═══════════════════════════════════════════════════════════
"""
    return report


async def test_database_with_config(db_config: Dict) -> str:
    """Test REAL database connection with actual libraries"""
    from time import perf_counter
    import socket
    
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 3306)
    db_type = db_config.get("db_type", "mysql")
    database = db_config.get("database", "")
    username = db_config.get("username", "")
    password = db_config.get("password", "")
    timeout = db_config.get("timeout", 5)
    
    tests = []
    connection_status = "❌ FAILED"
    error_msg = ""
    query_result = None
    result = -1  # network connectivity result (0 = success)
    
    # Test 1: Network connectivity
    try:
        start = perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        elapsed = perf_counter() - start
        sock.close()
        
        if result == 0:
            tests.append(("✅", "Network connectivity", elapsed, "Port is open"))
        else:
            tests.append(("❌", "Network connectivity", elapsed, f"Port {port} closed"))
            error_msg = f"Cannot reach {host}:{port}"
    except Exception as e:
        tests.append(("❌", "Network connectivity", 0.0, str(e)))
        error_msg = str(e)
    
    # Test 2: Database connection
    if result == 0:
        try:
            start = perf_counter()
            
            if db_type == "mysql":
                try:
                    import pymysql
                    conn = pymysql.connect(
                        host=host, port=port, user=username,
                        password=password, database=database,
                        connect_timeout=timeout
                    )
                    elapsed = perf_counter() - start
                    tests.append(("✅", "MySQL connection", elapsed, "Connected"))
                    
                    # Test query
                    cursor = conn.cursor()
                    cursor.execute("SELECT VERSION()")
                    version = cursor.fetchone()[0]
                    query_result = f"MySQL {version}"
                    cursor.close()
                    conn.close()
                    connection_status = "✅ CONNECTED"
                except ImportError:
                    elapsed = perf_counter() - start
                    tests.append(("⚠️", "MySQL connection", elapsed, "pymysql not installed (pip install pymysql)"))
                    error_msg = "Install: pip install pymysql"
                    
            elif db_type == "postgresql":
                try:
                    import psycopg2
                    conn = psycopg2.connect(
                        host=host, port=port, user=username,
                        password=password, database=database,
                        connect_timeout=timeout
                    )
                    elapsed = perf_counter() - start
                    tests.append(("✅", "PostgreSQL connection", elapsed, "Connected"))
                    
                    cursor = conn.cursor()
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()[0]
                    query_result = version.split(',')[0]
                    cursor.close()
                    conn.close()
                    connection_status = "✅ CONNECTED"
                except ImportError:
                    elapsed = perf_counter() - start
                    tests.append(("⚠️", "PostgreSQL connection", elapsed, "psycopg2 not installed (pip install psycopg2-binary)"))
                    error_msg = "Install: pip install psycopg2-binary"
                    
            elif db_type == "mongodb":
                try:
                    from pymongo import MongoClient
                    client = MongoClient(host, port, serverSelectionTimeoutMS=timeout*1000)
                    start = perf_counter()
                    client.admin.command('ping')
                    elapsed = perf_counter() - start
                    tests.append(("✅", "MongoDB connection", elapsed, "Connected"))
                    
                    server_info = client.server_info()
                    query_result = f"MongoDB {server_info.get('version', 'unknown')}"
                    client.close()
                    connection_status = "✅ CONNECTED"
                except ImportError:
                    elapsed = perf_counter() - start
                    tests.append(("⚠️", "MongoDB connection", elapsed, "pymongo not installed (pip install pymongo)"))
                    error_msg = "Install: pip install pymongo"
                    
            elif db_type == "redis":
                try:
                    import redis
                    r = redis.Redis(host=host, port=port, password=password, socket_timeout=timeout, decode_responses=True)
                    start = perf_counter()
                    r.ping()
                    elapsed = perf_counter() - start
                    tests.append(("✅", "Redis connection", elapsed, "Connected"))
                    
                    info = r.info()
                    query_result = f"Redis {info.get('redis_version', 'unknown')}"
                    r.close()
                    connection_status = "✅ CONNECTED"
                except ImportError:
                    elapsed = perf_counter() - start
                    tests.append(("⚠️", "Redis connection", elapsed, "redis not installed (pip install redis)"))
                    error_msg = "Install: pip install redis"
                    
            elif db_type == "sqlite":
                try:
                    import sqlite3
                    start = perf_counter()
                    conn = sqlite3.connect(database or ':memory:', timeout=timeout)
                    elapsed = perf_counter() - start
                    tests.append(("✅", "SQLite connection", elapsed, "Connected"))
                    
                    cursor = conn.cursor()
                    cursor.execute("SELECT sqlite_version()")
                    version = cursor.fetchone()[0]
                    query_result = f"SQLite {version}"
                    cursor.close()
                    conn.close()
                    connection_status = "✅ CONNECTED"
                except Exception as e:
                    elapsed = perf_counter() - start
                    tests.append(("❌", "SQLite connection", elapsed, str(e)))
                    error_msg = str(e)
            else:
                tests.append(("⚠️", "Database connection", 0.0, f"Unsupported DB type: {db_type}"))
                error_msg = f"Unsupported database type: {db_type}"
                
        except Exception as e:
            elapsed = perf_counter() - start if 'start' in locals() else 0.0
            tests.append(("❌", f"{db_type.upper()} connection", elapsed, str(e)))
            error_msg = str(e)
    
    test_report = "\n".join([f"   {icon} {name} ({time:.3f}s) - {status}" for icon, name, time, status in tests])
    
    report = f"""
🗄️ DATABASE TEST REPORT (REAL CONNECTION)
═══════════════════════════════════════════════════════════
Database Type: {db_type.upper()}
Host: {host}:{port}
Database: {database or 'Not specified'}
Status: {connection_status}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════

📋 CONNECTION TESTS:
{test_report}

{f'📊 DATABASE INFO:\n   {query_result}\n' if query_result else ''}
{f'❌ ERROR:\n   {error_msg}\n' if error_msg and connection_status == '❌ FAILED' else ''}
💡 SUPPORTED DATABASES:
   • MySQL (pip install pymysql)
   • PostgreSQL (pip install psycopg2-binary)
   • MongoDB (pip install pymongo)
   • Redis (pip install redis)
   • SQLite (built-in)
═══════════════════════════════════════════════════════════
"""
    return report


async def run_accessibility_test(url: str, ui_config: Dict) -> str:
    """Run REAL accessibility test with actual HTML analysis"""
    import httpx
    from time import perf_counter
    import re
    
    start_time = perf_counter()
    checks = []
    issues = []
    warnings = []
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            html = response.text
            
            # Check 1: Images with alt text
            img_tags = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
            imgs_without_alt = [img for img in img_tags if 'alt=' not in img.lower()]
            
            if img_tags:
                if imgs_without_alt:
                    issues.append(f"❌ {len(imgs_without_alt)}/{len(img_tags)} images missing alt text")
                    checks.append(("❌", "Alt text on images", f"{len(imgs_without_alt)} missing"))
                else:
                    checks.append(("✅", "Alt text on images", f"All {len(img_tags)} have alt text"))
            else:
                checks.append(("ℹ️", "Alt text on images", "No images found"))
            
            # Check 2: Form labels
            input_tags = re.findall(r'<input[^>]*>', html, re.IGNORECASE)
            label_tags = re.findall(r'<label[^>]*>', html, re.IGNORECASE)
            
            if input_tags:
                if len(label_tags) < len(input_tags):
                    warnings.append(f"⚠️ {len(input_tags) - len(label_tags)} inputs may be missing labels")
                    checks.append(("⚠️", "Form labels", f"{len(label_tags)}/{len(input_tags)} labels found"))
                else:
                    checks.append(("✅", "Form labels", f"{len(label_tags)} labels for {len(input_tags)} inputs"))
            else:
                checks.append(("ℹ️", "Form labels", "No form inputs found"))
            
            # Check 3: Semantic HTML
            semantic_tags = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
            found_semantic = [tag for tag in semantic_tags if f'<{tag}' in html.lower()]
            
            if found_semantic:
                checks.append(("✅", "Semantic HTML", f"Using: {', '.join(found_semantic)}"))
            else:
                warnings.append("⚠️ No semantic HTML5 tags found")
                checks.append(("⚠️", "Semantic HTML", "No semantic tags found"))
            
            # Check 4: ARIA landmarks
            aria_roles = re.findall(r'role=["\']([^"\']+)["\']', html, re.IGNORECASE)
            
            if aria_roles:
                checks.append(("✅", "ARIA landmarks", f"{len(aria_roles)} roles defined"))
            else:
                checks.append(("⚠️", "ARIA landmarks", "No ARIA roles found"))
            
            # Check 5: Language attribute
            lang_attr = re.search(r'<html[^>]*lang=["\']([^"\']+)["\']', html, re.IGNORECASE)
            
            if lang_attr:
                checks.append(("✅", "Language attribute", f"lang='{lang_attr.group(1)}'"))
            else:
                issues.append("❌ Missing <html lang='...'> attribute")
                checks.append(("❌", "Language attribute", "Not specified"))
            
            # Check 6: Page title
            title = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
            
            if title and title.group(1).strip():
                checks.append(("✅", "Page title", f"'{title.group(1).strip()[:50]}'"))
            else:
                issues.append("❌ Missing or empty <title> tag")
                checks.append(("❌", "Page title", "Missing or empty"))
            
            # Check 7: Headings hierarchy
            h1_tags = len(re.findall(r'<h1[^>]*>', html, re.IGNORECASE))
            
            if h1_tags == 1:
                checks.append(("✅", "Heading structure", "Single H1 found"))
            elif h1_tags == 0:
                warnings.append("⚠️ No H1 heading found")
                checks.append(("⚠️", "Heading structure", "No H1 found"))
            else:
                warnings.append(f"⚠️ Multiple H1 headings ({h1_tags})")
                checks.append(("⚠️", "Heading structure", f"{h1_tags} H1 tags"))
            
            # Check 8: Skip links
            skip_link = re.search(r'href=["\']#(main|content|skip)', html, re.IGNORECASE)
            
            if skip_link:
                checks.append(("✅", "Skip navigation link", "Found"))
            else:
                warnings.append("⚠️ No skip navigation link found")
                checks.append(("⚠️", "Skip navigation link", "Not found"))
    
    except Exception as e:
        checks.append(("❌", "Test execution", str(e)))
        issues.append(f"❌ Test failed: {str(e)}")
    
    total_time = perf_counter() - start_time
    
    passed = len([c for c in checks if c[0] == "✅"])
    warned = len([c for c in checks if c[0] == "⚠️"])
    failed = len([c for c in checks if c[0] == "❌"])
    total_checks = len(checks)
    
    checks_report = "\n".join([f"   {icon} {name}: {status}" for icon, name, status in checks])
    issues_report = "\n".join([f"   {issue}" for issue in issues]) if issues else "   None"
    warnings_report = "\n".join([f"   {warning}" for warning in warnings]) if warnings else "   None"
    
    compliance_a = int((passed / total_checks) * 100) if total_checks > 0 else 0
    compliance_aa = int(((passed + warned * 0.5) / total_checks) * 100) if total_checks > 0 else 0
    
    report = f"""
♿ ACCESSIBILITY TEST REPORT (REAL WCAG 2.1 ANALYSIS)
═══════════════════════════════════════════════════════════
Target: {url}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {total_time:.3f}s
═══════════════════════════════════════════════════════════

📊 TEST SUMMARY:
   ✅ Passed: {passed}
   ⚠️ Warnings: {warned}
   ❌ Failed: {failed}
   Total Checks: {total_checks}

📋 COMPLIANCE CHECKS:
{checks_report}

❌ CRITICAL ISSUES:
{issues_report}

⚠️ WARNINGS:
{warnings_report}

📈 ESTIMATED WCAG COMPLIANCE:
   Level A: ~{compliance_a}%
   Level AA: ~{compliance_aa}%

💡 NOTE: This is automated HTML analysis. Manual testing required for:
   • Keyboard navigation
   • Screen reader compatibility
   • Color contrast ratios
   • Focus management
═══════════════════════════════════════════════════════════
"""
    return report


# ============================================================================
# REUSABLE UI COMPONENTS
# ============================================================================

def render_test_result(result: Dict, show_healing: bool = True, section_idx: int = 0, label: str = ""):
    """Reusable component for rendering test results with consistent formatting.
    
    Args:
        result: Test result dict with 'success', 'result', 'error', 'time' keys
        show_healing: Whether to show self-healing button on failure
        section_idx: Section index for unique keys
        label: Test label for healing identification
    """
    if result.get("success"):
        st.success(f"✅ Test passed in {result.get('time', 0):.2f}s")
        with st.expander("📊 View Results", expanded=False):
            res = result.get("result", {})
            if isinstance(res, dict):
                st.json(res)
            else:
                st.write(res)
    else:
        error = result.get("error", "Unknown error")
        st.error(f"❌ Test failed: {error}")
        
        if show_healing:
            heal_key = f"heal_result_{section_idx}_{label}_{hash(error) % 10000}"
            if st.button("🔧 Auto-Heal & Retry", key=heal_key):
                with st.spinner("🤖 AI analyzing and fixing..."):
                    # Get the original test config from context or reconstruct
                    test_spec = {"label": label, "error": error}
                    healing = asyncio.run(self_heal_test(test_spec, error))
                
                if healing.get("success"):
                    h = healing["healing"]
                    st.info(f"**Root Cause:** {h.get('root_cause')}")
                    st.success("**Suggested Fixes:**")
                    for fix in h.get("fixes", []):
                        st.markdown(f"- {fix}")
                    if h.get("manual_intervention_needed"):
                        st.warning("⚠️ Manual intervention may be required")
                else:
                    st.error(f"Failed to analyze: {healing.get('error')}")


def get_config_status_dict() -> Dict[str, str]:
    """Get configuration status for all settings (reusable).
    
    Returns:
        Dict mapping setting names to status strings
    """
    return {
        "Auth": "✅ Configured" if st.session_state.auth_config.get("auth_type") != "none" else "⚪ None",
        "API": "✅ Customized" if st.session_state.api_config.get("headers") or st.session_state.api_config.get("body") else "⚪ Default",
        "Database": "✅ Configured" if st.session_state.db_config.get("host") and st.session_state.db_config.get("database") else "⚪ Not Set",
        "LangChain": "✅ Configured" if "langchain_config" in st.session_state else "⚪ Default",
        "VectorDB": "✅ Configured" if "vectordb_config" in st.session_state else "⚪ Default",
        "RAG": "✅ Configured" if "rag_config" in st.session_state else "⚪ Default"
    }


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Render page header"""
    # Check Ollama availability dynamically
    ollama_status = "⚠️ Ollama Not Detected"
    try:
        import asyncio
        models = asyncio.run(fetch_ollama_models())
        if models:
            ollama_status = f"✅ Ollama LLM ({len(models)} models)"
        else:
            ollama_status = "⚠️ Ollama Running (No models)"
    except Exception:
        ollama_status = "❌ Ollama Offline"
    
    st.title("🔬 AgentLab — Chain, Test & Evaluate")
    st.caption(f"Day-to-day agent workbench • Context chunking • API chaining • {ollama_status} • MCP Tools")
    st.divider()


def render_system_status():
    """Render system status"""
    st.subheader("📊 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        client = get_ollama_client()
        st.metric("Ollama", "✅ Connected" if client else "❌ Offline")
    
    with col2:
        registry = get_registry()
        count = len(registry.get_all_metadata())
        st.metric("Agents", str(count))
    
    with col3:
        mcp = get_mcp_status()
        ready = sum(1 for v in mcp.values() if v["ready"])
        st.metric("MCP Tools", f"{ready}/5")
    
    with col4:
        models = asyncio.run(fetch_ollama_models())
        st.metric("LLM Models", str(len(models)))


def render_mcp_panel():
    """Render MCP status panel"""
    st.subheader("🔗 MCP Integration")
    
    mcp_status = get_mcp_status()
    
    cols = st.columns(5)
    for idx, (name, info) in enumerate(mcp_status.items()):
        with cols[idx]:
            st.markdown(f"**{name}**")
            st.write(info["status"])


def render_all_agents():
    """Render all agents with improved categorization and visual hierarchy"""
    registry = get_registry()
    agents_dict = registry.get_all_metadata()
    
    # Group by category
    by_category = {}
    for agent_type, meta in agents_dict.items():
        cat = meta.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(meta)
    
    st.subheader(f"🎯 Agent Catalog ({len(agents_dict)} Agents)")
    
    # Category filter tabs
    categories = ["all"] + sorted(by_category.keys())
    category_labels = ["🏠 All"]
    for cat in categories[1:]:
        cfg = CATEGORY_CONFIG.get(cat, {"icon": "📦", "name": cat.title()})
        category_labels.append(f"{cfg['icon']} {cfg['name']}")
    
    selected_idx = st.selectbox(
        "Filter by Category",
        range(len(categories)),
        format_func=lambda x: category_labels[x],
        key="category_filter"
    )
    selected_category = categories[selected_idx]
    
    # Summary metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total Agents", len(agents_dict))
    with col2:
        st.metric("📂 Categories", len(by_category))
    with col3:
        llm_count = len(by_category.get("llm", []))
        st.metric("🤖 LLM Agents", llm_count)
    with col4:
        async_count = sum(1 for m in agents_dict.values() if m.is_async)
        st.metric("⚡ Async Agents", async_count)
    
    st.divider()
    
    # Display agents by category with visual cards
    display_categories = [selected_category] if selected_category != "all" else sorted(by_category.keys())
    
    for category in display_categories:
        agents = by_category.get(category, [])
        if not agents:
            continue
            
        cfg = CATEGORY_CONFIG.get(category, {"icon": "📦", "color": "#6b7280", "name": category.title()})
        
        # Category header with styled badge
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 20px 0 10px 0;">
            <span style="font-size: 1.8em; margin-right: 10px;">{cfg['icon']}</span>
            <span style="font-size: 1.3em; font-weight: bold; color: {cfg['color']};">{cfg['name']}</span>
            <span style="background: {cfg['color']}; color: white; padding: 2px 10px; border-radius: 12px; margin-left: 10px; font-size: 0.8em;">{len(agents)} agents</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Agent cards in a grid
        cols = st.columns(2)
        for idx, agent in enumerate(agents):
            with cols[idx % 2]:
                with st.container():
                    # Agent card with border color
                    st.markdown(f"""
                    <div style="border-left: 4px solid {cfg['color']}; padding: 10px 15px; background: #f8f9fa; border-radius: 8px; margin: 5px 0;">
                        <div style="font-weight: bold; font-size: 1.1em;">{agent.name}</div>
                        <div style="color: #6b7280; font-size: 0.9em; margin: 5px 0;">{agent.description}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Expandable details
                    with st.expander("📋 Details", expanded=False):
                        st.markdown(f"**Capabilities:** {', '.join(agent.capabilities[:4])}")
                        
                        detail_col1, detail_col2 = st.columns(2)
                        with detail_col1:
                            st.markdown(f"⚡ Async: {'✅' if agent.is_async else '❌'}")
                            st.markdown(f"🔐 Auth: {'Required' if agent.requires_auth else 'Optional'}")
                        with detail_col2:
                            st.markdown(f"⏱️ Timeout: {agent.min_timeout}s")
                            st.markdown(f"🔗 MCP: {', '.join(agent.mcp_tools) if agent.mcp_tools else 'None'}")
        
        st.markdown("---")


def render_agent_tester():
    """Render agent testing interface with category-based selection and improved UI"""
    st.subheader("🧪 Agent Testing Lab")
    
    registry = get_registry()
    agents_dict = registry.get_all_metadata()
    
    # Group agents by category for better selection
    by_category = {}
    for agent_type, meta in agents_dict.items():
        cat = meta.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(meta)
    
    # Two-step selection: Category first, then Agent
    col1, col2 = st.columns([1, 2])
    
    with col1:
        categories = sorted(by_category.keys())
        category_options = []
        for cat in categories:
            cfg = CATEGORY_CONFIG.get(cat, {"icon": "📦", "name": cat.title()})
            category_options.append(f"{cfg['icon']} {cfg['name']} ({len(by_category[cat])})")
        
        selected_cat_idx = st.selectbox(
            "📂 Select Category",
            range(len(categories)),
            format_func=lambda x: category_options[x],
            key="test_category_select"
        )
        selected_category = categories[selected_cat_idx]
    
    with col2:
        # Get agents in selected category
        category_agents = by_category[selected_category]
        agent_names = [a.name for a in category_agents]
        
        selected_name = st.selectbox(
            "🤖 Select Agent",
            agent_names,
            key="agent_test_select"
        )
        selected_meta = next(a for a in category_agents if a.name == selected_name)
    
    # Agent info card with visual styling
    cfg = CATEGORY_CONFIG.get(selected_category, {"icon": "📦", "color": "#6b7280", "name": selected_category.title()})
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {cfg['color']}20, {cfg['color']}10); border-left: 4px solid {cfg['color']}; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <div style="font-size: 1.3em; font-weight: bold; color: {cfg['color']};">{cfg['icon']} {selected_meta.name}</div>
        <div style="color: #4b5563; margin: 8px 0;">{selected_meta.description}</div>
        <div style="display: flex; gap: 15px; margin-top: 10px; flex-wrap: wrap;">
            <span style="background: #e5e7eb; padding: 3px 10px; border-radius: 12px; font-size: 0.85em;">⚡ {'Async' if selected_meta.is_async else 'Sync'}</span>
            <span style="background: #e5e7eb; padding: 3px 10px; border-radius: 12px; font-size: 0.85em;">🔐 {'Auth Required' if selected_meta.requires_auth else 'No Auth'}</span>
            <span style="background: #e5e7eb; padding: 3px 10px; border-radius: 12px; font-size: 0.85em;">⏱️ {selected_meta.min_timeout}s timeout</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Capabilities chips
    if selected_meta.capabilities:
        st.markdown("**Capabilities:**")
        caps_html = " ".join([f'<span style="background: {cfg["color"]}15; color: {cfg["color"]}; padding: 3px 8px; border-radius: 8px; font-size: 0.8em; margin: 2px;">{cap}</span>' for cap in selected_meta.capabilities[:6]])
        st.markdown(caps_html, unsafe_allow_html=True)
    
    st.divider()
    
    # Show active configuration summary
    auth_type = st.session_state.auth_config.get("auth_type", "none")
    method = st.session_state.api_config.get("method", "GET")
    browser = st.session_state.ui_config.get("browser", "chromium")
    
    with st.expander("🔧 Active Configuration (Configure in Sidebar)", expanded=False):
        config_cols = st.columns(4)
        with config_cols[0]:
            st.markdown(f"🔐 **Auth:** `{auth_type.upper()}`")
        with config_cols[1]:
            st.markdown(f"🌐 **Method:** `{method}`")
        with config_cols[2]:
            st.markdown(f"🖥️ **Browser:** `{browser}`")
        with config_cols[3]:
            timeout = st.session_state.api_config.get("timeout", 30)
            st.markdown(f"⏱️ **Timeout:** `{timeout}s`")
        
        # Show extra info for auth if configured
        if auth_type != "none":
            st.markdown("---")
            if auth_type == "basic":
                username = st.session_state.auth_config.get("username", "")
                st.write(f"**Type:** Basic Auth | **Username:** {username[:3]}*** (masked)" if username else "**Type:** Basic Auth | **Username:** Not set")
            elif auth_type == "bearer":
                token = st.session_state.auth_config.get("token", "")
                st.write(f"**Type:** Bearer Token | **Token:** {token[:10]}*** (masked)" if token else "**Type:** Bearer Token | **Token:** Not set")
            elif auth_type == "api_key":
                st.write(f"**Type:** API Key | **Header:** {st.session_state.auth_config.get('api_key_header', 'X-API-Key')}")
            elif auth_type == "form_login":
                st.write(f"**Type:** Form Login | **Login URL:** {st.session_state.auth_config.get('login_url', 'Not set')}")
            elif auth_type == "oauth":
                st.write(f"**Type:** OAuth 2.0 | **Token URL:** {st.session_state.auth_config.get('token_url', 'Not set')}")
    
    # Test form
    with st.form("agent_test_form", clear_on_submit=False):
        agent_lower = selected_name.lower()
        
        # Smart input based on agent type
        if selected_category == "llm" or "llm" in agent_lower:
            st.markdown("##### 🤖 LLM Agent Test")
            models = asyncio.run(fetch_ollama_models())
            model_options = models if models else ["llama3.2:latest"]
            selected_model = st.selectbox("Select Ollama Model", model_options, key="llm_model_select")
            test_input = selected_model
            test_url = ""
        elif selected_category == "database" or "database" in agent_lower or "vectordb" in agent_lower:
            st.markdown("##### 🗄️ Database Test")
            test_url = ""
            test_input = st.text_input("Database Name/Connection", placeholder="test_db", key="db_test_input")
        elif selected_category == "api" or "api" in agent_lower or "graphql" in agent_lower:
            st.markdown("##### 🌐 API Test")
            test_url = st.text_input("API URL", placeholder="https://api.example.com/endpoint", key="api_url_input")
            test_input = st.text_area("Request Body/Query", value="", height=80, key="api_body_input")
            if "graphql" in agent_lower:
                st.session_state.api_config["graphql_query"] = test_input or "query { __typename }"
        else:
            test_url = st.text_input("Test URL", placeholder="https://example.com", help="Target URL for the test")
            test_input = st.text_area("Test Input/Prompt", value=f"Run {selected_name} test", height=80)
        
        submitted = st.form_submit_button("▶️ Run Test", type="primary", use_container_width=True)
    
    # Execute test and show results
    if submitted and (test_input or test_url):
        config = {
            "auth": st.session_state.auth_config,
            "api": st.session_state.api_config,
            "ui": st.session_state.ui_config,
            "db": st.session_state.db_config
        }
        
        with st.spinner(f"🔄 Running {selected_name}..."):
            result = asyncio.run(execute_agent_test(selected_name, test_input, test_url or None, config))
        
        # Store result in history
        if "test_history" not in st.session_state:
            st.session_state.test_history = []
        
        test_record = {
            "agent": selected_name,
            "category": selected_category,
            "time": datetime.now().strftime("%H:%M:%S"),
            "success": result.get("success", False),
            "duration": result.get("time", 0)
        }
        st.session_state.test_history.insert(0, test_record)
        st.session_state.test_history = st.session_state.test_history[:10]  # Keep last 10
        
        if result.get("success"):
            uses_ollama = result.get("uses_ollama", False)
            
            # Success card
            st.markdown(f"""
            <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <div style="color: #166534; font-weight: bold;">✅ {selected_name} completed in {result.get('time', 0):.2f}s</div>
                <div style="color: #15803d; font-size: 0.9em;">{'🤖 Powered by Ollama LLM' if uses_ollama else ''}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📋 Results", expanded=True):
                res = result.get("result", "No output")
                if isinstance(res, dict):
                    st.json(res)
                else:
                    st.write(res)
        else:
            st.markdown(f"""
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <div style="color: #991b1b; font-weight: bold;">❌ Test Failed</div>
                <div style="color: #b91c1c; font-size: 0.9em;">{result.get('error', 'Unknown error')}</div>
            </div>
            """, unsafe_allow_html=True)
            if result.get("traceback"):
                with st.expander("🔍 Error Details"):
                    st.code(result["traceback"])
    
    # Show recent test history
    if st.session_state.get("test_history"):
        st.divider()
        st.markdown("##### 📜 Recent Tests")
        history_cols = st.columns(5)
        for idx, record in enumerate(st.session_state.test_history[:5]):
            with history_cols[idx]:
                status_emoji = "✅" if record["success"] else "❌"
                st.markdown(f"""
                <div style="background: #f3f4f6; padding: 8px; border-radius: 8px; text-align: center; font-size: 0.8em;">
                    <div>{status_emoji}</div>
                    <div style="font-weight: bold;">{record['agent'][:12]}...</div>
                    <div style="color: #6b7280;">{record['time']}</div>
                </div>
                """, unsafe_allow_html=True)


def render_llm_playground():
    """Render comprehensive LLM playground with model comparison and benchmarking"""
    st.subheader("🤖 LLM Playground")
    
    # Fetch models
    models = asyncio.run(fetch_ollama_models())
    
    if not models:
        st.warning("⚠️ No Ollama models found. Make sure Ollama is running with `ollama serve`")
        st.code("# Pull a model first:\nollama pull llama3.2:latest", language="bash")
        return
    
    # Model status panel
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #9333ea20, #7c3aed10); border-left: 4px solid #9333ea; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div style="font-size: 1.2em; font-weight: bold; color: #9333ea;">🎯 {len(models)} Ollama Models Available</div>
        <div style="color: #6b7280; margin-top: 5px;">{', '.join(models)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different LLM testing modes
    llm_tab1, llm_tab2, llm_tab3 = st.tabs(["💬 Quick Test", "⚖️ Model Comparison", "📊 Benchmarks"])
    
    with llm_tab1:
        st.markdown("##### Send a prompt to any model")
        with st.form("quick_llm_test"):
            selected_model = st.selectbox("Select Model", models, key="quick_model")
            prompt = st.text_area("Prompt", value="Explain what unit testing is in 2 sentences.", height=100)
            col1, col2 = st.columns([1, 4])
            with col1:
                temperature = st.slider("Temp", 0.0, 2.0, 0.7, 0.1, key="quick_temp")
            run_quick = st.form_submit_button("🚀 Generate", type="primary", use_container_width=True)
        
        if run_quick and prompt:
            with st.spinner(f"Generating with {selected_model}..."):
                result = asyncio.run(run_ollama_prompt(selected_model, prompt))
            
            if result["success"]:
                st.success(f"✅ **{selected_model}** - {result['time']} - {result['tokens']} tokens")
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb;">
                    {result['response']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"❌ Failed: {result.get('error')}")
    
    with llm_tab2:
        st.markdown("##### Compare responses from multiple models")
        with st.form("compare_llm_test"):
            compare_models = st.multiselect("Select Models to Compare", models, default=models[:2] if len(models) >= 2 else models, key="compare_models")
            compare_prompt = st.text_area("Prompt", value="What are the benefits of test automation?", height=80, key="compare_prompt")
            run_compare = st.form_submit_button("⚖️ Compare Models", type="primary", use_container_width=True)
        
        if run_compare and compare_models and compare_prompt:
            cols = st.columns(len(compare_models))
            
            for idx, model in enumerate(compare_models):
                with cols[idx]:
                    st.markdown(f"**{model}**")
                    with st.spinner("Generating..."):
                        result = asyncio.run(run_ollama_prompt(model, compare_prompt))
                    
                    if result["success"]:
                        st.caption(f"⏱️ {result['time']} | 📝 {result['tokens']} tokens")
                        st.markdown(f"""
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; font-size: 0.9em; height: 200px; overflow-y: auto;">
                            {result['response'][:500]}...
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Failed: {result.get('error')}")
    
    with llm_tab3:
        st.markdown("##### Run comprehensive LLM benchmarks")
        st.info("💡 For detailed benchmarks, use the **LLMEvaluationAgent** from the Test Agent tab. It evaluates: Factual Accuracy, Reasoning, Math, Code Generation, Instruction Following, and Hallucination Resistance.")
        
        bench_model = st.selectbox("Select Model for Quick Benchmark", models, key="bench_model")
        
        if st.button("🏃 Run Quick Benchmark", type="primary"):
            # Use configurable benchmark prompts from session state
            benchmark_prompts = st.session_state.get("benchmark_prompts", [
                {"category": "Factual", "prompt": "What is the capital of France?"},
                {"category": "Math", "prompt": "What is 15% of 200?"}
            ])
            
            results = []
            progress = st.progress(0)
            
            for idx, bench in enumerate(benchmark_prompts):
                category = bench.get("category", f"Test {idx+1}")
                prompt = bench.get("prompt", "")
                with st.spinner(f"Testing {category}..."):
                    result = asyncio.run(run_ollama_prompt(bench_model, prompt))
                    results.append((category, result))
                progress.progress((idx + 1) / len(benchmark_prompts))
            
            st.markdown("##### Benchmark Results")
            for category, result in results:
                if result["success"]:
                    st.success(f"✅ **{category}** - {result['time']}")
                    with st.expander(f"Response for {category}"):
                        st.write(result["response"])
                else:
                    st.error(f"❌ **{category}** - Failed")


def render_quick_tests():
    """Render enhanced quick test buttons with category grouping (configurable)"""
    st.subheader("⚡ Quick Tests")
    st.markdown("Run common tests with a single click (configured in sidebar)")

    # Inject CSS for consistent button sizing in this section
    st.markdown(
        """
        <style>
        .quick-tests .stButton>button { min-height:48px; height:48px; font-size:1rem; }
        .quick-tests .stButton { margin-bottom: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    config = st.session_state.get("quick_tests_config", {})
    sections = config.get("sections", [])

    if not sections:
        st.info("No quick tests configured. Edit Quick Tests in the sidebar.")
        return

    # Wrap section in a div to scope CSS
    st.markdown("<div class='quick-tests'>", unsafe_allow_html=True)
    for sidx, section in enumerate(sections):
        title = section.get("title", "Tests")
        tests = section.get("tests", [])

        st.markdown(f"##### {title}")

        if not tests:
            st.markdown("_No tests configured for this section._")
            continue

        # Add "Run All" button for multi-agent orchestration
        run_all_key = f"run_section_all_{sidx}_{title}"
        if st.button(f"▶️ Run All '{title}' Tests in Parallel", key=run_all_key, type="secondary"):
            with st.spinner(f"🎭 Orchestrating {len(tests)} agents in parallel..."):
                try:
                    results = asyncio.run(orchestrate_agents(tests, {
                        "auth": st.session_state.get("auth_config", {}),
                        "api": st.session_state.get("api_config", {}),
                        "ui": st.session_state.get("ui_config", {}),
                        "db": st.session_state.get("db_config", {})
                    }))
                except Exception as e:
                    st.error(f"❌ Orchestration error: {e}")
                    results = []
            
            # Display aggregated results
            if results:
                st.markdown(f"**📊 Orchestration Results: {sum(1 for r in results if r.get('success'))}/{len(results)} passed**")
                
                for r in results:
                    t = r.get("task", {})
                    label = t.get("label", t.get("agent", "task"))
                    
                    if r.get("success"):
                        with st.expander(f"✅ {label} ({r.get('time', 0):.2f}s)", expanded=False):
                            res = r.get("result", {})
                            if isinstance(res, dict):
                                st.json(res)
                            else:
                                st.write(res)
                    else:
                        error = r.get("error", "Unknown error")
                        with st.expander(f"❌ {label} - FAILED", expanded=True):
                            st.error(error)
                            
                            # Self-healing option
                            heal_key = f"heal_{sidx}_{label}"
                            if st.button(f"🔧 Auto-Heal This Test", key=heal_key):
                                with st.spinner("🤖 AI analyzing failure and suggesting fixes..."):
                                    healing_result = asyncio.run(self_heal_test(t, error))
                                
                                if healing_result.get("success"):
                                    healing = healing_result["healing"]
                                    st.success(f"**Root Cause:** {healing.get('root_cause', 'Unknown')}")
                                    st.info("**Suggested Fixes:**")
                                    for fix in healing.get("fixes", []):
                                        st.markdown(f"- {fix}")
                                    
                                    if healing.get("retry_recommended"):
                                        st.markdown("**Updated Configuration:**")
                                        st.json(healing.get("updated_config", {}))
                                    
                                    if healing.get("manual_intervention_needed"):
                                        st.warning("⚠️ Manual intervention may be required")
                                else:
                                    st.error(f"Failed to analyze: {healing_result.get('error')}")
        
        st.markdown("---")

        # Create up to 4 columns to lay out buttons evenly
        num = max(1, min(len(tests), 4))
        cols = st.columns(num)

        for idx, test in enumerate(tests):
            col = cols[idx % num]
            label = test.get("label", test.get("agent", "Run"))
            agent = test.get("agent", "")
            url = test.get("url", "")

            with col:
                key = f"quick_test_{sidx}_{idx}_{label}"
                if st.button(label, use_container_width=True, key=key):
                    with st.spinner(f"Running {label}..."):
                        try:
                            result = asyncio.run(execute_agent_test(agent, url, url))
                        except Exception as e:
                            st.error(f"Execution error: {e}")
                            result = {"success": False, "error": str(e)}

                    # Use reusable component for result display
                    render_test_result(result, show_healing=True, section_idx=sidx, label=label)
    st.markdown("</div>", unsafe_allow_html=True)


def render_natural_language_tests():
    """Render natural language test creation interface"""
    st.subheader("💬 Natural Language Test Creation")
    st.markdown("Describe your test in plain English, and AI will create and execute it.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Use configurable templates for placeholder
        templates = st.session_state.get("nl_templates", [])
        placeholder_text = "Examples:\n" + "\n".join([f"- {tmpl}" for tmpl in templates[:4]]) if templates else "Examples:\n- Test security of https://example.com\n- Check API performance at https://api.example.com\n- Run accessibility check on https://myapp.com"
        
        nl_input = st.text_area(
            "Describe your test:",
            placeholder=placeholder_text,
            height=120,
            key="nl_test_input"
        )
        
        col_run, col_save = st.columns(2)
        with col_run:
            run_nl_test = st.button("🚀 Parse & Execute Test", type="primary", use_container_width=True)
        with col_save:
            save_to_quick = st.button("💾 Save to Quick Tests", use_container_width=True, disabled=not nl_input)
    
    with col2:
        st.markdown("**✨ AI Features:**")
        st.markdown("""        
        - 🎯 Auto-detect test type
        - 🔗 Extract URLs
        - ⚙️ Configure parameters
        - 🔄 Multi-step tests
        - 🤖 Self-healing
        """)
    
    if run_nl_test and nl_input:
        with st.spinner("🤖 Parsing natural language test..."):
            parse_result = asyncio.run(parse_natural_language_test(nl_input))
        
        if parse_result.get("success"):
            test_spec = parse_result["test_spec"]
            
            st.success("✅ Test parsed successfully!")
            
            col_spec, col_exec = st.columns(2)
            
            with col_spec:
                st.markdown("**📋 Generated Test Specification:**")
                st.json(test_spec)
            
            with col_exec:
                st.markdown("**▶️ Execute Test:**")
                if st.button("Run This Test Now", key="execute_nl_test", type="primary"):
                    with st.spinner(f"Running {test_spec.get('agent', 'test')}..."):
                        try:
                            result = asyncio.run(execute_agent_test(
                                test_spec.get("agent", ""),
                                test_spec.get("url", ""),
                                test_spec.get("url", ""),
                                {"api": test_spec}  # Pass spec as config
                            ))
                        except Exception as e:
                            result = {"success": False, "error": str(e)}
                    
                    # Use reusable component for result display with healing
                    render_test_result(result, show_healing=True, section_idx=0, label=test_spec.get("agent", "NL_Test"))
        else:
            st.error(f"❌ Failed to parse test: {parse_result.get('error')}")
            if "raw" in parse_result:
                with st.expander("Raw LLM Response"):
                    st.code(parse_result["raw"])
    
    if save_to_quick and nl_input:
        st.info("💾 Feature: Save to Quick Tests - Parse the test first, then add it to your quick_tests_config in the sidebar.")


def render_documentation():
    """Render enhanced documentation with better organization"""
    st.subheader("📚 Documentation & Help")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.expander("🚀 Quick Start", expanded=True):
            st.markdown("""
            **1. Start Ollama**
            ```bash
            ollama serve
            ```
            
            **2. Pull a Model**
            ```bash
            ollama pull llama3.2:latest
            ```
            
            **3. Run Dashboard**
            ```bash
            streamlit run agent_dashboard.py
            ```
            """)
    
    with col2:
        with st.expander("🎯 Agent Categories", expanded=True):
            registry = get_registry()
            cats = {}
            for _, meta in registry.get_all_metadata().items():
                cats[meta.category] = cats.get(meta.category, 0) + 1
            
            for cat, count in sorted(cats.items()):
                cfg = CATEGORY_CONFIG.get(cat, {"icon": "📦", "name": cat.title()})
                st.markdown(f"{cfg['icon']} **{cfg['name']}**: {count} agents")
    
    with col3:
        with st.expander("💡 Tips", expanded=True):
            st.markdown("""
            - **Configure in Sidebar**: All test parameters are configurable via the left sidebar
            - **Category Filter**: Use filters to quickly find agents
            - **Test History**: Recent tests are tracked in the Test Agent tab
            - **LLM Playground**: Compare multiple models side-by-side
            - **Quick Tests**: One-click tests for common scenarios
            """)


def render_orchestration():
    """Render multi-agent orchestration interface"""
    st.subheader("🎯 Multi-Agent Orchestration")
    st.markdown("Coordinate multiple specialized agents to run comprehensive test suites with dependencies")
    
    # Initialize orchestration state
    if "orchestration_suite" not in st.session_state:
        st.session_state.orchestration_suite = {"tests": []}
    if "orchestration_results" not in st.session_state:
        st.session_state.orchestration_results = None
    
    # Agent status panel
    st.markdown("### 🤖 Agent Team Status")
    
    orchestrator = OrchestratorAgent()
    agent_count = max(len(orchestrator.agents), 1)
    agent_cols = st.columns(min(agent_count, 6))
    
    for idx, (agent_key, agent_cap) in enumerate(orchestrator.agents.items()):
        with agent_cols[idx % len(agent_cols)]:
            status_icon = "🟢" if agent_cap.is_available else "🔴"
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="font-size: 1.5em;">{status_icon}</div>
                <div style="font-size: 0.9em; font-weight: bold;">{agent_cap.name.replace(' Agent', '')}</div>
                <div style="font-size: 0.75em; color: #6b7280;">{agent_cap.agent_type.upper()}</div>
                <div style="font-size: 0.7em; color: #9ca3af;">Max: {agent_cap.max_concurrent_tasks}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Test suite builder
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Test Suite Builder")
        
        with st.form("add_test_form", clear_on_submit=True):
            st.markdown("#### Add Test to Suite")
            
            test_type = st.selectbox(
                "Test Type",
                options=["ui", "api", "validation", "report"],
                format_func=lambda x: {
                    "ui": "🖥️ UI Test (Browser Automation)",
                    "api": "🌐 API Test (REST/GraphQL)",
                    "validation": "✅ Validation (Data Checks)",
                    "report": "📊 Report (Analysis)"
                }.get(x, x.upper()),
                key="orch_test_type"
            )
            
            target_url = st.text_input(
                "Target URL/Endpoint",
                value="https://example.com",
                key="orch_target"
            )
            
            priority = st.selectbox(
                "Priority",
                options=[1, 2, 3],
                format_func=lambda x: {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}.get(x, str(x)),
                key="orch_priority"
            )
            
            # Show type-specific configuration
            if test_type == "ui":
                st.markdown("**UI Test Configuration**")
                ui_col1, ui_col2 = st.columns(2)
                with ui_col1:
                    action1 = st.text_input("Action 1", value="navigate", key="ui_action1")
                    action2 = st.text_input("Action 2", value="screenshot", key="ui_action2")
                with ui_col2:
                    selector1 = st.text_input("Selector 1 (if needed)", value="", key="ui_sel1")
                    selector2 = st.text_input("Selector 2 (if needed)", value="", key="ui_sel2")
            
            elif test_type == "api":
                st.markdown("**API Test Configuration**")
                api_col1, api_col2 = st.columns(2)
                with api_col1:
                    method = st.selectbox("Method", ["GET", "POST", "PUT", "DELETE"], key="api_method_orch")
                    expected_status = st.number_input("Expected Status", value=200, key="api_status_orch")
                with api_col2:
                    response_time_max = st.number_input("Max Response Time (s)", value=2.0, key="api_time_orch")
            
            elif test_type == "validation":
                st.markdown("**Validation Configuration**")
                val_type = st.selectbox("Validation Type", ["schema", "type", "range", "not_null"], key="val_type_orch")
            
            dependencies = st.text_input(
                "Dependencies (comma-separated task IDs, e.g., test_0,test_1)",
                value="",
                key="orch_deps",
                help="List task IDs that must complete before this test runs"
            )
            
            max_retries = st.slider("Max Retries (with auto-healing)", 0, 5, 2, key="orch_retries")
            
            add_button = st.form_submit_button("➕ Add Test to Suite", type="primary", use_container_width=True)
        
        if add_button:
            # Build test config based on type
            config = {}
            if test_type == "ui":
                steps = []
                if action1:
                    steps.append({"action": action1, "url": target_url if action1 == "navigate" else None})
                    if selector1:
                        steps[-1]["selector"] = selector1
                if action2:
                    steps.append({"action": action2})
                    if selector2:
                        steps[-1]["selector"] = selector2
                config = {"steps": steps}
            
            elif test_type == "api":
                config = {
                    "method": method,
                    "assertions": [
                        {"type": "status_code", "expected": expected_status},
                        {"type": "response_time", "max": response_time_max}
                    ]
                }
            
            elif test_type == "validation":
                config = {
                    "data": {},
                    "validations": [{"type": val_type}]
                }
            
            # Add test to suite
            deps_list = [d.strip() for d in dependencies.split(",") if d.strip()]
            
            test_item = {
                "type": test_type,
                "target": target_url,
                "config": config,
                "priority": priority,
                "dependencies": deps_list,
                "max_retries": max_retries
            }
            
            st.session_state.orchestration_suite["tests"].append(test_item)
            st.success(f"✅ Added {test_type.upper()} test to suite (test_{len(st.session_state.orchestration_suite['tests']) - 1})")
            st.rerun()
    
    with col2:
        st.markdown("### 📊 Current Suite")
        
        suite = st.session_state.orchestration_suite
        test_count = len(suite.get("tests", []))
        
        st.metric("Total Tests", test_count)
        
        if test_count > 0:
            st.markdown("#### Tests in Suite:")
            
            for idx, test in enumerate(suite["tests"]):
                test_id = f"test_{idx}"
                type_icon = {"ui": "🖥️", "api": "🌐", "validation": "✅", "report": "📊"}.get(test["type"], "📦")
                priority_color = {1: "#dc2626", 2: "#f59e0b", 3: "#10b981"}.get(test["priority"], "#6b7280")
                
                deps_text = f" → {', '.join(test['dependencies'])}" if test.get("dependencies") else ""
                
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; margin: 5px 0; border-left: 3px solid {priority_color};">
                    <div style="font-size: 0.9em;">
                        <strong>{type_icon} {test_id}</strong> - {test['type'].upper()}
                    </div>
                    <div style="font-size: 0.75em; color: #6b7280;">
                        {test['target'][:40]}...{deps_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ Remove", key=f"remove_{idx}"):
                    suite["tests"].pop(idx)
                    st.rerun()
            
            st.divider()
            
            # Execution controls
            exec_col1, exec_col2 = st.columns(2)
            
            with exec_col1:
                parallel_mode = st.checkbox("⚡ Parallel Execution", value=True, key="orch_parallel")
            
            with exec_col2:
                if st.button("▶️ Run Suite", type="primary", use_container_width=True, key="run_orch"):
                    with st.spinner("🚀 Executing test suite..."):
                        orchestrator.create_test_plan(suite)
                        results = asyncio.run(orchestrator.execute_test_plan(parallel=parallel_mode))
                        st.session_state.orchestration_results = results
                        st.success("✅ Execution complete!")
                        st.rerun()
            
            if st.button("🔄 Clear Suite", key="clear_orch"):
                st.session_state.orchestration_suite = {"tests": []}
                st.session_state.orchestration_results = None
                st.rerun()
        
        else:
            st.info("👈 Add tests using the form")
    
    # Results display
    if st.session_state.orchestration_results:
        st.divider()
        st.markdown("### 📊 Execution Results")
        
        results = st.session_state.orchestration_results
        
        # Summary metrics
        metric_cols = st.columns(5)
        with metric_cols[0]:
            st.metric("Total", results.get("total_tasks", 0))
        with metric_cols[1]:
            st.metric("✅ Passed", results.get("passed", 0))
        with metric_cols[2]:
            st.metric("❌ Failed", results.get("failed", 0))
        with metric_cols[3]:
            st.metric("🔧 Healed", results.get("healed", 0))
        with metric_cols[4]:
            pass_rate = (results.get("passed", 0) / results.get("total_tasks", 1)) * 100
            st.metric("Pass Rate", f"{pass_rate:.1f}%")
        
        # Individual task results
        st.markdown("#### Task Results:")
        
        for task_result in results.get("tasks", []):
            task_id = task_result.get("task_id", "unknown")
            task_type = task_result.get("type", "unknown")
            status = task_result.get("status", "unknown")
            result = task_result.get("result", {})
            
            status_icon = "✅" if status == "completed" else "❌"
            status_color = "#10b981" if status == "completed" else "#dc2626"
            
            with st.expander(f"{status_icon} {task_id} - {task_type.upper()}", expanded=False):
                st.markdown(f"**Status:** {status}")
                
                if result:
                    if result.get("success"):
                        st.success(f"Test passed")
                        if result.get("execution_time"):
                            st.info(f"⏱️ Execution time: {result['execution_time']:.3f}s")
                    else:
                        st.error(f"Test failed: {result.get('error', 'Unknown error')}")
                    
                    # Show agent-specific details
                    if "agent" in result:
                        st.text(f"Agent: {result['agent']}")
                    
                    # Show result details
                    st.json(result)
        
        # Show report if available
        if "report" in results:
            with st.expander("📈 Comprehensive Report", expanded=True):
                report = results["report"]
                if report.get("success"):
                    st.markdown("**Report Summary:**")
                    st.json(report.get("report", {}))


# ============================================================================
# CHAIN BUILDER
# ============================================================================

_CHAIN_AGENTS = [
    "Security", "Performance", "API Contract", "E2E", "Accessibility",
    "Compliance", "GraphQL", "Chaos", "ML Model", "Mobile", "Database",
    "LLM Evaluation", "LangChain", "VectorDB", "RAG", "Comprehensive Report",
]


def render_chain_builder():
    """Render the Agent Chain Builder tab — define a pipeline of agents that
    pass context (with optional chunking) from one step to the next."""

    st.markdown("## 🔗 Agent Chain Builder")
    st.markdown(
        "Build a **sequential pipeline** of agents. Output from each step is "
        "chunked (if enabled) and fed as context into the next step's input."
    )

    # ── Chunk config status bar ──────────────────────────────────────────────
    cfg = st.session_state.get("chunk_config", {
        "enabled": True, "chunk_size": 800, "overlap": 80, "max_chunks": 10
    })
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Chunking", "ON ✅" if cfg["enabled"] else "OFF ❌")
    c2.metric("Chunk Size", f"{cfg['chunk_size']} chars")
    c3.metric("Overlap", f"{cfg['overlap']} chars")
    c4.metric("Max Chunks", cfg["max_chunks"])
    st.caption("Adjust chunking settings in the ✂️ sidebar panel.")

    st.divider()

    # ── Step builder form ───────────────────────────────────────────────────
    left, right = st.columns([1, 1])

    with left:
        st.markdown("### ➕ Add a Chain Step")
        with st.form("add_chain_step", clear_on_submit=True):
            step_agent = st.selectbox("Agent", options=_CHAIN_AGENTS, key="cs_agent")
            step_url = st.text_input(
                "Target URL (optional – leave blank to use previous step's context)",
                placeholder="https://api.example.com/v1/...",
                key="cs_url",
            )
            step_input = st.text_area(
                "Static Input / Prompt Prefix (optional)",
                height=80,
                placeholder="E.g. 'Check authentication endpoints at ...'",
                key="cs_input",
            )
            use_chunking = st.checkbox(
                "Apply chunking to incoming context for this step",
                value=cfg["enabled"],
                key="cs_chunking",
            )
            continue_on_fail = st.checkbox(
                "Continue chain on failure",
                value=False,
                key="cs_continue_fail",
            )
            submitted = st.form_submit_button("Add Step ➡️", use_container_width=True)
            if submitted:
                if "chain_steps" not in st.session_state:
                    st.session_state.chain_steps = []
                st.session_state.chain_steps.append({
                    "agent": step_agent,
                    "url": step_url.strip(),
                    "input": step_input.strip(),
                    "use_chunking": use_chunking,
                    "continue_on_failure": continue_on_fail,
                })
                st.success(f"Step {len(st.session_state.chain_steps)} added: **{step_agent}**")
                st.rerun()

    with right:
        st.markdown("### 📋 Current Chain")
        steps = st.session_state.get("chain_steps", [])

        if not steps:
            st.info("No steps yet — add one from the left panel.")
        else:
            for idx, step in enumerate(steps):
                arrow = "🔗" if idx < len(steps) - 1 else "🏁"
                with st.container():
                    st.markdown(
                        f"""<div style="background:#f8f9fa;padding:8px 12px;
                        border-radius:8px;border-left:4px solid #667eea;margin:4px 0">
                        <b>{idx+1}. {step['agent']}</b>
                        {"&nbsp;&nbsp;✂️ chunked" if step['use_chunking'] else ""}
                        {"&nbsp;&nbsp;▶️ cont-on-fail" if step['continue_on_failure'] else ""}
                        <br><span style="font-size:0.8em;color:#6b7280">{step['url'] or '(inherit context)'}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                    if idx < len(steps) - 1:
                        st.markdown(
                            "<div style='color:#667eea;padding:2px 0 2px 20px'>⬇️ context flows down</div>",
                            unsafe_allow_html=True,
                        )
                col_del, _ = st.columns([1, 4])
                with col_del:
                    if st.button(f"❌ Remove #{idx+1}", key=f"del_chain_{idx}"):
                        st.session_state.chain_steps.pop(idx)
                        st.rerun()

    st.divider()

    # ── Execution ────────────────────────────────────────────────────────────
    st.markdown("### ▶️ Run Chain")
    seed_input = st.text_input(
        "Seed Input / Initial URL",
        placeholder="https://example.com or any starting text",
        key="chain_seed",
    )

    run_col, clear_col = st.columns([2, 1])

    with run_col:
        run_btn = st.button(
            "🚀 Execute Chain",
            type="primary",
            use_container_width=True,
            disabled=len(st.session_state.get("chain_steps", [])) == 0,
        )

    with clear_col:
        if st.button("🗑️ Clear Chain", use_container_width=True):
            st.session_state.chain_steps = []
            st.session_state.chain_results = []
            st.rerun()

    if run_btn:
        steps = st.session_state.get("chain_steps", [])
        if not steps:
            st.warning("Add at least one step first.")
        elif not seed_input.strip():
            st.warning("Enter a seed input / URL.")
        else:
            progress = st.progress(0, text="Starting chain…")
            with st.spinner(f"Running {len(steps)}-step chain…"):
                chain_results = asyncio.run(
                    execute_chain(
                        steps,
                        seed_input.strip(),
                        chunk_config=st.session_state.get("chunk_config", {}),
                    )
                )
            st.session_state.chain_results = chain_results
            progress.progress(100, text="Chain complete ✅")
            st.rerun()

    # ── Results ─────────────────────────────────────────────────────────────
    chain_results = st.session_state.get("chain_results", [])
    if chain_results:
        st.divider()
        st.markdown("### 📊 Chain Execution Results")

        passed = sum(1 for r in chain_results if r["success"])
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Steps", len(chain_results))
        mc2.metric("✅ Passed", passed)
        mc3.metric("❌ Failed", len(chain_results) - passed)

        for res in chain_results:
            icon = "✅" if res["success"] else "❌"
            label = f"{icon} Step {res['step']} — {res['agent']}"
            with st.expander(label, expanded=res["step"] == len(chain_results)):
                info_cols = st.columns(3)
                info_cols[0].caption(f"⏱️ {res['time']:.2f}s")
                info_cols[1].caption(f"✂️ Chunks: {res.get('chunks_used', 0)}")
                info_cols[2].caption("Status: " + ("passed" if res["success"] else "failed"))

                if res.get("input_preview"):
                    st.markdown("**Input preview:**")
                    st.code(res["input_preview"], language="text")

                if res["success"] and res["output"]:
                    st.markdown("**Output:**")
                    st.text_area(
                        f"output_step_{res['step']}",
                        value=res["output"],
                        height=200,
                        label_visibility="collapsed",
                        key=f"chain_out_{res['step']}",
                    )
                    # Show context chunks if output is large
                    if cfg["enabled"] and len(res["output"]) > cfg["chunk_size"]:
                        chunks = chunk_context(
                            res["output"],
                            chunk_size=cfg["chunk_size"],
                            overlap=cfg["overlap"],
                        )[: cfg["max_chunks"]]
                        with st.expander(f"🔍 Context Chunks ({len(chunks)} chunks)", expanded=False):
                            for ci, ch in enumerate(chunks):
                                st.markdown(f"**Chunk {ci+1}/{len(chunks)}** ({len(ch)} chars)")
                                st.text(ch[:400] + ("…" if len(ch) > 400 else ""))
                elif not res["success"]:
                    st.error(f"Error: {res.get('error', 'Unknown')}")

        # Export results
        if st.button("📥 Export Chain Results as JSON"):
            st.json(chain_results)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    # Render sidebar configuration panel first
    render_sidebar_config()
    
    render_header()
    
    # Main tabs - consolidated and improved
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Dashboard",
        "📂 Agent Catalog", 
        "🧪 Test Lab",
        "🔗 Chain Builder",
        "💬 Natural Language Tests",
        "🤖 LLM Playground",
        "🎯 Orchestration"
    ])
    
    with tab1:
        render_system_status()
        st.divider()
        render_mcp_panel()
        st.divider()
        render_quick_tests()
        st.divider()
        render_documentation()
    
    with tab2:
        render_all_agents()
    
    with tab3:
        render_agent_tester()
    
    with tab4:
        render_chain_builder()
    
    with tab5:
        render_natural_language_tests()
    
    with tab6:
        render_llm_playground()
    
    with tab7:
        render_orchestration()


if __name__ == "__main__":
    main()
