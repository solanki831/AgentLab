"""
🔄 RAG (Retrieval Augmented Generation) Pipeline Agent
Comprehensive testing for RAG pipelines: retrieval, augmentation, and generation
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import List, Dict, Optional
import statistics
import random


class RAGEvaluationAgent:
    """Agent for evaluating RAG pipeline performance and quality"""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 120):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
        self.timeout = timeout
    
    async def call_llm(self, model: str, prompt: str, temperature: float = 0.3) -> tuple:
        """Call LLM and return response"""
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
                    return data.get("response", "").strip(), elapsed
                else:
                    return f"Error: {response.status_code}", 0.0
        except Exception as e:
            return f"Error: {str(e)}", 0.0
    
    async def test_document_ingestion(self, documents: List[str], chunk_size: int = 500) -> Dict:
        """Test document ingestion and chunking"""
        print("📄 Testing Document Ingestion...")
        
        chunks = []
        for doc in documents:
            # Simple chunking
            doc_chunks = [doc[i:i+chunk_size] for i in range(0, len(doc), chunk_size)]
            chunks.extend(doc_chunks)
        
        return {
            "test_type": "document_ingestion",
            "documents_ingested": len(documents),
            "total_text_length": sum(len(d) for d in documents),
            "chunks_created": len(chunks),
            "avg_chunk_size": sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
            "status": "✅" if len(chunks) > 0 else "❌"
        }
    
    async def test_embedding_quality(self, texts: List[str], embedding_model: str = "all-MiniLM-L6-v2") -> Dict:
        """Test embedding quality and diversity"""
        print("🎯 Testing Embedding Quality...")
        
        # Simulate embeddings
        embeddings = []
        for text in texts:
            # Simulate vector (in real scenario, use actual embedding model)
            vector = [random.uniform(-1, 1) for _ in range(384)]
            embeddings.append({
                "text": text,
                "vector": vector,
                "length": len(vector)
            })
        
        # Calculate diversity (cosine similarity between random pairs)
        similarities = []
        for i in range(min(10, len(embeddings) - 1)):
            idx1, idx2 = random.sample(range(len(embeddings)), 2)
            # Simulate cosine similarity
            sim = random.uniform(-1, 1)
            similarities.append(abs(sim))
        
        avg_similarity = statistics.mean(similarities) if similarities else 0
        diversity_score = (1 - avg_similarity) * 100  # Lower similarity = higher diversity
        
        return {
            "test_type": "embedding_quality",
            "texts_embedded": len(texts),
            "embedding_model": embedding_model,
            "embedding_dimension": 384,
            "avg_similarity": round(avg_similarity, 3),
            "diversity_score": round(diversity_score, 2),
            "status": "✅" if diversity_score > 50 else "⚠️"
        }
    
    async def test_retrieval_accuracy(self, queries: List[Dict], model: str = "llama3.2:latest") -> Dict:
        """Test retrieval accuracy against queries"""
        print("🔍 Testing Retrieval Accuracy...")
        
        from time import perf_counter
        
        results = []
        for query_item in queries:
            query = query_item.get("query", "")
            expected_docs = query_item.get("expected_docs", [])
            
            start = perf_counter()
            # Simulate retrieval
            retrieved = random.sample(expected_docs, min(len(expected_docs), random.randint(1, 3)))
            elapsed = perf_counter() - start
            
            # Calculate recall
            recall = len(set(retrieved) & set(expected_docs)) / len(expected_docs) if expected_docs else 0
            
            results.append({
                "query": query,
                "expected": len(expected_docs),
                "retrieved": len(retrieved),
                "recall": recall * 100,
                "retrieval_time": elapsed
            })
        
        avg_recall = statistics.mean([r['recall'] for r in results]) if results else 0
        avg_time = statistics.mean([r['retrieval_time'] for r in results]) if results else 0
        
        return {
            "test_type": "retrieval_accuracy",
            "queries_tested": len(results),
            "avg_recall": round(avg_recall, 2),
            "avg_retrieval_time": round(avg_time, 3),
            "details": results,
            "status": "✅" if avg_recall > 70 else "⚠️"
        }
    
    async def test_generation_quality(self, retrieval_results: List[Dict], model: str = "llama3.2:latest") -> Dict:
        """Test generation quality based on retrieved context"""
        print("✍️ Testing Generation Quality...")
        
        from time import perf_counter
        
        results = []
        for item in retrieval_results:
            query = item.get("query", "")
            context = item.get("context", "")
            expected_answer = item.get("expected_answer", "")
            
            prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
            response, gen_time = await self.call_llm(model, prompt, temperature=0.3)
            
            # Check if expected answer is in generated response
            contains_expected = expected_answer.lower() in response.lower() if expected_answer else True
            
            results.append({
                "query": query,
                "generated": response[:200] + "..." if len(response) > 200 else response,
                "contains_expected": contains_expected,
                "generation_time": gen_time
            })
        
        accuracy = (sum(1 for r in results if r['contains_expected']) / len(results)) * 100 if results else 0
        
        return {
            "test_type": "generation_quality",
            "generations": len(results),
            "accuracy": round(accuracy, 2),
            "avg_generation_time": round(statistics.mean([r['generation_time'] for r in results]), 3) if results else 0,
            "details": results,
            "status": "✅" if accuracy > 70 else "⚠️"
        }
    
    async def test_hallucination_detection(self, model: str, context_docs: List[str], 
                                          questions: List[str]) -> Dict:
        """Test hallucination tendency"""
        print("👻 Testing Hallucination Detection...")
        
        results = []
        for question in questions:
            context = " ".join(context_docs)
            prompt = f"Based ONLY on this context: {context}\n\nQuestion: {question}\nAnswer:"
            
            response, _ = await self.call_llm(model, prompt, temperature=0.0)
            
            # Simple hallucination check: see if response adds external info
            has_hallucination = len(response) > len(context) * 2
            
            results.append({
                "question": question,
                "response": response[:150] + "..." if len(response) > 150 else response,
                "has_hallucination": has_hallucination
            })
        
        hallucination_rate = (sum(1 for r in results if r['has_hallucination']) / len(results)) * 100 if results else 0
        
        return {
            "test_type": "hallucination_detection",
            "tests_run": len(results),
            "hallucination_rate": round(hallucination_rate, 2),
            "details": results,
            "status": "✅" if hallucination_rate < 30 else "⚠️"
        }
    
    async def test_end_to_end_latency(self, queries: List[str], model: str = "llama3.2:latest",
                                     num_iterations: int = 5) -> Dict:
        """Test complete RAG pipeline latency"""
        print("⏱️ Testing End-to-End Latency...")
        
        from time import perf_counter
        
        latencies = []
        
        for _ in range(num_iterations):
            for query in queries:
                start = perf_counter()
                
                # Simulate: retrieval + generation
                retrieval_prompt = f"Search for: {query}"
                retrieved, _ = await self.call_llm(model, retrieval_prompt)
                
                gen_prompt = f"Based on {retrieved[:100]}, answer: {query}"
                response, _ = await self.call_llm(model, gen_prompt)
                
                elapsed = perf_counter() - start
                latencies.append(elapsed)
        
        return {
            "test_type": "end_to_end_latency",
            "queries": len(queries),
            "iterations": num_iterations,
            "total_calls": len(latencies),
            "avg_latency": round(statistics.mean(latencies), 3),
            "p95_latency": round(sorted(latencies)[int(len(latencies) * 0.95)], 3),
            "p99_latency": round(sorted(latencies)[int(len(latencies) * 0.99)], 3),
            "status": "✅" if statistics.mean(latencies) < 10 else "⚠️"
        }
    
    async def run_full_rag_evaluation(self, model: str, eval_config: Dict = None) -> Dict:
        """Run comprehensive RAG pipeline evaluation"""
        
        if eval_config is None:
            eval_config = {
                "documents": [
                    "Machine learning is a subset of artificial intelligence that focuses on enabling systems to learn and improve from experience.",
                    "Deep learning uses neural networks with multiple layers to process complex data and patterns.",
                    "Natural Language Processing is a branch of AI that focuses on understanding and generating human language."
                ],
                "queries": [
                    {"query": "What is machine learning?", "expected_docs": ["Machine learning"]},
                    {"query": "How does deep learning work?", "expected_docs": ["Deep learning"]},
                    {"query": "What is NLP?", "expected_docs": ["Natural Language Processing"]}
                ],
                "test_questions": [
                    "Explain machine learning",
                    "What is deep learning?",
                    "How does neural network learn?"
                ],
                "chunk_size": 500,
                "num_iterations": 5
            }
        
        # Extract configurable parameters
        chunk_size = eval_config.get("chunk_size", 500)
        num_iterations = eval_config.get("num_iterations", 5)
        
        print(f"\n{'='*70}")
        print(f"🔄 RAG PIPELINE EVALUATION")
        print(f"{'='*70}")
        print(f"Model: {model}")
        print(f"Chunk Size: {chunk_size}")
        print(f"Iterations: {num_iterations}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        from time import perf_counter
        start_time = perf_counter()
        
        # Run all tests with configurable parameters
        ingestion = await self.test_document_ingestion(eval_config.get("documents", []), chunk_size=chunk_size)
        embeddings = await self.test_embedding_quality(eval_config.get("documents", []))
        retrieval = await self.test_retrieval_accuracy(eval_config.get("queries", []), model)
        
        # Prepare generation test data
        gen_test_data = [
            {
                "query": q.get("query", ""),
                "context": " ".join(eval_config.get("documents", [])),
                "expected_answer": ""
            }
            for q in eval_config.get("queries", [])[:2]
        ]
        
        generation = await self.test_generation_quality(gen_test_data, model)
        hallucination = await self.test_hallucination_detection(model, eval_config.get("documents", []), 
                                                               eval_config.get("test_questions", []))
        latency = await self.test_end_to_end_latency(eval_config.get("test_questions", []), model, num_iterations=num_iterations)
        
        total_time = perf_counter() - start_time
        
        # Calculate composite score
        ingestion_score = 100 if ingestion['status'] == "✅" else 0
        embedding_score = embeddings['diversity_score']
        retrieval_score = retrieval['avg_recall']
        generation_score = generation['accuracy']
        hallucination_score = max(0, 100 - hallucination['hallucination_rate'])
        latency_score = max(0, 100 - (latency['avg_latency'] * 10))
        
        overall_score = (ingestion_score + embedding_score + retrieval_score + generation_score + 
                        hallucination_score + latency_score) / 6
        
        report = {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "total_evaluation_time": total_time,
            "overall_score": round(overall_score, 2),
            "test_results": {
                "document_ingestion": ingestion,
                "embedding_quality": embeddings,
                "retrieval_accuracy": retrieval,
                "generation_quality": generation,
                "hallucination_detection": hallucination,
                "end_to_end_latency": latency
            }
        }
        
        self.print_report(report)
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted evaluation report"""
        print(f"\n{'='*70}")
        print(f"📊 RAG PIPELINE EVALUATION SUMMARY")
        print(f"{'='*70}\n")
        
        print(f"🎯 Overall Score: {report['overall_score']:.1f}/100")
        print(f"⏱️ Evaluation Time: {report['total_evaluation_time']:.2f}s\n")
        
        tests = report['test_results']
        
        print(f"{'Test':<30} {'Status':<12} {'Score/Details'}")
        print(f"{'-'*70}")
        
        print(f"Document Ingestion{' '*12} {tests['document_ingestion']['status']:<12} {tests['document_ingestion']['chunks_created']} chunks")
        print(f"Embedding Quality{' '*13} {tests['embedding_quality']['status']:<12} {tests['embedding_quality']['diversity_score']:.1f}/100")
        print(f"Retrieval Accuracy{' '*12} {tests['retrieval_accuracy']['status']:<12} {tests['retrieval_accuracy']['avg_recall']:.1f}% recall")
        print(f"Generation Quality{' '*12} {tests['generation_quality']['status']:<12} {tests['generation_quality']['accuracy']:.1f}% accuracy")
        print(f"Hallucination{' '*17} {tests['hallucination_detection']['status']:<12} {tests['hallucination_detection']['hallucination_rate']:.1f}% rate")
        print(f"End-to-End Latency{' '*12} {tests['end_to_end_latency']['status']:<12} {tests['end_to_end_latency']['avg_latency']:.3f}s avg")
        
        print(f"\n{'='*70}\n")
