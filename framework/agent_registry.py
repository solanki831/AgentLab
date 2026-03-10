"""
🏭 Agent Registry - Centralized Agent Management
Provides a registry pattern for managing all testing agents with best practices
"""

from typing import Dict, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enumeration of all available agent types"""
    # Original agents
    DATABASE = "database"
    API = "api"
    EXCEL = "excel"
    UI_VISUAL_REGRESSION = "ui_visual_regression"
    API_CONTRACT_TESTING = "api_contract_testing"
    ACCESSIBILITY_TESTING = "accessibility_testing"
    DATA_VALIDATION = "data_validation"
    
    # Extended agents (from advanced_agents.py)
    SECURITY_SCANNING = "security_scanning"
    PERFORMANCE_TESTING = "performance_testing"
    MOBILE_APP_TESTING = "mobile_app_testing"
    GRAPHQL_TESTING = "graphql_testing"
    CHAOS_ENGINEERING = "chaos_engineering"
    COMPLIANCE_CHECKING = "compliance_checking"
    ML_MODEL_TESTING = "ml_model_testing"
    E2E_TESTING = "e2e_testing"
    REPORT_GENERATION = "report_generation"
    LLM_EVALUATION = "llm_evaluation"
    LANGCHAIN_TESTING = "langchain_testing"
    VECTORDB_EVALUATION = "vectordb_evaluation"
    RAG_TESTING = "rag_testing"


@dataclass
class AgentMetadata:
    """Metadata for an agent"""
    type: AgentType
    name: str
    description: str
    capabilities: List[str]
    mcp_tools: List[str]
    category: str  # security, ui, api, data, ml, etc.
    is_async: bool = True
    requires_auth: bool = False
    min_timeout: int = 30
    max_concurrent: int = 5


class AgentRegistry:
    """
    Central registry for all testing agents.
    Provides factory methods and metadata about available agents.
    """
    
    # Agent metadata definitions
    AGENTS_METADATA: Dict[AgentType, AgentMetadata] = {
        # Original Agents from agentFactory.py
        AgentType.DATABASE: AgentMetadata(
            type=AgentType.DATABASE,
            name="DatabaseAgent",
            description="Database connection and query execution",
            capabilities=["Execute queries", "Create connections", "Manage transactions"],
            mcp_tools=["MySQL MCP"],
            category="data",
            requires_auth=True
        ),
        AgentType.API: AgentMetadata(
            type=AgentType.API,
            name="APIAgent",
            description="General API testing and REST operations",
            capabilities=["HTTP requests", "Header manipulation", "Request/response inspection"],
            mcp_tools=["REST API MCP", "Filesystem MCP"],
            category="api"
        ),
        AgentType.EXCEL: AgentMetadata(
            type=AgentType.EXCEL,
            name="ExcelAgent",
            description="Excel file reading, writing, and manipulation",
            capabilities=["Read Excel", "Write Excel", "Format cells", "Create formulas"],
            mcp_tools=["Excel MCP"],
            category="data"
        ),
        AgentType.UI_VISUAL_REGRESSION: AgentMetadata(
            type=AgentType.UI_VISUAL_REGRESSION,
            name="UIVisualRegressionAgent",
            description="UI testing with screenshots and visual diff detection",
            capabilities=["Screenshot capture", "Visual diff", "Multi-browser testing", "Responsive testing"],
            mcp_tools=["Playwright MCP"],
            category="ui",
            requires_auth=True,
            min_timeout=60
        ),
        AgentType.API_CONTRACT_TESTING: AgentMetadata(
            type=AgentType.API_CONTRACT_TESTING,
            name="APIContractTestingAgent",
            description="API schema validation and contract compliance checking",
            capabilities=["Schema validation", "Breaking change detection", "Performance monitoring"],
            mcp_tools=["REST API MCP", "Filesystem MCP"],
            category="api"
        ),
        AgentType.ACCESSIBILITY_TESTING: AgentMetadata(
            type=AgentType.ACCESSIBILITY_TESTING,
            name="AccessibilityTestingAgent",
            description="WCAG compliance and accessibility audit",
            capabilities=["WCAG 2.1 scanning", "Keyboard navigation", "Screen reader compatibility"],
            mcp_tools=["Playwright MCP"],
            category="compliance",
            min_timeout=60
        ),
        AgentType.DATA_VALIDATION: AgentMetadata(
            type=AgentType.DATA_VALIDATION,
            name="DataValidationAgent",
            description="Data quality and ETL validation",
            capabilities=["Data profiling", "Quality checks", "Anomaly detection"],
            mcp_tools=["MySQL MCP", "Filesystem MCP"],
            category="data",
            requires_auth=True
        ),
        
        # Extended Agents from advanced_agents.py
        AgentType.SECURITY_SCANNING: AgentMetadata(
            type=AgentType.SECURITY_SCANNING,
            name="SecurityScanAgent",
            description="Security vulnerability and penetration testing",
            capabilities=["Vulnerability scanning", "SSL/TLS checking", "Header analysis", "Injection testing"],
            mcp_tools=["REST API MCP"],
            category="security"
        ),
        AgentType.PERFORMANCE_TESTING: AgentMetadata(
            type=AgentType.PERFORMANCE_TESTING,
            name="PerformanceTestAgent",
            description="Load testing, stress testing, and performance profiling",
            capabilities=["Load testing", "Latency measurement", "Throughput analysis"],
            mcp_tools=["REST API MCP"],
            category="performance"
        ),
        AgentType.MOBILE_APP_TESTING: AgentMetadata(
            type=AgentType.MOBILE_APP_TESTING,
            name="MobileAppTestAgent",
            description="Mobile application testing across devices and OS versions",
            capabilities=["Device emulation", "Responsive design", "Touch interaction", "Network throttling"],
            mcp_tools=["Playwright MCP"],
            category="ui",
            requires_auth=True
        ),
        AgentType.GRAPHQL_TESTING: AgentMetadata(
            type=AgentType.GRAPHQL_TESTING,
            name="GraphQLTestAgent",
            description="GraphQL API testing and query validation",
            capabilities=["Query execution", "Schema validation", "Performance monitoring"],
            mcp_tools=["REST API MCP"],
            category="api"
        ),
        AgentType.CHAOS_ENGINEERING: AgentMetadata(
            type=AgentType.CHAOS_ENGINEERING,
            name="ChaosEngineeringAgent",
            description="Resilience and fault tolerance testing",
            capabilities=["Latency injection", "Error injection", "Resource stress", "Network disruption"],
            mcp_tools=["REST API MCP"],
            category="reliability"
        ),
        AgentType.COMPLIANCE_CHECKING: AgentMetadata(
            type=AgentType.COMPLIANCE_CHECKING,
            name="ComplianceCheckAgent",
            description="Regulatory compliance verification (GDPR, HIPAA, SOC2, PCI-DSS)",
            capabilities=["GDPR scanning", "HIPAA validation", "SOC2 assessment", "PCI-DSS check"],
            mcp_tools=["REST API MCP", "Filesystem MCP"],
            category="compliance"
        ),
        AgentType.ML_MODEL_TESTING: AgentMetadata(
            type=AgentType.ML_MODEL_TESTING,
            name="MLModelTestAgent",
            description="Machine learning model validation and inference testing",
            capabilities=["Model validation", "Inference testing", "Bias detection", "Performance metrics"],
            mcp_tools=["REST API MCP"],
            category="ml"
        ),
        AgentType.E2E_TESTING: AgentMetadata(
            type=AgentType.E2E_TESTING,
            name="E2ETestAgent",
            description="End-to-end workflow testing with user scenarios",
            capabilities=["User scenario execution", "Multi-step workflows", "State validation", "Authentication flows"],
            mcp_tools=["Playwright MCP"],
            category="ui",
            requires_auth=True,
            min_timeout=120
        ),
        AgentType.REPORT_GENERATION: AgentMetadata(
            type=AgentType.REPORT_GENERATION,
            name="ReportGenerationAgent",
            description="Comprehensive test report generation and analysis",
            capabilities=["Report generation", "Data aggregation", "Trend analysis", "Export to multiple formats"],
            mcp_tools=["Excel MCP", "Filesystem MCP"],
            category="reporting"
        ),
        AgentType.LLM_EVALUATION: AgentMetadata(
            type=AgentType.LLM_EVALUATION,
            name="LLMEvaluationAgent",
            description="Comprehensive LLM evaluation with benchmarks: accuracy, reasoning, math, code, hallucination",
            capabilities=["Factual accuracy testing", "Reasoning evaluation", "Math problem solving", "Code generation", "Instruction following", "Hallucination detection"],
            mcp_tools=[],
            category="llm",
            is_async=True,
            min_timeout=300
        ),
        AgentType.LANGCHAIN_TESTING: AgentMetadata(
            type=AgentType.LANGCHAIN_TESTING,
            name="LangChainTestAgent",
            description="LangChain framework testing: chains, memory, tools, error handling",
            capabilities=["QA chain testing", "Summarization testing", "Translation testing", "Memory management", "Tool usage", "Error handling"],
            mcp_tools=[],
            category="llm",
            is_async=True,
            min_timeout=300
        ),
        AgentType.VECTORDB_EVALUATION: AgentMetadata(
            type=AgentType.VECTORDB_EVALUATION,
            name="VectorDBEvaluationAgent",
            description="Vector database performance and quality evaluation",
            capabilities=["Connection testing", "Write performance", "Query latency", "Search accuracy", "Scalability testing", "Memory profiling", "Cost analysis"],
            mcp_tools=[],
            category="database",
            is_async=True,
            min_timeout=300
        ),
        AgentType.RAG_TESTING: AgentMetadata(
            type=AgentType.RAG_TESTING,
            name="RAGEvaluationAgent",
            description="RAG pipeline evaluation: retrieval, augmentation, and generation quality",
            capabilities=["Document ingestion", "Embedding quality", "Retrieval accuracy", "Generation quality", "Hallucination detection", "End-to-end latency"],
            mcp_tools=[],
            category="llm",
            is_async=True,
            min_timeout=300
        ),
    }
    
    def __init__(self):
        """Initialize the agent registry"""
        self._agent_cache: Dict[AgentType, object] = {}
        self._factory = None
        logger.info(f"Initialized AgentRegistry with {len(self.AGENTS_METADATA)} agents")
    
    def set_factory(self, factory):
        """Set the agent factory for creating agent instances"""
        self._factory = factory
        logger.info("AgentFactory injected into registry")
    
    def get_metadata(self, agent_type: AgentType) -> Optional[AgentMetadata]:
        """Get metadata for an agent type"""
        return self.AGENTS_METADATA.get(agent_type)
    
    def get_all_metadata(self) -> Dict[AgentType, AgentMetadata]:
        """Get metadata for all agents"""
        return self.AGENTS_METADATA.copy()
    
    def get_agents_by_category(self, category: str) -> Dict[AgentType, AgentMetadata]:
        """Get all agents of a specific category"""
        return {
            agent_type: metadata 
            for agent_type, metadata in self.AGENTS_METADATA.items()
            if metadata.category == category
        }
    
    def get_agent_instance(self, agent_type: AgentType):
        """Get or create an agent instance"""
        if not self._factory:
            logger.error("AgentFactory not set. Call set_factory() first.")
            raise RuntimeError("AgentFactory not initialized")
        
        # Check cache first
        if agent_type in self._agent_cache:
            logger.debug(f"Returning cached agent: {agent_type.value}")
            return self._agent_cache[agent_type]
        
        # Create new instance based on type
        try:
            if agent_type == AgentType.DATABASE:
                agent = self._factory.create_database_agent(None)
            elif agent_type == AgentType.API:
                agent = self._factory.create_api_agent(None)
            elif agent_type == AgentType.EXCEL:
                agent = self._factory.create_excel_agent()
            elif agent_type == AgentType.UI_VISUAL_REGRESSION:
                agent = self._factory.create_ui_visual_regression_agent()
            elif agent_type == AgentType.API_CONTRACT_TESTING:
                agent = self._factory.create_api_contract_testing_agent()
            elif agent_type == AgentType.ACCESSIBILITY_TESTING:
                agent = self._factory.create_accessibility_testing_agent()
            elif agent_type == AgentType.DATA_VALIDATION:
                agent = self._factory.create_data_validation_agent()
            else:
                logger.warning(f"No factory method for agent type: {agent_type}")
                return None
            
            # Cache the instance
            self._agent_cache[agent_type] = agent
            logger.info(f"Created and cached agent: {agent_type.value}")
            return agent
        
        except Exception as e:
            logger.error(f"Failed to create agent {agent_type.value}: {str(e)}")
            raise
    
    def clear_cache(self):
        """Clear the agent cache"""
        self._agent_cache.clear()
        logger.info("Cleared agent cache")
    
    def list_agents(self) -> List[str]:
        """List all available agent names"""
        return [
            f"{metadata.name} ({metadata.category})" 
            for metadata in self.AGENTS_METADATA.values()
        ]
    
    def get_agent_info(self, agent_type: AgentType) -> str:
        """Get formatted agent information"""
        metadata = self.get_metadata(agent_type)
        if not metadata:
            return f"Unknown agent: {agent_type}"
        
        return f"""
{metadata.name}
{'=' * len(metadata.name)}
Description: {metadata.description}
Category: {metadata.category}
Capabilities:
{chr(10).join(f"  • {cap}" for cap in metadata.capabilities)}
MCP Tools: {', '.join(metadata.mcp_tools)}
Requires Auth: {metadata.requires_auth}
Min Timeout: {metadata.min_timeout}s
Max Concurrent: {metadata.max_concurrent}
"""


# Global registry instance
_global_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global agent registry (singleton pattern)"""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry


def reset_registry():
    """Reset the global registry (useful for testing)"""
    global _global_registry
    _global_registry = None
