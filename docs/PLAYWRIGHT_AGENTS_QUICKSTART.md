# 🎭 Playwright Agents - Quick Reference

## 🚀 Quick Start Commands

### Run CLI Examples
```powershell
# Test all agents with examples
python framework\playwright_agents_examples.py
```

### Launch Interactive UI
```powershell
# Option 1: Using launcher script
.\scripts\run_playwright_agents.ps1

# Option 2: Direct command
streamlit run framework\playwright_agents_ui.py
```

## 📋 Three Agents

### 1. Planner Agent 📋
**Purpose**: Create comprehensive test plans from requirements

**Example**:
```python
from framework.playwright_agents import create_test_plan

plan = await create_test_plan(
    target="Login Feature",
    requirements=["User can login", "Password reset works"]
)
```

### 2. Generator Agent 🔧
**Purpose**: Generate executable test code from plans

**Example**:
```python
from framework.playwright_agents import generate_test_code

code = await generate_test_code(
    test_plan=plan['test_plan'],
    framework='playwright',
    language='python'
)
```

### 3. Healer Agent 🔨
**Purpose**: Analyze and fix test failures automatically

**Example**:
```python
from framework.playwright_agents import heal_test_failure

healing = await heal_test_failure(
    test_name="test_login",
    error_info={'message': 'Timeout', 'type': 'TimeoutError'},
    auto_fix=True
)
```

## 🔄 Complete Workflow

```
Requirements → Planner → Test Plan → Generator → Test Code → Execute → Healer → Fixed Tests
```

## 📁 New Files Created

```
framework/
├── playwright_agents.py           # Core agents implementation
├── playwright_agents_ui.py        # Interactive Streamlit UI
└── playwright_agents_examples.py  # Usage examples

scripts/
└── run_playwright_agents.ps1      # UI launcher

docs/
└── playwright-agents-guide.md     # Full documentation
```

## 🎯 Key Features

### Planner
- ✅ Requirement analysis
- ✅ Test scenario generation
- ✅ Priority assignment
- ✅ Coverage calculation
- ✅ Risk assessment

### Generator
- ✅ Multi-framework (Playwright, Selenium)
- ✅ Multi-language (Python, TypeScript)
- ✅ Page object models
- ✅ Test fixtures
- ✅ Test data factories

### Healer
- ✅ Failure classification (7 types)
- ✅ Root cause analysis
- ✅ Auto-fix suggestions
- ✅ Confidence scoring
- ✅ Flaky test detection
- ✅ Success rate tracking

## 📊 Failure Types Healed

1. **Timeout** - Element loading delays
2. **Selector Issues** - Element not found
3. **Assertion Failures** - Expected vs actual mismatch
4. **Network Issues** - API/request failures
5. **Stale Elements** - DOM changes
6. **Timing Issues** - Race conditions
7. **Unknown** - Other failures

## 💡 Use Cases

### Use Case 1: New Feature Testing
1. Define requirements in Planner
2. Generate test code with Generator
3. Run tests
4. Fix failures with Healer

### Use Case 2: Flaky Test Investigation
1. Input failure details in Healer
2. Get root cause analysis
3. Review suggested fixes
4. Apply auto-fixes

### Use Case 3: Test Suite Creation
1. Batch create plans for all features
2. Generate all test code
3. Export and integrate into CI/CD

## 🖥️ UI Pages

- **Overview** 🏠 - Dashboard and quick actions
- **Planner** 📋 - Create test plans
- **Generator** 🔧 - Generate code
- **Healer** 🔨 - Fix failures
- **Analytics** 📊 - View metrics
- **Workflow** ⚙️ - End-to-end automation

## 🔧 Configuration

### Supported Frameworks
- Playwright (Python, TypeScript)
- Selenium (Python)
- Cypress (TypeScript) - Coming soon

### Auto-Healing Confidence Levels
- **90-100%**: Apply automatically
- **75-89%**: Review recommended
- **50-74%**: Manual review required
- **<50%**: Investigate further

## 📈 Success Metrics

Track these metrics in the UI:
- Total plans created
- Tests generated
- Failures healed
- Healing success rate
- Common failure patterns

## 🎓 Learn More

- **Full Documentation**: [docs/playwright-agents-guide.md](docs/playwright-agents-guide.md)
- **Examples**: Run `python framework\playwright_agents_examples.py`
- **UI Demo**: Launch dashboard with `streamlit run framework\playwright_agents_ui.py`

---

**Created by**: GitHub Copilot  
**Inspired by**: Playwright's intelligent testing patterns  
**Part of**: AgenticAIAutoGen Framework
