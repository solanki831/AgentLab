# 🦙 Testing Agents with Ollama - Complete Guide

## Overview

Run all Core Testing Agents **100% locally** using Ollama - no API keys, no cloud costs!

## Quick Start

### 1. Install Ollama

**Windows:**
```powershell
# Download from https://ollama.ai/download
# Run the installer
```

**Mac/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Start Ollama

```powershell
ollama serve
```

### 3. Pull a Model

Choose one of these models:

```powershell
# Recommended: Fast and efficient
ollama pull llama3.2:latest

# Alternative: Great for coding
ollama pull qwen2.5:latest

# Alternative: High performance
ollama pull mistral:latest
```

### 4. Run the Demo

```powershell
# Set Python path
$env:PYTHONPATH = "C:\Iris\python\AgenticAIAutoGen"

# Run Ollama-powered testing agents
python framework\ollama_demo.py
```

## Usage with AgentFactory

### Basic Usage

```python
from framework.ollama_helper import create_ollama_client
from framework.agentFactory import AgentFactory

# Create Ollama client
model_client = create_ollama_client(model="llama3.2:latest")

# Use with AgentFactory
factory = AgentFactory(model_client)

# Create any agent
api_agent = factory.create_api_contract_testing_agent()
visual_agent = factory.create_ui_visual_regression_agent()
accessibility_agent = factory.create_accessibility_testing_agent()
data_agent = factory.create_data_validation_agent()
```

### Complete Example

```python
import asyncio
from framework.ollama_helper import create_ollama_client, check_ollama_status
from framework.agentFactory import AgentFactory
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

async def main():
    # Check if Ollama is running
    is_running, models = check_ollama_status()
    if not is_running:
        print("Please start Ollama: ollama serve")
        return
    
    # Create Ollama client
    model_client = create_ollama_client(model="llama3.2:latest")
    
    # Create factory and agents
    factory = AgentFactory(model_client)
    
    agents = [
        factory.create_api_contract_testing_agent(
            system_message="Test the login API endpoint"
        ),
        factory.create_accessibility_testing_agent(
            system_message="Audit homepage for WCAG compliance"
        )
    ]
    
    # Create team
    team = RoundRobinGroupChat(
        participants=agents,
        termination_condition=TextMentionTermination("COMPLETE")
    )
    
    # Run testing workflow
    await team.run(task="Execute comprehensive testing")

asyncio.run(main())
```

## Recommended Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3.2:latest** | 2GB | ⚡⚡⚡ | ⭐⭐⭐ | General testing |
| **qwen2.5:latest** | 4.7GB | ⚡⚡ | ⭐⭐⭐⭐ | Code analysis |
| **mistral:latest** | 4.1GB | ⚡⚡ | ⭐⭐⭐⭐ | Complex tasks |
| phi3:latest | 2.3GB | ⚡⚡⚡⚡ | ⭐⭐ | Quick tests |

**Recommendation:** Start with `llama3.2:latest` for the best balance.

## Files Overview

### Updated for Ollama

- ✅ `framework/working_demo.py` - Modified to use Ollama
- ✅ `framework/ollama_demo.py` - Complete Ollama demonstration
- ✅ `framework/ollama_helper.py` - Helper functions for Ollama

### Works with Any Model

- `framework/agentFactory.py` - Agent factory (model-agnostic)
- `framework/mcp_config.py` - MCP workbench config
- `framework/test_tools_demo.py` - Direct tool testing (no LLM needed)

## Configuration

### Change Model

Edit the model in your code:

```python
# Use a different model
model_client = create_ollama_client(model="qwen2.5:latest")
```

### Change Ollama URL

If Ollama is running on a different port or host:

```python
model_client = create_ollama_client(
    model="llama3.2:latest",
    base_url="http://192.168.1.100:11434/v1"
)
```

## Troubleshooting

### Issue: "Ollama is not running"

**Solution:**
```powershell
# Start Ollama in a separate terminal
ollama serve
```

### Issue: "Model not found"

**Solution:**
```powershell
# List installed models
ollama list

# Pull the required model
ollama pull llama3.2:latest
```

### Issue: "Connection refused"

**Solution:**
```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Issue: Slow responses

**Solution:**
- Use a smaller model: `phi3:latest` or `llama3.2:latest`
- Ensure Ollama has GPU access
- Close other applications

## Comparison: OpenAI vs Ollama

| Feature | OpenAI | Ollama |
|---------|--------|--------|
| **Cost** | Pay per token | Free |
| **Privacy** | Cloud-based | 100% local |
| **Speed** | Fast | Depends on hardware |
| **Setup** | API key only | Install + download models |
| **Quality** | Very high | Good to very high |
| **Internet** | Required | Not required |

## Performance Tips

### 1. GPU Acceleration

Ollama automatically uses GPU if available. Check with:
```powershell
ollama run llama3.2 "test"
```

### 2. Model Selection

- **Fast testing:** Use `phi3:latest` or `llama3.2:latest`
- **Quality testing:** Use `qwen2.5:latest` or `mistral:latest`
- **Code analysis:** Use `codellama:latest` or `qwen2.5:latest`

### 3. Concurrent Requests

Ollama can handle multiple requests. Configure in agents:
```python
# Run agents in parallel if needed
results = await asyncio.gather(
    agent1.run(task1),
    agent2.run(task2),
    agent3.run(task3)
)
```

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Testing Agents with Ollama

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Ollama
        run: curl -fsSL https://ollama.com/install.sh | sh
      
      - name: Start Ollama
        run: ollama serve &
        
      - name: Pull model
        run: ollama pull llama3.2:latest
      
      - name: Run testing agents
        run: python framework/ollama_demo.py
```

### Docker Container

```dockerfile
FROM python:3.12

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy your code
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Start Ollama and run tests
CMD ollama serve & sleep 5 && ollama pull llama3.2 && python framework/ollama_demo.py
```

## Helper Tools

### Check Ollama Status

```powershell
python framework\ollama_helper.py
```

Output:
```
🦙 Ollama Helper - Testing Connection

✅ Ollama is running!

📦 Installed models (3):
   • llama3.2:latest
   • qwen2.5:latest
   • mistral:latest
```

### List Recommended Models

```python
from framework.ollama_helper import list_recommended_models
list_recommended_models()
```

## Advanced Configuration

### Custom System Messages

```python
agent = factory.create_api_contract_testing_agent(
    system_message="""
    You are testing payment APIs specifically.
    Focus on:
    1. Response times < 1 second
    2. PCI compliance (no card data in responses)
    3. Proper error codes for declined payments
    """
)
```

### Temperature and Sampling

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model="llama3.2:latest",
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    temperature=0.7,  # Adjust creativity (0.0-1.0)
    max_tokens=2000   # Control response length
)
```

## Benefits of Using Ollama

✅ **No API Costs** - Run unlimited tests without paying per token
✅ **Privacy** - All data stays on your machine
✅ **Offline** - Works without internet connection
✅ **Fast Iteration** - No rate limits
✅ **Multiple Models** - Switch between models easily
✅ **GPU Acceleration** - Leverages local GPU if available

## Next Steps

1. ✅ Install Ollama and pull a model
2. ✅ Run `python framework\ollama_demo.py`
3. ✅ Try different models to find the best fit
4. ✅ Integrate into your CI/CD pipeline
5. ✅ Customize agents for your specific needs

## Support

### Resources
- Ollama Documentation: https://ollama.ai/
- Ollama Models: https://ollama.ai/library
- Model Comparison: https://ollama.ai/blog/llama3.2

### Common Models
```powershell
ollama pull llama3.2       # Latest Llama
ollama pull qwen2.5        # Qwen coding model
ollama pull mistral        # Mistral AI
ollama pull codellama      # Code-focused
ollama pull phi3           # Lightweight
```

---

**Status:** ✅ **READY - 100% Local Testing Agents with Ollama**

No API keys, no cloud costs, complete privacy! 🎉