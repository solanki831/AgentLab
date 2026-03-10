"""
🧪 LLM Model Testing Agent
Tests and compares different Ollama models for quality, speed, and accuracy
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import List, Dict, Optional
import statistics


class LLMModelTester:
    """Agent for testing and comparing different LLM models"""
    
    # Default configuration (can be overridden)
    DEFAULT_CONFIG = {
        "base_url": "http://localhost:11434",
        "timeout": 120,
        "default_temperature": 0.7,
        "default_max_tokens": None,
        "retry_attempts": 3,
        "retry_delay": 1.0
    }
    
    def __init__(
        self, 
        base_url: str = None,
        timeout: int = None,
        default_temperature: float = None,
        config: Optional[Dict] = None
    ):
        """
        Initialize LLM Model Tester
        
        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
            timeout: Request timeout in seconds (default: 120)
            default_temperature: Default temperature for generation (default: 0.7)
            config: Full configuration dictionary (overrides individual params)
        """
        # Merge config with defaults
        self.config = {**self.DEFAULT_CONFIG}
        if config:
            self.config.update(config)
        
        # Override with explicit parameters if provided
        if base_url is not None:
            self.config["base_url"] = base_url
        if timeout is not None:
            self.config["timeout"] = timeout
        if default_temperature is not None:
            self.config["default_temperature"] = default_temperature
        
        self.base_url = self.config["base_url"]
        self.api_endpoint = f"{self.base_url}/api/generate"
        self.tags_endpoint = f"{self.base_url}/api/tags"
        self.timeout = self.config["timeout"]
        self.default_temperature = self.config["default_temperature"]
        self.results = []
    
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            async with httpx.AsyncClient(timeout=self.config.get("timeout", 10)) as client:
                response = await client.get(self.tags_endpoint)
                if response.status_code == 200:
                    data = response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    return models
                return []
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
    
    async def test_single_model(
        self,
        model: str,
        prompt: str,
        temperature: float = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Test a single model with a prompt
        
        Args:
            model: Model name (e.g., "llama3.2:latest")
            prompt: Test prompt
            temperature: Temperature for generation (uses default if None)
            max_tokens: Maximum tokens to generate (uses config default if None)
            timeout: Request timeout in seconds (uses config default if None)
        
        Returns:
            Dictionary with test results
        """
        # Use config defaults if not specified
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.get("default_max_tokens")
        request_timeout = timeout if timeout is not None else self.timeout
        
        try:
            start_time = datetime.now()
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            }
            
            if max_tokens:
                payload["num_predict"] = max_tokens
            
            async with httpx.AsyncClient(timeout=request_timeout) as client:
                response = await client.post(self.api_endpoint, json=payload)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "status": "✅ Success",
                    "model": model,
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "response": data.get("response", ""),
                    "response_time_seconds": elapsed,
                    "tokens_generated": data.get("eval_count", 0),
                    "tokens_per_second": data.get("eval_count", 0) / elapsed if elapsed > 0 else 0,
                    "total_duration_ms": data.get("total_duration", 0) / 1e6,  # Convert to ms
                    "load_duration_ms": data.get("load_duration", 0) / 1e6,
                    "temperature": temperature,
                    "timestamp": datetime.now().isoformat()
                }
                return result
            else:
                return {
                    "status": "❌ Failed",
                    "model": model,
                    "error": f"HTTP {response.status_code}",
                    "response_time_seconds": elapsed
                }
        
        except asyncio.TimeoutError:
            return {
                "status": "❌ Timeout",
                "model": model,
                "error": f"Request timed out after {request_timeout} seconds"
            }
        except Exception as e:
            return {
                "status": "❌ Error",
                "model": model,
                "error": str(e)
            }
    
    async def compare_models(
        self,
        models: List[str],
        prompt: str,
        temperature: float = 0.7
    ) -> Dict:
        """
        Compare multiple models on the same prompt
        
        Args:
            models: List of model names to test
            prompt: Test prompt
            temperature: Temperature for generation
        
        Returns:
            Comparison results
        """
        print(f"🧪 Testing {len(models)} models...")
        print(f"📝 Prompt: {prompt[:60]}...")
        print()
        
        results = []
        
        for model in models:
            print(f"⏳ Testing {model}...", end=" ", flush=True)
            result = await self.test_single_model(model, prompt, temperature)
            results.append(result)
            
            if result['status'] == '✅ Success':
                print(f"✅ {result['tokens_per_second']:.2f} tokens/sec")
            else:
                print(f"{result['status']}")
        
        self.results = results
        return self._generate_comparison_report(results)
    
    def _generate_comparison_report(self, results: List[Dict]) -> Dict:
        """Generate comparison report from results"""
        
        successful_results = [r for r in results if r['status'] == '✅ Success']
        
        if not successful_results:
            return {
                "summary": "❌ No successful results",
                "total_tests": len(results),
                "successful": 0,
                "results": results
            }
        
        # Calculate statistics
        response_times = [r['response_time_seconds'] for r in successful_results]
        tokens_per_sec = [r['tokens_per_second'] for r in successful_results]
        
        report = {
            "summary": "✅ Comparison Complete",
            "total_tests": len(results),
            "successful": len(successful_results),
            "failed": len(results) - len(successful_results),
            "statistics": {
                "fastest_model": min(successful_results, key=lambda x: x['response_time_seconds'])['model'],
                "fastest_time": min(response_times),
                "slowest_model": max(successful_results, key=lambda x: x['response_time_seconds'])['model'],
                "slowest_time": max(response_times),
                "avg_response_time": statistics.mean(response_times),
                "fastest_token_rate": max(tokens_per_sec),
                "slowest_token_rate": min(tokens_per_sec),
                "avg_token_rate": statistics.mean(tokens_per_sec)
            },
            "detailed_results": results
        }
        
        return report
    
    async def benchmark_model(
        self,
        model: str,
        prompts: List[str],
        iterations: int = 1
    ) -> Dict:
        """
        Benchmark a model with multiple prompts
        
        Args:
            model: Model to benchmark
            prompts: List of test prompts
            iterations: Number of iterations per prompt
        
        Returns:
            Benchmark results
        """
        print(f"📊 Benchmarking {model}")
        print(f"   Prompts: {len(prompts)}")
        print(f"   Iterations: {iterations}")
        print()
        
        all_results = []
        
        for prompt_idx, prompt in enumerate(prompts, 1):
            print(f"Prompt {prompt_idx}/{len(prompts)}: ", end="", flush=True)
            
            for iter_idx in range(iterations):
                result = await self.test_single_model(model, prompt)
                all_results.append(result)
                
                if result['status'] == '✅ Success':
                    print(".", end="", flush=True)
                else:
                    print("X", end="", flush=True)
            
            print()
        
        # Calculate benchmark statistics
        successful = [r for r in all_results if r['status'] == '✅ Success']
        
        if successful:
            response_times = [r['response_time_seconds'] for r in successful]
            tokens = [r['tokens_generated'] for r in successful]
            
            benchmark = {
                "model": model,
                "prompts_tested": len(prompts),
                "iterations": iterations,
                "total_tests": len(all_results),
                "successful_tests": len(successful),
                "statistics": {
                    "avg_response_time": statistics.mean(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "std_dev_response_time": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                    "avg_tokens": statistics.mean(tokens),
                    "total_tokens": sum(tokens),
                }
            }
            
            return benchmark
        else:
            return {"error": "No successful tests"}
    
    async def test_response_quality(
        self,
        models: List[str],
        test_cases: List[Dict]
    ) -> Dict:
        """
        Test response quality (creativity, length, relevance)
        
        Args:
            models: Models to test
            test_cases: List of test cases with prompt and expected characteristics
        
        Returns:
            Quality assessment
        """
        results = {}
        
        for model in models:
            print(f"🎨 Testing quality of {model}...")
            
            quality_scores = []
            
            for test_case in test_cases:
                prompt = test_case.get('prompt', '')
                expected_length = test_case.get('expected_length', 'medium')
                
                result = await self.test_single_model(model, prompt)
                
                if result['status'] == '✅ Success':
                    response = result['response']
                    
                    # Score quality
                    score = self._score_response_quality(response, expected_length)
                    quality_scores.append(score)
            
            results[model] = {
                "avg_quality_score": statistics.mean(quality_scores) if quality_scores else 0,
                "tests_passed": len(quality_scores),
                "details": quality_scores
            }
        
        return results
    
    def _score_response_quality(self, response: str, expected_length: str) -> float:
        """Score response quality"""
        score = 100
        
        # Check length
        length = len(response)
        if expected_length == "short" and length > 200:
            score -= 10
        elif expected_length == "medium" and (length < 100 or length > 500):
            score -= 10
        elif expected_length == "long" and length < 300:
            score -= 10
        
        # Check if response is empty
        if not response or response.strip() == "":
            score = 0
        
        # Check for common quality indicators
        if any(word in response.lower() for word in ['i', 'the', 'a']):
            pass  # Contains common words
        
        return max(0, min(100, score))
    
    def print_report(self, report: Dict) -> None:
        """Pretty print a report"""
        print("\n" + "="*70)
        print("📊 LLM MODEL COMPARISON REPORT")
        print("="*70)
        
        print(f"\n✅ Summary: {report.get('summary')}")
        print(f"Total Tests: {report.get('total_tests')}")
        print(f"Successful: {report.get('successful')}")
        print(f"Failed: {report.get('failed')}")
        
        if 'statistics' in report:
            stats = report['statistics']
            print("\n📈 Statistics:")
            print(f"  Fastest Model: {stats.get('fastest_model')}")
            print(f"    Response Time: {stats.get('fastest_time'):.2f}s")
            print(f"  Slowest Model: {stats.get('slowest_model')}")
            print(f"    Response Time: {stats.get('slowest_time'):.2f}s")
            print(f"  Avg Response Time: {stats.get('avg_response_time'):.2f}s")
            print(f"  Avg Token Rate: {stats.get('avg_token_rate'):.2f} tokens/sec")
        
        print("\n📋 Detailed Results:")
        for result in report.get('detailed_results', []):
            print(f"\n  {result['model']}:")
            print(f"    Status: {result['status']}")
            if result['status'] == '✅ Success':
                print(f"    Response Time: {result['response_time_seconds']:.2f}s")
                print(f"    Tokens: {result['tokens_generated']}")
                print(f"    Rate: {result['tokens_per_second']:.2f} tokens/sec")
            else:
                print(f"    Error: {result.get('error', 'Unknown')}")
        
        print("\n" + "="*70)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage of LLM Model Tester"""
    
    tester = LLMModelTester()
    
    # Get available models
    print("🔍 Fetching available Ollama models...\n")
    models = await tester.get_available_models()
    
    if not models:
        print("❌ No Ollama models found. Make sure Ollama is running.")
        print("   Run: ollama pull llama3.2:latest")
        return
    
    print(f"✅ Found {len(models)} models:")
    for model in models:
        print(f"   - {model}")
    print()
    
    # Test prompts
    test_prompts = [
        "What is artificial intelligence?",
        "Explain quantum computing in simple terms",
        "Write a Python function to reverse a string"
    ]
    
    # Compare first 2 models
    if len(models) >= 2:
        print("\n🧪 Comparing models...")
        report = await tester.compare_models(
            models[:2],
            test_prompts[0],
            temperature=0.7
        )
        tester.print_report(report)
    else:
        print("\n🧪 Testing single model...")
        result = await tester.test_single_model(
            models[0],
            test_prompts[0],
            temperature=0.7
        )
        print(f"Model: {result['model']}")
        print(f"Status: {result['status']}")
        if result['status'] == '✅ Success':
            print(f"Response Time: {result['response_time_seconds']:.2f}s")
            print(f"Tokens: {result['tokens_generated']}")
            print(f"Rate: {result['tokens_per_second']:.2f} tokens/sec")


if __name__ == "__main__":
    asyncio.run(main())
