# 🎭 Playwright-Inspired Agents

Three intelligent agents for automated test planning, generation, and healing - inspired by Playwright's intelligent testing patterns.

## 🧠 **NEW: LangChain AI Brain Integration**

All agents now have **AI memory and learning capabilities** powered by LangChain:

- **🎯 PlannerAgent**: Stores plans in vector DB, searches for similar past plans, suggests proven scenarios
- **🔧 GeneratorAgent**: Remembers code generation patterns, maintains context across generations
- **🔨 HealerAgent**: Learns from past fixes using RAG, suggests solutions that worked before

**Install LangChain** to enable these features:
```bash
pip install langchain langchain-community langchain-huggingface chromadb sentence-transformers
```

**Without LangChain**: Agents work normally (no memory/RAG)  
**With LangChain**: Agents learn and improve over time 🚀

👉 [See LangChain Integration Guide](./langchain-playwright-agents.md)

---

## 📋 Overview

### **Planner Agent** 📋
Analyzes requirements and creates comprehensive test plans with:
- Test scenario generation
- Priority assignment
- Coverage analysis
- Risk assessment
- Test data requirements
- Edge case identification
- **🧠 NEW: Similar plan search, scenario suggestions from past plans**

### **Generator Agent** 🔧
Generates executable test code from plans:
- Multi-framework support (Playwright, Selenium, Cypress)
- Multi-language support (Python, TypeScript, JavaScript)
- Page object model generation
- Test fixture creation
- Test data factories
- **🧠 NEW: Context-aware generation with memory**

### **Healer Agent** 🔨
Detects and automatically fixes test failures:
- Failure pattern analysis
- Flaky test detection
- Auto-healing for common issues
- Selector optimization
- Timeout adjustment
- Assertion updates
- **🧠 NEW: RAG-based fix suggestions from past successful healings**

## 🚀 Quick Start

### 1. Run Examples (CLI)

```powershell
# Run examples to see agents in action
python framework/playwright_agents_examples.py
```

### 2. Launch Interactive UI

```powershell
# Option 1: Using the launcher script
./scripts/run_playwright_agents.ps1

# Option 2: Direct streamlit command
streamlit run framework/playwright_agents_ui.py
```

### 3. Use as a Library

```python
from framework.playwright_agents import (
    PlannerAgent, GeneratorAgent, HealerAgent,
    create_test_plan, generate_test_code, heal_test_failure
)

# Create a test plan
plan = await create_test_plan(
    target="Login System",
    requirements=[
        "User can login with valid credentials",
        "Invalid credentials show error"
    ]
)

# Generate test code
code = await generate_test_code(
    test_plan=plan['test_plan'],
    framework='playwright',
    language='python'
)

# Heal a test failure
healing = await heal_test_failure(
    test_name="test_login",
    error_info={'message': 'Timeout error', 'type': 'TimeoutError'},
    auto_fix=True
)
```

## 📚 Features

### Planner Agent Capabilities

- **Requirement Analysis**: Parses and understands test requirements
- **Scenario Generation**: Creates detailed test scenarios with steps
- **Priority Assignment**: Assigns priorities based on criticality
- **Coverage Calculation**: Estimates test coverage percentage
- **Risk Assessment**: Identifies potential testing risks
- **Data Planning**: Determines test data requirements
- **Environment Setup**: Defines environment configurations

### Generator Agent Capabilities

- **Code Generation**: Creates executable test scripts
- **Framework Support**: 
  - Playwright (Python/TypeScript)
  - Selenium (Python/Java)
  - Cypress (JavaScript/TypeScript)
- **Pattern Generation**:
  - Page Object Models
  - Test Fixtures
  - Test Data Factories
  - Configuration Files
- **Best Practices**: Follows framework-specific best practices

### Healer Agent Capabilities

- **Failure Classification**:
  - Timeout errors
  - Selector issues
  - Assertion failures
  - Network problems
  - Stale elements
  - Timing issues
- **Root Cause Analysis**: Determines why tests fail
- **Fix Suggestions**: Provides specific code fixes
- **Auto-Healing**: Applies high-confidence fixes automatically
- **Flaky Detection**: Identifies intermittent test failures
- **Statistics**: Tracks healing success rates

## 🎯 Use Cases

### 1. Test Planning Phase

```python
# Define your requirements
requirements = [
    "User can search for products",
    "User can filter by category",
    "User can sort results"
]

# Create comprehensive test plan
planner = PlannerAgent()
plan = await planner.execute("E-commerce Search", {
    'requirements': requirements,
    'test_type': 'functional'
})

# Review generated scenarios
for scenario in plan['test_plan']['test_scenarios']:
    print(f"{scenario['id']}: {scenario['title']}")
```

### 2. Code Generation Phase

```python
# Generate Playwright Python tests
generator = GeneratorAgent()
result = await generator.execute('code_gen', {
    'test_plan': plan['test_plan'],
    'framework': 'playwright',
    'language': 'python'
})

# Save generated files
for filename, code in result['generated_files'].items():
    with open(filename, 'w') as f:
        f.write(code)
```

### 3. Healing Phase

```python
# Analyze a failed test
healer = HealerAgent()
result = await healer.execute('test_checkout', {
    'error_info': {
        'message': 'TimeoutError: button not found',
        'type': 'TimeoutError'
    },
    'test_code': test_code,
    'auto_fix': True
})

# Review suggested fixes
for fix in result['recommended_fixes']:
    print(f"{fix['type']}: {fix['description']}")
```

## 🖥️ UI Features

The interactive dashboard provides:

### **Overview Page** 🏠
- Agent capability summaries
- Workflow visualization
- Quick action buttons
- Statistics dashboard

### **Planner Page** 📋
- Requirement input forms
- Test plan visualization
- Scenario explorer
- Plan export (JSON)

### **Generator Page** 🔧
- Framework/language selection
- Code preview with syntax highlighting
- File-by-file code view
- Download individual or all files

### **Healer Page** 🔨
- Failure input forms
- Analysis results
- Fix recommendations
- Auto-healing toggle
- Healing statistics

### **Analytics Page** 📊
- Overall metrics
- Success rates
- Common failure patterns
- Workflow history

### **Workflow Page** ⚙️
- End-to-end automation
- Step-by-step execution
- Progress tracking

## 📖 API Reference

### PlannerAgent

```python
class PlannerAgent:
    async def execute(self, target: str, config: Dict) -> Dict:
        """
        Create a test plan
        
        Args:
            target: Application/feature to test
            config: {
                'requirements': List[str],
                'user_stories': List[str],
                'acceptance_criteria': List[str],
                'test_type': str
            }
        
        Returns:
            {
                'status': 'success',
                'plan_id': str,
                'test_plan': {...},
                'summary': {...}
            }
        """
```

### GeneratorAgent

```python
class GeneratorAgent:
    async def execute(self, target: str, config: Dict) -> Dict:
        """
        Generate test code
        
        Args:
            target: Test plan ID or description
            config: {
                'test_plan': Dict,
                'framework': 'playwright'|'selenium',
                'language': 'python'|'typescript'
            }
        
        Returns:
            {
                'status': 'success',
                'generated_files': Dict[str, str],
                'summary': {...}
            }
        """
```

### HealerAgent

```python
class HealerAgent:
    async def execute(self, target: str, config: Dict) -> Dict:
        """
        Analyze and heal test failure
        
        Args:
            target: Failed test name
            config: {
                'error_info': Dict,
                'test_code': str,
                'logs': List[str],
                'auto_fix': bool
            }
        
        Returns:
            {
                'status': 'success',
                'analysis': {...},
                'recommended_fixes': List[Dict],
                'applied_fixes': List[Dict]
            }
        """
```

## 🔧 Configuration

### Framework Support Matrix

| Framework  | Python | TypeScript | JavaScript | Java |
|-----------|--------|------------|------------|------|
| Playwright | ✅     | ✅         | ✅         | ❌   |
| Selenium   | ✅     | ❌         | ❌         | 🚧   |
| Cypress    | ❌     | ✅         | ✅         | ❌   |

### Healing Confidence Levels

- **90-100%**: High confidence - Apply automatically
- **75-89%**: Good confidence - Review recommended
- **50-74%**: Medium confidence - Manual review required
- **<50%**: Low confidence - Investigate further

## 📁 File Structure

```
framework/
├── playwright_agents.py          # Core agent implementations
├── playwright_agents_ui.py       # Streamlit dashboard
├── playwright_agents_examples.py # Usage examples
└── ...

scripts/
└── run_playwright_agents.ps1     # UI launcher script

docs/
└── playwright-agents-guide.md    # This file
```

## 🎓 Examples

### Example 1: Basic Test Planning

```python
import asyncio
from framework.playwright_agents import create_test_plan

async def main():
    plan = await create_test_plan(
        target="User Authentication",
        requirements=[
            "Login with email and password",
            "Password reset functionality",
            "Remember me feature"
        ],
        test_type='functional'
    )
    
    print(f"Created {plan['summary']['total_scenarios']} scenarios")
    print(f"Coverage: {plan['test_plan']['coverage']}%")

asyncio.run(main())
```

### Example 2: Generate and Save Tests

```python
import asyncio
from framework.playwright_agents import generate_test_code
import os

async def main():
    result = await generate_test_code(
        test_plan=my_test_plan,
        framework='playwright',
        language='python'
    )
    
    # Create output directory
    os.makedirs('generated_tests', exist_ok=True)
    
    # Save all files
    for filename, code in result['generated_files'].items():
        filepath = os.path.join('generated_tests', filename)
        with open(filepath, 'w') as f:
            f.write(code)
        print(f"Saved: {filepath}")

asyncio.run(main())
```

### Example 3: Heal with Auto-Fix

```python
import asyncio
from framework.playwright_agents import heal_test_failure

async def main():
    result = await heal_test_failure(
        test_name="test_submit_form",
        error_info={
            'message': 'TimeoutError: Locator not found',
            'type': 'TimeoutError'
        },
        test_code='''
        page.goto("/form")
        page.click("button#submit")
        ''',
        auto_fix=True  # Enable auto-healing
    )
    
    if result['applied_fixes']:
        print("✅ Fixes applied:")
        for fix in result['applied_fixes']:
            print(f"  - {fix['description']}")

asyncio.run(main())
```

## 🤝 Integration

### With Existing Test Suites

```python
# In your conftest.py or test setup
from framework.playwright_agents import HealerAgent

healer = HealerAgent()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.failed and call.when == "call":
        # Heal the failure
        healing = asyncio.run(healer.execute(
            item.name,
            {
                'error_info': {'message': str(rep.longrepr), 'type': 'Unknown'},
                'test_code': '',
                'auto_fix': False
            }
        ))
        
        # Log healing suggestions
        for fix in healing['recommended_fixes']:
            print(f"Suggested fix: {fix['description']}")
```

## 📊 Metrics & Analytics

### Track Success Rates

```python
healer = HealerAgent()

# After healing multiple tests
stats = healer.get_healing_stats()

print(f"Total healings: {stats['total_healings']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Common failures: {stats['common_failures']}")
```

## 🚀 Advanced Usage

### Custom LLM Integration

```python
# Use your own LLM for smarter planning/healing
from your_llm import YourLLMClient

llm = YourLLMClient()

planner = PlannerAgent(llm_client=llm)
generator = GeneratorAgent(llm_client=llm)
healer = HealerAgent(llm_client=llm)
```

### Batch Processing

```python
# Process multiple test plans
plans = []
for target, requirements in test_inputs:
    plan = await create_test_plan(target, requirements)
    plans.append(plan)

# Generate all code
for plan in plans:
    code = await generate_test_code(plan['test_plan'])
    # Save code...
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Error**: Ensure you're running from the project root
   ```powershell
   cd c:\Iris\python\AgenticAIAutoGen
   python -m framework.playwright_agents_examples
   ```

2. **Streamlit Not Found**: Install required packages
   ```powershell
   pip install streamlit
   ```

3. **Port Already in Use**: Change the port
   ```powershell
   streamlit run framework/playwright_agents_ui.py --server.port 8502
   ```

## 📝 License

Part of the AgenticAIAutoGen framework.

## 🙏 Acknowledgments

Inspired by:
- Playwright's intelligent testing capabilities
- AI-powered test generation patterns
- Self-healing test automation concepts

---

**Ready to start?** Run `python framework/playwright_agents_examples.py` to see the agents in action!
