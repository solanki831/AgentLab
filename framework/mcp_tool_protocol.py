"""
🔧 MCP TOOL PROTOCOL - Core MCP Implementation
True Model Context Protocol principles:
- Agents expose tools with JSON Schema
- Structured tool_call / tool_result format
- LLM-agnostic tool invocation
- Registry-based tool discovery
"""

import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# MCP PROTOCOL DATA STRUCTURES
# =============================================================================

@dataclass
class ToolParameter:
    """JSON Schema parameter definition"""
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None
    properties: Optional[Dict[str, Any]] = None  # For object types
    items: Optional[Dict[str, Any]] = None  # For array types

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format"""
        schema = {
            "type": self.type,
            "description": self.description
        }
        if self.default is not None:
            schema["default"] = self.default
        if self.enum:
            schema["enum"] = self.enum
        if self.properties:
            schema["properties"] = self.properties
        if self.items:
            schema["items"] = self.items
        return schema


@dataclass
class ToolDefinition:
    """MCP Tool Definition with JSON Schema"""
    name: str
    description: str
    parameters: List[ToolParameter]
    returns: Dict[str, Any]  # JSON Schema for return type
    category: str = "general"
    agent_id: str = ""
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI/Anthropic compatible function schema"""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def to_ollama_format(self) -> Dict[str, Any]:
        """Convert to Ollama tools format"""
        return self.to_json_schema()


@dataclass
class ToolCall:
    """Structured tool call request"""
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.call_id:
            self.call_id = f"call_{self.tool_name}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.call_id,
            "type": "function",
            "function": {
                "name": self.tool_name,
                "arguments": json.dumps(self.arguments)
            }
        }


@dataclass
class ToolResult:
    """Structured tool execution result"""
    call_id: str
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_call_id": self.call_id,
            "role": "tool",
            "name": self.tool_name,
            "content": json.dumps({
                "success": self.success,
                "result": self.result,
                "error": self.error,
                "execution_time": self.execution_time,
                "metadata": self.metadata
            })
        }


# =============================================================================
# MCP TOOL BASE CLASS
# =============================================================================

class MCPTool(ABC):
    """
    Base class for MCP-compliant tools
    
    All tools must:
    1. Define their schema via get_tool_definition()
    2. Implement execute() with structured input/output
    3. Validate inputs against schema
    """
    
    @abstractmethod
    def get_tool_definition(self) -> ToolDefinition:
        """Return the tool's JSON Schema definition"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with validated arguments"""
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate arguments against tool schema"""
        definition = self.get_tool_definition()
        
        # Check required parameters
        for param in definition.parameters:
            if param.required and param.name not in arguments:
                return False, f"Missing required parameter: {param.name}"
            
            if param.name in arguments:
                value = arguments[param.name]
                # Type checking
                if param.type == "string" and not isinstance(value, str):
                    return False, f"Parameter {param.name} must be string"
                elif param.type == "number" and not isinstance(value, (int, float)):
                    return False, f"Parameter {param.name} must be number"
                elif param.type == "boolean" and not isinstance(value, bool):
                    return False, f"Parameter {param.name} must be boolean"
                elif param.type == "array" and not isinstance(value, list):
                    return False, f"Parameter {param.name} must be array"
                elif param.type == "object" and not isinstance(value, dict):
                    return False, f"Parameter {param.name} must be object"
                
                # Enum checking
                if param.enum and value not in param.enum:
                    return False, f"Parameter {param.name} must be one of: {param.enum}"
        
        return True, None
    
    async def __call__(self, tool_call: ToolCall) -> ToolResult:
        """Execute tool from ToolCall object"""
        start_time = datetime.now()
        
        # Validate arguments
        valid, error = self.validate_arguments(tool_call.arguments)
        if not valid:
            return ToolResult(
                call_id=tool_call.call_id,
                tool_name=tool_call.tool_name,
                success=False,
                result=None,
                error=error,
                execution_time=0.0
            )
        
        try:
            result = await self.execute(**tool_call.arguments)
            result.call_id = tool_call.call_id
            result.execution_time = (datetime.now() - start_time).total_seconds()
            return result
        except Exception as e:
            return ToolResult(
                call_id=tool_call.call_id,
                tool_name=tool_call.tool_name,
                success=False,
                result=None,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )


# =============================================================================
# MCP TOOL REGISTRY
# =============================================================================

class MCPToolRegistry:
    """
    Central registry for MCP tools
    Enables tool discovery and LLM-driven selection
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, MCPTool] = {}
            cls._instance._categories: Dict[str, List[str]] = {}
        return cls._instance
    
    def register(self, tool: MCPTool) -> None:
        """Register a tool in the registry"""
        definition = tool.get_tool_definition()
        self._tools[definition.name] = tool
        
        # Index by category
        if definition.category not in self._categories:
            self._categories[definition.category] = []
        if definition.name not in self._categories[definition.category]:
            self._categories[definition.category].append(definition.name)
        
        logger.info(f"🔧 Registered MCP tool: {definition.name} [{definition.category}]")
    
    def unregister(self, tool_name: str) -> None:
        """Unregister a tool"""
        if tool_name in self._tools:
            definition = self._tools[tool_name].get_tool_definition()
            del self._tools[tool_name]
            if definition.category in self._categories:
                self._categories[definition.category].remove(tool_name)
            logger.info(f"🔧 Unregistered MCP tool: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        return self._tools.get(tool_name)
    
    def get_tools_by_category(self, category: str) -> List[MCPTool]:
        """Get all tools in a category"""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_all_tools(self) -> Dict[str, MCPTool]:
        """Get all registered tools"""
        return self._tools.copy()
    
    def get_tool_definitions(self, category: Optional[str] = None) -> List[ToolDefinition]:
        """Get tool definitions (for LLM context)"""
        if category:
            tools = self.get_tools_by_category(category)
        else:
            tools = list(self._tools.values())
        return [tool.get_tool_definition() for tool in tools]
    
    def get_tools_for_llm(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tools in LLM-compatible format (OpenAI/Ollama)"""
        definitions = self.get_tool_definitions(category)
        return [d.to_json_schema() for d in definitions]
    
    def get_tools_summary(self) -> str:
        """Get human-readable tools summary"""
        lines = ["Available MCP Tools:", "=" * 50]
        for category, tool_names in self._categories.items():
            lines.append(f"\n📁 {category.upper()}")
            for name in tool_names:
                tool = self._tools.get(name)
                if tool:
                    definition = tool.get_tool_definition()
                    lines.append(f"  • {name}: {definition.description}")
        return "\n".join(lines)
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool by ToolCall"""
        tool = self.get_tool(tool_call.tool_name)
        if not tool:
            return ToolResult(
                call_id=tool_call.call_id,
                tool_name=tool_call.tool_name,
                success=False,
                result=None,
                error=f"Tool not found: {tool_call.tool_name}"
            )
        return await tool(tool_call)


# =============================================================================
# MCP AGENT BASE CLASS
# =============================================================================

class MCPAgent(ABC):
    """
    Base class for MCP-compliant agents
    
    Agents:
    1. Expose one or more tools
    2. Register tools with the registry
    3. Can be discovered by the orchestrator
    """
    
    def __init__(self, agent_id: str, agent_name: str, category: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.category = category
        self._tools: List[MCPTool] = []
        self._registry = MCPToolRegistry()
        self.is_available = True  # Add availability status
        self.current_tasks = []  # Track current tasks
        self.max_concurrent_tasks = 5  # Default max concurrent
    
    @property
    def name(self) -> str:
        """Alias for agent_name (for dashboard compatibility)"""
        return self.agent_name
    
    @property
    def agent_type(self) -> str:
        """Alias for category (for dashboard compatibility)"""
        return self.category
    
    @abstractmethod
    def get_tools(self) -> List[MCPTool]:
        """Return list of tools this agent provides"""
        pass
    
    def register_tools(self) -> None:
        """Register all agent tools with the registry"""
        self._tools = self.get_tools()
        for tool in self._tools:
            self._registry.register(tool)
        logger.info(f"🤖 Agent '{self.agent_name}' registered {len(self._tools)} tools")
    
    def unregister_tools(self) -> None:
        """Unregister all agent tools"""
        for tool in self._tools:
            definition = tool.get_tool_definition()
            self._registry.unregister(definition.name)
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """Get definitions of all tools this agent provides"""
        return [tool.get_tool_definition() for tool in self._tools]
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Get agent capabilities summary"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "category": self.category,
            "tools": [t.get_tool_definition().name for t in self._tools],
            "tool_count": len(self._tools)
        }


# =============================================================================
# GLOBAL REGISTRY ACCESSOR
# =============================================================================

def get_tool_registry() -> MCPToolRegistry:
    """Get the global MCP tool registry"""
    return MCPToolRegistry()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_tool_call(tool_name: str, **kwargs) -> ToolCall:
    """Helper to create a ToolCall"""
    return ToolCall(tool_name=tool_name, arguments=kwargs)


def parse_llm_tool_calls(llm_response: Dict[str, Any]) -> List[ToolCall]:
    """Parse tool calls from LLM response (OpenAI/Ollama format)"""
    tool_calls = []
    
    # Handle OpenAI format
    if "tool_calls" in llm_response:
        for tc in llm_response["tool_calls"]:
            tool_calls.append(ToolCall(
                call_id=tc.get("id", ""),
                tool_name=tc["function"]["name"],
                arguments=json.loads(tc["function"]["arguments"])
            ))
    
    # Handle Ollama format
    elif "message" in llm_response and "tool_calls" in llm_response.get("message", {}):
        for tc in llm_response["message"]["tool_calls"]:
            tool_calls.append(ToolCall(
                call_id=tc.get("id", ""),
                tool_name=tc["function"]["name"],
                arguments=tc["function"]["arguments"] if isinstance(tc["function"]["arguments"], dict) 
                          else json.loads(tc["function"]["arguments"])
            ))
    
    return tool_calls


def format_tool_results_for_llm(results: List[ToolResult]) -> List[Dict[str, Any]]:
    """Format tool results for LLM context"""
    return [result.to_dict() for result in results]
