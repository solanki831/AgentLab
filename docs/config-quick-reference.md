# 🎛️ Configuration Quick Reference

## How to Configure Everything

### 🔐 Authentication
**Sidebar → 🔐 Authentication**
- Select auth type: none, basic, bearer, api_key, form_login, oauth
- Enter credentials
- Applies to ALL agents automatically

### 🌐 API Settings  
**Sidebar → 🌐 API Settings**
- Method: GET/POST/PUT/etc
- Headers: JSON format `{"X-Custom": "value"}`
- Body: Request body for POST/PUT
- Timeout: 5-300 seconds

### ⚡ Quick Tests
**Sidebar → ⚡ Quick Tests (Configurable)**
```json
{
  "sections": [
    {
      "title": "Your Section",
      "tests": [
        {"label": "🔍 Test Name", "agent": "AgentType", "url": "https://example.com"}
      ]
    }
  ]
}
```

### 📝 Templates & Samples
**Sidebar → 📝 Templates & Samples (Advanced)**

**NL Templates:**
```json
["Test {agent_type} for {url}"]
```

**Benchmark Prompts:**
```json
[{"category": "Name", "prompt": "Question"}]
```

**RAG Documents:**
```json
["Your document text here"]
```

## Where Settings Are Used

| Setting | Used By | Effect |
|---------|---------|--------|
| `auth_config` | All agents | Authentication headers |
| `api_config` | API, Performance, Security | HTTP settings |
| `ui_config` | E2E, Accessibility | Browser settings |
| `db_config` | Database | Connection params |
| `langchain_config` | LangChain agent | Test selection |
| `vectordb_config` | VectorDB agent | Eval parameters |
| `rag_config` | RAG agent | Pipeline settings |
| `quick_tests_config` | Dashboard | Quick test buttons |
| `nl_templates` | NL Test tab | Example templates |
| `benchmark_prompts` | LLM Playground | Benchmark tests |
| `rag_documents` | RAG agent | Sample data |

## Quick Actions

### Reset Single Config
Click "🔁 Reset" button in each section

### Reset All Configs
**Sidebar → Bottom → 🔄 Reset All Config**

### View Config Status
**Sidebar → 📊 Config Status**

### Export Config (Manual)
Copy JSON from text areas, save to file

### Test with Custom Config
1. Set config in sidebar
2. Run test from any tab
3. Config automatically applied

## Tips

✅ **Do:**
- Test after config changes
- Use JSON validator for complex configs
- Document custom configs
- Share configs with team

❌ **Don't:**
- Leave invalid JSON
- Use production secrets
- Set very short timeouts
- Assume persistence after refresh

## Troubleshooting

**Q: Changes not applied?**  
A: Click away from input or press Enter

**Q: Invalid JSON error?**  
A: Check quotes, commas, brackets

**Q: Config reset?**  
A: Streamlit sessions are temporary - export/import as needed

**Q: Which config is active?**  
A: Check "🔧 Active Configuration" in Test Lab

## Example Workflows

### Workflow 1: API Testing with Auth
1. Sidebar → 🔐 Auth → Select "bearer"
2. Paste JWT token
3. Test Lab → Select API agent
4. Enter URL → Run test
5. Auth automatically included

### Workflow 2: Custom Quick Tests
1. Sidebar → ⚡ Quick Tests
2. Edit JSON to add your tests
3. Dashboard → See new buttons
4. Click to run instantly

### Workflow 3: Custom Benchmarks
1. Sidebar → 📝 Templates & Samples
2. Edit Benchmark Prompts JSON
3. LLM Playground → Run Quick Benchmark
4. Your custom prompts execute

---

**Everything is configurable - no code changes needed!** 🎉
