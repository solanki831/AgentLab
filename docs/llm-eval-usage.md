# LLM Evaluation Agent - Usage Guide

## Overview

The **LLMEvaluationAgent** is a comprehensive evaluation tool that benchmarks LLM models across 6 critical dimensions:

1. **📚 Factual Accuracy** (25% weight) - Tests knowledge correctness
2. **🧠 Reasoning & Logic** (20% weight) - Tests logical deduction
3. **🔢 Math Problem Solving** (15% weight) - Tests mathematical abilities
4. **💻 Code Generation** (15% weight) - Tests programming capabilities
5. **📋 Instruction Following** (15% weight) - Tests compliance with instructions
6. **🔍 Hallucination Detection** (10% weight) - Tests truthfulness

## Quick Start

### CLI Usage

```bash
# Evaluate default model (llama3.2:latest)
python framework/llm_eval_agent.py

# Evaluate specific model
python framework/llm_eval_agent.py llama3:latest

# Evaluate another model
python framework/llm_eval_agent.py llama3.2:1b
```

### Dashboard Usage

1. **Run the dashboard:**
   ```bash
   streamlit run agent_dashboard.py
   ```

2. **Select Agent:** Choose `LLMEvaluationAgent`

3. **Input:** Enter model name (e.g., `llama3.2:latest`) or leave blank for default

4. **Click:** "Run LLMEvaluationAgent test"

## Evaluation Categories

### 1. Factual Accuracy (5 questions)
Tests basic factual knowledge:
- Capital of France?
- Who wrote Romeo and Juliet?
- Speed of light?
- WWII end year?
- Chemical symbol for gold?

**Scoring:** Checks if correct answer is in response

### 2. Reasoning & Logic (3 tests)
Tests logical thinking:
- Logical deduction
- Math word problems (bat and ball)
- Proportional reasoning

**Scoring:** Checks for correct logical conclusion

### 3. Math Problem Solving (4 problems)
Tests mathematical abilities:
- Percentage calculations
- Algebraic equations
- Square roots
- Geometry

**Scoring:** Extracts numbers and validates against expected answer

### 4. Code Generation (2 tasks)
Tests programming capabilities:
- Prime number checker
- String reversal

**Scoring:** Checks for required keywords (def, return, logic)

### 5. Instruction Following (2 tests)
Tests compliance:
- Exact formatting ("list 3 colors")
- Precise output ("only say HELLO")

**Scoring:** Validates format and content exactly

### 6. Hallucination Detection (1 test)
Tests truthfulness:
- Context-based question answering
- Checks for added false information

**Scoring:** Validates model stays within context

## Sample Output

```
═══════════════════════════════════════════════════════════
🎯 COMPREHENSIVE LLM EVALUATION
═══════════════════════════════════════════════════════════
Model: llama3.2:latest
Time: 2026-02-03 16:30:00
═══════════════════════════════════════════════════════════

📚 Testing Factual Accuracy...
🧠 Testing Reasoning & Logic...
🔢 Testing Math Problem Solving...
💻 Testing Code Generation...
📋 Testing Instruction Following...
🔍 Testing Hallucination Detection...

═══════════════════════════════════════════════════════════
📊 EVALUATION SUMMARY
═══════════════════════════════════════════════════════════

🎯 Overall Score: 78.5/100
⏱️  Total Time: 45.32s

Category                       Score           Details
----------------------------------------------------------------------
📚 Factual Accuracy             80.0/100       4/5 correct
🧠 Reasoning & Logic            66.7/100       2/3 correct
🔢 Math Problem Solving         75.0/100       3/4 correct
💻 Code Generation              100.0/100      2/2 passed
📋 Instruction Following        50.0/100       1/2 passed
🔍 Hallucination Resistance     100.0/100      1/1 no hallucinations

═══════════════════════════════════════════════════════════

🏆 Grade: B (Good)
═══════════════════════════════════════════════════════════

💾 Report saved to: llm_eval_llama3.2_latest_20260203_163000.json
```

## Grading Scale

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 90-100 | A+ | Excellent - Production-ready |
| 80-89  | A  | Very Good - Highly capable |
| 70-79  | B  | Good - Capable with minor issues |
| 60-69  | C  | Fair - Needs improvement |
| < 60   | D  | Needs Improvement - Not recommended |

## Output Files

The agent saves a detailed JSON report:

```json
{
  "model": "llama3.2:latest",
  "timestamp": "2026-02-03T16:30:00",
  "total_evaluation_time": 45.32,
  "overall_score": 78.5,
  "categories": {
    "factual_accuracy": {
      "score": 80.0,
      "correct": 4,
      "total": 5,
      "details": [...]
    },
    ...
  }
}
```

## Comparing Models

To compare multiple models:

```bash
# Evaluate model 1
python framework/llm_eval_agent.py llama3.2:latest

# Evaluate model 2
python framework/llm_eval_agent.py llama3.2:1b

# Compare the JSON outputs
```

## Customization

To add custom test cases, edit `llm_eval_agent.py`:

```python
# Add to factual_qa
self.factual_qa.append({
    "question": "What is the tallest mountain?",
    "answer": "Mount Everest"
})

# Add to reasoning_tests
self.reasoning_tests.append({
    "question": "Your custom logic problem",
    "answer": "Expected answer",
    "reasoning": "type of reasoning"
})
```

## Performance Tips

1. **Temperature:** Agent uses 0.0 for deterministic results
2. **Timeout:** Set to 120s, increase for slower models
3. **Parallel Testing:** Run multiple models in separate terminals
4. **Caching:** Results are saved, no need to re-evaluate

## Integration

### Python Code

```python
from framework.llm_eval_agent import LLMEvaluationAgent

# Create evaluator
evaluator = LLMEvaluationAgent()

# Run evaluation
report = await evaluator.run_full_evaluation("llama3.2:latest")

# Access results
print(f"Score: {report['overall_score']}")
print(f"Factual: {report['categories']['factual_accuracy']['score']}")
```

### Automated CI/CD

```bash
#!/bin/bash
# eval_llm.sh - Run in CI pipeline

python framework/llm_eval_agent.py $MODEL_NAME

# Check exit code
if [ $? -eq 0 ]; then
  echo "✅ Evaluation passed"
else
  echo "❌ Evaluation failed"
  exit 1
fi
```

## Troubleshooting

**Issue:** Model not found  
**Solution:** Check Ollama is running: `ollama list`

**Issue:** Timeout errors  
**Solution:** Increase timeout in constructor: `LLMEvaluationAgent(timeout=300)`

**Issue:** Low scores  
**Solution:** This is real evaluation! Model may need fine-tuning or use a larger model

## Use Cases

1. **Model Selection** - Compare models before deployment
2. **Fine-tuning Validation** - Verify improvements after fine-tuning
3. **Regression Testing** - Ensure model updates don't degrade performance
4. **Benchmarking** - Create standardized performance reports
5. **Research** - Academic evaluation of new models

---

**Created:** 2026-02-03  
**Agent:** LLMEvaluationAgent  
**Location:** framework/llm_eval_agent.py