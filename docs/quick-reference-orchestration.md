# 🎯 Multi-Agent Orchestration - Quick Reference Card

## 🚀 Quick Start (3 Lines)

```python
from framework.orchestrator_agent import OrchestratorAgent
import asyncio

orchestrator = OrchestratorAgent()
orchestrator.create_test_plan({"tests": [...]})
results = await orchestrator.execute_test_plan(parallel=True)
```

## 🤖 6 Specialized Agents

| Agent | Role | Capabilities | File |
|-------|------|--------------|------|
| **Orchestrator** | Test Lead | Task coordination, dependencies, parallel execution | `orchestrator_agent.py` |
| **UI Test** | Automation Engineer | Browser automation, screenshots, form filling | `ui_test_agent.py` |
| **API Test** | API Tester | REST/GraphQL, performance, validation | `api_test_agent.py` |
| **Healing** | Flaky Test Fixer | AI analysis, auto-repair, retry logic | `healing_agent.py` |
| **Validation** | Reviewer | Schema, data assertions, integrity checks | `validation_agent.py` |
| **Report** | Analyst | RCA, metrics, trend analysis, reports | `report_agent.py` |

## 📝 Test Task Template

```python
{
    "type": "ui|api|validation|healing|report",
    "target": "https://example.com",
    "config": { ... },
    "priority": 1,  # 1=high, 2=medium, 3=low
    "dependencies": ["test_0"],  # Task IDs
    "max_retries": 2
}
```

## 🎨 UI Test (Browser Automation)

```python
{
    "type": "ui",
    "target": "https://example.com",
    "config": {
        "steps": [
            {"action": "navigate", "url": "https://example.com"},
            {"action": "click", "selector": "#button"},
            {"action": "fill", "selector": "#input", "value": "text"},
            {"action": "type", "selector": "#field", "text": "text"},
            {"action": "screenshot"},
            {"action": "wait", "selector": ".loaded"},
            {"action": "assert_text", "selector": "h1", "expected": "Welcome"},
            {"action": "assert_visible", "selector": ".content"}
        ]
    }
}
```

## 🌐 API Test (REST/GraphQL)

```python
{
    "type": "api",
    "target": "https://api.example.com/users",
    "config": {
        "method": "GET|POST|PUT|DELETE|PATCH",
        "headers": {"Authorization": "Bearer token"},
        "body": '{"key": "value"}',
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

## ✅ Validation (Data Checks)

```python
{
    "type": "validation",
    "target": "data_name",
    "config": {
        "data": {"id": 123, "name": "Test"},
        "validations": [
            {"type": "equals", "field": "id", "expected": 123},
            {"type": "contains", "field": "tags", "expected": "tag"},
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

## 🔧 Healing (Auto-Repair)

```python
{
    "type": "healing",
    "target": "failed_test",
    "config": {
        "failed_test": {"name": "test", "type": "ui"},
        "error_info": "Element not found: #button",
        "test_config": {...}
    }
}
```

## 📊 Report (Analysis)

```python
{
    "type": "report",
    "target": "final_report",
    "config": {
        "results": [...],
        "report_type": "summary|detailed|executive|html|markdown",
        "options": {"include_rca": True, "include_metrics": True}
    }
}
```

## 🎭 Orchestration Example

```python
async def run_test():
    orchestrator = OrchestratorAgent()
    
    test_suite = {
        "tests": [
            # UI Test
            {"type": "ui", "target": "https://example.com", ...},
            
            # API Test (parallel with UI)
            {"type": "api", "target": "https://api.example.com", ...},
            
            # Validation (after API)
            {"type": "validation", "dependencies": ["test_1"], ...}
        ]
    }
    
    orchestrator.create_test_plan(test_suite)
    results = await orchestrator.execute_test_plan(parallel=True)
    
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"🔧 Healed: {results['healed']}")
```

## 🔥 Individual Agent Usage

```python
# UI Agent
from framework.ui_test_agent import UITestAgent
ui = UITestAgent()
result = await ui.execute("https://example.com", {"steps": [...]})

# API Agent
from framework.api_test_agent import APITestAgent
api = APITestAgent()
result = await api.execute("https://api.example.com", {"method": "GET"})

# Validation Agent
from framework.validation_agent import ValidationAgent
val = ValidationAgent()
result = await val.execute("data", {"data": {...}, "validations": [...]})

# Healing Agent
from framework.healing_agent import HealingAgent
heal = HealingAgent()
result = await heal.execute("test", {"failed_test": {...}, "error_info": "..."})

# Report Agent
from framework.report_agent import ReportAgent
report = ReportAgent()
result = await report.execute("report", {"results": [...], "report_type": "summary"})
```

## 📊 Result Format

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

## ⚡ Performance Testing

```python
from framework.api_test_agent import APITestAgent

api = APITestAgent()
perf = await api.performance_test(
    "https://api.example.com",
    num_requests=100,
    config={"method": "GET"}
)

print(f"Requests/sec: {perf['requests_per_second']}")
```

## 🔍 Batch Validation

```python
from framework.validation_agent import ValidationAgent

val = ValidationAgent()
result = await val.batch_validate(
    items=[{...}, {...}, {...}],
    validation_rules=[...]
)
```

## 📈 Check Agent Status

```python
agent.get_status()
# {
#   "agent_type": "ui",
#   "name": "UI Test Agent",
#   "role": "Automation Engineer",
#   "capabilities": [...],
#   "is_available": True
# }
```

## 🎯 Execution Modes

```python
# Parallel (respects dependencies)
results = await orchestrator.execute_test_plan(parallel=True)

# Sequential (one by one)
results = await orchestrator.execute_test_plan(parallel=False)
```

## 🔧 Auto-Healing Flow

```
1. Test fails
2. Orchestrator detects failure
3. Healing Agent analyzes error
4. Generates healing strategy
5. Updates test configuration
6. Retries test (up to max_retries)
7. If successful, marks as "healed"
```

## 📝 MCP Tool Integration

### UI Agent (Playwright)
- `mcp_microsoft_pla_browser_navigate`
- `mcp_microsoft_pla_browser_click`
- `mcp_microsoft_pla_browser_fill`
- `mcp_microsoft_pla_browser_type`
- `mcp_microsoft_pla_browser_take_screenshot`
- `mcp_microsoft_pla_browser_wait_for`

### API Agent (REST)
- REST API MCP tools (coming soon)
- GraphQL MCP tools (coming soon)

## 📚 Documentation

- **Complete Guide**: `docs/multi-agent-orchestration-guide.md`
- **Examples**: `framework/orchestration_examples.py`
- **Implementation**: `docs/implementation-summary.md`
- **Quick Ref**: This file

## 🚀 Run Examples

```bash
cd c:\Iris\python\AgenticAIAutoGen
python framework\orchestration_examples.py
```

## 🎓 Best Practices

1. ✅ Use dependencies for sequential tests
2. ✅ Set appropriate priorities (1=high, 3=low)
3. ✅ Configure max_retries for flaky tests
4. ✅ Use validation after API tests
5. ✅ Always generate final report
6. ✅ Use parallel execution for speed
7. ✅ Monitor healing success rates
8. ✅ Review RCA for failed tests

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent not available | Check import: `from framework.X import Y` |
| Task not assigned | Check agent capacity and task type |
| Healing not working | Ensure max_retries > 0 |
| Report missing | Add report task at end |
| Slow execution | Use parallel=True |

## 🔗 Integration

### Dashboard
```python
# In agent_dashboard.py
from framework.orchestrator_agent import OrchestratorAgent
orchestrator = OrchestratorAgent()
```

### MCP Production
```python
# Replace simulations with:
result = await mcp_microsoft_pla_browser_navigate(url=url)
```

### LLM
```python
from framework.ollama_helper import call_ollama
healing = HealingAgent(llm_client=call_ollama)
```

## 📊 Metrics

```python
results['total_tasks']  # Total tests
results['passed']       # Passed tests
results['failed']       # Failed tests
results['healed']       # Auto-healed tests

# From report
metrics['pass_rate']              # Pass percentage
metrics['avg_execution_time']     # Avg time per test
metrics['healing_rate']           # Healing success rate
metrics['tests_per_second']       # Throughput
```

## 🎉 Quick Win

```python
# Copy this and run!
from framework.orchestrator_agent import OrchestratorAgent
import asyncio

async def quick_test():
    o = OrchestratorAgent()
    o.create_test_plan({"tests": [
        {"type": "api", "target": "https://api.example.com/status",
         "config": {"method": "GET", "assertions": [{"type": "status_code", "expected": 200}]}}
    ]})
    r = await o.execute_test_plan()
    print(f"✅ {r['passed']} passed, ❌ {r['failed']} failed")

asyncio.run(quick_test())
```

---

**🎯 Ready to orchestrate your QA team!**

For full details: `docs/multi-agent-orchestration-guide.md`
