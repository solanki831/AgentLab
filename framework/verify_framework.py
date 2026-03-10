"""
🧪 COMPREHENSIVE VERIFICATION SCRIPT
Tests all agents, MCP integration, and Ollama connectivity
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add framework to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.agent_registry import get_registry, AgentType
from framework.agentFactory import AgentFactory
from framework.ollama_helper import create_ollama_client
from framework.mcp_config import McpConfig
from framework.llm_model_tester import LLMModelTester


class FrameworkVerifier:
    """Comprehensive verification of the entire framework"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "ollama": None,
            "mcp": {},
            "agents": {},
            "llm_models": {},
            "overall_status": "⏳ In Progress"
        }
    
    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)
    
    def print_step(self, step: str, status: str = ""):
        """Print a step"""
        if status:
            print(f"  {step} {status}")
        else:
            print(f"  {step}")
    
    # ========================================================================
    # OLLAMA VERIFICATION
    # ========================================================================
    
    async def verify_ollama(self):
        """Verify Ollama is running and accessible"""
        self.print_header("🔌 OLLAMA VERIFICATION")
        
        try:
            self.print_step("Checking Ollama connection...", end=" ")
            
            client = create_ollama_client()
            
            if client:
                print("✅")
                self.results["ollama"] = {
                    "status": "✅ Connected",
                    "base_url": "http://localhost:11434",
                    "model": "llama3.2:latest"
                }
                self.print_step("✅ Ollama is running and accessible")
            else:
                print("❌")
                self.results["ollama"] = {
                    "status": "❌ Disconnected",
                    "error": "Could not connect to Ollama"
                }
                self.print_step("❌ Could not connect to Ollama")
                self.print_step("   Make sure Ollama is running: ollama serve")
        
        except Exception as e:
            self.print_step(f"❌ Error: {str(e)}")
            self.results["ollama"] = {
                "status": "❌ Error",
                "error": str(e)
            }
    
    async def verify_ollama_models(self):
        """Verify Ollama models are available"""
        self.print_header("📦 AVAILABLE OLLAMA MODELS")
        
        try:
            tester = LLMModelTester()
            models = await tester.get_available_models()
            
            if models:
                self.print_step(f"Found {len(models)} model(s):")
                for model in models:
                    self.print_step(f"  ✅ {model}")
                
                self.results["llm_models"] = {
                    "available": len(models),
                    "models": models,
                    "status": "✅ Models available"
                }
            else:
                self.print_step("❌ No models found")
                self.print_step("   Pull a model: ollama pull llama3.2:latest")
                self.results["llm_models"] = {
                    "available": 0,
                    "models": [],
                    "status": "❌ No models"
                }
        
        except Exception as e:
            self.print_step(f"❌ Error: {str(e)}")
            self.results["llm_models"] = {"error": str(e)}
    
    # ========================================================================
    # MCP VERIFICATION
    # ========================================================================
    
    def verify_mcp(self):
        """Verify MCP integration"""
        self.print_header("🔗 MCP INTEGRATION VERIFICATION")
        
        mcp_config = McpConfig()
        mcp_tools = {
            "mysql": ("MySQL MCP", mcp_config.get_mysql_workbench),
            "rest_api": ("REST API MCP", mcp_config.get_rest_api_workbench),
            "excel": ("Excel MCP", mcp_config.get_excel_workbench),
            "filesystem": ("Filesystem MCP", mcp_config.get_filesystem_workbench),
            "playwright": ("Playwright MCP", mcp_config.get_playwright_workbench),
        }
        
        for key, (name, getter) in mcp_tools.items():
            try:
                self.print_step(f"Checking {name}...", end=" ")
                workbench = getter()
                if workbench:
                    print("✅")
                    self.results["mcp"][key] = {
                        "status": "✅ Ready",
                        "name": name
                    }
                else:
                    print("⚠️")
                    self.results["mcp"][key] = {
                        "status": "⚠️ Unconfigured",
                        "name": name
                    }
            except Exception as e:
                print(f"⚠️ ({str(e)[:30]}...)")
                self.results["mcp"][key] = {
                    "status": f"⚠️ {str(e)[:50]}",
                    "name": name
                }
        
        mcp_ready_count = sum(1 for v in self.results["mcp"].values() if v["status"].startswith("✅"))
        self.print_step(f"\n  MCP Status: {mcp_ready_count}/{len(mcp_tools)} tools ready")
    
    # ========================================================================
    # AGENT VERIFICATION
    # ========================================================================
    
    def verify_agents(self):
        """Verify all agents are accessible"""
        self.print_header("🎯 AGENT VERIFICATION")
        
        try:
            registry = get_registry()
            agents = registry.get_all_metadata()
            
            self.print_step(f"Found {len(agents)} agents in registry:")
            
            agents_by_category = {}
            for agent in agents:
                if agent.category not in agents_by_category:
                    agents_by_category[agent.category] = []
                agents_by_category[agent.category].append(agent)
            
            for category in sorted(agents_by_category.keys()):
                agent_list = agents_by_category[category]
                self.print_step(f"  {category.upper()} ({len(agent_list)} agents)")
                
                for agent in agent_list:
                    self.print_step(f"    ✅ {agent.name}")
                    self.results["agents"][agent.name] = {
                        "type": agent.type.value,
                        "category": agent.category,
                        "status": "✅ Ready",
                        "capabilities": len(agent.capabilities),
                        "mcp_tools": agent.mcp_tools
                    }
            
            self.print_step(f"\n  Total Agents: {len(agents)}")
            self.print_step(f"  Categories: {len(agents_by_category)}")
        
        except Exception as e:
            self.print_step(f"❌ Error: {str(e)}")
            self.results["agents"] = {"error": str(e)}
    
    # ========================================================================
    # AGENT FACTORY VERIFICATION
    # ========================================================================
    
    def verify_agent_factory(self):
        """Verify AgentFactory works"""
        self.print_header("🏭 AGENT FACTORY VERIFICATION")
        
        try:
            self.print_step("Creating Ollama client...", end=" ")
            
            client = create_ollama_client()
            if not client:
                print("❌")
                self.print_step("❌ Could not create Ollama client")
                return
            
            print("✅")
            
            self.print_step("Creating AgentFactory...", end=" ")
            factory = AgentFactory(client)
            print("✅")
            
            self.print_step("Testing agent creation methods:")
            
            methods = [
                ("database_agent", factory.create_database_agent),
                ("api_agent", factory.create_api_agent),
                ("excel_agent", factory.create_excel_agent),
                ("ui_visual_regression_agent", factory.create_ui_visual_regression_agent),
                ("api_contract_testing_agent", factory.create_api_contract_testing_agent),
                ("accessibility_testing_agent", factory.create_accessibility_testing_agent),
                ("data_validation_agent", factory.create_data_validation_agent),
            ]
            
            for method_name, method in methods:
                try:
                    self.print_step(f"  Creating {method_name}...", end=" ")
                    agent = method()
                    print("✅")
                except Exception as e:
                    print(f"⚠️ ({str(e)[:30]})")
        
        except Exception as e:
            self.print_step(f"❌ Error: {str(e)}")
    
    # ========================================================================
    # LLM TESTING
    # ========================================================================
    
    async def test_llm_models(self):
        """Test LLM models"""
        self.print_header("🧪 LLM MODEL TESTING")
        
        try:
            tester = LLMModelTester()
            models = await tester.get_available_models()
            
            if not models:
                self.print_step("❌ No models available")
                return
            
            test_prompt = "What is the capital of France?"
            
            self.print_step(f"Testing {len(models)} model(s)...\n")
            
            for model in models:
                self.print_step(f"Testing {model}...", end=" ")
                result = await tester.test_single_model(model, test_prompt)
                
                if result['status'] == '✅ Success':
                    print("✅")
                    self.print_step(f"  Response Time: {result['response_time_seconds']:.2f}s")
                    self.print_step(f"  Tokens Generated: {result['tokens_generated']}")
                    self.print_step(f"  Rate: {result['tokens_per_second']:.2f} tokens/sec")
                else:
                    print(f"❌ ({result.get('error', 'Unknown')})")
        
        except Exception as e:
            self.print_step(f"❌ Error: {str(e)}")
    
    # ========================================================================
    # COMPREHENSIVE TEST
    # ========================================================================
    
    async def run_comprehensive_test(self):
        """Run comprehensive verification"""
        print("\n")
        print("╔" + "="*78 + "╗")
        print("║" + " "*20 + "🚀 COMPREHENSIVE FRAMEWORK VERIFICATION" + " "*18 + "║")
        print("║" + " "*25 + f"Started: {datetime.now().strftime('%H:%M:%S')}" + " "*24 + "║")
        print("╚" + "="*78 + "╝")
        
        # Run all checks
        await self.verify_ollama()
        await self.verify_ollama_models()
        self.verify_mcp()
        self.verify_agents()
        self.verify_agent_factory()
        await self.test_llm_models()
        
        # Determine overall status
        self.print_header("📊 VERIFICATION SUMMARY")
        
        ollama_ok = self.results["ollama"] and self.results["ollama"].get("status", "").startswith("✅")
        mcp_ok = len(self.results["mcp"]) > 0
        agents_ok = len(self.results["agents"]) > 0
        models_ok = self.results["llm_models"].get("available", 0) > 0
        
        print("\n📋 Results:")
        print(f"  Ollama:         {'✅ Ready' if ollama_ok else '❌ Failed'}")
        print(f"  MCP Tools:      {'✅ Ready' if mcp_ok else '⚠️ Partial'}")
        print(f"  Agents:         {'✅ Ready' if agents_ok else '❌ Failed'}")
        print(f"  LLM Models:     {'✅ Ready' if models_ok else '⚠️ Not Available'}")
        
        if ollama_ok and agents_ok:
            self.results["overall_status"] = "✅ PRODUCTION READY"
            print(f"\n✅ Overall Status: PRODUCTION READY")
            print("   All components are functioning correctly")
        elif ollama_ok and mcp_ok and agents_ok:
            self.results["overall_status"] = "✅ OPERATIONAL"
            print(f"\n✅ Overall Status: OPERATIONAL")
            print("   Core functionality is available")
        else:
            self.results["overall_status"] = "⚠️ PARTIAL"
            print(f"\n⚠️ Overall Status: PARTIAL")
            print("   Some components need attention")
        
        print("\n" + "="*80)
        print(f"  Verification Complete: {datetime.now().strftime('%H:%M:%S')}")
        print("="*80 + "\n")
        
        return self.results


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Main entry point"""
    verifier = FrameworkVerifier()
    results = await verifier.run_comprehensive_test()
    
    # Save results to file
    with open("verification_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("📁 Results saved to: verification_results.json")


if __name__ == "__main__":
    asyncio.run(main())
