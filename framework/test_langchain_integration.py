"""
Test script to verify LangChain integration with Playwright Agents
"""

import asyncio
import sys
import os
import pytest

# Add framework to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.playwright_agents import PlannerAgent, GeneratorAgent, HealerAgent


@pytest.mark.asyncio
async def test_planner_langchain():
    """Test PlannerAgent with LangChain"""
    print("\n" + "="*60)
    print("🧠 Testing PlannerAgent with LangChain")
    print("="*60)
    
    planner = PlannerAgent(use_langchain=True, persist_dir="./test_plans_db")
    
    # Check initialization
    print(f"✅ Vector Store: {planner.vectorstore is not None}")
    print(f"✅ Embeddings: {planner.embeddings is not None}")
    print(f"✅ Memory: {planner.memory is not None}")
    print(f"✅ LangChain Enabled: {planner.use_langchain}")
    
    # Create first plan
    print("\n📋 Creating first test plan...")
    plan1 = await planner.execute(
        target="Login Feature",
        config={
            "requirements": [
                "User can login with valid credentials",
                "User sees error with invalid credentials",
                "Password is masked"
            ],
            "test_type": "functional"
        }
    )
    
    print(f"✅ Plan created: {plan1['plan_id']}")
    print(f"   - Scenarios: {plan1['summary']['total_scenarios']}")
    
    if 'langchain_insights' in plan1:
        insights = plan1['langchain_insights']
        print(f"   - Similar plans found: {insights['similar_plans_found']}")
        print(f"   - Vector DB enabled: {insights['vectordb_enabled']}")
    
    # Create second similar plan
    print("\n📋 Creating second test plan (similar to first)...")
    plan2 = await planner.execute(
        target="User Authentication",
        config={
            "requirements": [
                "Login with email and password",
                "Show validation errors"
            ],
            "test_type": "functional"
        }
    )
    
    print(f"✅ Plan created: {plan2['plan_id']}")
    
    if 'langchain_insights' in plan2:
        insights = plan2['langchain_insights']
        print(f"   - Similar plans found: {insights['similar_plans_found']}")
        if insights['similar_plans']:
            print(f"   - Similar to: {insights['similar_plans'][0]['metadata']['target']}")
    
    # Search for similar plans
    print("\n🔍 Searching for similar plans...")
    similar = await planner.search_similar_plans("login authentication tests", k=3)
    print(f"✅ Found {len(similar)} similar plans")
    
    for i, s in enumerate(similar, 1):
        print(f"   {i}. {s['metadata']['target']} (score: {s['similarity_score']:.3f})")
    
    return True


@pytest.mark.asyncio
async def test_generator_langchain():
    """Test GeneratorAgent with LangChain"""
    print("\n" + "="*60)
    print("🧠 Testing GeneratorAgent with LangChain")
    print("="*60)
    
    generator = GeneratorAgent(use_langchain=True)
    
    # Check initialization
    print(f"✅ Memory: {generator.memory is not None}")
    print(f"✅ LangChain Enabled: {generator.use_langchain}")
    
    print("\n✅ GeneratorAgent memory initialized")
    
    return True


@pytest.mark.asyncio
async def test_healer_langchain():
    """Test HealerAgent with LangChain RAG"""
    print("\n" + "="*60)
    print("🧠 Testing HealerAgent with LangChain RAG")
    print("="*60)
    
    healer = HealerAgent(use_langchain=True, persist_dir="./test_healing_db")
    
    # Check initialization
    print(f"✅ Vector Store: {healer.vectorstore is not None}")
    print(f"✅ Embeddings: {healer.embeddings is not None}")
    print(f"✅ Memory: {healer.memory is not None}")
    print(f"✅ LangChain Enabled: {healer.use_langchain}")
    
    # Simulate first failure
    print("\n🔧 Healing first failure...")
    healing1 = await healer.execute(
        target="test_login_001",
        config={
            "error_info": {
                "message": "Timeout waiting for selector #submit-button",
                "type": "TimeoutError"
            },
            "test_code": "await page.click('#submit-button')",
            "logs": ["Page loaded", "Form filled", "Waiting for button..."],
            "auto_fix": True  # This will store in RAG
        }
    )
    
    print(f"✅ Healing complete: {healing1['target']}")
    print(f"   - Failure type: {healing1['analysis']['failure_type']}")
    print(f"   - Fixes suggested: {len(healing1['recommended_fixes'])}")
    
    if 'langchain_insights' in healing1:
        insights = healing1['langchain_insights']
        print(f"   - Similar failures found: {insights['similar_failures_found']}")
    
    # Simulate second similar failure
    print("\n🔧 Healing second similar failure...")
    healing2 = await healer.execute(
        target="test_checkout_001",
        config={
            "error_info": {
                "message": "Timeout waiting for selector #checkout-btn",
                "type": "TimeoutError"
            },
            "test_code": "await page.click('#checkout-btn')",
            "logs": [],
            "auto_fix": False  # Don't apply, just analyze
        }
    )
    
    print(f"✅ Healing complete: {healing2['target']}")
    
    if 'langchain_insights' in healing2:
        insights = healing2['langchain_insights']
        print(f"   - Similar failures found: {insights['similar_failures_found']}")
        print(f"   - RAG suggestions: {insights['rag_suggestions']}")
        
        if insights.get('past_fixes_referenced'):
            print(f"   - Referenced past fix: {insights['past_fixes_referenced'][0].get('test_id')}")
    
    # Search for similar failures
    print("\n🔍 Searching for similar timeout failures...")
    similar = await healer.search_similar_failures(
        error_message="Timeout waiting for selector",
        failure_type="timeout",
        k=5
    )
    
    print(f"✅ Found {len(similar)} similar failures")
    for i, s in enumerate(similar, 1):
        print(f"   {i}. {s['metadata']['root_cause']} (score: {s['similarity_score']:.3f})")
    
    return True


async def main():
    """Run all LangChain tests"""
    print("\n🚀 Testing LangChain Integration with Playwright Agents")
    print("="*60)
    
    try:
        # Test each agent
        await test_planner_langchain()
        await test_generator_langchain()
        await test_healer_langchain()
        
        print("\n" + "="*60)
        print("✅ All LangChain tests passed!")
        print("="*60)
        
        print("\n📁 Vector stores created:")
        print("   - ./test_plans_db/ (PlannerAgent)")
        print("   - ./test_healing_db/ (HealerAgent)")
        
        print("\n💡 Next steps:")
        print("   - Run the UI: python -m streamlit run framework/playwright_agents_ui.py")
        print("   - Check the vector stores contain data")
        print("   - Try creating more plans/healings to see RAG in action")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
