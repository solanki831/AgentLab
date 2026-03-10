# 🎛️ Complete Configuration Guide

## Overview
**Everything in the Agent Dashboard is now configurable from the UI** - no hardcoding required.

All configurations are stored in `st.session_state` and can be edited through the sidebar or saved/loaded via JSON.

---

## Configuration Locations

### 📍 Main Sidebar Sections

#### 1. **🔐 Authentication** 
Configure authentication for all agents:
- `auth_type`: none, basic, bearer, api_key, form_login, oauth
- Credentials (username, password, token, API keys, OAuth configs)
- Form selectors for UI testing

#### 2. **🌐 API Settings**
HTTP request configuration:
- `method`: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- `content_type`: application/json, application/xml, etc.
- `timeout`: 5-300 seconds
- `headers`: Custom HTTP headers (JSON format)
- `body`: Request body for POST/PUT/PATCH
- `num_requests`: Performance test iterations
- `chaos_type`: latency, error, timeout, random
- `compliance_type`: gdpr, hipaa, pci-dss, soc2, owasp

#### 3. **🖥️ UI Testing**
Browser automation settings:
- `browser`: chromium, firefox, webkit
- `headless`: True/False
- `screenshot`: True/False
- `viewport_width`: 320-3840px
- `viewport_height`: 240-2160px
- `wait_timeout`: 1000-60000ms
- `test_scenario`: smoke, regression, functional, visual, accessibility

#### 4. **🤖 LLM & LangChain**
Test selection for LangChain agent:
- `test_qa`: QA Chains
- `test_summarization`: Summarization
- `test_translation`: Translation
- `test_memory`: Memory Management
- `test_tools`: Tool Usage
- `test_error_handling`: Error Handling

#### 5. **🗃️ Vector Database**
VectorDB evaluation parameters:
- `dimension`: 128-1536
- `num_vectors`: 100-100,000
- `query_count`: 10-1,000
- `batch_size`: 10-500

#### 6. **🔄 RAG Pipeline**
RAG testing configuration:
- `chunk_size`: 100-2000
- `num_documents`: 1-20
- `num_queries`: 1-20
- `num_iterations`: 1-20

#### 7. **🗄️ Database**
Database connection settings:
- `db_type`: mysql, postgresql, sqlite, mssql, mongodb, redis
- `host`: hostname/IP
- `port`: port number
- `database`: database name
- `username`: DB username
- `password`: DB password

#### 8. **⚡ Quick Tests (Configurable)**
Complete quick test configuration in JSON:
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

#### 9. **📝 Templates & Samples (Advanced)**
Configure all templates and samples used by the system:

**Natural Language Test Templates:**
```json
[
  "Test security of {url}",
  "Check API performance at {url} with {num_requests} requests",
  "Run accessibility check on {url}",
  "Validate {compliance_type} compliance for {url}"
]
```

**LLM Benchmark Prompts:**
```json
[
  {"category": "Factual", "prompt": "What is the capital of France?"},
  {"category": "Math", "prompt": "What is 15% of 200?"},
  {"category": "Reasoning", "prompt": "Your reasoning question here"},
  {"category": "Code", "prompt": "Write a Python function to check if a number is prime."}
]
```

**RAG Sample Documents:**
```json
[
  "Machine learning is a subset of artificial intelligence...",
  "Deep learning uses neural networks with multiple layers...",
  "Natural Language Processing is a branch of AI..."
]
```

---

## Configuration Storage

All configurations are stored in `st.session_state` with these keys:

### Core Configs
- `auth_config` - Authentication settings
- `api_config` - API/HTTP settings
- `ui_config` - UI testing settings
- `db_config` - Database settings
- `langchain_config` - LangChain test selection
- `vectordb_config` - VectorDB parameters
- `rag_config` - RAG pipeline settings

### Quick Tests & Templates
- `quick_tests_config` - Quick test sections and tests
- `nl_templates` - Natural language test templates
- `benchmark_prompts` - LLM benchmark prompts
- `rag_documents` - RAG sample documents
- `rag_queries` - RAG test queries

### System State
- `ollama_client` - Ollama client instance
- `ollama_models` - Available models list
- `mcp_status` - MCP integration status
- `test_results` - Test execution results
- `test_history` - Recent test history (last 10)
- `selected_category` - Agent catalog filter

---

## How to Configure

### Method 1: UI Sidebar (Recommended)
1. Open sidebar in the dashboard
2. Find the relevant section
3. Edit values in the UI
4. Changes take effect immediately

### Method 2: JSON Editor (Advanced)
1. Open sidebar → expand "⚡ Quick Tests (Configurable)" or "📝 Templates & Samples"
2. Edit JSON directly in text area
3. Invalid JSON will show a warning
4. Click "Reset to Defaults" to restore original values

### Method 3: Programmatic (For Developers)
```python
# In your code or console
st.session_state.api_config["timeout"] = 60
st.session_state.quick_tests_config["sections"].append({
    "title": "Custom Section",
    "tests": [...]
})
```

---

## Configuration Examples

### Example 1: Add Custom Quick Test
```json
{
  "sections": [
    {
      "title": "My Custom Tests",
      "tests": [
        {
          "label": "🔍 SEO Check",
          "agent": "API Contract",
          "url": "https://mysite.com"
        },
        {
          "label": "📱 Mobile Test",
          "agent": "E2E",
          "url": "https://mysite.com/mobile"
        }
      ]
    }
  ]
}
```

### Example 2: Configure Bearer Token Auth
In sidebar → 🔐 Authentication:
- Select "bearer"
- Paste your JWT token
- All agents will now use this token automatically

### Example 3: Custom Benchmark Prompts
In sidebar → 📝 Templates & Samples:
```json
[
  {"category": "Domain Knowledge", "prompt": "Explain quantum computing in simple terms"},
  {"category": "Creativity", "prompt": "Write a haiku about testing"},
  {"category": "Analysis", "prompt": "Compare REST vs GraphQL APIs"}
]
```

### Example 4: Add Natural Language Templates
```json
[
  "Test {agent_type} for {url}",
  "Run {test_scenario} test on {url} with {browser} browser",
  "Validate {url} against {compliance_type} standards",
  "Performance test {url} with {num_requests} concurrent requests"
]
```

---

## Reset Configurations

### Reset Individual Sections
- Click "🔁 Reset Quick Tests to Defaults" in Quick Tests section
- Click "🔄 Reset All Config" at bottom of sidebar (resets everything)

### Reset Programmatically
```python
# Reset specific config
if "quick_tests_config" in st.session_state:
    del st.session_state["quick_tests_config"]
st.rerun()

# Or reset everything
st.session_state.clear()
st.rerun()
```

---

## Configuration Validation

The dashboard performs automatic validation:

- **JSON Configs**: Invalid JSON shows warnings, won't be applied
- **Timeouts**: Clamped to valid ranges (5-300s for API, 1000-60000ms for UI)
- **Numbers**: min/max enforced on numeric inputs
- **Enums**: Dropdowns enforce valid values
- **Required Fields**: URL required for most agents

---

## Configuration Status

View current config status in sidebar under "📊 Config Status":

| Setting | Status |
|---------|--------|
| Auth | ✅ Configured / ⚪ None |
| API | ✅ Customized / ⚪ Default |
| Database | ✅ Configured / ⚪ Not Set |
| LangChain | ✅ Configured / ⚪ Default |
| VectorDB | ✅ Configured / ⚪ Default |
| RAG | ✅ Configured / ⚪ Default |

---

## Configuration Persistence

### Current Session
All configs persist for the duration of your Streamlit session (until browser refresh/close).

### Save/Load Configurations
To persist configs across sessions:

1. Export current config:
```python
import json
config_snapshot = {
    "auth": st.session_state.auth_config,
    "api": st.session_state.api_config,
    "quick_tests": st.session_state.quick_tests_config,
    # ... other configs
}
with open("my_config.json", "w") as f:
    json.dump(config_snapshot, f, indent=2)
```

2. Load saved config:
```python
with open("my_config.json", "r") as f:
    config = json.load(f)
    st.session_state.auth_config = config["auth"]
    st.session_state.api_config = config["api"]
    # ... etc
```

---

## Best Practices

### ✅ Do's
- Start with defaults, customize as needed
- Use JSON editor for bulk changes
- Test your config changes before relying on them
- Document custom configs for your team
- Use descriptive labels in quick tests
- Set realistic timeouts based on your services

### ❌ Don'ts
- Don't hardcode values in agent code
- Don't use production credentials in configs
- Don't set extremely short timeouts (<5s for most tests)
- Don't leave invalid JSON in editors
- Don't assume configs persist after browser refresh

---

## Troubleshooting

### Problem: Changes not taking effect
**Solution**: Click away from input field or check for validation errors

### Problem: Invalid JSON warning
**Solution**: Use a JSON validator, check for:
- Missing quotes around strings
- Trailing commas
- Unescaped special characters

### Problem: Config reset after refresh
**Solution**: Streamlit sessions are temporary. Export/import configs as needed.

### Problem: Test using wrong config
**Solution**: Check "🔧 Active Configuration" expander in Test Lab to verify current settings

---

## Configuration Schema Reference

### Quick Tests Config
```typescript
{
  sections: Array<{
    title: string,
    tests: Array<{
      label: string,
      agent: string,
      url: string
    }>
  }>
}
```

### Benchmark Prompts
```typescript
Array<{
  category: string,
  prompt: string
}>
```

### RAG Queries
```typescript
Array<{
  query: string,
  expected_docs: string[]
}>
```

---

## Advanced: Dynamic Configuration

### Config Templates
Create reusable config templates:
```python
CONFIGS = {
    "development": {
        "api": {"timeout": 30, "num_requests": 10},
        "ui": {"headless": True}
    },
    "production": {
        "api": {"timeout": 60, "num_requests": 100},
        "ui": {"headless": False}
    }
}

# Apply template
env = "development"
st.session_state.api_config.update(CONFIGS[env]["api"])
```

### Config Inheritance
```python
# Base config
base_config = {"timeout": 30, "headers": {}}

# Extend for specific test
test_config = {**base_config, "timeout": 60, "headers": {"X-Custom": "value"}}
```

---

## Summary

✅ **Zero Hard-coding**: All values configurable from UI  
✅ **No Redundancy**: Reusable components for common patterns  
✅ **Full Control**: JSON editors for advanced customization  
✅ **Live Validation**: Immediate feedback on invalid inputs  
✅ **Status Visibility**: Clear indicators of configuration state  
✅ **Easy Reset**: One-click restore to defaults  

**Everything is now configurable!** 🎉
