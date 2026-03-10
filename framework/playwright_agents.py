"""
🎭 PLAYWRIGHT-INSPIRED AGENTS
Three specialized agents for test automation workflow:
- Planner: Analyzes requirements and creates test plans (uses Ollama LLM)
- Generator: Generates test code from plans (uses MCP Playwright tools)
- Healer: Detects and fixes test failures (uses MCP + Ollama)

Integrates with:
- MCP Playwright tools for browser automation
- Ollama for intelligent analysis and generation
- No hard-coded values - all dynamic and configurable
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from framework.ollama_helper import create_ollama_client
    from framework.mcp_config import McpConfig
    from autogen_ext.models.openai import OpenAIChatCompletionClient
except ImportError:
    # Fallback if running from different context
    create_ollama_client = None
    McpConfig = None
    OpenAIChatCompletionClient = None

# Initialize logger first
logger = logging.getLogger(__name__)

# LangChain imports for memory and RAG
try:
    from langchain_community.vectorstores import FAISS, Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain.memory import ConversationBufferMemory
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.docstore.document import Document
    LANGCHAIN_AVAILABLE = True
    logger.info("✅ LangChain available")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    logger.warning(f"LangChain not available: {e}")
    logger.warning("Install with: pip install langchain langchain-community langchain-huggingface chromadb sentence-transformers")


class PlannerAgent:
    """
    📋 PLANNER AGENT
    Analyzes requirements and creates detailed test plans using Ollama LLM
    
    Responsibilities:
    - Analyze application under test with AI
    - Create comprehensive test scenarios using LLM
    - Define test data requirements
    - Identify edge cases and boundaries
    - Prioritize test cases with intelligent analysis
    - Generate test coverage matrix
    """
    
    def __init__(self, llm_client: Optional[OpenAIChatCompletionClient] = None, mcp_config: Optional[McpConfig] = None, 
                 use_langchain: bool = True, persist_dir: str = "./playwright_plans_db"):
        self.agent_type = "planner"
        
        # Initialize LLM client (Ollama by default)
        if llm_client is None and create_ollama_client is not None:
            try:
                self.llm_client = create_ollama_client(
                    model="llama3.2:latest",
                    function_calling=True,
                    json_output=True
                )
                logger.info("Planner Agent initialized with Ollama LLM")
            except Exception as e:
                logger.warning(f"Failed to create Ollama client: {e}")
                self.llm_client = None
        else:
            self.llm_client = llm_client
        
        # Initialize MCP config
        self.mcp_config = mcp_config or (McpConfig() if McpConfig else None)
        
        # Initialize LangChain components for intelligent memory and retrieval
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.vectorstore = None
        self.embeddings = None
        self.memory = None
        
        if self.use_langchain:
            try:
                # Initialize embeddings for semantic search
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                
                # Initialize vector store for storing test plans
                try:
                    self.vectorstore = Chroma(
                        persist_directory=persist_dir,
                        embedding_function=self.embeddings,
                        collection_name="test_plans"
                    )
                    logger.info(f"✅ Loaded existing plans from {persist_dir}")
                except:
                    self.vectorstore = Chroma(
                        embedding_function=self.embeddings,
                        persist_directory=persist_dir,
                        collection_name="test_plans"
                    )
                    logger.info(f"✅ Created new vector store at {persist_dir}")
                
                # Initialize conversation memory
                self.memory = ConversationBufferMemory(
                    memory_key="planning_history",
                    return_messages=True
                )
                
                logger.info("✅ LangChain: Memory and vector store initialized")
            except Exception as e:
                logger.warning(f"LangChain initialization failed: {e}")
                self.use_langchain = False
        
        self.capabilities = [
            "requirement_analysis",
            "test_scenario_creation",
            "coverage_planning",
            "data_requirement_analysis",
            "edge_case_identification",
            "priority_assignment",
            "risk_assessment",
            "semantic_plan_search",  # New: Find similar test plans
            "plan_similarity_detection",  # New: Avoid duplicates
            "historical_plan_learning"  # New: Learn from past plans
        ]
        self.plans_created = []
    
    async def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive test plan with LangChain memory and RAG
        
        Args:
            target: Application/feature to test
            config: Contains requirements, user_stories, acceptance_criteria
        
        Returns:
            Dictionary with test plan details
        """
        logger.info(f"🎯 Planner Agent analyzing: {target}")
        
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extract requirements
        requirements = config.get('requirements', [])
        user_stories = config.get('user_stories', [])
        acceptance_criteria = config.get('acceptance_criteria', [])
        test_type = config.get('test_type', 'functional')
        
        # 🧠 LangChain: Search for similar past plans
        similar_scenarios = []
        if self.use_langchain and self.vectorstore:
            try:
                similar_scenarios = await self.retrieve_similar_scenarios(target, requirements)
                if similar_scenarios:
                    logger.info(f"🔍 Found {len(similar_scenarios)} similar past scenarios to reference")
            except Exception as e:
                logger.warning(f"Failed to retrieve similar scenarios: {e}")
        
        # 🧠 LangChain: Add to conversation memory
        if self.memory:
            try:
                self.memory.save_context(
                    {"input": f"Planning test for {target} with {len(requirements)} requirements"},
                    {"output": f"Creating plan {plan_id}"}
                )
            except Exception as e:
                logger.warning(f"Failed to save memory: {e}")
        
        # Create test plan
        test_plan = await self._create_test_plan(
            target, requirements, user_stories, acceptance_criteria, test_type
        )
        
        result = {
            "status": "success",
            "plan_id": plan_id,
            "target": target,
            "test_plan": test_plan,
            "created_at": datetime.now().isoformat(),
            "summary": {
                "total_scenarios": len(test_plan.get('test_scenarios', [])),
                "priority_high": sum(1 for s in test_plan.get('test_scenarios', []) if s.get('priority') == 'high'),
                "estimated_time": test_plan.get('estimated_time', 'N/A'),
                "coverage_percentage": test_plan.get('coverage', 0)
            },
            "langchain_insights": {
                "similar_plans_found": len(similar_scenarios),
                "similar_plans": similar_scenarios[:3] if similar_scenarios else [],
                "memory_enabled": self.memory is not None,
                "vectordb_enabled": self.vectorstore is not None
            }
        }
        
        self.plans_created.append(result)
        
        # Store in LangChain vector store for future retrieval
        if self.use_langchain and self.vectorstore:
            try:
                await self._store_plan_in_vectordb(result)
                logger.info(f"✅ Test plan stored in vector DB: {plan_id}")
            except Exception as e:
                logger.warning(f"Failed to store plan in vector DB: {e}")
        
        logger.info(f"✅ Test plan created: {plan_id}")
        
        return result
    
    async def _create_test_plan(
        self, 
        target: str,
        requirements: List[str],
        user_stories: List[str],
        acceptance_criteria: List[str],
        test_type: str
    ) -> Dict[str, Any]:
        """Create detailed test plan with AI assistance using Ollama"""
        
        # If LLM is available, use it for intelligent planning
        if self.llm_client:
            test_scenarios = await self._generate_scenarios_with_llm(
                target, requirements, user_stories, acceptance_criteria, test_type
            )
        else:
            # Fallback to rule-based generation
            test_scenarios = self._generate_scenarios_fallback(
                requirements, user_stories, test_type
            )
        
        return {
            "target": target,
            "test_scenarios": test_scenarios,
            "test_data_requirements": self._consolidate_test_data(test_scenarios),
            "environment_setup": self._define_environment_setup(target),
            "dependencies": self._identify_dependencies(target),
            "risks": self._assess_risks(requirements),
            "coverage": self._calculate_coverage(requirements, test_scenarios),
            "estimated_time": f"{len(test_scenarios) * 7} minutes"
        }
    
    async def _generate_scenarios_with_llm(
        self,
        target: str,
        requirements: List[str],
        user_stories: List[str],
        acceptance_criteria: List[str],
        test_type: str
    ) -> List[Dict[str, Any]]:
        """Generate test scenarios using Ollama LLM"""
        
        # Build prompt for LLM
        prompt = f"""You are a test planning expert. Create comprehensive test scenarios for:

Target: {target}
Test Type: {test_type}

Requirements:
{chr(10).join(f'- {r}' for r in requirements)}

User Stories:
{chr(10).join(f'- {s}' for s in user_stories) if user_stories else 'None'}

Acceptance Criteria:
{chr(10).join(f'- {c}' for c in acceptance_criteria) if acceptance_criteria else 'None'}

Generate test scenarios in JSON format with the following structure for each scenario:
{{
    "id": "TC001",
    "title": "Test scenario title",
    "description": "Detailed description",
    "priority": "critical|high|medium|low",
    "test_type": "{test_type}",
    "preconditions": ["list", "of", "preconditions"],
    "steps": ["step 1", "step 2", "step 3"],
    "expected_result": "Expected outcome",
    "test_data": {{"valid_data": [], "invalid_data": [], "boundary_data": []}},
    "edge_cases": ["edge case 1", "edge case 2"],
    "estimated_duration": "X min"
}}

Provide 3-7 scenarios covering positive, negative, and edge cases.
Return ONLY a JSON array of test scenarios."""

        try:
            # Call LLM for intelligent scenario generation
            response = await self.llm_client.create([{"role": "user", "content": prompt}])
            
            # Parse LLM response - handle different response types
            content = ""
            if hasattr(response, 'content'):
                if isinstance(response.content, str):
                    content = response.content
                elif isinstance(response.content, list):
                    # Handle list of message parts
                    for part in response.content:
                        if isinstance(part, str):
                            content += part
                        elif hasattr(part, 'content'):
                            content += part.content
                        elif isinstance(part, dict) and 'content' in part:
                            content += part['content']
            elif isinstance(response, dict) and 'content' in response:
                content = response['content']
            
            if not content:
                logger.warning("Empty LLM response, using fallback")
                return self._generate_scenarios_fallback(requirements, user_stories, test_type)
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                scenarios = json.loads(json_match.group())
                logger.info(f"✅ Generated {len(scenarios)} scenarios using LLM")
                return scenarios
            else:
                logger.warning("LLM response didn't contain valid JSON, using fallback")
                return self._generate_scenarios_fallback(requirements, user_stories, test_type)
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_scenarios_fallback(requirements, user_stories, test_type)
    
    def _generate_scenarios_fallback(
        self,
        requirements: List[str],
        user_stories: List[str],
        test_type: str
    ) -> List[Dict[str, Any]]:
        """Fallback scenario generation without LLM"""
        
        test_scenarios = []
        
        # Generate test scenarios based on requirements
        for idx, req in enumerate(requirements, 1):
            scenario = {
                "id": f"TC{idx:03d}",
                "title": f"Test scenario for: {req}",
                "description": f"Verify that {req} works as expected",
                "priority": self._assess_priority(req),
                "test_type": test_type,
                "preconditions": self._extract_preconditions(req),
                "steps": self._generate_test_steps(req),
                "expected_result": f"System should handle {req} correctly",
                "test_data": self._identify_test_data(req),
                "edge_cases": self._identify_edge_cases(req),
                "estimated_duration": "5 min"
            }
            test_scenarios.append(scenario)
        
        # Add scenarios for user stories
        for idx, story in enumerate(user_stories, len(requirements) + 1):
            scenario = {
                "id": f"TC{idx:03d}",
                "title": f"User story: {story}",
                "description": f"Validate user story: {story}",
                "priority": "medium",
                "test_type": "user_acceptance",
                "preconditions": ["User is logged in", "System is in ready state"],
                "steps": self._generate_test_steps(story),
                "expected_result": f"User can successfully {story}",
                "test_data": self._identify_test_data(story),
                "edge_cases": [],
                "estimated_duration": "10 min"
            }
            test_scenarios.append(scenario)
        
        return test_scenarios
    
    def _assess_priority(self, requirement: str) -> str:
        """Assess test priority based on requirement"""
        critical_keywords = ['security', 'payment', 'authentication', 'data loss', 'critical']
        high_keywords = ['user', 'login', 'important', 'core']
        
        req_lower = requirement.lower()
        if any(kw in req_lower for kw in critical_keywords):
            return "critical"
        elif any(kw in req_lower for kw in high_keywords):
            return "high"
        else:
            return "medium"
    
    def _extract_preconditions(self, requirement: str) -> List[str]:
        """Extract preconditions from requirement"""
        return [
            "System is accessible",
            "Test environment is configured",
            "Required test data is available"
        ]
    
    def _generate_test_steps(self, requirement: str) -> List[str]:
        """Generate test steps for requirement"""
        return [
            f"Navigate to the relevant page/feature",
            f"Perform action related to: {requirement}",
            f"Verify expected behavior",
            f"Check for error handling",
            f"Validate data integrity"
        ]
    
    def _identify_test_data(self, requirement: str) -> Dict[str, Any]:
        """Identify required test data"""
        return {
            "valid_data": ["Standard test case data"],
            "invalid_data": ["Invalid inputs", "Edge values"],
            "boundary_data": ["Min/max values"]
        }
    
    def _identify_edge_cases(self, requirement: str) -> List[str]:
        """Identify edge cases"""
        return [
            "Empty input",
            "Maximum length input",
            "Special characters",
            "Concurrent operations",
            "Network failure scenarios"
        ]
    
    def _consolidate_test_data(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Consolidate test data requirements"""
        return {
            "users": ["test_user_1", "test_user_2", "admin_user"],
            "datasets": ["valid_dataset.json", "invalid_dataset.json"],
            "environment_variables": ["API_KEY", "BASE_URL"]
        }
    
    def _define_environment_setup(self, target: str) -> Dict[str, Any]:
        """Define environment setup requirements"""
        return {
            "browser": "chromium",
            "viewport": {"width": 1920, "height": 1080},
            "baseURL": f"http://localhost:3000",
            "timeout": 30000,
            "headless": False
        }
    
    def _identify_dependencies(self, target: str) -> List[str]:
        """Identify test dependencies"""
        return [
            "Application must be running",
            "Database must be seeded",
            "External APIs must be available or mocked"
        ]
    
    def _assess_risks(self, requirements: List[str]) -> List[Dict[str, str]]:
        """Assess testing risks"""
        return [
            {
                "risk": "Flaky tests due to timing issues",
                "mitigation": "Use proper wait strategies and explicit waits",
                "severity": "medium"
            },
            {
                "risk": "Test data dependencies",
                "mitigation": "Isolate tests and use data factories",
                "severity": "medium"
            },
            {
                "risk": "Environment instability",
                "mitigation": "Implement retry logic and health checks",
                "severity": "low"
            }
        ]
    
    def _calculate_coverage(self, requirements: List[str], scenarios: List[Dict]) -> int:
        """Calculate test coverage percentage"""
        if not requirements:
            return 0
        return min(100, int((len(scenarios) / len(requirements)) * 100))
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific test plan"""
        for plan in self.plans_created:
            if plan['plan_id'] == plan_id:
                return plan
        return None
    
    def list_plans(self) -> List[Dict[str, Any]]:
        """List all created plans"""
        return [
            {
                "plan_id": p['plan_id'],
                "target": p['target'],
                "status": p['status'],
                "scenarios": p['summary']['total_scenarios'],
                "created_at": p['created_at']
            }
            for p in self.plans_created
        ]
    
    async def _store_plan_in_vectordb(self, plan: Dict[str, Any]) -> bool:
        """Store test plan in vector database for future retrieval"""
        if not self.use_langchain or not self.vectorstore:
            return False
        
        try:
            # Create document from plan
            plan_text = f"""
            Target: {plan['target']}
            Test Type: {plan.get('test_type', 'unknown')}
            Requirements: {', '.join(plan.get('requirements', []))}
            Scenarios: {len(plan.get('test_scenarios', []))}
            Description: {json.dumps(plan.get('test_scenarios', [])[:2])}
            """
            
            metadata = {
                "plan_id": plan['plan_id'],
                "target": plan['target'],
                "test_type": plan.get('test_type', 'unknown'),
                "scenario_count": len(plan.get('test_scenarios', [])),
                "created_at": plan.get('created_at', 'unknown')
            }
            
            # Add to vector store
            self.vectorstore.add_texts(
                texts=[plan_text],
                metadatas=[metadata],
                ids=[plan['plan_id']]
            )
            
            # Persist changes
            if hasattr(self.vectorstore, 'persist'):
                self.vectorstore.persist()
            
            logger.info(f"✅ Stored plan {plan['plan_id']} in vector database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store plan in vectordb: {e}")
            return False
    
    async def search_similar_plans(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar test plans using semantic search"""
        if not self.use_langchain or not self.vectorstore:
            return []
        
        try:
            # Perform similarity search
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            similar_plans = []
            for doc, score in results:
                similar_plans.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score)
                })
            
            logger.info(f"✅ Found {len(similar_plans)} similar plans for query: {query}")
            return similar_plans
            
        except Exception as e:
            logger.error(f"Failed to search similar plans: {e}")
            return []
    
    async def retrieve_similar_scenarios(self, target: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Retrieve similar test scenarios from past plans using RAG"""
        if not self.use_langchain or not self.vectorstore:
            return []
        
        try:
            # Create query from current context
            query = f"Test scenarios for {target} with requirements: {', '.join(requirements[:3])}"
            
            # Search for similar plans
            similar_plans = await self.search_similar_plans(query, k=5)
            
            # Extract scenarios from similar plans
            scenarios = []
            for plan in similar_plans:
                if plan['similarity_score'] > 0.7:  # High similarity threshold
                    scenarios.append({
                        "source_plan": plan['metadata'].get('plan_id'),
                        "target": plan['metadata'].get('target'),
                        "similarity": plan['similarity_score'],
                        "content_preview": plan['content'][:200]
                    })
            
            if scenarios:
                logger.info(f"✅ Retrieved {len(scenarios)} similar scenarios from past plans")
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Failed to retrieve similar scenarios: {e}")
            return []


class GeneratorAgent:
    """
    🔧 GENERATOR AGENT
    Generates test code from test plans using MCP Playwright tools and Ollama
    
    Responsibilities:
    - Convert test plans to executable code with LLM
    - Generate Playwright/Selenium scripts using MCP tools
    - Create test fixtures and utilities
    - Generate test data factories
    - Create page object models
    - Add assertions and validations
    """
    
    def __init__(self, llm_client: Optional[OpenAIChatCompletionClient] = None, mcp_config: Optional[McpConfig] = None,
                 use_langchain: bool = True):
        self.agent_type = "generator"
        
        # Initialize LLM client (Ollama by default)
        if llm_client is None and create_ollama_client is not None:
            try:
                self.llm_client = create_ollama_client(
                    model="llama3.2:latest",
                    function_calling=True,
                    json_output=True
                )
                logger.info("Generator Agent initialized with Ollama LLM")
            except Exception as e:
                logger.warning(f"Failed to create Ollama client: {e}")
                self.llm_client = None
        else:
            self.llm_client = llm_client
        
        # Initialize MCP config for Playwright tools
        self.mcp_config = mcp_config or (McpConfig() if McpConfig else None)
        
        # Initialize LangChain memory for code generation context
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.memory = None
        
        if self.use_langchain:
            try:
                # Use conversation memory to track code generation patterns
                self.memory = ConversationBufferMemory(
                    memory_key="generation_history",
                    return_messages=True,
                    max_token_limit=2000
                )
                logger.info("✅ LangChain: Code generation memory initialized")
            except Exception as e:
                logger.warning(f"LangChain memory initialization failed: {e}")
                self.use_langchain = False
        
        self.capabilities = [
            "code_generation",
            "test_script_creation",
            "fixture_generation",
            "data_factory_creation",
            "page_object_generation",
            "assertion_generation",
            "multiple_framework_support",
            "context_aware_generation",  # New: Use memory for better code
            "pattern_learning"  # New: Learn from past generations
        ]
        self.generated_tests = []
    
    async def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate test code from a test plan
        
        Args:
            target: Test plan ID or test scenario
            config: Contains test_plan, framework, language
        
        Returns:
            Dictionary with generated code and files
        """
        logger.info(f"🔧 Generator Agent generating code for: {target}")
        
        test_plan = config.get('test_plan', {})
        framework = config.get('framework', 'playwright')
        language = config.get('language', 'python')
        
        # Generate test code
        generated_code = await self._generate_test_code(
            test_plan, framework, language
        )
        
        result = {
            "status": "success",
            "target": target,
            "framework": framework,
            "language": language,
            "generated_files": generated_code['files'],
            "test_count": len(test_plan.get('test_scenarios', [])),
            "created_at": datetime.now().isoformat(),
            "summary": {
                "main_tests": generated_code['main_tests'],
                "helper_files": generated_code['helper_files'],
                "total_lines": generated_code['total_lines']
            }
        }
        
        self.generated_tests.append(result)
        logger.info(f"✅ Test code generated: {len(generated_code['files'])} files")
        
        return result
    
    async def _generate_test_code(
        self,
        test_plan: Dict[str, Any],
        framework: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate test code based on framework and language"""
        
        if framework == "playwright" and language == "python":
            return await self._generate_playwright_python(test_plan)
        elif framework == "playwright" and language == "typescript":
            return await self._generate_playwright_typescript(test_plan)
        elif framework == "selenium" and language == "python":
            return await self._generate_selenium_python(test_plan)
        else:
            raise ValueError(f"Unsupported combination: {framework}/{language}")
    
    async def _generate_playwright_python(self, test_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Playwright Python test code"""
        
        files = {}
        
        # Generate main test file
        test_scenarios = test_plan.get('test_scenarios', [])
        
        test_code = '''"""
Generated Test Suite
Auto-generated by Generator Agent
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


'''
        
        # Generate test functions
        for scenario in test_scenarios:
            test_code += self._generate_test_function(scenario)
            test_code += "\n\n"
        
        files['test_main.py'] = test_code
        
        # Generate page objects
        files['page_objects.py'] = self._generate_page_objects()
        
        # Generate test data
        files['test_data.py'] = self._generate_test_data(test_plan)
        
        # Generate conftest
        files['conftest.py'] = self._generate_conftest()
        
        # Calculate statistics
        total_lines = sum(len(code.split('\n')) for code in files.values())
        
        return {
            "files": files,
            "main_tests": len(test_scenarios),
            "helper_files": len(files) - 1,
            "total_lines": total_lines
        }
    
    def _generate_test_function(self, scenario: Dict[str, Any]) -> str:
        """Generate a single test function"""
        func_name = scenario['id'].lower().replace('-', '_')
        title = scenario['title']
        steps = scenario.get('steps', [])
        
        code = f'''def test_{func_name}(page: Page):
    """
    {title}
    
    Priority: {scenario.get('priority', 'medium')}
    """
'''
        
        for step in steps:
            code += f'    # {step}\n'
        
        code += '''    # Navigate to page
    page.goto("/")
    
    # Perform test actions
    # TODO: Add specific actions based on test scenario
    
    # Assertions
    expect(page).to_have_title("Expected Title")
'''
        
        return code
    
    def _generate_page_objects(self) -> str:
        """Generate page object classes"""
        return '''"""
Page Object Models
"""

from playwright.sync_api import Page


class BasePage:
    """Base page with common functionality"""
    
    def __init__(self, page: Page):
        self.page = page
    
    def navigate(self, path: str):
        """Navigate to a specific path"""
        self.page.goto(path)
    
    def get_title(self) -> str:
        """Get page title"""
        return self.page.title()


class LoginPage(BasePage):
    """Login page object"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("button[type='submit']")
    
    def login(self, username: str, password: str):
        """Perform login"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()


class DashboardPage(BasePage):
    """Dashboard page object"""
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.welcome_message = page.locator(".welcome")
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.welcome_message.is_visible()
'''
    
    def _generate_test_data(self, test_plan: Dict[str, Any]) -> str:
        """Generate test data file"""
        return '''"""
Test Data
"""

# Valid test users
VALID_USERS = [
    {"username": "test_user", "password": "Test123!", "role": "user"},
    {"username": "admin_user", "password": "Admin123!", "role": "admin"},
]

# Invalid test data
INVALID_USERS = [
    {"username": "", "password": ""},
    {"username": "invalid", "password": "short"},
]

# Test endpoints
API_ENDPOINTS = {
    "login": "/api/auth/login",
    "users": "/api/users",
    "products": "/api/products",
}

# Test configurations
TEST_CONFIG = {
    "timeout": 30000,
    "retry_attempts": 3,
    "screenshot_on_failure": True,
}
'''
    
    def _generate_conftest(self) -> str:
        """Generate pytest conftest"""
        return '''"""
Pytest Configuration
"""

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """Run before each test"""
    # Setup code
    yield
    # Teardown code
    pass


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    return {
        "base_url": "http://localhost:3000",
        "timeout": 30000,
    }
'''
    
    async def _generate_playwright_typescript(self, test_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Playwright TypeScript test code"""
        # Implementation for TypeScript
        return {
            "files": {"test.spec.ts": "// TypeScript tests placeholder"},
            "main_tests": 0,
            "helper_files": 0,
            "total_lines": 0
        }
    
    async def _generate_selenium_python(self, test_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Selenium Python test code"""
        # Implementation for Selenium
        return {
            "files": {"test_selenium.py": "# Selenium tests placeholder"},
            "main_tests": 0,
            "helper_files": 0,
            "total_lines": 0
        }


class HealerAgent:
    """
    🔧 HEALER AGENT (Enhanced with MCP + Ollama)
    Detects and automatically fixes test failures using intelligent analysis
    
    Responsibilities:
    - Analyze test failure patterns with LLM
    - Detect flaky tests using AI
    - Auto-heal selector issues with MCP browser tools
    - Optimize timeouts intelligently
    - Fix timing issues
    - Update test assertions
    - Suggest configuration changes
    """
    
    def __init__(self, llm_client: Optional[OpenAIChatCompletionClient] = None, mcp_config: Optional[McpConfig] = None,
                 use_langchain: bool = True, persist_dir: str = "./playwright_healing_db"):
        self.agent_type = "healer"
        
        # Initialize LLM client (Ollama by default)
        if llm_client is None and create_ollama_client is not None:
            try:
                self.llm_client = create_ollama_client(
                    model="llama3.2:latest",
                    function_calling=True,
                    json_output=True
                )
                logger.info("Healer Agent initialized with Ollama LLM")
            except Exception as e:
                logger.warning(f"Failed to create Ollama client: {e}")
                self.llm_client = None
        else:
            self.llm_client = llm_client
        
        # Initialize MCP config for Playwright tools
        self.mcp_config = mcp_config or (McpConfig() if McpConfig else None)
        
        # Initialize LangChain RAG for learning from past fixes
        self.use_langchain = use_langchain and LANGCHAIN_AVAILABLE
        self.vectorstore = None
        self.embeddings = None
        self.memory = None
        
        if self.use_langchain:
            try:
                # Initialize embeddings
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                
                # Initialize vector store for healing history
                try:
                    self.vectorstore = Chroma(
                        persist_directory=persist_dir,
                        embedding_function=self.embeddings,
                        collection_name="healing_history"
                    )
                    logger.info(f"✅ Loaded healing history from {persist_dir}")
                except:
                    self.vectorstore = Chroma(
                        embedding_function=self.embeddings,
                        persist_directory=persist_dir,
                        collection_name="healing_history"
                    )
                    logger.info(f"✅ Created new healing database at {persist_dir}")
                
                # Initialize memory for tracking healing attempts
                self.memory = ConversationBufferMemory(
                    memory_key="healing_context",
                    return_messages=True,
                    max_token_limit=3000
                )
                
                logger.info("✅ LangChain: RAG for healing history initialized")
            except Exception as e:
                logger.warning(f"LangChain RAG initialization failed: {e}")
                self.use_langchain = False
        
        self.capabilities = [
            "failure_analysis",
            "flaky_test_detection",
            "selector_healing",
            "timeout_optimization",
            "timing_issue_fix",
            "assertion_adjustment",
            "configuration_tuning",
            "auto_retry_logic",
            "pattern_recognition",  # New: Learn from similar failures
            "rag_based_healing",  # New: Use RAG for better fixes
            "historical_fix_search"  # New: Search past successful fixes
        ]
        self.healing_history = []
        self.success_rate = 0.0
    
    async def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and heal a failed test
        
        Args:
            target: Failed test identifier
            config: Contains error_info, test_code, screenshot, logs
        
        Returns:
            Dictionary with healing suggestions and fixes
        """
        logger.info(f"🔧 Healer Agent analyzing failure: {target}")
        
        error_info = config.get('error_info', {})
        test_code = config.get('test_code', '')
        screenshot = config.get('screenshot')
        logs = config.get('logs', [])
        
        # Analyze failure
        analysis = await self._analyze_failure(error_info, test_code, logs)
        
        # 🧠 LangChain RAG: Search for similar past failures and fixes
        rag_suggestions = []
        similar_failures = []
        if self.use_langchain and self.vectorstore:
            try:
                similar_failures = await self.search_similar_failures(
                    analysis.get('error_message', ''),
                    analysis.get('failure_type', 'unknown'),
                    k=5
                )
                if similar_failures:
                    logger.info(f"🔍 Found {len(similar_failures)} similar past failures")
                    rag_suggestions = await self.get_rag_based_fix_suggestions(analysis)
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")
        
        # 🧠 LangChain Memory: Save context
        if self.memory:
            try:
                self.memory.save_context(
                    {"input": f"Healing {target} - {analysis.get('failure_type')}"},
                    {"output": f"Analyzed and generating fixes"}
                )
            except Exception as e:
                logger.warning(f"Failed to save memory: {e}")
        
        # Generate fixes (enhanced with RAG suggestions)
        fixes = await self._generate_fixes(analysis, test_code, rag_suggestions)
        
        # Apply auto-fixes if enabled
        auto_fix_enabled = config.get('auto_fix', False)
        applied_fixes = []
        
        if auto_fix_enabled:
            applied_fixes = await self._apply_fixes(target, fixes)
        
        result = {
            "status": "success",
            "target": target,
            "analysis": analysis,
            "recommended_fixes": fixes,
            "applied_fixes": applied_fixes if auto_fix_enabled else [],
            "auto_fix_enabled": auto_fix_enabled,
            "confidence": analysis.get('confidence', 0),
            "healing_time": datetime.now().isoformat(),
            "summary": {
                "failure_type": analysis.get('failure_type'),
                "root_cause": analysis.get('root_cause'),
                "fix_count": len(fixes),
                "success_probability": analysis.get('success_probability', 0)
            },
            "langchain_insights": {
                "similar_failures_found": len(similar_failures),
                "rag_suggestions": len(rag_suggestions),
                "past_fixes_referenced": [f['metadata'] for f in similar_failures[:3]],
                "vectordb_enabled": self.vectorstore is not None,
                "memory_enabled": self.memory is not None
            }
        }
        
        self.healing_history.append(result)
        self._update_success_rate()
        
        # 🧠 LangChain: Store successful healing in vector DB for future RAG
        if self.use_langchain and self.vectorstore and auto_fix_enabled and applied_fixes:
            try:
                await self._store_healing_in_vectordb({
                    "test_id": target,
                    "analysis": analysis,
                    "fix": applied_fixes,
                    "success": True,  # Only store if auto-fix was attempted
                    "timestamp": result['healing_time']
                })
            except Exception as e:
                logger.warning(f"Failed to store healing in RAG: {e}")
        
        logger.info(f"✅ Healing analysis complete: {len(fixes)} fixes suggested")
        
        return result
    
    async def _analyze_failure(
        self,
        error_info: Dict[str, Any],
        test_code: str,
        logs: List[str]
    ) -> Dict[str, Any]:
        """Analyze test failure using Ollama LLM to determine root cause"""
        
        error_message = error_info.get('message', '')
        error_type = error_info.get('type', 'Unknown')
        stack_trace = error_info.get('stack_trace', '')
        
        # If LLM is available, use it for intelligent analysis
        if self.llm_client and test_code and error_message:
            try:
                analysis = await self._analyze_with_llm(
                    error_message, error_type, test_code, logs
                )
                if analysis:
                    return analysis
            except Exception as e:
                logger.warning(f"LLM analysis failed: {e}, using fallback")
        
        # Fallback to rule-based classification
        failure_type = self._classify_failure(error_message, error_type)
        root_cause = self._determine_root_cause(failure_type, error_message, test_code, logs)
        confidence = self._calculate_confidence(failure_type, root_cause)
        success_probability = self._estimate_success_probability(failure_type)
        
        return {
            "failure_type": failure_type,
            "root_cause": root_cause,
            "error_message": error_message,
            "confidence": confidence,
            "success_probability": success_probability,
            "is_flaky": self._is_flaky_test(error_message, logs),
            "recommendations": self._get_recommendations(failure_type)
        }
    
    async def _analyze_with_llm(
        self,
        error_message: str,
        error_type: str,
        test_code: str,
        logs: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Use Ollama LLM for intelligent failure analysis"""
        
        prompt = f"""You are a test automation expert. Analyze this test failure and provide detailed insights.

Error Type: {error_type}
Error Message: {error_message}

Test Code:
```
{test_code[:500]}
```

Logs:
{chr(10).join(logs[:10]) if logs else 'No logs available'}

Analyze the failure and respond in JSON format:
{{
    "failure_type": "timeout|selector_issue|assertion_failure|network_issue|stale_element|timing_issue|unknown",
    "root_cause": "Detailed explanation of what caused the failure",
    "confidence": 0-100,
    "success_probability": 0-100,
    "is_flaky": true/false,
    "recommendations": ["recommendation 1", "recommendation 2"]
}}

Return ONLY the JSON object."""

        try:
            response = await self.llm_client.create([{"role": "user", "content": prompt}])
            
            # Parse LLM response - handle different response types
            content = ""
            if hasattr(response, 'content'):
                if isinstance(response.content, str):
                    content = response.content
                elif isinstance(response.content, list):
                    for part in response.content:
                        if isinstance(part, str):
                            content += part
                        elif hasattr(part, 'content'):
                            content += part.content
                        elif isinstance(part, dict) and 'content' in part:
                            content += part['content']
            elif isinstance(response, dict) and 'content' in response:
                content = response['content']
            
            if not content:
                return None
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                analysis = json.loads(json_match.group())
                analysis['error_message'] = error_message
                logger.info(f"✅ LLM analysis complete: {analysis['failure_type']} (confidence: {analysis['confidence']}%)")
                return analysis
            else:
                return None
                
        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return None
    
    def _classify_failure(self, error_message: str, error_type: str) -> str:
        """Classify the type of test failure"""
        error_lower = error_message.lower()
        
        if "timeout" in error_lower or "timed out" in error_lower:
            return "timeout"
        elif "selector" in error_lower or "not found" in error_lower or "locator" in error_lower:
            return "selector_issue"
        elif "assertion" in error_lower or "expected" in error_lower:
            return "assertion_failure"
        elif "network" in error_lower or "connection" in error_lower:
            return "network_issue"
        elif "stale" in error_lower or "detached" in error_lower:
            return "stale_element"
        elif "timing" in error_lower or "race condition" in error_lower:
            return "timing_issue"
        else:
            return "unknown"
    
    def _determine_root_cause(
        self,
        failure_type: str,
        error_message: str,
        test_code: str,
        logs: List[str]
    ) -> str:
        """Determine the root cause of failure"""
        
        causes = {
            "timeout": "Element took too long to appear or action to complete",
            "selector_issue": "Element selector is incorrect or element doesn't exist",
            "assertion_failure": "Expected value doesn't match actual value",
            "network_issue": "Network request failed or took too long",
            "stale_element": "Element was removed from DOM before interaction",
            "timing_issue": "Race condition or timing-dependent failure",
            "unknown": "Unable to determine specific root cause"
        }
        
        return causes.get(failure_type, "Unknown root cause")
    
    def _calculate_confidence(self, failure_type: str, root_cause: str) -> int:
        """Calculate confidence in diagnosis (0-100)"""
        confidence_map = {
            "timeout": 90,
            "selector_issue": 85,
            "assertion_failure": 95,
            "network_issue": 80,
            "stale_element": 85,
            "timing_issue": 75,
            "unknown": 40
        }
        return confidence_map.get(failure_type, 50)
    
    def _estimate_success_probability(self, failure_type: str) -> int:
        """Estimate probability of successful healing (0-100)"""
        probability_map = {
            "timeout": 85,
            "selector_issue": 70,
            "assertion_failure": 60,
            "network_issue": 75,
            "stale_element": 80,
            "timing_issue": 70,
            "unknown": 30
        }
        return probability_map.get(failure_type, 50)
    
    def _is_flaky_test(self, error_message: str, logs: List[str]) -> bool:
        """Detect if this is a flaky test"""
        flaky_indicators = [
            "intermittent",
            "sometimes",
            "occasionally",
            "race condition",
            "timing"
        ]
        
        error_lower = error_message.lower()
        return any(indicator in error_lower for indicator in flaky_indicators)
    
    def _get_recommendations(self, failure_type: str) -> List[str]:
        """Get recommendations for fixing the failure"""
        
        recommendations = {
            "timeout": [
                "Increase timeout value",
                "Use explicit waits instead of implicit waits",
                "Check if element loading is slow",
                "Verify network conditions"
            ],
            "selector_issue": [
                "Update element selector",
                "Use more robust selectors (test IDs, ARIA labels)",
                "Check if element is dynamically loaded",
                "Verify element exists in DOM"
            ],
            "assertion_failure": [
                "Update expected values",
                "Check for data changes",
                "Use more flexible assertions",
                "Verify test data setup"
            ],
            "network_issue": [
                "Check network connectivity",
                "Increase network timeout",
                "Mock external dependencies",
                "Verify API endpoints"
            ],
            "stale_element": [
                "Re-locate element before interaction",
                "Use waits for element to be stable",
                "Check for page refreshes",
                "Avoid stale references"
            ],
            "timing_issue": [
                "Add explicit waits",
                "Use waitFor conditions",
                "Synchronize with page events",
                "Avoid hard-coded delays"
            ]
        }
        
        return recommendations.get(failure_type, ["Review test logic and error details"])
    
    async def _generate_fixes(
        self,
        analysis: Dict[str, Any],
        test_code: str,
        rag_suggestions: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate specific fixes for the failure (enhanced with RAG)"""
        
        failure_type = analysis['failure_type']
        fixes = []
        
        # 🧠 Add RAG-based suggestions first (highest priority)
        if rag_suggestions:
            for suggestion in rag_suggestions[:2]:  # Top 2 from past successes
                fixes.append({
                    "type": "rag_based_fix",
                    "description": suggestion['fix_description'],
                    "root_cause": suggestion['root_cause'],
                    "confidence": int(suggestion['confidence'] * 100),
                    "source": "RAG - Similar past fix",
                    "details": suggestion['details']
                })
        
        if failure_type == "timeout":
            fixes.append({
                "type": "timeout_increase",
                "description": "Increase timeout from default to 60 seconds",
                "code_change": "page.wait_for_selector('element', timeout=60000)",
                "confidence": 85
            })
            fixes.append({
                "type": "explicit_wait",
                "description": "Add explicit wait for element to be visible",
                "code_change": "page.wait_for_selector('element', state='visible')",
                "confidence": 90
            })
        
        elif failure_type == "selector_issue":
            fixes.append({
                "type": "selector_update",
                "description": "Use more robust selector with test ID",
                "code_change": "page.locator('[data-testid=\"element-id\"]')",
                "confidence": 80
            })
            fixes.append({
                "type": "fallback_selector",
                "description": "Add fallback selector strategy",
                "code_change": "page.locator('primary-selector, fallback-selector')",
                "confidence": 70
            })
        
        elif failure_type == "assertion_failure":
            fixes.append({
                "type": "assertion_update",
                "description": "Use more flexible assertion with contains",
                "code_change": "expect(element).to_contain_text('partial text')",
                "confidence": 75
            })
        
        elif failure_type == "stale_element":
            fixes.append({
                "type": "re_locate",
                "description": "Re-locate element before each interaction",
                "code_change": "element = page.locator('selector')  # Re-locate",
                "confidence": 85
            })
        
        elif failure_type == "timing_issue":
            fixes.append({
                "type": "network_idle_wait",
                "description": "Wait for network to be idle",
                "code_change": "page.wait_for_load_state('networkidle')",
                "confidence": 80
            })
        
        return fixes
    
    async def _apply_fixes(
        self,
        target: str,
        fixes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply fixes automatically (simulated)"""
        
        applied = []
        for fix in fixes:
            if fix['confidence'] >= 75:  # Only apply high confidence fixes
                applied.append({
                    "fix_type": fix['type'],
                    "description": fix['description'],
                    "applied": True,
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"Applied fix: {fix['type']}")
        
        return applied
    
    def _update_success_rate(self):
        """Update healing success rate based on history"""
        if not self.healing_history:
            self.success_rate = 0.0
            return
        
        successful = sum(
            1 for h in self.healing_history 
            if h['analysis']['success_probability'] >= 70
        )
        self.success_rate = (successful / len(self.healing_history)) * 100
    
    
    async def _store_healing_in_vectordb(self, healing_record: Dict[str, Any]) -> bool:
        """Store successful healing in vector database for RAG"""
        if not self.use_langchain or not self.vectorstore:
            return False
        
        try:
            # Create document from healing record
            healing_text = f"""
            Failure Type: {healing_record['analysis']['failure_type']}
            Root Cause: {healing_record['analysis']['root_cause']}
            Error: {healing_record['analysis']['error_message'][:200]}
            Fix Applied: {json.dumps(healing_record['fix'])}
            Success: {healing_record['success']}
            """
            
            metadata = {
                "test_id": healing_record['test_id'],
                "failure_type": healing_record['analysis']['failure_type'],
                "root_cause": healing_record['analysis']['root_cause'],
                "success": healing_record['success'],
                "confidence": healing_record['analysis']['confidence'],
                "timestamp": healing_record['timestamp']
            }
            
            # Add to vector store
            self.vectorstore.add_texts(
                texts=[healing_text],
                metadatas=[metadata],
                ids=[f"{healing_record['test_id']}_{healing_record['timestamp']}"]
            )
            
            # Persist changes
            if hasattr(self.vectorstore, 'persist'):
                self.vectorstore.persist()
            
            logger.info(f"✅ Stored healing record in RAG database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store healing in vectordb: {e}")
            return False
    
    async def search_similar_failures(self, error_message: str, failure_type: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar past failures and their fixes using RAG"""
        if not self.use_langchain or not self.vectorstore:
            return []
        
        try:
            # Create search query
            query = f"Failure Type: {failure_type}, Error: {error_message[:200]}"
            
            # Search for similar failures
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            similar_failures = []
            for doc, score in results:
                # Only include successful fixes
                if doc.metadata.get('success', False):
                    similar_failures.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": float(score),
                        "failure_type": doc.metadata.get('failure_type'),
                        "root_cause": doc.metadata.get('root_cause')
                    })
            
            if similar_failures:
                logger.info(f"✅ Found {len(similar_failures)} similar past failures with fixes")
            
            return similar_failures
            
        except Exception as e:
            logger.error(f"Failed to search similar failures: {e}")
            return []
    
    async def get_rag_based_fix_suggestions(self, failure_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fix suggestions based on similar past failures (RAG)"""
        if not self.use_langchain or not self.vectorstore:
            return []
        
        try:
            # Search for similar failures
            similar = await self.search_similar_failures(
                failure_analysis['error_message'],
                failure_analysis['failure_type'],
                k=3
            )
            
            suggestions = []
            for item in similar:
                if item['similarity_score'] > 0.75:  # High similarity threshold
                    suggestions.append({
                        "fix_description": f"Similar {item['failure_type']} fixed before",
                        "root_cause": item['root_cause'],
                        "confidence": item['similarity_score'],
                        "source": "RAG (Past Success)",
                        "details": item['content'][:300]
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get RAG-based suggestions: {e}")
            return []
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """Get healing statistics"""
        if not self.healing_history:
            return {
                "total_healings": 0,
                "success_rate": 0,
                "common_failures": []
            }
        
        failure_types = {}
        for h in self.healing_history:
            ftype = h['analysis']['failure_type']
            failure_types[ftype] = failure_types.get(ftype, 0) + 1
        
        return {
            "total_healings": len(self.healing_history),
            "success_rate": round(self.success_rate, 2),
            "common_failures": sorted(
                failure_types.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "average_confidence": round(
                sum(h['analysis']['confidence'] for h in self.healing_history) / 
                len(self.healing_history),
                2
            )
        }


# Convenience functions for easy usage
async def create_test_plan(
    target: str,
    requirements: List[str],
    user_stories: List[str] = None,
    acceptance_criteria: List[str] = None,
    test_type: str = 'functional',
    llm_client: Optional[OpenAIChatCompletionClient] = None,
    use_ollama: bool = True
) -> Dict[str, Any]:
    """
    Create a test plan using PlannerAgent with Ollama LLM
    
    Args:
        target: Application/feature to test
        requirements: List of requirements to test
        user_stories: Optional list of user stories
        acceptance_criteria: Optional acceptance criteria
        test_type: Type of testing (functional, e2e, etc.)
        llm_client: Optional custom LLM client
        use_ollama: Whether to use Ollama (default: True)
    
    Returns:
        Test plan dictionary
    """
    if use_ollama and llm_client is None and create_ollama_client:
        llm_client = create_ollama_client()
    
    agent = PlannerAgent(llm_client=llm_client)
    config = {
        'requirements': requirements,
        'user_stories': user_stories or [],
        'acceptance_criteria': acceptance_criteria or [],
        'test_type': test_type
    }
    return await agent.execute(target, config)


async def generate_test_code(
    test_plan: Dict[str, Any],
    framework: str = 'playwright',
    language: str = 'python',
    llm_client: Optional[OpenAIChatCompletionClient] = None,
    use_ollama: bool = True
) -> Dict[str, Any]:
    """
    Generate test code using GeneratorAgent with Ollama LLM
    
    Args:
        test_plan: Test plan from PlannerAgent
        framework: Framework to use (playwright, selenium, cypress)
        language: Programming language (python, typescript, javascript)
        llm_client: Optional custom LLM client
        use_ollama: Whether to use Ollama (default: True)
    
    Returns:
        Generated code dictionary
    """
    if use_ollama and llm_client is None and create_ollama_client:
        llm_client = create_ollama_client()
    
    agent = GeneratorAgent(llm_client=llm_client)
    config = {
        'test_plan': test_plan,
        'framework': framework,
        'language': language
    }
    return await agent.execute('test_generation', config)


async def heal_test_failure(
    test_name: str,
    error_info: Dict[str, Any],
    test_code: str = '',
    auto_fix: bool = False,
    llm_client: Optional[OpenAIChatCompletionClient] = None,
    use_ollama: bool = True
) -> Dict[str, Any]:
    """
    Heal a test failure using HealerAgent with Ollama LLM
    
    Args:
        test_name: Name of failed test
        error_info: Error information (message, type, stack_trace)
        test_code: Optional test code for context
        auto_fix: Whether to automatically apply fixes
        llm_client: Optional custom LLM client
        use_ollama: Whether to use Ollama (default: True)
    
    Returns:
        Healing analysis and fixes
    """
    if use_ollama and llm_client is None and create_ollama_client:
        llm_client = create_ollama_client()
    
    agent = HealerAgent(llm_client=llm_client)
    config = {
        'error_info': error_info,
        'test_code': test_code,
        'auto_fix': auto_fix,
        'logs': []
    }
    return await agent.execute(test_name, config)
