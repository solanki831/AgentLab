"""
🔗 LangChain Testing Agent
Comprehensive testing for LangChain chains, memory, tools, and integrations
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import List, Dict, Optional
import re
import statistics


class LangChainTestAgent:
    """Agent for testing LangChain workflows and integrations"""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 60):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
        self.timeout = timeout
    
    async def call_llm(self, model: str, prompt: str, temperature: float = 0.7) -> tuple:
        """Call LLM and return response with timing and token count"""
        from time import perf_counter
        
        start = perf_counter()
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
                    elapsed = perf_counter() - start
                    tokens = data.get("eval_count", 0)
                    return data.get("response", "").strip(), elapsed, tokens
                else:
                    return f"Error: {response.status_code}", 0.0, 0
        except Exception as e:
            return f"Error: {str(e)}", 0.0, 0
    
    async def test_qa_chain(self, model: str, questions: List[str]) -> Dict:
        """Test QA chain functionality"""
        print("🤖 Testing QA Chain...")
        
        # Handle empty questions list
        if not questions:
            return {
                "chain_type": "qa",
                "tests_run": 0,
                "avg_response_time": 0,
                "total_tokens": 0,
                "details": [],
                "status": "⏭️ Skipped (no questions configured)"
            }
        
        results = []
        for question in questions:
            response, time_taken, tokens = await self.call_llm(model, question)
            
            results.append({
                "question": question,
                "response": response[:200] + "..." if len(response) > 200 else response,
                "time": time_taken,
                "tokens": tokens,
                "tokens_per_sec": tokens / time_taken if time_taken > 0 else 0
            })
        
        avg_time = statistics.mean([r['time'] for r in results]) if results else 0
        total_tokens = sum(r['tokens'] for r in results)
        
        return {
            "chain_type": "qa",
            "tests_run": len(results),
            "avg_response_time": avg_time,
            "total_tokens": total_tokens,
            "details": results,
            "status": "✅ Passed"
        }
    
    async def test_summarization_chain(self, model: str, documents: List[str]) -> Dict:
        """Test summarization chain"""
        print("📝 Testing Summarization Chain...")
        
        # Handle empty documents list
        if not documents:
            return {
                "chain_type": "summarization",
                "tests_run": 0,
                "avg_compression": 0,
                "details": [],
                "status": "⏭️ Skipped (no documents configured)"
            }
        
        results = []
        for doc in documents:
            prompt = f"Summarize this in 2-3 sentences:\n{doc}"
            response, time_taken, tokens = await self.call_llm(model, prompt)
            
            results.append({
                "document": doc[:100] + "..." if len(doc) > 100 else doc,
                "summary": response[:150] + "..." if len(response) > 150 else response,
                "time": time_taken,
                "tokens": tokens,
                "compression_ratio": len(doc) / len(response) if response else 0
            })
        
        valid_compressions = [r['compression_ratio'] for r in results if r['compression_ratio'] > 0]
        avg_compression = statistics.mean(valid_compressions) if valid_compressions else 0
        
        return {
            "chain_type": "summarization",
            "tests_run": len(results),
            "avg_compression": avg_compression,
            "details": results,
            "status": "✅ Passed"
        }
    
    async def test_translation_chain(self, model: str, texts: List[str], target_lang: str = "Spanish") -> Dict:
        """Test translation chain"""
        print("🌐 Testing Translation Chain...")
        
        # Handle empty texts list
        if not texts:
            return {
                "chain_type": "translation",
                "target_language": target_lang,
                "tests_run": 0,
                "details": [],
                "status": "⏭️ Skipped (no texts configured)"
            }
        
        results = []
        for text in texts:
            prompt = f"Translate to {target_lang}:\n{text}"
            response, time_taken, tokens = await self.call_llm(model, prompt)
            
            results.append({
                "original": text,
                "translated": response,
                "time": time_taken,
                "tokens": tokens,
                "language": target_lang
            })
        
        return {
            "chain_type": "translation",
            "target_language": target_lang,
            "tests_run": len(results),
            "details": results,
            "status": "✅ Passed"
        }
    
    async def test_chain_memory(self, model: str, conversation: List[str], memory_type: str = "buffer") -> Dict:
        """Test chain with memory"""
        print(f"💾 Testing {memory_type} Memory Chain...")
        
        # Handle empty conversation list
        if not conversation:
            return {
                "memory_type": memory_type,
                "conversation_turns": 0,
                "final_context_length": 0,
                "details": [],
                "status": "⏭️ Skipped (no conversation configured)"
            }
        
        context = ""
        results = []
        for turn, user_input in enumerate(conversation, 1):
            # Simulate memory by including previous context
            prompt = f"Context: {context}\n\nUser: {user_input}\nAssistant:"
            response, time_taken, tokens = await self.call_llm(model, prompt, temperature=0.5)
            
            context += f"User: {user_input}\nAssistant: {response}\n"
            
            results.append({
                "turn": turn,
                "input": user_input,
                "output": response[:150] + "..." if len(response) > 150 else response,
                "time": time_taken,
                "tokens": tokens,
                "context_length": len(context)
            })
        
        return {
            "memory_type": memory_type,
            "conversation_turns": len(conversation),
            "final_context_length": len(context),
            "details": results,
            "status": "✅ Passed"
        }
    
    async def test_tool_usage(self, model: str, prompts_with_tools: List[Dict]) -> Dict:
        """Test chain with tool usage"""
        print("🔧 Testing Tool Usage...")
        
        # Handle empty tools list
        if not prompts_with_tools:
            return {
                "chain_type": "tool_usage",
                "tests_run": 0,
                "tool_success_rate": 0,
                "details": [],
                "status": "⏭️ Skipped (no tools configured)"
            }
        
        results = []
        for item in prompts_with_tools:
            prompt = item.get("prompt", "")
            expected_tool = item.get("expected_tool", "")
            
            response, time_taken, tokens = await self.call_llm(model, prompt, temperature=0.0)
            
            # Check if tool name appears in response
            uses_tool = expected_tool.lower() in response.lower()
            
            results.append({
                "prompt": prompt,
                "expected_tool": expected_tool,
                "uses_tool": uses_tool,
                "response": response[:200] + "..." if len(response) > 200 else response,
                "time": time_taken,
                "tokens": tokens
            })
        
        tool_success_rate = (sum(1 for r in results if r['uses_tool']) / len(results)) * 100 if results else 0
        
        return {
            "chain_type": "tool_usage",
            "tests_run": len(results),
            "tool_success_rate": tool_success_rate,
            "details": results,
            "status": "✅ Passed" if tool_success_rate > 50 else "⚠️ Warning"
        }
    
    async def test_error_handling(self, model: str, edge_cases: List[str]) -> Dict:
        """Test error handling and fallbacks"""
        print("⚠️ Testing Error Handling...")
        
        # Handle empty edge_cases list
        if not edge_cases:
            return {
                "test_type": "error_handling",
                "edge_cases_tested": 0,
                "success_rate": 0,
                "details": [],
                "status": "⏭️ Skipped (no edge cases configured)"
            }
        
        results = []
        for case in edge_cases:
            response, time_taken, tokens = await self.call_llm(model, case)
            
            # Check if model handled edge case gracefully
            is_valid_response = len(response) > 0 and "error" not in response.lower()
            
            results.append({
                "edge_case": case,
                "response": response,
                "handled_gracefully": is_valid_response,
                "time": time_taken
            })
        
        success_rate = (sum(1 for r in results if r['handled_gracefully']) / len(results)) * 100 if results else 0
        
        return {
            "test_type": "error_handling",
            "edge_cases_tested": len(results),
            "success_rate": success_rate,
            "details": results,
            "status": "✅ Passed" if success_rate > 80 else "⚠️ Warning"
        }
    
    async def run_full_langchain_test(self, model: str, test_config: Dict = None) -> Dict:
        """Run comprehensive LangChain testing"""
        from time import perf_counter
        
        # Default test data
        default_test_data = {
            "qa_questions": [
                "What is machine learning?",
                "Explain deep learning",
                "How does a neural network work?"
            ],
            "documents_to_summarize": [
                "Machine learning is a subset of artificial intelligence that focuses on enabling systems to learn and improve from experience without being explicitly programmed.",
                "Deep learning uses artificial neural networks with multiple layers to process data and make predictions."
            ],
            "texts_to_translate": [
                "Hello, how are you?",
                "The weather is beautiful today."
            ],
            "conversation": [
                "What is AI?",
                "Can you explain machine learning?",
                "How is it different from traditional programming?",
                "Give me an example."
            ],
            "tools": [
                {"prompt": "Search for the capital of France", "expected_tool": "search"},
                {"prompt": "Calculate 15 + 25", "expected_tool": "calculator"}
            ],
            "edge_cases": [
                "",
                "What's the meaning of life?",
                "Can you list 1000 items?",
                "Repeat this: " + "a" * 100
            ]
        }
        
        # Handle config - support both formats:
        # 1. Full test data: {"qa_questions": [...], "documents_to_summarize": [...]}
        # 2. Sidebar boolean flags: {"test_qa": True, "test_summarization": False}
        if test_config is None:
            test_config = {}
        
        # Check if config has boolean flags (sidebar format)
        has_boolean_flags = any(key.startswith("test_") for key in test_config.keys())
        
        if has_boolean_flags:
            # Sidebar config format - use defaults with boolean flags
            should_test_qa = test_config.get("test_qa", True)
            should_test_summarization = test_config.get("test_summarization", True)
            should_test_translation = test_config.get("test_translation", True)
            should_test_memory = test_config.get("test_memory", True)
            should_test_tools = test_config.get("test_tools", True)
            should_test_error_handling = test_config.get("test_error_handling", True)
            
            # Build effective test data based on flags
            effective_config = {
                "qa_questions": default_test_data["qa_questions"] if should_test_qa else [],
                "documents_to_summarize": default_test_data["documents_to_summarize"] if should_test_summarization else [],
                "texts_to_translate": default_test_data["texts_to_translate"] if should_test_translation else [],
                "conversation": default_test_data["conversation"] if should_test_memory else [],
                "tools": default_test_data["tools"] if should_test_tools else [],
                "edge_cases": default_test_data["edge_cases"] if should_test_error_handling else []
            }
        else:
            # Full test data format - merge with defaults
            effective_config = {
                "qa_questions": test_config.get("qa_questions", default_test_data["qa_questions"]),
                "documents_to_summarize": test_config.get("documents_to_summarize", default_test_data["documents_to_summarize"]),
                "texts_to_translate": test_config.get("texts_to_translate", default_test_data["texts_to_translate"]),
                "conversation": test_config.get("conversation", default_test_data["conversation"]),
                "tools": test_config.get("tools", default_test_data["tools"]),
                "edge_cases": test_config.get("edge_cases", default_test_data["edge_cases"])
            }
        
        print(f"\n{'='*70}")
        print(f"🔗 LANGCHAIN TESTING SUITE")
        print(f"{'='*70}")
        print(f"Model: {model}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        start_time = perf_counter()
        
        # Run all tests
        qa_result = await self.test_qa_chain(model, effective_config.get("qa_questions", []))
        summarization_result = await self.test_summarization_chain(model, effective_config.get("documents_to_summarize", []))
        translation_result = await self.test_translation_chain(model, effective_config.get("texts_to_translate", []))
        memory_result = await self.test_chain_memory(model, effective_config.get("conversation", []), "buffer")
        tools_result = await self.test_tool_usage(model, effective_config.get("tools", []))
        error_result = await self.test_error_handling(model, effective_config.get("edge_cases", []))
        
        total_time = perf_counter() - start_time
        
        # Calculate composite scores (only count tests that were run)
        scores = []
        if qa_result['tests_run'] > 0:
            scores.append(100)  # QA passed
        if summarization_result['tests_run'] > 0:
            scores.append(min(summarization_result.get('avg_compression', 1) * 20, 100))
        if translation_result['tests_run'] > 0:
            scores.append(100)  # Translation passed
        if memory_result['conversation_turns'] > 0:
            scores.append(100)  # Memory passed
        if tools_result['tests_run'] > 0:
            scores.append(tools_result.get('tool_success_rate', 0))
        if error_result['edge_cases_tested'] > 0:
            scores.append(error_result.get('success_rate', 0))
        
        overall_score = statistics.mean(scores) if scores else 0
        
        report = {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "total_evaluation_time": total_time,
            "overall_score": round(overall_score, 2),
            "test_results": {
                "qa_chain": qa_result,
                "summarization": summarization_result,
                "translation": translation_result,
                "memory": memory_result,
                "tools": tools_result,
                "error_handling": error_result
            },
            "metrics": {
                "avg_response_time": qa_result.get('avg_response_time', 0),
                "total_tokens": qa_result.get('total_tokens', 0) + summarization_result.get('total_tokens', 0),
                "success_rate": overall_score
            }
        }
        
        self.print_report(report)
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted test report"""
        print(f"\n{'='*70}")
        print(f"📊 LANGCHAIN TEST SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"🎯 Overall Score: {report['overall_score']:.1f}/100")
        print(f"⏱️ Total Test Time: {report['total_evaluation_time']:.2f}s\n")
        
        results = report['test_results']
        
        print(f"{'Test Type':<25} {'Status':<15} {'Details'}")
        print(f"{'-'*70}")
        
        # QA Chain
        qa = results.get('qa_chain', {})
        qa_status = qa.get('status', '⏭️ Skipped')
        qa_details = f"{qa.get('tests_run', 0)} questions"
        if qa.get('avg_response_time', 0) > 0:
            qa_details += f", avg {qa['avg_response_time']:.2f}s"
        print(f"QA Chain{' '*17}{qa_status:<15} {qa_details}")
        
        # Summarization
        summ = results.get('summarization', {})
        summ_status = summ.get('status', '⏭️ Skipped')
        summ_details = f"{summ.get('tests_run', 0)} docs"
        if summ.get('avg_compression', 0) > 0:
            summ_details += f", ratio {summ['avg_compression']:.2f}"
        print(f"Summarization{' '*12}{summ_status:<15} {summ_details}")
        
        # Translation
        trans = results.get('translation', {})
        trans_status = trans.get('status', '⏭️ Skipped')
        print(f"Translation{' '*14}{trans_status:<15} {trans.get('tests_run', 0)} translations")
        
        # Memory
        mem = results.get('memory', {})
        mem_status = mem.get('status', '⏭️ Skipped')
        print(f"Memory{' '*19}{mem_status:<15} {mem.get('conversation_turns', 0)} turns")
        
        # Tool Usage
        tools = results.get('tools', {})
        tools_status = tools.get('status', '⏭️ Skipped')
        print(f"Tool Usage{' '*15}{tools_status:<15} {tools.get('tool_success_rate', 0):.1f}% success")
        
        # Error Handling
        err = results.get('error_handling', {})
        err_status = err.get('status', '⏭️ Skipped')
        print(f"Error Handling{' '*11}{err_status:<15} {err.get('success_rate', 0):.1f}% handled")
        
        print(f"\n{'='*70}\n")
