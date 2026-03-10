# 🎯 Multi-Agent Orchestration System - Complete Guide

## Overview
This guide explains how to use the **True Multi-Agent Orchestration System** that mimics a real QA team structure with specialized agents working together.

## Agent Team Structure

### 1. **Orchestrator Agent** (Test Lead)
- **Role**: Coordinates all other agents
- **Responsibilities**:
  - Create test execution plans
  - Assign tasks to specialized agents
  - Manage dependencies between tasks
  - Handle parallel/sequential execution
  - Retry failed tests with healing
  - Generate final reports

### 2. **UI Test Agent** (Automation Engineer)
- **Role**: Browser automation specialist
- **Capabilities**:
  - Navigate to URLs
  - Click elements
  - Fill forms
  - Type text
  - Capture screenshots
  - Wait for elements
  - Assertions
- **MCP Tools**: Uses `mcp_microsoft_pla_browser_*` tools

### 3. **API Test Agent** (API Tester)
- **Role**: API testing specialist
- **Capabilities**:
  - REST API testing (GET, POST, PUT, DELETE, PATCH)
  - GraphQL queries
  - Performance testing
  - Response validation
  - Status code checks
  - Header validation
  - JSON schema validation
- **MCP Tools**: Uses REST API MCP tools

### 4. **Healing Agent** (Flaky Test Fixer)
- **Role**: Auto-repair failed tests
- **Capabilities**:
  - Failure analysis using AI
  - Pattern detection (timeout, selector, network, auth)
  - Generate healing strategies
  - Update test configurations
  - Retry with healed config
  - Track healing success rates

### 5. **Validation Agent** (Reviewer)
- **Role**: Data validation specialist
- **Capabilities**:
  - Schema validation
  - Type checking
  - Regex validation
  - Range validation
  - JSON path validation
  - Uniqueness checks
  - Data integrity verification

### 6. **Report Agent** (Analyst)
- **Role**: Reporting and analysis specialist
- **Capabilities**:
  - Result aggregation
  - Metrics calculation
  - Root cause analysis (RCA)
  - Trend analysis
  - HTML/Markdown/JSON reports
  - Executive summaries

## Usage Examples

### Example 1: Simple UI Test

```python
from framework.orchestrator_agent import OrchestratorAgent
import asyncio

async def run_ui_test():
    # Create orchestrator
    orchestrator = OrchestratorAgent()
    
    # Define test suite
    test_suite = {
        "tests": [
            {
                "type": "ui",
                "target": "https://example.com",
                "config": {
                    "steps": [
                        {"action": "navigate", "url": "https://example.com"},
                        {"action": "click", "selector": "#login-button"},
                        {"action": "type", "selector": "#username", "text": "testuser"},
                        {"action": "screenshot"}
                    ]
                }
            }
        ]
    }
    
    # Create plan and execute
    orchestrator.create_test_plan(test_suite)
    results = await orchestrator.execute_test_plan(parallel=False)
    
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"🔧 Healed: {results['healed']}")

# Run
asyncio.run(run_ui_test())
```

### Example 2: API Test with Validation

```python
async def run_api_validation_test():
    orchestrator = OrchestratorAgent()
    
    test_suite = {
        "tests": [
            {
                "type": "api",
                "target": "https://api.example.com/users",
                "config": {
                    "method": "GET",
                    "headers": {"Authorization": "Bearer token123"},
                    "assertions": [
                        {"type": "status_code", "expected": 200},
                        {"type": "response_time", "max": 2.0},
                        {"type": "json_path", "path": "data.id", "expected": 123}
                    ]
                },
                "priority": 1
            },
            {
                "type": "validation",
                "target": "api_response",
                "config": {
                    "data": {},  # Will be filled from API response
                    "validations": [
                        {"type": "schema", "schema": {
                            "required": ["id", "name", "status"],
                            "properties": {
                                "id": {"type": "number"},
                                "name": {"type": "string"},
                                "status": {"type": "string"}
                            }
                        }}
                    ]
                },
                "dependencies": ["test_0"]  # Runs after API test
            }
        ]
    }
    
    orchestrator.create_test_plan(test_suite)
    results = await orchestrator.execute_test_plan(parallel=True)
    
    return results

asyncio.run(run_api_validation_test())
```

### Example 3: Full Suite with Healing and Reporting

```python
async def run_full_test_suite():
    orchestrator = OrchestratorAgent()
    
    test_suite = {
        "tests": [
            # UI Test
            {
                "type": "ui",
                "target": "https://example.com/dashboard",
                "config": {
                    "steps": [
                        {"action": "navigate", "url": "https://example.com/dashboard"},
                        {"action": "wait", "selector": ".dashboard-loaded"},
                        {"action": "assert_visible", "selector": ".user-info"}
                    ]
                },
                "priority": 1
            },
            # API Performance Test
            {
                "type": "api",
                "target": "https://api.example.com/health",
                "config": {
                    "method": "GET",
                    "assertions": [
                        {"type": "status_code", "expected": 200},
                        {"type": "response_time", "max": 1.0}
                    ]
                },
                "priority": 1
            },
            # Data Validation
            {
                "type": "validation",
                "target": "test_data",
                "config": {
                    "data": {"id": 123, "name": "Test", "count": 42},
                    "validations": [
                        {"type": "type", "field": "id", "expected_type": "integer"},
                        {"type": "range", "field": "count", "min": 0, "max": 100}
                    ]
                },
                "priority": 2
            }
        ]
    }
    
    orchestrator.create_test_plan(test_suite)
    results = await orchestrator.execute_test_plan(parallel=True)
    
    # Results include:
    # - Individual test results
    # - Auto-healing attempts
    # - Comprehensive report with RCA
    
    print(f"\n📊 Test Summary:")
    print(f"Total: {results['total_tasks']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    print(f"Healed: {results['healed']} 🔧")
    
    if 'report' in results:
        report = results['report']
        print(f"\nPass Rate: {report.get('metrics', {}).get('pass_rate', 0):.1f}%")
    
    return results

asyncio.run(run_full_test_suite())
```

### Example 4: Using Individual Agents

```python
from framework.ui_test_agent import UITestAgent
from framework.api_test_agent import APITestAgent
from framework.healing_agent import HealingAgent
from framework.validation_agent import ValidationAgent

# Use UI Agent directly
async def test_ui():
    ui_agent = UITestAgent()
    
    config = {
        "steps": [
            {"action": "navigate", "url": "https://example.com"},
            {"action": "click", "selector": "#submit"},
            {"action": "screenshot"}
        ]
    }
    
    result = await ui_agent.execute("https://example.com", config)
    return result

# Use API Agent directly
async def test_api():
    api_agent = APITestAgent()
    
    config = {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": '{"name": "Test"}',
        "assertions": [
            {"type": "status_code", "expected": 201}
        ]
    }
    
    result = await api_agent.execute("https://api.example.com/items", config)
    return result

# Use Healing Agent
async def heal_failed_test():
    healing_agent = HealingAgent()
    
    config = {
        "failed_test": {
            "name": "login_test",
            "type": "ui"
        },
        "error_info": "Element not found: #login-button",
        "test_config": {"selector": "#login-button"}
    }
    
    result = await healing_agent.execute("heal_login", config)
    return result

# Use Validation Agent
async def validate_data():
    validation_agent = ValidationAgent()
    
    config = {
        "data": {"id": 123, "name": "Test", "email": "test@example.com"},
        "validations": [
            {"type": "not_null", "field": "id"},
            {"type": "regex", "field": "email", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
            {"type": "type", "field": "name", "expected_type": "string"}
        ]
    }
    
    result = await validation_agent.execute("user_data", config)
    return result
```

## Task Configuration Reference

### UI Task Config
```python
{
    "type": "ui",
    "target": "https://example.com",
    "config": {
        "steps": [
            {"action": "navigate", "url": "..."},
            {"action": "click", "selector": "..."},
            {"action": "fill", "selector": "...", "value": "..."},
            {"action": "type", "selector": "...", "text": "..."},
            {"action": "screenshot"},
            {"action": "wait", "selector": "..."},
            {"action": "assert_text", "selector": "...", "expected": "..."},
            {"action": "assert_visible", "selector": "..."}
        ]
    },
    "priority": 1,  # 1=high, 2=medium, 3=low
    "dependencies": [],  # Task IDs that must complete first
    "max_retries": 2
}
```

### API Task Config
```python
{
    "type": "api",  # or "rest", "graphql"
    "target": "https://api.example.com/endpoint",
    "config": {
        "method": "GET",  # GET, POST, PUT, DELETE, PATCH
        "headers": {"Authorization": "Bearer token"},
        "body": '{"key": "value"}',  # For POST/PUT/PATCH
        "assertions": [
            {"type": "status_code", "expected": 200},
            {"type": "response_time", "max": 2.0},
            {"type": "json_path", "path": "data.id", "expected": 123},
            {"type": "header", "name": "Content-Type", "expected": "application/json"},
            {"type": "schema", "schema": {...}}
        ]
    }
}
```

### Validation Task Config
```python
{
    "type": "validation",
    "target": "data_name",
    "config": {
        "data": {...},  # Data to validate
        "validations": [
            {"type": "equals", "field": "id", "expected": 123},
            {"type": "contains", "field": "tags", "expected": "important"},
            {"type": "regex", "field": "email", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
            {"type": "schema", "schema": {...}},
            {"type": "type", "field": "count", "expected_type": "integer"},
            {"type": "range", "field": "score", "min": 0, "max": 100},
            {"type": "json_path", "path": "user.name", "expected": "John"},
            {"type": "length", "field": "items", "min": 1, "max": 10},
            {"type": "unique", "field": "ids"},
            {"type": "not_null", "field": "email"}
        ]
    }
}
```

### Healing Task Config
```python
{
    "type": "healing",
    "target": "failed_test_id",
    "config": {
        "failed_test": {
            "name": "test_name",
            "type": "ui"
        },
        "error_info": "Element not found...",
        "test_config": {...}  # Original test config
    }
}
```

### Report Task Config
```python
{
    "type": "report",
    "target": "final_report",
    "config": {
        "results": [...],  # List of test results
        "report_type": "detailed",  # summary, detailed, executive, html, markdown
        "options": {
            "include_rca": True,
            "include_metrics": True
        }
    }
}
```

## Execution Modes

### Parallel Execution
```python
# Run tests in parallel where possible (respects dependencies)
results = await orchestrator.execute_test_plan(parallel=True)
```

### Sequential Execution
```python
# Run tests one by one in order
results = await orchestrator.execute_test_plan(parallel=False)
```

## Auto-Healing

The orchestrator automatically attempts to heal failed tests using the Healing Agent:

1. Test fails
2. Orchestrator calls Healing Agent
3. Healing Agent analyzes failure (timeout, selector, network, etc.)
4. Generates healing strategy
5. Updates test configuration
6. Retries test with healed config
7. If successful, marks as "healed"

## Agent Capabilities

### Check Agent Status
```python
from framework.ui_test_agent import UITestAgent

ui_agent = UITestAgent()
status = ui_agent.get_status()
print(status)
# {
#   "agent_type": "ui",
#   "name": "UI Test Agent",
#   "role": "Automation Engineer",
#   "capabilities": [...],
#   "is_available": True
# }
```

### Get Agent Capabilities
```python
capabilities = ui_agent.get_capabilities()
# ["browser_automation", "ui_testing", "screenshot", ...]
```

## Best Practices

### 1. Use Dependencies for Sequential Tests
```python
{
    "tests": [
        {"type": "api", "target": "...", ...},  # test_0
        {"type": "validation", "target": "...", "dependencies": ["test_0"]}  # Waits for test_0
    ]
}
```

### 2. Set Appropriate Priorities
- `priority: 1` - Critical tests (login, auth)
- `priority: 2` - Important tests (core features)
- `priority: 3` - Nice-to-have tests (edge cases)

### 3. Configure Max Retries
```python
{
    "type": "ui",
    "max_retries": 3,  # Try up to 3 times with healing
    ...
}
```

### 4. Use Validation After API Tests
```python
# API test
{"type": "api", "target": "...", ...},  # test_0

# Validate response
{"type": "validation", "target": "...", "dependencies": ["test_0"]}
```

### 5. Always Generate Final Report
```python
# Add report task at the end
{
    "type": "report",
    "target": "final_report",
    "config": {
        "results": [],  # Will be auto-filled
        "report_type": "detailed"
    }
}
```

## Error Handling

All agents return standardized results:

```python
{
    "success": True/False,
    "agent": "Agent Name",
    "target": "test_target",
    "execution_time": 1.23,
    # ... agent-specific data
    "error": "Error message"  # If failed
}
```

## Performance Tips

1. **Use Parallel Execution** for independent tests
2. **Set max_concurrent_tasks** appropriately per agent
3. **Use Validation Agent** for bulk data checks (very fast)
4. **Cache healing strategies** for repeated failures
5. **Generate reports** at the end, not during execution

## Integration with Dashboard

The orchestration system integrates with the Agent Dashboard through:
1. Session state configuration
2. Real-time result updates
3. Visual progress tracking
4. Report display

See the dashboard for UI-based test creation and execution.

## MCP Tool Integration

### Current Status
- **UI Agent**: Simulated (ready for production MCP Playwright tools)
- **API Agent**: Simulated (ready for production MCP REST tools)

### Production Integration
Replace simulation with actual MCP tool calls:

```python
# Instead of simulation
await asyncio.sleep(0.1)

# Use actual MCP tools
result = await mcp_microsoft_pla_browser_navigate(url=url)
```

## Troubleshooting

### Agent Not Available
```python
# Check if agent is imported
from framework.ui_test_agent import UITestAgent
if UITestAgent:
    print("UI Agent available")
```

### Task Fails to Assign
- Check agent capacity (`max_concurrent_tasks`)
- Verify agent type matches task type
- Check agent availability

### Healing Not Working
- Ensure `HealingAgent` is imported
- Check max_retries is > 0
- Verify failure type is healable

### Report Generation Fails
- Ensure all tasks complete before report
- Check results format
- Verify ReportAgent is available

## Advanced Features

### Custom Agent
Create custom agents by following the pattern:
```python
class MyCustomAgent:
    def __init__(self):
        self.agent_type = "custom"
        self.capabilities = [...]
    
    async def execute(self, target: str, config: Dict) -> Dict:
        # Your logic
        return {
            "success": True,
            "agent": "My Custom Agent",
            "target": target,
            ...
        }
    
    def get_status(self) -> Dict:
        return {...}
```

### Register Custom Agent
```python
orchestrator.agents["custom_agent"] = AgentCapability(
    name="My Custom Agent",
    agent_type="custom",
    capabilities=[...],
    max_concurrent_tasks=5
)
```

## Summary

The Multi-Agent Orchestration System provides:
- ✅ **True multi-agent architecture** matching QA team structure
- ✅ **Specialized agents** for UI, API, healing, validation, reporting
- ✅ **Intelligent orchestration** with dependency management
- ✅ **Auto-healing** for flaky tests
- ✅ **Comprehensive reporting** with RCA
- ✅ **MCP tool integration** (Playwright, REST API)
- ✅ **Parallel/sequential execution** modes
- ✅ **Production-ready** architecture

Start with simple examples and progressively add complexity!
