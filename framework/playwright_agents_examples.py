"""
🎭 PLAYWRIGHT AGENTS - EXAMPLES
Demonstrates usage of Planner, Generator, and Healer agents

Run this file to see the agents in action!
"""

import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.playwright_agents import (
    PlannerAgent, GeneratorAgent, HealerAgent,
    create_test_plan, generate_test_code, heal_test_failure
)


async def example_1_create_plan():
    """Example 1: Create a test plan"""
    print("\n" + "="*60)
    print("📋 EXAMPLE 1: Creating a Test Plan")
    print("="*60)
    
    # Initialize planner
    planner = PlannerAgent()
    
    # Define requirements
    target = "E-commerce Checkout Flow"
    config = {
        'requirements': [
            "User can add items to cart",
            "User can view cart contents",
            "User can proceed to checkout",
            "User can enter payment information",
            "User can complete order"
        ],
        'user_stories': [
            "As a customer, I want to add products to my cart",
            "As a customer, I want to complete my purchase securely"
        ],
        'acceptance_criteria': [
            "Cart displays correct item count",
            "Payment form validates credit card",
            "Order confirmation is shown"
        ],
        'test_type': 'e2e'
    }
    
    # Create plan
    result = await planner.execute(target, config)
    
    print(f"\n✅ Test plan created: {result['plan_id']}")
    print(f"📊 Total scenarios: {result['summary']['total_scenarios']}")
    print(f"🎯 High priority: {result['summary']['priority_high']}")
    print(f"📈 Coverage: {result['test_plan']['coverage']}%")
    print(f"⏱️  Estimated time: {result['summary']['estimated_time']}")
    
    print("\n📝 Test Scenarios:")
    for scenario in result['test_plan']['test_scenarios'][:3]:  # Show first 3
        print(f"  - {scenario['id']}: {scenario['title']} ({scenario['priority']})")
    
    return result


async def example_2_generate_code(test_plan):
    """Example 2: Generate test code from plan"""
    print("\n" + "="*60)
    print("🔧 EXAMPLE 2: Generating Test Code")
    print("="*60)
    
    # Initialize generator
    generator = GeneratorAgent()
    
    # Generate code
    config = {
        'test_plan': test_plan,
        'framework': 'playwright',
        'language': 'python'
    }
    
    result = await generator.execute('test_generation', config)
    
    print(f"\n✅ Code generated successfully")
    print(f"📦 Files created: {len(result['generated_files'])}")
    print(f"🧪 Test functions: {result['summary']['main_tests']}")
    print(f"📄 Helper files: {result['summary']['helper_files']}")
    print(f"📏 Total lines: {result['summary']['total_lines']}")
    
    print("\n📁 Generated Files:")
    for filename in result['generated_files'].keys():
        print(f"  - {filename}")
    
    print("\n📝 Sample Code (test_main.py):")
    print("-" * 60)
    test_code = result['generated_files']['test_main.py']
    print(test_code[:500] + "...\n")
    
    return result


async def example_3_heal_failure():
    """Example 3: Heal a test failure"""
    print("\n" + "="*60)
    print("🔨 EXAMPLE 3: Healing a Test Failure")
    print("="*60)
    
    # Initialize healer
    healer = HealerAgent()
    
    # Simulate a failure
    test_name = "test_user_login"
    error_info = {
        'message': 'TimeoutError: Locator "button#submit" not found within 30000ms',
        'type': 'TimeoutError',
        'stack_trace': 'at Page.click (page.py:123)'
    }
    
    config = {
        'error_info': error_info,
        'test_code': '''
def test_user_login(page):
    page.goto("/login")
    page.fill("#username", "test@example.com")
    page.fill("#password", "password123")
    page.click("button#submit")  # This times out
    expect(page).to_have_url("/dashboard")
''',
        'logs': [
            'INFO: Navigating to /login',
            'INFO: Filling username',
            'INFO: Filling password',
            'ERROR: Timeout waiting for button#submit'
        ],
        'auto_fix': False
    }
    
    # Analyze and heal
    result = await healer.execute(test_name, config)
    
    print(f"\n✅ Analysis complete")
    print(f"🔍 Failure type: {result['analysis']['failure_type']}")
    print(f"🎯 Root cause: {result['analysis']['root_cause']}")
    print(f"📊 Confidence: {result['analysis']['confidence']}%")
    print(f"📈 Success probability: {result['analysis']['success_probability']}%")
    print(f"⚠️  Flaky test: {result['analysis']['is_flaky']}")
    
    print(f"\n💡 Recommendations:")
    for rec in result['analysis']['recommendations']:
        print(f"  - {rec}")
    
    print(f"\n🔧 Suggested Fixes ({len(result['recommended_fixes'])}):")
    for fix in result['recommended_fixes']:
        print(f"  - {fix['type']}: {fix['description']}")
        print(f"    Confidence: {fix['confidence']}%")
        print(f"    Code: {fix['code_change']}")
    
    return result


async def example_4_complete_workflow():
    """Example 4: Complete workflow (Plan → Generate → Heal)"""
    print("\n" + "="*60)
    print("🔄 EXAMPLE 4: Complete Workflow")
    print("="*60)
    
    # Step 1: Plan
    print("\n📋 Step 1: Planning...")
    plan_result = await create_test_plan(
        target="Login System",
        requirements=[
            "User can login with valid credentials",
            "Invalid credentials show error",
            "Password reset works"
        ],
        test_type='functional'
    )
    print(f"✅ Created {plan_result['summary']['total_scenarios']} test scenarios")
    
    # Step 2: Generate
    print("\n🔧 Step 2: Generating code...")
    gen_result = await generate_test_code(
        test_plan=plan_result['test_plan'],
        framework='playwright',
        language='python'
    )
    print(f"✅ Generated {len(gen_result['generated_files'])} files")
    
    # Step 3: Simulate execution (would be done externally)
    print("\n▶️  Step 3: Execute tests (external)")
    print("   (Tests would be run using pytest or similar)")
    
    # Step 4: Heal failure
    print("\n🔨 Step 4: Healing failures...")
    heal_result = await heal_test_failure(
        test_name="test_login_valid",
        error_info={
            'message': 'Element not found: input#email',
            'type': 'ElementNotFoundError'
        },
        auto_fix=False
    )
    print(f"✅ Analyzed failure: {heal_result['analysis']['failure_type']}")
    print(f"   Suggested {len(heal_result['recommended_fixes'])} fixes")
    
    print("\n🎉 Complete workflow finished!")


async def example_5_healing_statistics():
    """Example 5: Get healing statistics"""
    print("\n" + "="*60)
    print("📊 EXAMPLE 5: Healing Statistics")
    print("="*60)
    
    # Create some healing history
    healer = HealerAgent()
    
    # Heal multiple failures
    failures = [
        {
            'name': 'test_1',
            'error': {'message': 'Timeout error', 'type': 'TimeoutError'}
        },
        {
            'name': 'test_2',
            'error': {'message': 'Element not found', 'type': 'SelectorError'}
        },
        {
            'name': 'test_3',
            'error': {'message': 'Assertion failed', 'type': 'AssertionError'}
        }
    ]
    
    for failure in failures:
        await healer.execute(
            failure['name'],
            {
                'error_info': failure['error'],
                'test_code': '',
                'logs': [],
                'auto_fix': False
            }
        )
    
    # Get statistics
    stats = healer.get_healing_stats()
    
    print(f"\n📊 Statistics:")
    print(f"  Total healings: {stats['total_healings']}")
    print(f"  Success rate: {stats['success_rate']}%")
    print(f"  Average confidence: {stats['average_confidence']}%")
    
    print(f"\n🔝 Most common failures:")
    for failure_type, count in stats['common_failures']:
        print(f"  - {failure_type}: {count} occurrences")


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("🎭 PLAYWRIGHT AGENTS - DEMONSTRATION")
    print("="*80)
    print("\nThree intelligent agents for test automation:")
    print("  📋 Planner  - Creates comprehensive test plans")
    print("  🔧 Generator - Generates executable test code")
    print("  🔨 Healer   - Analyzes and fixes test failures")
    print("="*80)
    
    try:
        # Run examples
        plan = await example_1_create_plan()
        await asyncio.sleep(1)
        
        await example_2_generate_code(plan['test_plan'])
        await asyncio.sleep(1)
        
        await example_3_heal_failure()
        await asyncio.sleep(1)
        
        await example_4_complete_workflow()
        await asyncio.sleep(1)
        
        await example_5_healing_statistics()
        
        print("\n" + "="*80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n💡 Next Steps:")
        print("  1. Run the UI: python framework/playwright_agents_ui.py")
        print("  2. Or use: streamlit run framework/playwright_agents_ui.py")
        print("  3. Explore the interactive dashboard for visual workflow")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
