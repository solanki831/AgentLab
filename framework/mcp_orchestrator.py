"""
🎯 MCP ORCHESTRATOR - LLM-DRIVEN TOOL SELECTION
True MCP principles implementation:
- LLM analyzes task and decides which tools to call
- Tools are discovered via registry
- Structured tool_call / tool_result protocol
- LLM-agnostic design (works with any LLM)
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import logging

try:
    from framework.mcp_tool_protocol import (
        MCPTool, MCPAgent, ToolDefinition, ToolParameter,
        ToolCall, ToolResult, get_tool_registry,
        parse_llm_tool_calls, format_tool_results_for_llm
    )
    from framework.mcp_ui_agent import UITestAgentMCP
    from framework.mcp_api_agent import APITestAgentMCP
except ImportError:
    from mcp_tool_protocol import (
        MCPTool, MCPAgent, ToolDefinition, ToolParameter,
        ToolCall, ToolResult, get_tool_registry,
        parse_llm_tool_calls, format_tool_results_for_llm
    )
    from mcp_ui_agent import UITestAgentMCP
    from mcp_api_agent import APITestAgentMCP

logger = logging.getLogger(__name__)


# =============================================================================
# LLM INTERFACE - AGNOSTIC ADAPTER
# =============================================================================

class LLMAdapter:
    """
    LLM-agnostic adapter for tool calling
    Supports Ollama, OpenAI, Anthropic, etc.
    """
    
    def __init__(self, provider: str = "ollama", model: str = "llama3.2:latest"):
        self.provider = provider
        self.model = model
        self._client = None
    
    async def _get_ollama_client(self):
        """Get or create Ollama client using httpx"""
        if self._client is None:
            try:
                import httpx
                # Test if Ollama is running
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://127.0.0.1:11434/api/tags", timeout=5.0)
                    if response.status_code == 200:
                        self._client = "httpx"  # Use httpx for Ollama API
                    else:
                        self._client = None
            except Exception:
                logger.warning("Ollama not available, using rule-based fallback")
                self._client = None
        return self._client
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """
        Send chat request with tool definitions
        Returns LLM response with potential tool_calls
        """
        if self.provider == "ollama":
            return await self._ollama_chat(messages, tools)
        elif self.provider == "openai":
            return await self._openai_chat(messages, tools, tool_choice)
        else:
            # Fallback to rule-based tool selection
            return await self._fallback_chat(messages, tools)
    
    async def _ollama_chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Ollama chat with tools using httpx"""
        client = await self._get_ollama_client()
        
        if client is None:
            return await self._fallback_chat(messages, tools)
        
        try:
            import httpx
            
            # Convert tools to Ollama format
            ollama_tools = []
            for tool in tools:
                if "function" in tool:
                    ollama_tools.append({
                        "type": "function",
                        "function": tool["function"]
                    })
            
            # Build request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }
            if ollama_tools:
                payload["tools"] = ollama_tools
            
            async with httpx.AsyncClient(timeout=120.0) as http_client:
                response = await http_client.post(
                    "http://127.0.0.1:11434/api/chat",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message = data.get("message", {})
                    return {
                        "content": message.get("content", ""),
                        "tool_calls": message.get("tool_calls", []),
                        "model": self.model,
                        "provider": "ollama"
                    }
                else:
                    logger.warning(f"Ollama API error: {response.status_code}")
                    return await self._fallback_chat(messages, tools)
        
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return await self._fallback_chat(messages, tools)
    
    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_choice: str
    ) -> Dict[str, Any]:
        """OpenAI chat with tools (if openai package installed)"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI()
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice
            )
            
            message = response.choices[0].message
            return {
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in (message.tool_calls or [])
                ],
                "model": self.model,
                "provider": "openai"
            }
        
        except ImportError:
            return await self._fallback_chat(messages, tools)
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return await self._fallback_chat(messages, tools)
    
    async def _fallback_chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Rule-based fallback when LLM tool calling unavailable
        Analyzes user message and selects appropriate tools
        """
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break
        
        tool_calls = []
        
        # Keyword-based tool selection
        if any(kw in user_message for kw in ["ui", "browser", "click", "navigate", "screenshot", "e2e", "form"]):
            # Find UI test tool
            for tool in tools:
                if tool.get("function", {}).get("name") in ["run_ui_test", "browser_navigate"]:
                    tool_calls.append({
                        "id": f"call_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "function": {
                            "name": tool["function"]["name"],
                            "arguments": json.dumps(self._extract_params_from_message(user_message, tool))
                        }
                    })
                    break
        
        if any(kw in user_message for kw in ["api", "endpoint", "request", "http", "rest", "get", "post"]):
            # Find API test tool
            for tool in tools:
                if tool.get("function", {}).get("name") in ["run_api_test", "api_request"]:
                    tool_calls.append({
                        "id": f"call_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "function": {
                            "name": tool["function"]["name"],
                            "arguments": json.dumps(self._extract_params_from_message(user_message, tool))
                        }
                    })
                    break
        
        if any(kw in user_message for kw in ["performance", "load", "stress", "concurrent"]):
            for tool in tools:
                if tool.get("function", {}).get("name") == "api_performance_test":
                    tool_calls.append({
                        "id": f"call_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "function": {
                            "name": "api_performance_test",
                            "arguments": json.dumps(self._extract_params_from_message(user_message, tool))
                        }
                    })
                    break
        
        return {
            "content": f"I'll execute the appropriate tools based on your request.",
            "tool_calls": tool_calls,
            "model": "fallback",
            "provider": "rule-based"
        }
    
    def _extract_params_from_message(self, message: str, tool: Dict) -> Dict[str, Any]:
        """Extract tool parameters from natural language message"""
        params = {}
        
        # Extract URLs
        import re
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', message)
        if urls:
            params["url"] = urls[0]
        else:
            params["url"] = "https://www.saucedemo.com/"  # Default
        
        # Extract method
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        for method in methods:
            if method.lower() in message.lower():
                params["method"] = method
                break
        
        # Extract numbers for requests
        numbers = re.findall(r'\d+', message)
        if numbers and "request" in message.lower():
            params["num_requests"] = int(numbers[0])
        
        # Extract steps for UI tests
        if "steps" in tool.get("function", {}).get("parameters", {}).get("properties", {}):
            params["steps"] = [{"action": "navigate", "url": params.get("url", "https://www.saucedemo.com/")}]
        
        return params


# =============================================================================
# MCP ORCHESTRATOR - LLM-DRIVEN
# =============================================================================

@dataclass
class OrchestratorConfig:
    """Orchestrator configuration"""
    llm_provider: str = "ollama"
    llm_model: str = "llama3.2:latest"
    max_iterations: int = 10
    parallel_execution: bool = True
    auto_healing: bool = True
    verbose: bool = True


class MCPOrchestrator:
    """
    LLM-Driven MCP Orchestrator
    
    True MCP principles:
    1. Discovers tools from registry
    2. LLM decides which tools to call
    3. Structured tool_call / tool_result
    4. Iterates until task complete
    """
    
    def __init__(self, config: OrchestratorConfig = None):
        self.config = config or OrchestratorConfig()
        self.registry = get_tool_registry()
        self.llm = LLMAdapter(
            provider=self.config.llm_provider,
            model=self.config.llm_model
        )
        self.conversation_history: List[Dict[str, str]] = []
        self.tool_results: List[ToolResult] = []
        
        # Initialize agents (registers their tools)
        self._init_agents()
    
    def _init_agents(self):
        """Initialize all MCP agents"""
        self.agents = {
            "ui": UITestAgentMCP(),
            "api": APITestAgentMCP()
        }
        logger.info(f"🎯 MCPOrchestrator initialized with {len(self.registry.get_all_tools())} tools")
    
    def get_system_prompt(self) -> str:
        """Generate system prompt with tool descriptions"""
        tools_summary = self.registry.get_tools_summary()
        
        return f"""You are an intelligent QA orchestrator that coordinates testing tools.

{tools_summary}

INSTRUCTIONS:
1. Analyze the user's testing request
2. Decide which tool(s) to call based on the request
3. Call tools with appropriate parameters
4. Analyze results and determine if more tools are needed
5. Provide a summary when testing is complete

RULES:
- Use run_ui_test for browser/UI testing
- Use run_api_test for API endpoint testing
- Use api_performance_test for load/performance testing
- Use browser_screenshot to capture visual evidence
- Chain tools logically (e.g., navigate before click)
- Report failures clearly with details

When you have completed all necessary tool calls, summarize the results for the user."""

    async def execute(self, user_request: str) -> Dict[str, Any]:
        """
        Execute user request using LLM-driven tool selection
        
        This is the core MCP orchestration loop:
        1. Send user request + tools to LLM
        2. LLM returns tool_calls
        3. Execute tools
        4. Send tool_results back to LLM
        5. Repeat until LLM responds without tool_calls
        """
        start_time = datetime.now()
        iteration = 0
        all_results = []
        
        # Initialize conversation
        self.conversation_history = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": user_request}
        ]
        
        # Get available tools
        tools = self.registry.get_tools_for_llm()
        
        if self.config.verbose:
            logger.info(f"🎯 Orchestrator: Processing request with {len(tools)} available tools")
        
        while iteration < self.config.max_iterations:
            iteration += 1
            
            if self.config.verbose:
                logger.info(f"📍 Iteration {iteration}")
            
            # Get LLM response
            response = await self.llm.chat_with_tools(
                messages=self.conversation_history,
                tools=tools
            )
            
            tool_calls = response.get("tool_calls", [])
            content = response.get("content", "")
            
            # If no tool calls, LLM is done
            if not tool_calls:
                if self.config.verbose:
                    logger.info("✅ Orchestrator: LLM finished (no more tool calls)")
                break
            
            # Execute tool calls
            if self.config.verbose:
                logger.info(f"🔧 Executing {len(tool_calls)} tool call(s)")
            
            # Parse tool calls
            parsed_calls = []
            for tc in tool_calls:
                try:
                    args = tc.get("function", {}).get("arguments", "{}")
                    if isinstance(args, str):
                        args = json.loads(args)
                    
                    parsed_calls.append(ToolCall(
                        call_id=tc.get("id", ""),
                        tool_name=tc.get("function", {}).get("name", ""),
                        arguments=args
                    ))
                except Exception as e:
                    logger.error(f"Failed to parse tool call: {e}")
            
            # Execute tools (parallel or sequential)
            if self.config.parallel_execution and len(parsed_calls) > 1:
                results = await self._execute_parallel(parsed_calls)
            else:
                results = await self._execute_sequential(parsed_calls)
            
            all_results.extend(results)
            
            # Add assistant message with tool calls
            self.conversation_history.append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls
            })
            
            # Add tool results to conversation
            for result in results:
                self.conversation_history.append(result.to_dict())
            
            # Auto-healing for failures
            if self.config.auto_healing:
                for result in results:
                    if not result.success:
                        heal_result = await self._attempt_healing(result)
                        if heal_result:
                            all_results.append(heal_result)
        
        # Generate summary
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": all(r.success for r in all_results) if all_results else False,
            "request": user_request,
            "iterations": iteration,
            "tool_calls_made": len(all_results),
            "results": [
                {
                    "tool": r.tool_name,
                    "success": r.success,
                    "result": r.result,
                    "error": r.error,
                    "execution_time": r.execution_time
                }
                for r in all_results
            ],
            "execution_time": execution_time,
            "llm_provider": self.config.llm_provider,
            "llm_model": self.config.llm_model
        }
    
    async def _execute_parallel(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute tool calls in parallel"""
        tasks = [self.registry.execute_tool(tc) for tc in tool_calls]
        return await asyncio.gather(*tasks)
    
    async def _execute_sequential(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute tool calls sequentially"""
        results = []
        for tc in tool_calls:
            result = await self.registry.execute_tool(tc)
            results.append(result)
        return results
    
    async def _attempt_healing(self, failed_result: ToolResult) -> Optional[ToolResult]:
        """Attempt to heal a failed tool call"""
        if not failed_result.error:
            return None
        
        logger.info(f"🔧 Attempting to heal: {failed_result.tool_name}")
        
        # Ask LLM for healing suggestion
        heal_prompt = f"""A tool call failed:
Tool: {failed_result.tool_name}
Error: {failed_result.error}

Suggest a fix or alternative tool call. Return JSON with:
{{"retry": true/false, "modified_args": {{...}}, "alternative_tool": "tool_name" or null}}"""
        
        response = await self.llm.chat_with_tools(
            messages=[
                {"role": "system", "content": "You are a test automation expert. Help fix failing tests."},
                {"role": "user", "content": heal_prompt}
            ],
            tools=[]  # No tools, just analysis
        )
        
        # For now, just log the healing attempt
        logger.info(f"🔧 Healing suggestion: {response.get('content', 'No suggestion')[:200]}")
        
        return None  # Future: implement actual retry


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def run_test(request: str, config: OrchestratorConfig = None) -> Dict[str, Any]:
    """Run a test request through the MCP orchestrator"""
    orchestrator = MCPOrchestrator(config)
    return await orchestrator.execute(request)


def create_orchestrator(
    llm_provider: str = "ollama",
    llm_model: str = "llama3.2:latest",
    parallel: bool = True
) -> MCPOrchestrator:
    """Create a configured MCP orchestrator"""
    config = OrchestratorConfig(
        llm_provider=llm_provider,
        llm_model=llm_model,
        parallel_execution=parallel
    )
    return MCPOrchestrator(config)


# =============================================================================
# BACKWARDS COMPATIBILITY
# =============================================================================

class OrchestratorAgent:
    """
    Legacy interface for backwards compatibility
    Wraps the MCP orchestrator
    """
    
    def __init__(self):
        self._mcp_orchestrator = MCPOrchestrator()
        self.agents = self._mcp_orchestrator.agents
        self.tasks = {}
        self.results = {}
        self.registry = self._mcp_orchestrator.registry  # Add registry for compatibility
        self._test_plan = None  # Store test plan for dashboard
    
    def create_test_plan(self, test_suite: Dict[str, Any]) -> None:
        """Create a test plan from the suite (for dashboard compatibility)"""
        self._test_plan = test_suite
        logger.info(f"📋 Test plan created with {len(test_suite.get('tests', []))} tests")
    
    async def execute_test_plan(self, parallel: bool = True) -> Dict[str, Any]:
        """Execute the test plan (for dashboard compatibility)"""
        if not self._test_plan:
            return {"success": False, "error": "No test plan created", "total_tasks": 0, "passed": 0, "failed": 0, "healed": 0, "tasks": []}
        
        return await self.execute_suite(self._test_plan, parallel=parallel)
    
    async def execute_suite(self, test_suite: Dict[str, Any], parallel: bool = True) -> Dict[str, Any]:
        """Execute a test suite"""
        raw_results = []
        tests = test_suite.get("tests", [])
        
        if parallel and len(tests) > 1:
            # Execute tests in parallel
            tasks = []
            for test in tests:
                request = f"Run {test.get('type', 'api')} test on {test.get('target', 'https://example.com')}"
                if test.get('config'):
                    request += f" with config: {test.get('config')}"
                tasks.append(self._mcp_orchestrator.execute(request))
            
            raw_results = await asyncio.gather(*tasks, return_exceptions=True)
            # Convert exceptions to error results
            raw_results = [
                r if isinstance(r, dict) else {"success": False, "error": str(r)}
                for r in raw_results
            ]
        else:
            # Execute tests sequentially
            for test in tests:
                request = f"Run {test.get('type', 'api')} test on {test.get('target', 'https://example.com')}"
                if test.get('config'):
                    request += f" with config: {test.get('config')}"
                
                result = await self._mcp_orchestrator.execute(request)
                raw_results.append(result)
        
        # Transform raw results into the format expected by the orchestration UI
        task_results = []
        for idx, (test, raw) in enumerate(zip(tests, raw_results)):
            task_success = raw.get("success", False)
            task_results.append({
                "task_id": f"test_{idx}",
                "type": test.get("type", "api"),
                "status": "completed" if task_success else "failed",
                "result": {
                    "success": task_success,
                    "execution_time": raw.get("execution_time", 0.0),
                    "error": None if task_success else raw.get("error", "Test failed"),
                    "agent": f"{test.get('type', 'api').upper()} Agent",
                    "tool_calls": raw.get("tool_calls_made", 0),
                    "iterations": raw.get("iterations", 0),
                    "llm_provider": raw.get("llm_provider", ""),
                    "details": raw.get("results", [])
                }
            })
        
        passed = sum(1 for r in task_results if r["status"] == "completed")
        failed = len(task_results) - passed
        
        return {
            "success": failed == 0,
            "total_tasks": len(task_results),
            "passed": passed,
            "failed": failed,
            "healed": 0,
            "tasks": task_results
        }


# Backwards compatible TestTask
@dataclass
class TestTask:
    """Test task definition (backwards compatible)"""
    task_id: str
    task_type: str
    target: str
    config: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Optional[Dict] = None
    assigned_to: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 2


# =============================================================================
# DEMO
# =============================================================================

async def demo():
    """Demo the MCP orchestrator"""
    print("=" * 60)
    print("🎯 MCP ORCHESTRATOR DEMO")
    print("=" * 60)
    
    orchestrator = create_orchestrator()
    
    # Demo requests
    requests = [
        "Test the API endpoint https://httpbin.org/get and verify it returns 200",
        "Run a UI test to navigate to https://www.saucedemo.com/ and take a screenshot",
        "Run a performance test on https://httpbin.org/get with 5 concurrent requests"
    ]
    
    for request in requests:
        print(f"\n📋 Request: {request}")
        print("-" * 50)
        
        result = await orchestrator.execute(request)
        
        print(f"✅ Success: {result['success']}")
        print(f"⏱️ Time: {result['execution_time']:.2f}s")
        print(f"🔧 Tool calls: {result['tool_calls_made']}")
        
        for tool_result in result.get("results", []):
            status = "✅" if tool_result["success"] else "❌"
            print(f"   {status} {tool_result['tool']}: {tool_result.get('error') or 'OK'}")


if __name__ == "__main__":
    asyncio.run(demo())
