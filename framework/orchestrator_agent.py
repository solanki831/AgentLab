"""
🎯 MULTI-AGENT ORCHESTRATION SYSTEM
Real QA team structure with specialized agents coordinated by an Orchestrator.

Agents:
- Orchestrator Agent (Test Lead) - Coordinates all agents
- UI Test Agent (Automation Engineer) - Browser automation via MCP Playwright
- API Test Agent (API Tester) - API testing via MCP REST tools
- Healing Agent (Flaky Test Fixer) - Auto-fixes failing tests
- Validation Agent (Reviewer) - Validates test results
- Report Agent (Analyst) - Generates reports and RCA
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import logging

# Dynamic imports for agents
try:
    from framework.ui_test_agent import UITestAgent
except ImportError:
    UITestAgent = None

try:
    from framework.api_test_agent import APITestAgent
except ImportError:
    APITestAgent = None

try:
    from framework.healing_agent import HealingAgent
except ImportError:
    HealingAgent = None

try:
    from framework.validation_agent import ValidationAgent
except ImportError:
    ValidationAgent = None

try:
    from framework.report_agent import ReportAgent
except ImportError:
    ReportAgent = None

logger = logging.getLogger(__name__)


@dataclass
class TestTask:
    """Represents a test task to be executed"""
    task_id: str
    task_type: str  # 'ui', 'api', 'validation', 'report'
    target: str  # URL or endpoint
    config: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1=high, 2=medium, 3=low
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict] = None
    assigned_to: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 2


@dataclass
class AgentCapability:
    """Defines what an agent can do"""
    name: str
    agent_type: str
    capabilities: List[str]
    max_concurrent_tasks: int = 3
    is_available: bool = True
    current_tasks: List[str] = field(default_factory=list)


class OrchestratorAgent:
    """
    Test Lead - Coordinates all specialized agents
    Responsibilities:
    - Task distribution
    - Dependency management
    - Retry logic
    - Result aggregation
    - Progress tracking
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentCapability] = {}
        self.tasks: Dict[str, TestTask] = {}
        self.execution_plan: List[TestTask] = []
        self.results: Dict[str, Any] = {}
        
        # Register available agents
        self._register_agents()
    
    def _register_agents(self):
        """Register all available specialized agents"""
        self.agents = {
            "ui_agent": AgentCapability(
                name="UI Test Agent",
                agent_type="ui",
                capabilities=["browser_automation", "ui_testing", "screenshot", "form_filling", "navigation"],
                max_concurrent_tasks=2
            ),
            "api_agent": AgentCapability(
                name="API Test Agent",
                agent_type="api",
                capabilities=["api_testing", "rest_calls", "graphql", "performance", "contract_validation"],
                max_concurrent_tasks=5
            ),
            "healing_agent": AgentCapability(
                name="Healing Agent",
                agent_type="healing",
                capabilities=["test_repair", "flaky_detection", "auto_fix", "retry_logic"],
                max_concurrent_tasks=3
            ),
            "validation_agent": AgentCapability(
                name="Validation Agent",
                agent_type="validation",
                capabilities=["assertion", "data_validation", "schema_check", "response_validation"],
                max_concurrent_tasks=10
            ),
            "report_agent": AgentCapability(
                name="Report Agent",
                agent_type="report",
                capabilities=["reporting", "rca", "metrics", "trend_analysis"],
                max_concurrent_tasks=1
            )
        }
        
        logger.info(f"🎯 Orchestrator: Registered {len(self.agents)} specialized agents")
    
    def create_test_plan(self, test_suite: Dict[str, Any]) -> List[TestTask]:
        """
        Create execution plan from test suite
        Analyzes dependencies and creates optimal execution order
        """
        tasks = []
        
        # Parse test suite and create tasks
        for idx, test_spec in enumerate(test_suite.get("tests", [])):
            task = TestTask(
                task_id=f"task_{idx}_{test_spec.get('type', 'unknown')}",
                task_type=test_spec.get("type", "api"),
                target=test_spec.get("target", ""),
                config=test_spec.get("config", {}),
                priority=test_spec.get("priority", 2),
                dependencies=test_spec.get("dependencies", [])
            )
            tasks.append(task)
            self.tasks[task.task_id] = task
        
        # Sort by priority and dependencies
        self.execution_plan = self._optimize_execution_order(tasks)
        
        logger.info(f"📋 Created test plan with {len(tasks)} tasks")
        return self.execution_plan
    
    def _optimize_execution_order(self, tasks: List[TestTask]) -> List[TestTask]:
        """Optimize task execution order based on dependencies and priority"""
        # Topological sort for dependency resolution
        sorted_tasks = []
        completed = set()
        
        def can_execute(task: TestTask) -> bool:
            return all(dep in completed for dep in task.dependencies)
        
        remaining = tasks.copy()
        while remaining:
            # Find tasks that can be executed
            ready = [t for t in remaining if can_execute(t)]
            
            if not ready:
                # Circular dependency or missing dependency
                logger.warning("⚠️ Dependency resolution issue, executing remaining tasks anyway")
                ready = remaining
            
            # Sort ready tasks by priority
            ready.sort(key=lambda t: t.priority)
            
            # Take the highest priority task
            task = ready[0]
            sorted_tasks.append(task)
            completed.add(task.task_id)
            remaining.remove(task)
        
        return sorted_tasks
    
    def assign_task(self, task: TestTask) -> Optional[str]:
        """Assign task to appropriate agent based on type and availability"""
        # Map task types to agent types
        type_mapping = {
            "ui": "ui_agent",
            "browser": "ui_agent",
            "e2e": "ui_agent",
            "api": "api_agent",
            "rest": "api_agent",
            "graphql": "api_agent",
            "validation": "validation_agent",
            "assert": "validation_agent",
            "report": "report_agent",
            "rca": "report_agent"
        }
        
        agent_key = type_mapping.get(task.task_type, "api_agent")
        agent = self.agents.get(agent_key)
        
        if not agent:
            logger.error(f"❌ No agent found for task type: {task.task_type}")
            return None
        
        # Check if agent has capacity
        if len(agent.current_tasks) >= agent.max_concurrent_tasks:
            logger.warning(f"⚠️ {agent.name} at capacity, task queued")
            return None
        
        # Assign task
        agent.current_tasks.append(task.task_id)
        task.assigned_to = agent_key
        task.status = "assigned"
        
        logger.info(f"✅ Assigned {task.task_id} to {agent.name}")
        return agent_key
    
    async def execute_test_plan(self, parallel: bool = True) -> Dict[str, Any]:
        """
        Execute the test plan
        Coordinates all agents and manages execution
        """
        logger.info(f"🚀 Starting test execution: {len(self.execution_plan)} tasks")
        start_time = datetime.now()
        
        results = {
            "total_tasks": len(self.execution_plan),
            "passed": 0,
            "failed": 0,
            "healed": 0,
            "tasks": []
        }
        
        if parallel:
            # Execute tasks in parallel where possible
            results = await self._execute_parallel()
        else:
            # Execute tasks sequentially
            results = await self._execute_sequential()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        results["execution_time"] = execution_time
        
        # Generate final report
        final_report = await self._generate_final_report(results)
        
        logger.info(f"✅ Test execution complete: {results['passed']}/{results['total_tasks']} passed")
        return final_report
    
    async def _execute_parallel(self) -> Dict[str, Any]:
        """Execute tasks in parallel respecting dependencies"""
        results = {
            "total_tasks": len(self.execution_plan),
            "passed": 0,
            "failed": 0,
            "healed": 0,
            "tasks": []
        }
        
        completed = set()
        
        while len(completed) < len(self.execution_plan):
            # Find tasks ready to execute
            ready_tasks = [
                task for task in self.execution_plan
                if task.task_id not in completed
                and task.status == "pending"
                and all(dep in completed for dep in task.dependencies)
            ]
            
            if not ready_tasks:
                # Wait for running tasks to complete
                await asyncio.sleep(0.1)
                continue
            
            # Execute ready tasks in parallel
            task_coros = []
            for task in ready_tasks:
                agent_key = self.assign_task(task)
                if agent_key:
                    task_coros.append(self._execute_task(task, agent_key))
            
            # Wait for batch to complete
            if task_coros:
                batch_results = await asyncio.gather(*task_coros, return_exceptions=True)
                
                for task, result in zip(ready_tasks, batch_results):
                    if isinstance(result, Exception):
                        task.status = "failed"
                        task.result = {"error": str(result)}
                        results["failed"] += 1
                    else:
                        task.status = "completed"
                        task.result = result
                        if result.get("success"):
                            results["passed"] += 1
                        else:
                            # Try healing
                            healed = await self._try_heal_task(task)
                            if healed:
                                results["healed"] += 1
                                results["passed"] += 1
                            else:
                                results["failed"] += 1
                    
                    completed.add(task.task_id)
                    results["tasks"].append({
                        "task_id": task.task_id,
                        "type": task.task_type,
                        "status": task.status,
                        "result": task.result
                    })
                    
                    # Release agent
                    if task.assigned_to:
                        self.agents[task.assigned_to].current_tasks.remove(task.task_id)
        
        return results
    
    async def _execute_sequential(self) -> Dict[str, Any]:
        """Execute tasks one by one"""
        results = {
            "total_tasks": len(self.execution_plan),
            "passed": 0,
            "failed": 0,
            "healed": 0,
            "tasks": []
        }
        
        for task in self.execution_plan:
            agent_key = self.assign_task(task)
            if not agent_key:
                task.status = "failed"
                task.result = {"error": "No agent available"}
                results["failed"] += 1
                continue
            
            result = await self._execute_task(task, agent_key)
            
            if result.get("success"):
                results["passed"] += 1
            else:
                # Try healing
                healed = await self._try_heal_task(task)
                if healed:
                    results["healed"] += 1
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            
            results["tasks"].append({
                "task_id": task.task_id,
                "type": task.task_type,
                "status": task.status,
                "result": task.result
            })
            
            # Release agent
            if task.assigned_to:
                self.agents[task.assigned_to].current_tasks.remove(task.task_id)
        
        return results
    
    async def _execute_task(self, task: TestTask, agent_key: str) -> Dict[str, Any]:
        """Execute a single task using the assigned agent"""
        logger.info(f"⚡ Executing {task.task_id} with {agent_key}")
        task.status = "running"
        task.start_time = datetime.now()
        
        try:
            # Execute based on agent type with proper imports
            if agent_key == "ui_agent" and UITestAgent:
                agent = UITestAgent()
                result = await agent.execute(task.target, task.config)
            elif agent_key == "api_agent" and APITestAgent:
                agent = APITestAgent()
                result = await agent.execute(task.target, task.config)
            elif agent_key == "validation_agent" and ValidationAgent:
                agent = ValidationAgent()
                result = await agent.execute(task.target, task.config)
            elif agent_key == "report_agent" and ReportAgent:
                agent = ReportAgent()
                result = await agent.execute(task.target, task.config)
            elif agent_key == "healing_agent" and HealingAgent:
                agent = HealingAgent()
                result = await agent.execute(task.target, task.config)
            else:
                result = {"success": False, "error": f"Agent not available: {agent_key}"}
            
            task.status = "completed" if result.get("success") else "failed"
            task.result = result
            task.end_time = datetime.now()
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Task execution error: {e}")
            task.status = "failed"
            task.result = {"success": False, "error": str(e)}
            task.end_time = datetime.now()
            return task.result
    
    async def _try_heal_task(self, task: TestTask) -> bool:
        """Try to heal a failed task using Healing Agent"""
        if task.retry_count >= task.max_retries:
            logger.warning(f"⚠️ Task {task.task_id} exceeded max retries")
            return False
        
        if not HealingAgent:
            return False
        
        try:
            healing_agent = HealingAgent()
            
            healing_config = {
                "failed_test": {
                    "name": task.task_id,
                    "type": task.task_type
                },
                "error_info": task.result.get("error", ""),
                "test_config": task.config
            }
            
            healing_result = await healing_agent.execute(task.task_id, healing_config)
            
            if healing_result.get("success"):
                # Retry with healed configuration
                task.config = healing_result.get("healed_config", task.config)
                task.retry_count += 1
                
                # Re-execute
                result = await self._execute_task(task, task.assigned_to)
                
                if result.get("success"):
                    logger.info(f"✅ Task {task.task_id} healed successfully")
                    return True
        
        except Exception as e:
            logger.error(f"❌ Healing failed: {e}")
        
        return False
    
    async def _generate_final_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not ReportAgent:
            return results
        
        try:
            report_agent = ReportAgent()
            
            report_config = {
                "results": results.get("tasks", []),
                "report_type": "detailed",
                "options": {
                    "include_rca": results.get("failed", 0) > 0,
                    "include_metrics": True
                }
            }
            
            report_result = await report_agent.execute("final_report", report_config)
            
            return {
                **results,
                "report": report_result
            }
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            return results


# Singleton orchestrator instance
_orchestrator = None

def get_orchestrator() -> OrchestratorAgent:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent()
    return _orchestrator
