"""
🌐 API TEST AGENT - TRUE MCP IMPLEMENTATION
Exposes API testing tools via MCP protocol

Tools Exposed:
- api_request: Make HTTP request
- api_validate_response: Validate response
- api_validate_schema: Validate JSON schema
- api_performance_test: Run performance test
- run_api_test: Execute full API test
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

try:
    from framework.mcp_tool_protocol import (
        MCPTool, MCPAgent, ToolDefinition, ToolParameter,
        ToolCall, ToolResult, get_tool_registry
    )
except ImportError:
    from mcp_tool_protocol import (
        MCPTool, MCPAgent, ToolDefinition, ToolParameter,
        ToolCall, ToolResult, get_tool_registry
    )

logger = logging.getLogger(__name__)


# =============================================================================
# MCP TOOLS - API Testing
# =============================================================================

class APIRequestTool(MCPTool):
    """Make HTTP API request"""
    
    def get_tool_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="api_request",
            description="Make an HTTP request to an API endpoint. Supports all HTTP methods, headers, and body.",
            category="api_testing",
            agent_id="api_test_agent",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="API endpoint URL",
                    required=True
                ),
                ToolParameter(
                    name="method",
                    type="string",
                    description="HTTP method",
                    required=False,
                    default="GET",
                    enum=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="Request headers as key-value pairs",
                    required=False
                ),
                ToolParameter(
                    name="body",
                    type="string",
                    description="Request body (JSON string for POST/PUT/PATCH)",
                    required=False
                ),
                ToolParameter(
                    name="timeout",
                    type="number",
                    description="Request timeout in seconds",
                    required=False,
                    default=30
                )
            ],
            returns={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "status_code": {"type": "number"},
                    "response_time": {"type": "number"},
                    "headers": {"type": "object"},
                    "body": {"type": "string"}
                }
            }
        )
    
    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        body: str = None,
        timeout: float = 30
    ) -> ToolResult:
        """Execute HTTP request"""
        logger.info(f"🌐 API Request: {method} {url}")
        start_time = time.time()
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                request_kwargs = {
                    "method": method,
                    "url": url,
                    "headers": headers or {},
                    "timeout": aiohttp.ClientTimeout(total=timeout)
                }
                
                if body and method in ["POST", "PUT", "PATCH"]:
                    request_kwargs["data"] = body
                    if "Content-Type" not in (headers or {}):
                        request_kwargs["headers"]["Content-Type"] = "application/json"
                
                async with session.request(**request_kwargs) as response:
                    response_time = time.time() - start_time
                    response_body = await response.text()
                    
                    return ToolResult(
                        call_id="",
                        tool_name="api_request",
                        success=True,
                        result={
                            "status_code": response.status,
                            "response_time": round(response_time * 1000, 2),  # ms
                            "headers": dict(response.headers),
                            "body": response_body[:10000],  # Limit response size
                            "body_size": len(response_body),
                            "url": str(response.url)
                        }
                    )
        
        except asyncio.TimeoutError:
            return ToolResult(
                call_id="",
                tool_name="api_request",
                success=False,
                result=None,
                error=f"Request timed out after {timeout}s"
            )
        except Exception as e:
            return ToolResult(
                call_id="",
                tool_name="api_request",
                success=False,
                result=None,
                error=str(e)
            )


class APIValidateResponseTool(MCPTool):
    """Validate API response"""
    
    def get_tool_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="api_validate_response",
            description="Validate API response against expected values. Check status codes, headers, and body content.",
            category="api_testing",
            agent_id="api_test_agent",
            parameters=[
                ToolParameter(
                    name="response",
                    type="object",
                    description="Response object from api_request",
                    required=True,
                    properties={
                        "status_code": {"type": "number"},
                        "headers": {"type": "object"},
                        "body": {"type": "string"}
                    }
                ),
                ToolParameter(
                    name="expected_status",
                    type="number",
                    description="Expected HTTP status code",
                    required=False
                ),
                ToolParameter(
                    name="expected_headers",
                    type="object",
                    description="Expected headers (partial match)",
                    required=False
                ),
                ToolParameter(
                    name="body_contains",
                    type="array",
                    description="Strings that must appear in response body",
                    required=False,
                    items={"type": "string"}
                ),
                ToolParameter(
                    name="body_not_contains",
                    type="array",
                    description="Strings that must NOT appear in response body",
                    required=False,
                    items={"type": "string"}
                ),
                ToolParameter(
                    name="max_response_time",
                    type="number",
                    description="Maximum acceptable response time in ms",
                    required=False
                )
            ],
            returns={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "validations": {"type": "array"},
                    "passed": {"type": "number"},
                    "failed": {"type": "number"}
                }
            }
        )
    
    async def execute(
        self,
        response: Dict[str, Any],
        expected_status: int = None,
        expected_headers: Dict[str, str] = None,
        body_contains: List[str] = None,
        body_not_contains: List[str] = None,
        max_response_time: float = None
    ) -> ToolResult:
        """Validate response"""
        logger.info("✅ Validating API response")
        
        validations = []
        passed = 0
        failed = 0
        
        # Status code validation
        if expected_status is not None:
            actual_status = response.get("status_code")
            if actual_status == expected_status:
                validations.append({"check": "status_code", "passed": True, "expected": expected_status, "actual": actual_status})
                passed += 1
            else:
                validations.append({"check": "status_code", "passed": False, "expected": expected_status, "actual": actual_status})
                failed += 1
        
        # Header validation
        if expected_headers:
            actual_headers = response.get("headers", {})
            for key, value in expected_headers.items():
                actual_value = actual_headers.get(key)
                if actual_value and value.lower() in actual_value.lower():
                    validations.append({"check": f"header:{key}", "passed": True, "expected": value, "actual": actual_value})
                    passed += 1
                else:
                    validations.append({"check": f"header:{key}", "passed": False, "expected": value, "actual": actual_value})
                    failed += 1
        
        # Body contains validation
        if body_contains:
            body = response.get("body", "")
            for text in body_contains:
                if text in body:
                    validations.append({"check": f"body_contains:{text[:30]}", "passed": True})
                    passed += 1
                else:
                    validations.append({"check": f"body_contains:{text[:30]}", "passed": False})
                    failed += 1
        
        # Body not contains validation
        if body_not_contains:
            body = response.get("body", "")
            for text in body_not_contains:
                if text not in body:
                    validations.append({"check": f"body_not_contains:{text[:30]}", "passed": True})
                    passed += 1
                else:
                    validations.append({"check": f"body_not_contains:{text[:30]}", "passed": False})
                    failed += 1
        
        # Response time validation
        if max_response_time is not None:
            actual_time = response.get("response_time", 0)
            if actual_time <= max_response_time:
                validations.append({"check": "response_time", "passed": True, "expected": f"<={max_response_time}ms", "actual": f"{actual_time}ms"})
                passed += 1
            else:
                validations.append({"check": "response_time", "passed": False, "expected": f"<={max_response_time}ms", "actual": f"{actual_time}ms"})
                failed += 1
        
        return ToolResult(
            call_id="",
            tool_name="api_validate_response",
            success=failed == 0,
            result={
                "validations": validations,
                "passed": passed,
                "failed": failed,
                "all_passed": failed == 0
            }
        )


class APIValidateSchemaTool(MCPTool):
    """Validate JSON schema"""
    
    def get_tool_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="api_validate_schema",
            description="Validate response body against JSON schema. Ensures response structure matches expected format.",
            category="api_testing",
            agent_id="api_test_agent",
            parameters=[
                ToolParameter(
                    name="body",
                    type="string",
                    description="JSON response body to validate",
                    required=True
                ),
                ToolParameter(
                    name="schema",
                    type="object",
                    description="JSON Schema to validate against",
                    required=True
                )
            ],
            returns={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "valid": {"type": "boolean"},
                    "errors": {"type": "array"}
                }
            }
        )
    
    async def execute(self, body: str, schema: Dict[str, Any]) -> ToolResult:
        """Validate against JSON schema"""
        logger.info("📋 Validating JSON schema")
        
        try:
            # Parse JSON body
            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                return ToolResult(
                    call_id="",
                    tool_name="api_validate_schema",
                    success=False,
                    result={"valid": False, "errors": [f"Invalid JSON: {str(e)}"]}
                )
            
            # Try to use jsonschema if available
            try:
                import jsonschema
                jsonschema.validate(data, schema)
                return ToolResult(
                    call_id="",
                    tool_name="api_validate_schema",
                    success=True,
                    result={"valid": True, "errors": []}
                )
            except ImportError:
                # Basic validation without jsonschema
                errors = self._basic_validate(data, schema)
                return ToolResult(
                    call_id="",
                    tool_name="api_validate_schema",
                    success=len(errors) == 0,
                    result={"valid": len(errors) == 0, "errors": errors}
                )
            except jsonschema.ValidationError as e:
                return ToolResult(
                    call_id="",
                    tool_name="api_validate_schema",
                    success=False,
                    result={"valid": False, "errors": [str(e.message)]}
                )
        
        except Exception as e:
            return ToolResult(
                call_id="",
                tool_name="api_validate_schema",
                success=False,
                result=None,
                error=str(e)
            )
    
    def _basic_validate(self, data: Any, schema: Dict[str, Any], path: str = "") -> List[str]:
        """Basic JSON validation without jsonschema library"""
        errors = []
        
        # Type checking
        expected_type = schema.get("type")
        if expected_type:
            type_map = {
                "object": dict,
                "array": list,
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
                "null": type(None)
            }
            expected = type_map.get(expected_type)
            if expected and not isinstance(data, expected):
                errors.append(f"{path or 'root'}: expected {expected_type}, got {type(data).__name__}")
        
        # Required properties
        if expected_type == "object" and "required" in schema:
            for req in schema["required"]:
                if req not in data:
                    errors.append(f"{path or 'root'}: missing required property '{req}'")
        
        # Recursive validation for properties
        if expected_type == "object" and "properties" in schema and isinstance(data, dict):
            for prop, prop_schema in schema["properties"].items():
                if prop in data:
                    errors.extend(self._basic_validate(data[prop], prop_schema, f"{path}.{prop}" if path else prop))
        
        return errors


class APIPerformanceTestTool(MCPTool):
    """Run API performance test"""
    
    def get_tool_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="api_performance_test",
            description="Run performance/load test on API endpoint. Measures response times under load.",
            category="api_testing",
            agent_id="api_test_agent",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="API endpoint URL",
                    required=True
                ),
                ToolParameter(
                    name="method",
                    type="string",
                    description="HTTP method",
                    required=False,
                    default="GET",
                    enum=["GET", "POST", "PUT", "DELETE"]
                ),
                ToolParameter(
                    name="num_requests",
                    type="number",
                    description="Number of requests to make",
                    required=False,
                    default=10
                ),
                ToolParameter(
                    name="concurrent",
                    type="number",
                    description="Number of concurrent requests",
                    required=False,
                    default=5
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="Request headers",
                    required=False
                ),
                ToolParameter(
                    name="body",
                    type="string",
                    description="Request body",
                    required=False
                )
            ],
            returns={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "total_requests": {"type": "number"},
                    "successful_requests": {"type": "number"},
                    "failed_requests": {"type": "number"},
                    "avg_response_time": {"type": "number"},
                    "min_response_time": {"type": "number"},
                    "max_response_time": {"type": "number"},
                    "p95_response_time": {"type": "number"},
                    "requests_per_second": {"type": "number"}
                }
            }
        )
    
    async def execute(
        self,
        url: str,
        method: str = "GET",
        num_requests: int = 10,
        concurrent: int = 5,
        headers: Dict[str, str] = None,
        body: str = None
    ) -> ToolResult:
        """Execute performance test"""
        logger.info(f"⚡ Performance test: {num_requests} requests to {url}")
        
        response_times = []
        success_count = 0
        fail_count = 0
        start_time = time.time()
        
        registry = get_tool_registry()
        api_request_tool = registry.get_tool("api_request")
        
        if not api_request_tool:
            return ToolResult(
                call_id="",
                tool_name="api_performance_test",
                success=False,
                result=None,
                error="api_request tool not found"
            )
        
        # Create batches for concurrent execution
        semaphore = asyncio.Semaphore(concurrent)
        
        async def make_request():
            nonlocal success_count, fail_count
            async with semaphore:
                result = await api_request_tool.execute(
                    url=url,
                    method=method,
                    headers=headers,
                    body=body,
                    timeout=30
                )
                if result.success:
                    success_count += 1
                    response_times.append(result.result.get("response_time", 0))
                else:
                    fail_count += 1
        
        # Execute all requests
        tasks = [make_request() for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        if response_times:
            sorted_times = sorted(response_times)
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            p95_idx = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_idx] if p95_idx < len(sorted_times) else max_time
            rps = num_requests / total_time if total_time > 0 else 0
        else:
            avg_time = min_time = max_time = p95_time = rps = 0
        
        return ToolResult(
            call_id="",
            tool_name="api_performance_test",
            success=True,
            result={
                "total_requests": num_requests,
                "successful_requests": success_count,
                "failed_requests": fail_count,
                "success_rate": round((success_count / num_requests) * 100, 2) if num_requests > 0 else 0,
                "avg_response_time": round(avg_time, 2),
                "min_response_time": round(min_time, 2),
                "max_response_time": round(max_time, 2),
                "p95_response_time": round(p95_time, 2),
                "requests_per_second": round(rps, 2),
                "total_time": round(total_time, 2)
            }
        )


class RunAPITestTool(MCPTool):
    """Execute complete API test"""
    
    def get_tool_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="run_api_test",
            description="Execute a complete API test with request and validations. Combines api_request and api_validate_response.",
            category="api_testing",
            agent_id="api_test_agent",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="API endpoint URL",
                    required=True
                ),
                ToolParameter(
                    name="method",
                    type="string",
                    description="HTTP method",
                    required=False,
                    default="GET",
                    enum=["GET", "POST", "PUT", "PATCH", "DELETE"]
                ),
                ToolParameter(
                    name="headers",
                    type="object",
                    description="Request headers",
                    required=False
                ),
                ToolParameter(
                    name="body",
                    type="string",
                    description="Request body",
                    required=False
                ),
                ToolParameter(
                    name="expected_status",
                    type="number",
                    description="Expected HTTP status code",
                    required=False,
                    default=200
                ),
                ToolParameter(
                    name="body_contains",
                    type="array",
                    description="Strings that must appear in response",
                    required=False,
                    items={"type": "string"}
                ),
                ToolParameter(
                    name="schema",
                    type="object",
                    description="JSON schema to validate response",
                    required=False
                )
            ],
            returns={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "status_code": {"type": "number"},
                    "response_time": {"type": "number"},
                    "validations": {"type": "array"},
                    "response_body": {"type": "string"}
                }
            }
        )
    
    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        body: str = None,
        expected_status: int = 200,
        body_contains: List[str] = None,
        schema: Dict[str, Any] = None
    ) -> ToolResult:
        """Execute full API test"""
        logger.info(f"🧪 Running API test: {method} {url}")
        
        registry = get_tool_registry()
        
        # Make request
        request_tool = registry.get_tool("api_request")
        if not request_tool:
            return ToolResult(
                call_id="",
                tool_name="run_api_test",
                success=False,
                result=None,
                error="api_request tool not found"
            )
        
        request_result = await request_tool.execute(
            url=url,
            method=method,
            headers=headers,
            body=body
        )
        
        if not request_result.success:
            return ToolResult(
                call_id="",
                tool_name="run_api_test",
                success=False,
                result={
                    "request_error": request_result.error,
                    "validations": []
                },
                error=request_result.error
            )
        
        response = request_result.result
        validations = []
        
        # Validate response
        validate_tool = registry.get_tool("api_validate_response")
        if validate_tool:
            validate_result = await validate_tool.execute(
                response=response,
                expected_status=expected_status,
                body_contains=body_contains
            )
            if validate_result.result:
                validations.extend(validate_result.result.get("validations", []))
        
        # Validate schema if provided
        if schema:
            schema_tool = registry.get_tool("api_validate_schema")
            if schema_tool:
                schema_result = await schema_tool.execute(
                    body=response.get("body", ""),
                    schema=schema
                )
                if schema_result.result:
                    for error in schema_result.result.get("errors", []):
                        validations.append({"check": "schema", "passed": False, "error": error})
                    if not schema_result.result.get("errors"):
                        validations.append({"check": "schema", "passed": True})
        
        passed = sum(1 for v in validations if v.get("passed", False))
        failed = sum(1 for v in validations if not v.get("passed", True))
        
        return ToolResult(
            call_id="",
            tool_name="run_api_test",
            success=failed == 0,
            result={
                "status_code": response.get("status_code"),
                "response_time": response.get("response_time"),
                "response_size": response.get("body_size"),
                "validations": validations,
                "passed": passed,
                "failed": failed,
                "response_body": response.get("body", "")[:1000]  # Limit size
            }
        )


# =============================================================================
# API TEST AGENT - MCP COMPLIANT
# =============================================================================

class APITestAgentMCP(MCPAgent):
    """
    API Test Agent - MCP Compliant
    Exposes API testing tools via MCP protocol
    """
    
    def __init__(self):
        super().__init__(
            agent_id="api_test_agent",
            agent_name="API Test Agent",
            category="api_testing"
        )
        self.register_tools()
    
    def get_tools(self) -> List[MCPTool]:
        """Return all API testing tools"""
        return [
            APIRequestTool(),
            APIValidateResponseTool(),
            APIValidateSchemaTool(),
            APIPerformanceTestTool(),
            RunAPITestTool()
        ]


# =============================================================================
# BACKWARDS COMPATIBILITY - Original APITestAgent interface
# =============================================================================

class APITestAgent:
    """
    Legacy interface for backwards compatibility
    Wraps the MCP-compliant agent
    """
    
    def __init__(self):
        self._mcp_agent = APITestAgentMCP()
        self.agent_type = "api"
        self.capabilities = [
            "rest_api_testing",
            "graphql_testing",
            "performance_testing",
            "contract_validation",
            "response_validation",
            "status_code_check",
            "header_validation",
            "json_schema_validation"
        ]
    
    async def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API test using MCP tools"""
        registry = get_tool_registry()
        tool = registry.get_tool("run_api_test")
        
        if tool:
            result = await tool.execute(
                url=target,
                method=config.get("method", "GET"),
                headers=config.get("headers"),
                body=config.get("body"),
                expected_status=config.get("expected_status", 200),
                body_contains=config.get("body_contains"),
                schema=config.get("schema")
            )
            
            return {
                "success": result.success,
                "agent": "API Test Agent",
                "target": target,
                "method": config.get("method", "GET"),
                "status_code": result.result.get("status_code") if result.result else None,
                "response_time": result.result.get("response_time") if result.result else None,
                "validations": result.result.get("validations", []) if result.result else [],
                "passed": result.result.get("passed", 0) if result.result else 0,
                "failed": result.result.get("failed", 0) if result.result else 0,
                "execution_time": result.execution_time
            }
        
        return {
            "success": False,
            "agent": "API Test Agent",
            "error": "run_api_test tool not found in registry"
        }
