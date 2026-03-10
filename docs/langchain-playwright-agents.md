# 🧠 LangChain Integration with Playwright Agents

## Overview

The Playwright agents now have **AI "brain" capabilities** powered by LangChain, enabling:
- **Memory**: Contextual awareness across test planning and healing sessions
- **Vector Stores**: Semantic search and retrieval of past test plans and fixes
- **RAG (Retrieval Augmented Generation)**: Learning from historical data for better decisions

---

## 🎯 PlannerAgent with LangChain

### Capabilities Added

1. **Vector Store for Test Plans**
   - Stores all created test plans in a Chroma vector database
   - Enables semantic search to find similar past test plans
   - Avoids duplicate planning efforts

2. **Conversation Memory**
   - Tracks planning history and context
   - Maintains continuity across multiple planning sessions

3. **RAG for Scenario Suggestions**
   - Retrieves similar test scenarios from past plans
   - Suggests improvements based on historical patterns

### Usage Example

```python
from framework.playwright_agents import PlannerAgent
import asyncio

async def plan_with_memory():
    # Initialize with LangChain enabled
    planner = PlannerAgent(
        use_langchain=True,
        persist_dir="./my_plans_db"
    )
    
    # Create a test plan
    result = await planner.execute(
        target="Login Feature",
        config={
            "requirements": [
                "User can login with valid credentials",
                "User sees error with invalid credentials"
            ],
            "test_type": "functional"
        }
    )
    
    # Check LangChain insights
    insights = result["langchain_insights"]
    print(f"Similar plans found: {insights['similar_plans_found']}")
    print(f"Vector DB enabled: {insights['vectordb_enabled']}")
    
    # Search for similar plans
    similar = await planner.search_similar_plans(
        "login authentication tests",
        k=3
    )
    
    for plan in similar:
        print(f"Similar plan: {plan['metadata']['target']}")
        print(f"Similarity: {plan['similarity_score']}")

asyncio.run(plan_with_memory())
```

### How It Works

1. **Plan Creation**:
   - User creates a test plan → Planner generates scenarios
   - Plan is automatically stored in Chroma vector DB
   - Embeddings created using HuggingFace sentence-transformers

2. **Similar Plan Search**:
   - Before creating new plan, searches for similar existing plans
   - Uses semantic similarity (not just keyword matching)
   - Suggests reusable scenarios from past plans

3. **Memory Tracking**:
   - Each planning session is recorded in conversation memory
   - Context preserved across multiple plan iterations

---

## 🔧 GeneratorAgent with LangChain

### Capabilities Added

1. **Conversation Memory for Code Generation**
   - Remembers code generation patterns
   - Maintains context across multiple test script generations
   - Learns preferred coding styles

### Usage Example

```python
from framework.playwright_agents import GeneratorAgent
import asyncio

async def generate_with_memory():
    # Initialize with memory
    generator = GeneratorAgent(use_langchain=True)
    
    # Generate test code
    result = await generator.execute(
        target="plan_001",
        config={
            "test_plan": test_plan,
            "framework": "playwright-python"
        }
    )
    
    # Memory automatically tracks generation patterns

asyncio.run(generate_with_memory())
```

### Benefits

- **Context-Aware Generation**: Remembers previous code structures
- **Pattern Learning**: Identifies and reuses successful patterns
- **Consistency**: Maintains coding style across test suite

---

## 🩹 HealerAgent with LangChain RAG

### Capabilities Added (Most Powerful!)

1. **Vector Store for Healing History**
   - Stores all successful test fixes
   - Enables searching for similar past failures
   - Builds knowledge base of solutions

2. **RAG-Based Fix Suggestions**
   - Searches for similar failures in history
   - Suggests fixes that worked before
   - Provides confidence scores based on similarity

3. **Pattern Recognition**
   - Identifies recurring failure patterns
   - Learns common root causes
   - Improves fix accuracy over time

### Usage Example

```python
from framework.playwright_agents import HealerAgent
import asyncio

async def heal_with_rag():
    # Initialize with RAG enabled
    healer = HealerAgent(
        use_langchain=True,
        persist_dir="./my_healing_db"
    )
    
    # Heal a failed test
    result = await healer.execute(
        target="test_login_001",
        config={
            "error_info": {
                "message": "Timeout waiting for selector #submit-btn",
                "type": "TimeoutError"
            },
            "test_code": "await page.click('#submit-btn')",
            "auto_fix": True
        }
    )
    
    # Check RAG insights
    insights = result["langchain_insights"]
    print(f"Similar failures found: {insights['similar_failures_found']}")
    print(f"RAG suggestions: {insights['rag_suggestions']}")
    print(f"Past fixes referenced: {insights['past_fixes_referenced']}")
    
    # Search for similar failures manually
    similar = await healer.search_similar_failures(
        error_message="Timeout waiting for selector",
        failure_type="timeout",
        k=5
    )
    
    for failure in similar:
        print(f"Past failure: {failure['metadata']['root_cause']}")
        print(f"Similarity: {failure['similarity_score']}")

asyncio.run(heal_with_rag())
```

### How RAG Works

1. **Failure Analysis**:
   - Test fails → Healer analyzes error
   - Searches vector DB for similar past failures
   - Retrieves successful fixes for similar issues

2. **Fix Suggestion with RAG**:
   ```
   Current Failure → Embeddings → Vector Search
                              ↓
                    Similar Past Failures (with fixes)
                              ↓
                    Extract Successful Fixes
                              ↓
                    Rank by Similarity Score
                              ↓
                    Suggest Top Fixes First
   ```

3. **Learning from Success**:
   - When auto-fix succeeds → Store in vector DB
   - Includes: error type, root cause, fix applied, success status
   - Future similar failures benefit from this knowledge

---

## 🔄 Complete Workflow with LangChain

```python
import asyncio
from framework.playwright_agents import PlannerAgent, GeneratorAgent, HealerAgent

async def intelligent_test_workflow():
    # Step 1: Plan with memory and similarity search
    planner = PlannerAgent(use_langchain=True)
    plan = await planner.execute(
        target="E-commerce Checkout",
        config={
            "requirements": ["Add to cart", "Proceed to checkout", "Payment"],
            "test_type": "end-to-end"
        }
    )
    
    # LangChain finds 3 similar past plans for checkout flows
    print(f"Found {plan['langchain_insights']['similar_plans_found']} similar plans")
    
    # Step 2: Generate code with context memory
    generator = GeneratorAgent(use_langchain=True)
    code = await generator.execute(
        target=plan['plan_id'],
        config={
            "test_plan": plan['test_plan'],
            "framework": "playwright-python"
        }
    )
    
    # Step 3: Run tests (they fail sometimes...)
    # Simulating a failure:
    
    # Step 4: Heal with RAG-based suggestions
    healer = HealerAgent(use_langchain=True)
    healing = await healer.execute(
        target="test_checkout_001",
        config={
            "error_info": {
                "message": "Element not found: #checkout-button",
                "type": "ElementNotFoundError"
            },
            "test_code": "await page.click('#checkout-button')",
            "auto_fix": True
        }
    )
    
    # RAG finds 2 similar past failures and suggests proven fixes
    print(f"RAG found {healing['langchain_insights']['rag_suggestions']} proven fixes")

asyncio.run(intelligent_test_workflow())
```

---

## 📊 Vector Store Details

### Chroma Configuration

**PlannerAgent Vector Store**:
- Location: `./playwright_plans_db/`
- Collection: `test_plans`
- Stores: Test plans with requirements, scenarios, coverage

**HealerAgent Vector Store**:
- Location: `./playwright_healing_db/`
- Collection: `healing_history`
- Stores: Failed tests, root causes, fixes, success status

### Embeddings Model

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimensions: 384
- Fast and accurate for semantic similarity

---

## 🎓 Key Benefits

### 1. **Avoid Reinventing the Wheel**
- Don't create duplicate test plans
- Reuse proven test scenarios
- Learn from past successes

### 2. **Faster Healing**
- Get fix suggestions in seconds
- Based on actual past solutions
- Higher success rate over time

### 3. **Knowledge Accumulation**
- System gets smarter with use
- Builds organizational test knowledge
- Captures expert solutions

### 4. **Context Awareness**
- Remembers planning patterns
- Maintains coding consistency
- Tracks healing history

---

## 🚀 Getting Started

### Installation

```bash
# LangChain dependencies already in requirements.txt
pip install -r requirements.txt
```

### Quick Test

```python
from framework.playwright_agents import PlannerAgent, HealerAgent
import asyncio

async def test_langchain():
    # Test PlannerAgent
    planner = PlannerAgent(use_langchain=True)
    print(f"✅ Planner - Vector DB: {planner.vectorstore is not None}")
    print(f"✅ Planner - Memory: {planner.memory is not None}")
    
    # Test HealerAgent
    healer = HealerAgent(use_langchain=True)
    print(f"✅ Healer - Vector DB: {healer.vectorstore is not None}")
    print(f"✅ Healer - Memory: {healer.memory is not None}")
    
    # Create a plan to populate vector store
    plan = await planner.execute(
        "Test Feature",
        {"requirements": ["Req 1", "Req 2"], "test_type": "functional"}
    )
    
    # Search for it
    results = await planner.search_similar_plans("test feature requirements")
    print(f"✅ Found {len(results)} similar plans")

asyncio.run(test_langchain())
```

### Configuration

Disable LangChain if needed:

```python
# Disable for a specific agent
planner = PlannerAgent(use_langchain=False)
generator = GeneratorAgent(use_langchain=False)
healer = HealerAgent(use_langchain=False)
```

---

## 📁 Persisted Data

LangChain creates persistent directories:

```
AgenticAIAutoGen/
├── playwright_plans_db/      # PlannerAgent vector store
│   └── chroma.sqlite3
└── playwright_healing_db/    # HealerAgent vector store
    └── chroma.sqlite3
```

**These directories grow over time** as you create more plans and heal more tests. They contain the "brain" of your test automation system!

---

## 🔍 Advanced Features

### Custom Similarity Thresholds

```python
# Only retrieve highly similar items
similar = await planner.search_similar_plans(
    "login tests",
    k=10  # Get top 10
)

# Filter by similarity score
high_similarity = [
    s for s in similar 
    if s['similarity_score'] > 0.85
]
```

### Memory Management

```python
# Access memory context
if planner.memory:
    messages = planner.memory.load_memory_variables({})
    print(messages)
```

### Vector Store Statistics

```python
# Check what's stored
if planner.vectorstore:
    collection = planner.vectorstore._collection
    print(f"Total plans stored: {collection.count()}")
```

---

## 🎯 Best Practices

1. **Enable LangChain in Production**: The more you use it, the smarter it gets
2. **Backup Vector Stores**: The DBs contain valuable knowledge
3. **Monitor Similarity Scores**: Tune thresholds based on your needs
4. **Review RAG Suggestions**: Validate before applying fixes automatically
5. **Periodic Cleanup**: Remove outdated or invalid entries

---

## 🐛 Troubleshooting

### Issue: "HuggingFace model download failed"

```python
# Pre-download the model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

### Issue: "Chroma database locked"

```python
# Close agents properly
del planner
del healer
# Wait for persistence to complete
```

### Issue: "No similar items found"

- Vector store is empty (create more plans/healings)
- Similarity threshold too high
- Query doesn't match stored content semantically

---

## 🎉 Summary

✅ **PlannerAgent**: Memory + Vector store for test plans  
✅ **GeneratorAgent**: Memory for code generation patterns  
✅ **HealerAgent**: RAG for learning from past fixes  

**Result**: Smarter agents that learn and improve over time! 🚀

---

For more information, see:
- [playwright-agents-guide.md](./playwright-agents-guide.md) - Complete agent documentation
- [PLAYWRIGHT_AGENTS_QUICKSTART.md](./PLAYWRIGHT_AGENTS_QUICKSTART.md) - Quick start guide
- [langchain-vectordb-rag.md](./langchain-vectordb-rag.md) - General LangChain usage

