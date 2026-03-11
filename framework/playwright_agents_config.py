"""
🎭 PLAYWRIGHT AGENTS CONFIGURATION
Environment-based configuration for Planner, Generator, and Healer agents

All values can be configured via environment variables - no hard-coded defaults
"""

import os
from typing import Dict, Any, Optional, List

# =============================================================================
# OLLAMA LLM CONFIGURATION
# =============================================================================

OLLAMA_CONFIG = {
    "host": os.environ.get("OLLAMA_HOST", "localhost"),
    "port": os.environ.get("OLLAMA_PORT", "11434"),
    "model": os.environ.get("OLLAMA_MODEL", "llama3.2:latest"),
    "timeout": int(os.environ.get("OLLAMA_TIMEOUT", "120")),
    "api_key": os.environ.get("OLLAMA_API_KEY", "ollama"),
}

# =============================================================================
# MCP PLAYWRIGHT CONFIGURATION
# =============================================================================

MCP_PLAYWRIGHT_CONFIG = {
    "browser": os.environ.get("PLAYWRIGHT_BROWSER", "chromium"),
    "headless": os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() == "true",
    "viewport_width": int(os.environ.get("PLAYWRIGHT_VIEWPORT_WIDTH", "1920")),
    "viewport_height": int(os.environ.get("PLAYWRIGHT_VIEWPORT_HEIGHT", "1080")),
    "timeout": int(os.environ.get("PLAYWRIGHT_TIMEOUT", "30000")),
    "screenshot_path": os.environ.get("PLAYWRIGHT_SCREENSHOT_PATH", "./screenshots"),
}

# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

PLANNER_CONFIG = {
    "default_test_type": os.environ.get("PLANNER_TEST_TYPE", "functional"),
    "max_scenarios": int(os.environ.get("PLANNER_MAX_SCENARIOS", "20")),
    "enable_llm": os.environ.get("PLANNER_ENABLE_LLM", "true").lower() == "true",
    "llm_model": os.environ.get("PLANNER_LLM_MODEL", "llama3.2:latest"),
}

GENERATOR_CONFIG = {
    "default_framework": os.environ.get("GENERATOR_FRAMEWORK", "playwright"),
    "default_language": os.environ.get("GENERATOR_LANGUAGE", "python"),
    "enable_llm": os.environ.get("GENERATOR_ENABLE_LLM", "true").lower() == "true",
    "llm_model": os.environ.get("GENERATOR_LLM_MODEL", "llama3.2:latest"),
    "include_page_objects": os.environ.get("GENERATOR_PAGE_OBJECTS", "true").lower() == "true",
    "include_fixtures": os.environ.get("GENERATOR_FIXTURES", "true").lower() == "true",
}

HEALER_CONFIG = {
    "enable_llm": os.environ.get("HEALER_ENABLE_LLM", "true").lower() == "true",
    "llm_model": os.environ.get("HEALER_LLM_MODEL", "llama3.2:latest"),
    "auto_fix_threshold": int(os.environ.get("HEALER_AUTO_FIX_THRESHOLD", "75")),
    "max_retry_attempts": int(os.environ.get("HEALER_MAX_RETRIES", "3")),
    "enable_mcp_healing": os.environ.get("HEALER_ENABLE_MCP", "true").lower() == "true",
}

# =============================================================================
# SUPPORTED FRAMEWORKS AND LANGUAGES
# =============================================================================

SUPPORTED_FRAMEWORKS = {
    "playwright": {
        "languages": ["python", "typescript", "javascript"],
        "mcp_tools": ["browser_navigate", "browser_click", "browser_fill", "browser_snapshot"],
        "description": "Modern end-to-end testing framework"
    },
    "selenium": {
        "languages": ["python", "java", "javascript"],
        "mcp_tools": [],
        "description": "Classic browser automation framework"
    },
    "cypress": {
        "languages": ["javascript", "typescript"],
        "mcp_tools": [],
        "description": "JavaScript end-to-end testing framework"
    }
}

# =============================================================================
# FAILURE TYPE CONFIGURATIONS
# =============================================================================

FAILURE_TYPES = {
    "timeout": {
        "confidence": 90,
        "success_probability": 85,
        "common_fixes": ["increase_timeout", "explicit_wait", "network_idle_wait"],
        "mcp_tools": ["browser_wait", "browser_snapshot"]
    },
    "selector_issue": {
        "confidence": 85,
        "success_probability": 70,
        "common_fixes": ["update_selector", "use_test_id", "fallback_selector"],
        "mcp_tools": ["browser_snapshot", "browser_click"]
    },
    "assertion_failure": {
        "confidence": 95,
        "success_probability": 60,
        "common_fixes": ["update_assertion", "flexible_assertion"],
        "mcp_tools": ["browser_snapshot"]
    },
    "network_issue": {
        "confidence": 80,
        "success_probability": 75,
        "common_fixes": ["add_retry", "check_endpoint", "mock_request"],
        "mcp_tools": ["browser_navigate"]
    },
    "stale_element": {
        "confidence": 85,
        "success_probability": 80,
        "common_fixes": ["relocate_element", "wait_for_stability"],
        "mcp_tools": ["browser_wait", "browser_click"]
    },
    "timing_issue": {
        "confidence": 75,
        "success_probability": 70,
        "common_fixes": ["add_wait", "network_idle", "synchronize"],
        "mcp_tools": ["browser_wait", "browser_snapshot"]
    },
    "unknown": {
        "confidence": 40,
        "success_probability": 30,
        "common_fixes": ["manual_review", "add_logging"],
        "mcp_tools": ["browser_snapshot"]
    }
}

# =============================================================================
# MCP TOOL MAPPINGS
# =============================================================================

MCP_TOOLS = {
    # Browser navigation
    "browser_navigate": {
        "description": "Navigate to URL",
        "agent": "playwright",
        "parameters": ["url", "wait_until"]
    },
    "browser_click": {
        "description": "Click element",
        "agent": "playwright",
        "parameters": ["selector", "text", "button"]
    },
    "browser_fill": {
        "description": "Fill form field",
        "agent": "playwright",
        "parameters": ["selector", "value"]
    },
    "browser_type": {
        "description": "Type text",
        "agent": "playwright",
        "parameters": ["selector", "text", "delay"]
    },
    "browser_screenshot": {
        "description": "Take screenshot",
        "agent": "playwright",
        "parameters": ["path", "full_page"]
    },
    "browser_wait": {
        "description": "Wait for condition",
        "agent": "playwright",
        "parameters": ["selector", "state", "timeout"]
    },
    "browser_snapshot": {
        "description": "Get page snapshot",
        "agent": "playwright",
        "parameters": []
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_ollama_config() -> Dict[str, Any]:
    """Get Ollama configuration"""
    return OLLAMA_CONFIG.copy()

def get_mcp_playwright_config() -> Dict[str, Any]:
    """Get MCP Playwright configuration"""
    return MCP_PLAYWRIGHT_CONFIG.copy()

def get_planner_config() -> Dict[str, Any]:
    """Get Planner agent configuration"""
    return PLANNER_CONFIG.copy()

def get_generator_config() -> Dict[str, Any]:
    """Get Generator agent configuration"""
    return GENERATOR_CONFIG.copy()

def get_healer_config() -> Dict[str, Any]:
    """Get Healer agent configuration"""
    return HEALER_CONFIG.copy()

def get_failure_type_config(failure_type: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific failure type"""
    return FAILURE_TYPES.get(failure_type)

def get_mcp_tool_config(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific MCP tool"""
    return MCP_TOOLS.get(tool_name)

def is_framework_supported(framework: str, language: str) -> bool:
    """Check if framework and language combination is supported"""
    if framework not in SUPPORTED_FRAMEWORKS:
        return False
    return language in SUPPORTED_FRAMEWORKS[framework]["languages"]

def get_framework_mcp_tools(framework: str) -> List[str]:
    """Get MCP tools available for a framework"""
    if framework not in SUPPORTED_FRAMEWORKS:
        return []
    return SUPPORTED_FRAMEWORKS[framework]["mcp_tools"]

def get_all_mcp_tools() -> List[str]:
    """Get all available MCP tools"""
    return list(MCP_TOOLS.keys())

# =============================================================================
# ENVIRONMENT CONFIGURATION EXAMPLES
# =============================================================================

"""
Set these environment variables to customize agent behavior:

# Ollama LLM
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export OLLAMA_MODEL=llama3.2:latest

# MCP Playwright
export PLAYWRIGHT_BROWSER=chromium
export PLAYWRIGHT_HEADLESS=true
export PLAYWRIGHT_TIMEOUT=30000

# Planner Agent
export PLANNER_ENABLE_LLM=true
export PLANNER_MAX_SCENARIOS=20

# Generator Agent
export GENERATOR_FRAMEWORK=playwright
export GENERATOR_LANGUAGE=python
export GENERATOR_ENABLE_LLM=true

# Healer Agent
export HEALER_ENABLE_LLM=true
export HEALER_AUTO_FIX_THRESHOLD=75
export HEALER_ENABLE_MCP=true
"""
