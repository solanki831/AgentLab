# 🎭 Playwright Agents

Three intelligent agents for automated test planning, generation, and healing.

## Quick Start

```powershell
# Run examples
python framework\playwright_agents_examples.py

# Launch UI
streamlit run framework\playwright_agents_ui.py
```

## The Three Agents

### 📋 Planner Agent
Creates comprehensive test plans from requirements with scenarios, priorities, and coverage analysis.

### 🔧 Generator Agent
Generates executable test code supporting Playwright, Selenium, and multiple languages.

### 🔨 Healer Agent
Analyzes test failures, detects root causes, and suggests/applies fixes automatically.

## Files

- `playwright_agents.py` - Core agent implementations
- `playwright_agents_ui.py` - Interactive Streamlit dashboard
- `playwright_agents_examples.py` - Usage examples and demos

## Documentation

See [docs/playwright-agents-guide.md](../docs/playwright-agents-guide.md) for complete documentation.

## Features

- ✅ Test planning with coverage analysis
- ✅ Multi-framework code generation
- ✅ Auto-healing with confidence scoring
- ✅ Flaky test detection
- ✅ Interactive UI dashboard
- ✅ Export capabilities
- ✅ Workflow automation

## Example Usage

```python
from framework.playwright_agents import (
    create_test_plan,
    generate_test_code,
    heal_test_failure
)

# Create plan
plan = await create_test_plan(
    target="Login Feature",
    requirements=["User can login", "Password reset"]
)

# Generate code
code = await generate_test_code(
    test_plan=plan['test_plan'],
    framework='playwright',
    language='python'
)

# Heal failure
healing = await heal_test_failure(
    test_name="test_login",
    error_info={'message': 'Timeout', 'type': 'TimeoutError'},
    auto_fix=True
)
```

---

Inspired by Playwright's intelligent testing patterns.
