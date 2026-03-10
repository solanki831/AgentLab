"""
🏭 Agent Factory - Create and manage AutoGen agents
Best practices: Dependency injection, error handling, logging
"""

import logging
from typing import Optional, List
from autogen_agentchat.agents import AssistantAgent
from framework.mcp_config import McpConfig

# Configure logging
logger = logging.getLogger(__name__)


class AgentFactoryError(Exception):
    """Custom exception for agent factory errors"""
    pass


class AgentFactory:
    """
    Factory for creating AutoGen agents with MCP workbenches.
    
    Implements factory design pattern with:
    - Dependency injection
    - Comprehensive error handling
    - Logging
    - Configuration management
    """

    def __init__(self, model_client, mcp_config: Optional[McpConfig] = None):
        """
        Initialize the agent factory.
        
        Args:
            model_client: The LLM client (e.g., Ollama, OpenAI)
            mcp_config: Optional MCP configuration (creates default if None)
            
        Raises:
            AgentFactoryError: If model_client is None
        """
        if model_client is None:
            logger.error("model_client cannot be None")
            raise AgentFactoryError("model_client is required")
        
        self.model_client = model_client
        self.mcp_config = mcp_config or McpConfig()
        logger.info("AgentFactory initialized successfully")

    def create_database_agent(self, system_message: Optional[str] = None) -> AssistantAgent:
        """
        Create a Database Agent for MySQL operations.
        
        Args:
            system_message: Custom system message for the agent
            
        Returns:
            AssistantAgent configured for database operations
            
        Raises:
            AgentFactoryError: If agent creation fails
        """
        try:
            if system_message is None:
                system_message = """You are a Database Agent specializing in MySQL operations.
                Your responsibilities:
                1. Execute SQL queries safely
                2. Validate query syntax
                3. Handle database connections
                4. Manage transactions
                5. Provide clear feedback on operation results"""
            
            database_agent = AssistantAgent(
                name="DatabaseAgent",
                model_client=self.model_client,
                workbench=self.mcp_config.get_mysql_workbench(),
                system_message=system_message
            )
            logger.info("DatabaseAgent created successfully")
            return database_agent
        except Exception as e:
            logger.error(f"Failed to create DatabaseAgent: {str(e)}")
            raise AgentFactoryError(f"DatabaseAgent creation failed: {str(e)}")

    def create_api_agent(self, system_message: Optional[str] = None) -> AssistantAgent:
        """
        Create an API Agent for REST API operations.
        
        Args:
            system_message: Custom system message for the agent
            
        Returns:
            AssistantAgent configured for API testing
            
        Raises:
            AgentFactoryError: If agent creation fails
        """
        try:
            if system_message is None:
                system_message = """You are an API Testing Agent specializing in REST APIs.
                Your responsibilities:
                1. Make HTTP requests with appropriate methods
                2. Handle authentication and headers
                3. Parse and validate responses
                4. Manage request payloads
                5. Provide detailed API interaction reports"""
            
            rest_api_workbench = self.mcp_config.get_rest_api_workbench()
            file_system_workbench = self.mcp_config.get_filesystem_workbench()

            api_agent = AssistantAgent(
                name="APIAgent",
                model_client=self.model_client,
                workbench=[rest_api_workbench, file_system_workbench],
                system_message=system_message
            )
            logger.info("APIAgent created successfully")
            return api_agent
        except Exception as e:
            logger.error(f"Failed to create APIAgent: {str(e)}")
            raise AgentFactoryError(f"APIAgent creation failed: {str(e)}")

    def create_excel_agent(self, system_message: Optional[str] = None) -> AssistantAgent:
        """
        Create an Excel Agent for spreadsheet operations.
        
        Args:
            system_message: Custom system message for the agent
            
        Returns:
            AssistantAgent configured for Excel operations
            
        Raises:
            AgentFactoryError: If agent creation fails
        """
        try:
            if system_message is None:
                system_message = """You are an Excel Agent specializing in spreadsheet operations.
                Your responsibilities:
                1. Read and write Excel files
                2. Format cells and ranges
                3. Create formulas and macros
                4. Manage sheets and workbooks
                5. Validate data in spreadsheets"""
            
            excel_workbench = self.mcp_config.get_excel_workbench()

            excel_agent = AssistantAgent(
                name="ExcelAgent",
                model_client=self.model_client,
                workbench=excel_workbench,
                system_message=system_message
            )
            logger.info("ExcelAgent created successfully")
            return excel_agent
        except Exception as e:
            logger.error(f"Failed to create ExcelAgent: {str(e)}")
            raise AgentFactoryError(f"ExcelAgent creation failed: {str(e)}")

    def create_ui_visual_regression_agent(self, system_message: Optional[str] = None) -> AssistantAgent:
        """
        Create a UI/Visual Regression Testing agent.
        
        Captures screenshots across different browsers and viewports, compares them 
        against baselines, and flags visual differences.
        
        Args:
            system_message: Custom system message for the agent
            
        Returns:
            AssistantAgent configured for visual testing
            
        Raises:
            AgentFactoryError: If agent creation fails
        """
        try:
            playwright_workbench = self.mcp_config.get_playwright_workbench()
            
            if system_message is None:
                system_message = """You are a UI/Visual Regression Testing specialist.
                
                Your responsibilities:
                1. Capture screenshots across different browsers (Chrome, Firefox, Safari) and viewports
                2. Compare screenshots against baseline images to detect visual differences
                3. Flag visual regressions (layout shifts, color changes, missing elements)
                4. Generate detailed reports with pixel-level accuracy
                5. Categorize issues by severity (critical, major, minor)
                
                Use Playwright to:
                - Navigate to pages and wait for full load
                - Take full-page and element-specific screenshots
                - Test responsive designs across viewport sizes
                - Verify visual consistency across browser engines
                
                Report all findings with clear descriptions and evidence."""
            
            agent = AssistantAgent(
                name="UIVisualRegressionAgent",
                model_client=self.model_client,
                workbench=playwright_workbench,
                system_message=system_message
            )
            logger.info("UIVisualRegressionAgent created successfully")
            return agent
        except Exception as e:
            logger.error(f"Failed to create UIVisualRegressionAgent: {str(e)}")
            raise AgentFactoryError(f"UIVisualRegressionAgent creation failed: {str(e)}")

    def create_api_contract_testing_agent(self, system_message: Optional[str] = None) -> AssistantAgent:
        """
        Create an API Contract Testing agent.
        
        Validates API responses match their schemas, checks for breaking changes, 
        and monitors response times.
        
        Args:
            system_message: Custom system message for the agent
            
        Returns:
            AssistantAgent configured for API contract testing
            
        Raises:
            AgentFactoryError: If agent creation fails
        """
        try:
            rest_api_workbench = self.mcp_config.get_rest_api_workbench()
            filesystem_workbench = self.mcp_config.get_filesystem_workbench()
            
            if system_message is None:
                system_message = """You are an API Contract Testing specialist.
                
                Your responsibilities:
                1. Validate API responses match defined schemas (OpenAPI/Swagger specs)
                2. Detect breaking changes in API contracts
                3. Monitor API response times and flag performance degradations
                4. Verify status codes, headers, and response formats
                5. Test error handling and edge cases
                6. Compare API behavior across different environments
                
                Alert teams immediately to contract violations."""
            
            agent = AssistantAgent(
                name="APIContractTestingAgent",
                model_client=self.model_client,
                workbench=[rest_api_workbench, filesystem_workbench],
                system_message=system_message
            )
            logger.info("APIContractTestingAgent created successfully")
            return agent
        except Exception as e:
            logger.error(f"Failed to create APIContractTestingAgent: {str(e)}")
            raise AgentFactoryError(f"APIContractTestingAgent creation failed: {str(e)}")

    def create_accessibility_testing_agent(self, system_message: Optional[str] = None) -> AssistantAgent:
        """
        Create an Accessibility Testing agent.
        
        Scans for WCAG compliance issues, keyboard navigation problems, 
        screen reader compatibility, and color contrast violations.
        
        Args:
            system_message: Custom system message for the agent
            
        Returns:
            AssistantAgent configured for accessibility testing
            
        Raises:
            AgentFactoryError: If agent creation fails
        """
        try:
            playwright_workbench = self.mcp_config.get_playwright_workbench()
            
            if system_message is None:
                system_message = """You are an Accessibility Testing specialist focused on WCAG compliance.
                
                Your responsibilities:
                1. Scan pages for WCAG 2.1 Level AA compliance issues
                2. Test keyboard navigation (Tab order, focus indicators, skip links)
                3. Verify screen reader compatibility (ARIA labels, semantic HTML, alt text)
                4. Check color contrast ratios (minimum 4.5:1 for normal text, 3:1 for large text)
                5. Validate form labels, error messages, and input associations
                6. Test focus management in modals, dropdowns, and dynamic content
                
                Categorize findings:
                - Critical: Blocks users from completing tasks
                - Major: Significant barriers
                - Minor: Usability improvements
                
                Provide remediation suggestions with code examples."""
            
            agent = AssistantAgent(
                name="AccessibilityTestingAgent",
                model_client=self.model_client,
                workbench=playwright_workbench,
                system_message=system_message
            )
            logger.info("AccessibilityTestingAgent created successfully")
            return agent
        except Exception as e:
            logger.error(f"Failed to create AccessibilityTestingAgent: {str(e)}")
            raise AgentFactoryError(f"AccessibilityTestingAgent creation failed: {str(e)}")

    def create_data_validation_agent(self, system_message: Optional[str] = None) -> AssistantAgent:
        """
        Create a Data Validation agent.
        
        Monitors databases and data pipelines for anomalies, schema violations, 
        null values, and data quality issues.
        
        Args:
            system_message: Custom system message for the agent
            
        Returns:
            AssistantAgent configured for data validation
            
        Raises:
            AgentFactoryError: If agent creation fails
        """
        try:
            database_workbench = self.mcp_config.get_mysql_workbench()
            filesystem_workbench = self.mcp_config.get_filesystem_workbench()
            
            if system_message is None:
                system_message = """You are a Data Validation and Quality specialist.
                
                Your responsibilities:
                1. Monitor databases for data anomalies and quality issues
                2. Validate data against expected schemas and constraints
                3. Detect null values in columns that should have data
                4. Identify data type mismatches and format violations
                5. Check referential integrity (foreign key consistency)
                6. Monitor for duplicate records
                7. Validate data ranges (dates, numbers within expected bounds)
                8. Track data freshness (last updated timestamps)
                
                Data quality checks:
                - Completeness: Are required fields populated?
                - Accuracy: Do values match expected formats?
                - Consistency: Is data consistent across related tables?
                - Uniqueness: Are unique constraints being honored?
                - Validity: Are values within acceptable ranges?
                
                Generate data quality reports with issue severity and remediation."""
            
            agent = AssistantAgent(
                name="DataValidationAgent",
                model_client=self.model_client,
                workbench=[database_workbench, filesystem_workbench],
                system_message=system_message
            )
            logger.info("DataValidationAgent created successfully")
            return agent
        except Exception as e:
            logger.error(f"Failed to create DataValidationAgent: {str(e)}")
            raise AgentFactoryError(f"DataValidationAgent creation failed: {str(e)}")


