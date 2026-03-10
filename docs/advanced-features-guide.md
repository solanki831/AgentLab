# 🚀 Advanced Features Guide

## Multi-Agent Orchestration

Run multiple agents in parallel for comprehensive testing:

### Features
- ▶️ **Run All Tests in Parallel** - Execute entire test sections simultaneously
- 📊 **Aggregated Results** - View all test results in one consolidated view
- ⚡ **Performance** - Tests run concurrently using asyncio.gather
- 🎯 **Smart Coordination** - Automatic task distribution and result collection

### Usage
1. Navigate to **Dashboard** tab
2. Find the **Quick Tests** section
3. Click "▶️ Run All '[Section Name]' Tests in Parallel"
4. View results for all tests in the section

### Example
```python
# Behind the scenes, orchestrate_agents() runs:
orchestrate_agents([
    {"agent": "Security", "url": "https://example.com", "label": "🔒 Security Scan"},
    {"agent": "Compliance", "url": "https://example.com", "label": "📋 GDPR Check"}
])
```

---

## Natural Language Test Creation

Write tests in plain English - AI converts them to executable tests:

### Features
- 💬 **Plain English Input** - Describe tests naturally
- 🎯 **Auto-Detection** - AI identifies test type, URL, parameters
- 🔄 **Multi-Step Tests** - Support for complex test scenarios
- ✅ **Instant Execution** - Parse and run tests immediately
- 💾 **Save to Quick Tests** - Add to your quick test library

### Usage
1. Navigate to **Natural Language Tests** tab
2. Describe your test in the text area
3. Click "🚀 Parse & Execute Test"
4. Review generated test specification
5. Click "Run This Test Now" to execute

### Example Inputs
```
✅ Test security of https://example.com
✅ Check API performance at https://api.example.com with 50 requests
✅ Run accessibility check on https://myapp.com
✅ Validate GDPR compliance for https://site.com
✅ Test E2E login flow on https://app.example.com
```

### Generated Output
```json
{
  "agent": "Security",
  "url": "https://example.com",
  "method": "GET",
  "expected_status": 200,
  "assertions": ["check SSL", "scan vulnerabilities"]
}
```

---

## Self-Healing Tests

AI automatically analyzes failures and suggests fixes:

### Features
- 🔍 **Root Cause Analysis** - AI identifies why tests fail
- 💡 **Smart Suggestions** - Provides actionable fixes
- 🔄 **Auto-Retry** - Applies fixes and retries automatically
- 📝 **Fix Documentation** - Documents all applied fixes
- ⚙️ **Config Updates** - Updates test configurations intelligently

### When It Activates
Self-healing is offered when:
- Individual quick tests fail
- Orchestrated tests fail
- Natural language tests fail

### Usage
1. Run any test that fails
2. Click "🔧 Auto-Heal This Test" button
3. Review AI analysis and suggestions
4. Test automatically retries with fixes if recommended

### Example Healing Output
```json
{
  "root_cause": "Connection timeout - endpoint taking too long to respond",
  "fixes": [
    "Increase timeout from 30s to 60s",
    "Add retry logic with exponential backoff",
    "Verify endpoint URL is correct"
  ],
  "updated_config": {
    "timeout": 60,
    "retry_count": 3
  },
  "retry_recommended": true,
  "manual_intervention_needed": false
}
```

### Common Fixes Applied
- ⏱️ Timeout adjustments
- 🔗 URL/endpoint corrections
- 🔐 Authentication updates
- 📊 Expected value modifications
- 🎯 Selector updates (UI tests)
- 🔄 Retry logic additions

---

## Configuration

### Quick Tests (Configurable)
Edit in sidebar: **⚡ Quick Tests (Configurable)**

```json
{
  "sections": [
    {
      "title": "Security & Compliance",
      "tests": [
        {"label": "🔒 Security Scan", "agent": "Security", "url": "https://example.com"},
        {"label": "📋 GDPR Check", "agent": "Compliance", "url": "https://example.com"}
      ]
    }
  ]
}
```

### Add Custom Tests
1. Open sidebar expander "⚡ Quick Tests (Configurable)"
2. Edit JSON configuration
3. Add new sections or tests
4. Tests appear immediately in Dashboard

---

## Best Practices

### Multi-Agent Orchestration
✅ Group related tests in sections
✅ Use consistent naming
✅ Balance test distribution
❌ Don't overload with too many parallel tests (>10)

### Natural Language Tests
✅ Be specific about URLs and parameters
✅ Use clear action verbs (test, check, validate, run)
✅ Include expected outcomes when relevant
❌ Avoid ambiguous descriptions

### Self-Healing
✅ Review AI suggestions before applying
✅ Document manual interventions
✅ Monitor healing success rates
❌ Don't rely solely on auto-healing for critical tests

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Agent Dashboard UI                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Natural    │  │  Multi-Agent │  │   Self-   │ │
│  │   Language   │  │ Orchestration│  │  Healing  │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                 │                 │       │
│         v                 v                 v       │
│  ┌──────────────────────────────────────────────┐  │
│  │     Ollama LLM (llama3.2:latest)             │  │
│  └──────────────────────────────────────────────┘  │
│         │                 │                 │       │
│         v                 v                 v       │
│  ┌──────────────────────────────────────────────┐  │
│  │        Agent Execution Engine                │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │  │
│  │  │ Security │ │ Performance│ │   E2E   │    │  │
│  │  └──────────┘ └──────────┘ └──────────┘    │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Orchestration Issues
**Problem:** Tests not running in parallel
**Solution:** Check asyncio compatibility, ensure all agents support async execution

**Problem:** Some tests timeout
**Solution:** Adjust timeout in API Settings sidebar

### Natural Language Parsing
**Problem:** LLM returns invalid JSON
**Solution:** Make description more specific, include URL explicitly

**Problem:** Wrong agent selected
**Solution:** Use exact agent names: Security, Performance, API Contract, E2E, Accessibility, Compliance

### Self-Healing
**Problem:** Healing suggestions not applicable
**Solution:** Manual intervention needed - review error logs

**Problem:** Test still fails after healing
**Solution:** Check if suggested fixes were applied correctly, may require manual debugging

---

## Requirements

- Python 3.8+
- Ollama running locally (port 11434)
- Model: llama3.2:latest (or other compatible model)
- streamlit
- httpx
- asyncio

---

## Quick Start

```bash
# 1. Start Ollama
ollama serve

# 2. Pull model
ollama pull llama3.2:latest

# 3. Run dashboard
cd framework
streamlit run agent_dashboard.py

# 4. Open browser
http://localhost:8502
```

---

## API Reference

### orchestrate_agents()
```python
async def orchestrate_agents(
    tasks: List[Dict[str, Any]], 
    config: Dict = None
) -> List[Dict]
```

### parse_natural_language_test()
```python
async def parse_natural_language_test(
    nl_input: str
) -> Dict[str, Any]
```

### self_heal_test()
```python
async def self_heal_test(
    failed_test: Dict, 
    error_info: str
) -> Dict[str, Any]
```

---

## Version History

### v2.0.0 (Current)
- ✨ Multi-agent orchestration
- ✨ Natural language test creation
- ✨ Self-healing tests
- ✨ Configurable quick tests
- ✨ Consistent button sizing

### v1.0.0
- Initial release with basic agent support
