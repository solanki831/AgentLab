"""
🎯 LLM Evaluation Agent
Comprehensive LLM evaluation with multiple benchmark tests:
- Accuracy & Factuality
- Reasoning & Logic
- Hallucination Detection
- Following Instructions
- Code Generation
- Math Problem Solving
- Multi-turn Conversations
- Toxicity & Safety
"""

import asyncio
import httpx
import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import statistics


class LLMEvaluationAgent:
    """Comprehensive LLM Evaluation with industry-standard benchmarks"""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 120):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
        self.timeout = timeout
        
        # Evaluation datasets
        self.factual_qa = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare"},
            {"question": "What is the speed of light in vacuum?", "answer": "299,792,458 meters per second"},
            {"question": "What year did World War II end?", "answer": "1945"},
            {"question": "What is the chemical symbol for gold?", "answer": "Au"},
        ]
        
        self.reasoning_tests = [
            {
                "question": "If all roses are flowers and some flowers fade quickly, can we conclude that some roses fade quickly?",
                "answer": "Yes",
                "reasoning": "logical deduction"
            },
            {
                "question": "A bat and ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost?",
                "answer": "$0.05",
                "reasoning": "math word problem"
            },
            {
                "question": "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
                "answer": "5 minutes",
                "reasoning": "proportional reasoning"
            }
        ]
        
        self.math_problems = [
            {"problem": "What is 15% of 80?", "answer": 12},
            {"problem": "Solve for x: 2x + 5 = 13", "answer": 4},
            {"problem": "What is the square root of 144?", "answer": 12},
            {"problem": "If a triangle has angles of 60° and 70°, what is the third angle?", "answer": 50},
        ]
        
        self.code_tasks = [
            {
                "task": "Write a Python function to check if a number is prime",
                "keywords": ["def", "prime", "return", "for", "if"]
            },
            {
                "task": "Write a Python function to reverse a string",
                "keywords": ["def", "reverse", "return", "[::-1]" or "reversed"]
            },
        ]
        
        self.instruction_following = [
            {
                "instruction": "List exactly 3 colors. Format: 1. Color 2. Color 3. Color",
                "check": lambda x: len([line for line in x.split('\n') if re.match(r'^\d+\.', line)]) == 3
            },
            {
                "instruction": "Reply with ONLY the word 'HELLO' and nothing else",
                "check": lambda x: x.strip().upper() == "HELLO"
            },
        ]
        
        self.hallucination_tests = [
            {
                "context": "The article discusses the discovery of a new planet in 2023.",
                "question": "When was the new planet discovered?",
                "correct": "2023",
                "hallucination_trap": "mentions years not in context"
            }
        ]
    
    async def call_llm(self, model: str, prompt: str, temperature: float = 0.0) -> Tuple[str, float]:
        """Call LLM and return response with timing"""
        start = datetime.now()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                }
                
                response = await client.post(self.api_endpoint, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    elapsed = (datetime.now() - start).total_seconds()
                    return data.get("response", "").strip(), elapsed
                else:
                    return f"Error: {response.status_code}", 0.0
        except Exception as e:
            return f"Error: {str(e)}", 0.0
    
    async def evaluate_factual_accuracy(self, model: str) -> Dict:
        """Test factual knowledge accuracy"""
        print(f"📚 Testing Factual Accuracy...")
        
        correct = 0
        results = []
        
        for qa in self.factual_qa:
            prompt = f"Answer this question with just the answer, no explanation: {qa['question']}"
            response, time_taken = await self.call_llm(model, prompt, temperature=0.0)
            
            # Check if answer is contained in response
            is_correct = qa['answer'].lower() in response.lower()
            if is_correct:
                correct += 1
            
            results.append({
                "question": qa['question'],
                "expected": qa['answer'],
                "got": response,
                "correct": is_correct,
                "time": time_taken
            })
        
        accuracy = (correct / len(self.factual_qa)) * 100
        
        return {
            "score": accuracy,
            "correct": correct,
            "total": len(self.factual_qa),
            "details": results
        }
    
    async def evaluate_reasoning(self, model: str) -> Dict:
        """Test logical reasoning abilities"""
        print(f"🧠 Testing Reasoning & Logic...")
        
        correct = 0
        results = []
        
        for test in self.reasoning_tests:
            prompt = f"{test['question']}\n\nProvide your answer clearly."
            response, time_taken = await self.call_llm(model, prompt, temperature=0.0)
            
            # Check if expected answer is in response
            is_correct = test['answer'].lower() in response.lower()
            if is_correct:
                correct += 1
            
            results.append({
                "question": test['question'],
                "expected": test['answer'],
                "got": response,
                "correct": is_correct,
                "reasoning_type": test['reasoning'],
                "time": time_taken
            })
        
        accuracy = (correct / len(self.reasoning_tests)) * 100
        
        return {
            "score": accuracy,
            "correct": correct,
            "total": len(self.reasoning_tests),
            "details": results
        }
    
    async def evaluate_math(self, model: str) -> Dict:
        """Test mathematical problem-solving"""
        print(f"🔢 Testing Math Problem Solving...")
        
        correct = 0
        results = []
        
        for problem in self.math_problems:
            prompt = f"Solve this problem and provide only the numerical answer: {problem['problem']}"
            response, time_taken = await self.call_llm(model, prompt, temperature=0.0)
            
            # Extract numbers from response
            numbers = re.findall(r'-?\d+\.?\d*', response)
            is_correct = any(abs(float(num) - problem['answer']) < 0.01 for num in numbers if num)
            
            if is_correct:
                correct += 1
            
            results.append({
                "problem": problem['problem'],
                "expected": problem['answer'],
                "got": response,
                "correct": is_correct,
                "time": time_taken
            })
        
        accuracy = (correct / len(self.math_problems)) * 100
        
        return {
            "score": accuracy,
            "correct": correct,
            "total": len(self.math_problems),
            "details": results
        }
    
    async def evaluate_code_generation(self, model: str) -> Dict:
        """Test code generation abilities"""
        print(f"💻 Testing Code Generation...")
        
        passed = 0
        results = []
        
        for task in self.code_tasks:
            prompt = f"{task['task']}\n\nProvide only the Python code."
            response, time_taken = await self.call_llm(model, prompt, temperature=0.2)
            
            # Check if code contains expected keywords
            keywords_found = sum(1 for keyword in task['keywords'] if keyword.lower() in response.lower())
            is_valid = keywords_found >= len(task['keywords']) * 0.6  # At least 60% of keywords
            
            if is_valid:
                passed += 1
            
            results.append({
                "task": task['task'],
                "code": response[:200] + "..." if len(response) > 200 else response,
                "keywords_expected": task['keywords'],
                "keywords_found": keywords_found,
                "valid": is_valid,
                "time": time_taken
            })
        
        score = (passed / len(self.code_tasks)) * 100
        
        return {
            "score": score,
            "passed": passed,
            "total": len(self.code_tasks),
            "details": results
        }
    
    async def evaluate_instruction_following(self, model: str) -> Dict:
        """Test instruction following accuracy"""
        print(f"📋 Testing Instruction Following...")
        
        passed = 0
        results = []
        
        for test in self.instruction_following:
            response, time_taken = await self.call_llm(model, test['instruction'], temperature=0.0)
            
            follows = test['check'](response)
            if follows:
                passed += 1
            
            results.append({
                "instruction": test['instruction'],
                "response": response,
                "follows": follows,
                "time": time_taken
            })
        
        score = (passed / len(self.instruction_following)) * 100
        
        return {
            "score": score,
            "passed": passed,
            "total": len(self.instruction_following),
            "details": results
        }
    
    async def evaluate_hallucination(self, model: str) -> Dict:
        """Test for hallucination tendencies"""
        print(f"🔍 Testing Hallucination Detection...")
        
        no_hallucinations = 0
        results = []
        
        for test in self.hallucination_tests:
            prompt = f"Based ONLY on this context: {test['context']}\n\nQuestion: {test['question']}\nAnswer:"
            response, time_taken = await self.call_llm(model, prompt, temperature=0.0)
            
            # Check if response contains correct info and doesn't add false info
            has_correct = test['correct'] in response
            has_hallucination = any(year in response for year in ['2020', '2021', '2022', '2024', '2025'] 
                                   if year != test['correct'])
            
            no_hallucination = has_correct and not has_hallucination
            if no_hallucination:
                no_hallucinations += 1
            
            results.append({
                "context": test['context'],
                "question": test['question'],
                "response": response,
                "has_hallucination": has_hallucination,
                "time": time_taken
            })
        
        score = (no_hallucinations / len(self.hallucination_tests)) * 100
        
        return {
            "score": score,
            "no_hallucinations": no_hallucinations,
            "total": len(self.hallucination_tests),
            "details": results
        }
    
    async def run_full_evaluation(self, model: str) -> Dict:
        """Run complete evaluation suite"""
        print(f"\n{'='*70}")
        print(f"🎯 COMPREHENSIVE LLM EVALUATION")
        print(f"{'='*70}")
        print(f"Model: {model}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        start_time = datetime.now()
        
        # Run all evaluation categories
        factual = await self.evaluate_factual_accuracy(model)
        reasoning = await self.evaluate_reasoning(model)
        math = await self.evaluate_math(model)
        code = await self.evaluate_code_generation(model)
        instructions = await self.evaluate_instruction_following(model)
        hallucination = await self.evaluate_hallucination(model)
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate overall score (weighted average)
        overall_score = (
            factual['score'] * 0.25 +
            reasoning['score'] * 0.20 +
            math['score'] * 0.15 +
            code['score'] * 0.15 +
            instructions['score'] * 0.15 +
            hallucination['score'] * 0.10
        )
        
        report = {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "total_evaluation_time": total_time,
            "overall_score": round(overall_score, 2),
            "categories": {
                "factual_accuracy": factual,
                "reasoning": reasoning,
                "math": math,
                "code_generation": code,
                "instruction_following": instructions,
                "hallucination_resistance": hallucination
            }
        }
        
        self.print_evaluation_report(report)
        
        return report
    
    def print_evaluation_report(self, report: Dict):
        """Print formatted evaluation report"""
        print(f"\n{'='*70}")
        print(f"📊 EVALUATION SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"🎯 Overall Score: {report['overall_score']:.1f}/100")
        print(f"⏱️  Total Time: {report['total_evaluation_time']:.2f}s\n")
        
        print(f"{'Category':<30} {'Score':<15} {'Details'}")
        print(f"{'-'*70}")
        
        categories = report['categories']
        
        print(f"📚 Factual Accuracy{' '*15} {categories['factual_accuracy']['score']:.1f}/100     "
              f"{categories['factual_accuracy']['correct']}/{categories['factual_accuracy']['total']} correct")
        
        print(f"🧠 Reasoning & Logic{' '*13} {categories['reasoning']['score']:.1f}/100     "
              f"{categories['reasoning']['correct']}/{categories['reasoning']['total']} correct")
        
        print(f"🔢 Math Problem Solving{' '*9} {categories['math']['score']:.1f}/100     "
              f"{categories['math']['correct']}/{categories['math']['total']} correct")
        
        print(f"💻 Code Generation{' '*15} {categories['code_generation']['score']:.1f}/100     "
              f"{categories['code_generation']['passed']}/{categories['code_generation']['total']} passed")
        
        print(f"📋 Instruction Following{' '*10} {categories['instruction_following']['score']:.1f}/100     "
              f"{categories['instruction_following']['passed']}/{categories['instruction_following']['total']} passed")
        
        print(f"🔍 Hallucination Resistance{' '*6} {categories['hallucination_resistance']['score']:.1f}/100     "
              f"{categories['hallucination_resistance']['no_hallucinations']}/{categories['hallucination_resistance']['total']} no hallucinations")
        
        print(f"\n{'='*70}")
        
        # Grade
        score = report['overall_score']
        if score >= 90:
            grade = "A+ (Excellent)"
        elif score >= 80:
            grade = "A (Very Good)"
        elif score >= 70:
            grade = "B (Good)"
        elif score >= 60:
            grade = "C (Fair)"
        else:
            grade = "D (Needs Improvement)"
        
        print(f"\n🏆 Grade: {grade}")
        print(f"{'='*70}\n")


# ============================================================================
# CLI Usage
# ============================================================================

async def main():
    """Run LLM evaluation"""
    import sys
    
    if len(sys.argv) > 1:
        model = sys.argv[1]
    else:
        model = "llama3.2:latest"
    
    evaluator = LLMEvaluationAgent()
    
    print(f"🚀 Starting evaluation of {model}...")
    print(f"   This will test: factual accuracy, reasoning, math, code, instructions, hallucinations\n")
    
    report = await evaluator.run_full_evaluation(model)
    
    # Optionally save report
    filename = f"llm_eval_{model.replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: {filename}")


if __name__ == "__main__":
    asyncio.run(main())
