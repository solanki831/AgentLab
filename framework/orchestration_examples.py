"""
🎯 Multi-Agent Orchestration - Quick Start Example

This script demonstrates how to use the multi-agent orchestration system
to run a complete test suite with UI tests, API tests, validation, healing, and reporting.
"""

import asyncio
import json
from datetime import datetime
from framework.orchestrator_agent import OrchestratorAgent


async def example_1_simple_ui_test():
    """Example 1: Simple UI test with single agent"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple UI Test")
    print("="*80)
    
    orchestrator = OrchestratorAgent()
    
    test_suite = {
        "tests": [
            {
                "type": "ui",
                "target": "https://example.com",
                "config": {
                    "steps": [
                        {"action": "navigate", "url": "https://example.com"},
                        {"action": "wait", "selector": "h1"},
                        {"action": "assert_visible", "selector": "h1"},
                        {"action": "screenshot"}
                    ]
                },
                "priority": 1
            }
        ]
    }
    
    orchestrator.create_test_plan(test_suite)
    results = await orchestrator.execute_test_plan(parallel=False)
    
    print(f"\n✅ Results:")
    print(f"   Total: {results['total_tasks']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    
    return results


async def example_2_api_with_validation():
    """Example 2: API test with response validation"""
    print("\n" + "="*80)
    print("EXAMPLE 2: API Test with Validation")
    print("="*80)
    
    orchestrator = OrchestratorAgent()
    
    test_suite = {
        "tests": [
            {
                "type": "api",
                "target": "https://api.example.com/users/123",
                "config": {
                    "method": "GET",
                    "headers": {"Accept": "application/json"},
                    "assertions": [
                        {"type": "status_code", "expected": 200},
                        {"type": "response_time", "max": 2.0},
                        {"type": "json_path", "path": "data.id", "expected": 123}
                    ]
                },
                "priority": 1
            },
            {
                "type": "validation",
                "target": "user_data",
                "config": {
                    "data": {"id": 123, "name": "John Doe", "email": "john@example.com"},
                    "validations": [
                        {"type": "not_null", "field": "id"},
                        {"type": "type", "field": "name", "expected_type": "string"},
                        {"type": "regex", "field": "email", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"}
                    ]
                },
                "priority": 2,
                "dependencies": ["test_0"]  # Runs after API test
            }
        ]
    }
    
    orchestrator.create_test_plan(test_suite)
    results = await orchestrator.execute_test_plan(parallel=True)
    
    print(f"\n✅ Results:")
    print(f"   Total: {results['total_tasks']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    
    return results


async def example_3_full_suite_with_healing():
    """Example 3: Full test suite with auto-healing and reporting"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Full Test Suite with Healing & Reporting")
    print("="*80)
    
    orchestrator = OrchestratorAgent()
    
    test_suite = {
        "tests": [
            # UI Test
            {
                "type": "ui",
                "target": "https://example.com/login",
                "config": {
                    "steps": [
                        {"action": "navigate", "url": "https://example.com/login"},
                        {"action": "fill", "selector": "#username", "value": "testuser"},
                        {"action": "fill", "selector": "#password", "value": "password123"},
                        {"action": "click", "selector": "#login-button"},
                        {"action": "wait", "selector": ".dashboard"},
                        {"action": "assert_visible", "selector": ".user-profile"}
                    ]
                },
                "priority": 1,
                "max_retries": 3  # Enable auto-healing
            },
            
            # API Health Check
            {
                "type": "api",
                "target": "https://api.example.com/health",
                "config": {
                    "method": "GET",
                    "assertions": [
                        {"type": "status_code", "expected": 200},
                        {"type": "response_time", "max": 1.0}
                    ]
                },
                "priority": 1
            },
            
            # API User Data
            {
                "type": "api",
                "target": "https://api.example.com/users/current",
                "config": {
                    "method": "GET",
                    "headers": {"Authorization": "Bearer test_token"},
                    "assertions": [
                        {"type": "status_code", "expected": 200},
                        {"type": "json_path", "path": "data.username", "expected": "testuser"}
                    ]
                },
                "priority": 2,
                "dependencies": ["test_0"]  # After login
            },
            
            # Validate User Data
            {
                "type": "validation",
                "target": "user_profile",
                "config": {
                    "data": {
                        "id": 123,
                        "username": "testuser",
                        "email": "test@example.com",
                        "role": "user",
                        "active": True
                    },
                    "validations": [
                        {"type": "schema", "schema": {
                            "required": ["id", "username", "email"],
                            "properties": {
                                "id": {"type": "number"},
                                "username": {"type": "string"},
                                "email": {"type": "string"},
                                "active": {"type": "boolean"}
                            }
                        }},
                        {"type": "regex", "field": "email", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
                        {"type": "range", "field": "id", "min": 1, "max": 999999}
                    ]
                },
                "priority": 2,
                "dependencies": ["test_2"]  # After user API call
            }
        ]
    }
    
    orchestrator.create_test_plan(test_suite)
    print(f"\n📋 Created plan with {len(orchestrator.execution_plan)} tasks")
    
    # Show execution order
    print("\n📊 Execution Order:")
    for i, task in enumerate(orchestrator.execution_plan, 1):
        deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
        print(f"   {i}. {task.task_type.upper()}: {task.target}{deps}")
    
    # Execute
    print("\n🚀 Executing test plan...")
    results = await orchestrator.execute_test_plan(parallel=True)
    
    # Display results
    print(f"\n{'='*80}")
    print("📊 EXECUTION RESULTS")
    print(f"{'='*80}")
    print(f"   Total Tasks: {results['total_tasks']}")
    print(f"   ✅ Passed: {results['passed']}")
    print(f"   ❌ Failed: {results['failed']}")
    print(f"   🔧 Healed: {results['healed']}")
    
    # Show individual task results
    print(f"\n📝 Task Details:")
    for task in results['tasks']:
        status_icon = "✅" if task['status'] == 'completed' else "❌"
        print(f"   {status_icon} {task['task_id']}: {task['type']} - {task['status']}")
        if task.get('result', {}).get('execution_time'):
            print(f"      ⏱️  Execution time: {task['result']['execution_time']:.3f}s")
    
    # Show report if available
    if 'report' in results:
        report = results['report']
        print(f"\n📈 Report Summary:")
        if 'metrics' in report:
            metrics = report['metrics']
            print(f"   Pass Rate: {metrics.get('pass_rate', 0):.1f}%")
            print(f"   Avg Execution Time: {metrics.get('avg_execution_time', 0):.3f}s")
    
    return results


async def example_4_individual_agents():
    """Example 4: Using individual agents directly (without orchestrator)"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Using Individual Agents")
    print("="*80)
    
    # UI Agent
    print("\n1️⃣ UI Test Agent:")
    from framework.ui_test_agent import UITestAgent
    ui_agent = UITestAgent()
    
    ui_result = await ui_agent.execute(
        "https://example.com",
        {
            "steps": [
                {"action": "navigate", "url": "https://example.com"},
                {"action": "screenshot"}
            ]
        }
    )
    print(f"   {'✅' if ui_result['success'] else '❌'} {ui_result['agent']}: {ui_result['target']}")
    
    # API Agent
    print("\n2️⃣ API Test Agent:")
    from framework.api_test_agent import APITestAgent
    api_agent = APITestAgent()
    
    api_result = await api_agent.execute(
        "https://api.example.com/status",
        {
            "method": "GET",
            "assertions": [{"type": "status_code", "expected": 200}]
        }
    )
    print(f"   {'✅' if api_result['success'] else '❌'} {api_result['agent']}: {api_result['method']} {api_result['target']}")
    print(f"   Status: {api_result['status_code']}, Response Time: {api_result['response_time']:.3f}s")
    
    # Validation Agent
    print("\n3️⃣ Validation Agent:")
    from framework.validation_agent import ValidationAgent
    validation_agent = ValidationAgent()
    
    validation_result = await validation_agent.execute(
        "user_data",
        {
            "data": {"id": 123, "name": "Test User"},
            "validations": [
                {"type": "not_null", "field": "id"},
                {"type": "type", "field": "name", "expected_type": "string"}
            ]
        }
    )
    print(f"   {'✅' if validation_result['success'] else '❌'} {validation_result['agent']}: {validation_result['passed']}/{validation_result['total_validations']} passed")
    
    # Healing Agent
    print("\n4️⃣ Healing Agent:")
    from framework.healing_agent import HealingAgent
    healing_agent = HealingAgent()
    
    healing_result = await healing_agent.execute(
        "failed_ui_test",
        {
            "failed_test": {"name": "login_test", "type": "ui"},
            "error_info": "Element not found: #login-button (timeout)",
            "test_config": {"timeout": 5000}
        }
    )
    print(f"   {'✅' if healing_result['success'] else '❌'} {healing_result['agent']}: {healing_result['analysis']['failure_type']}")
    print(f"   Strategy: {healing_result['healing_strategy']['name']}")
    
    # Report Agent
    print("\n5️⃣ Report Agent:")
    from framework.report_agent import ReportAgent
    report_agent = ReportAgent()
    
    report_result = await report_agent.execute(
        "test_summary",
        {
            "results": [ui_result, api_result, validation_result],
            "report_type": "summary"
        }
    )
    print(f"   {'✅' if report_result['success'] else '❌'} {report_result['agent']}")
    print(f"   Summary: {report_result['report']['summary']}")
    
    return {
        "ui": ui_result,
        "api": api_result,
        "validation": validation_result,
        "healing": healing_result,
        "report": report_result
    }


async def example_5_performance_testing():
    """Example 5: API Performance Testing"""
    print("\n" + "="*80)
    print("EXAMPLE 5: API Performance Testing")
    print("="*80)
    
    from framework.api_test_agent import APITestAgent
    api_agent = APITestAgent()
    
    print("\n⚡ Running performance test with 10 concurrent requests...")
    
    perf_result = await api_agent.performance_test(
        "https://api.example.com/products",
        num_requests=10,
        config={"method": "GET"}
    )
    
    print(f"\n📊 Performance Results:")
    print(f"   Total Requests: {perf_result['total_requests']}")
    print(f"   ✅ Successful: {perf_result['successful']}")
    print(f"   ❌ Failed: {perf_result['failed']}")
    print(f"   ⏱️  Avg Response Time: {perf_result['avg_response_time']:.3f}s")
    print(f"   🚀 Requests/Second: {perf_result['requests_per_second']:.2f}")
    print(f"   ⏳ Total Time: {perf_result['total_time']:.3f}s")
    
    return perf_result


async def example_6_batch_validation():
    """Example 6: Batch Data Validation"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Batch Data Validation")
    print("="*80)
    
    from framework.validation_agent import ValidationAgent
    validation_agent = ValidationAgent()
    
    # Validate multiple user records
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 30},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35},
    ]
    
    validation_rules = [
        {"type": "not_null", "field": "id"},
        {"type": "type", "field": "name", "expected_type": "string"},
        {"type": "regex", "field": "email", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
        {"type": "range", "field": "age", "min": 18, "max": 120}
    ]
    
    print(f"\n🔍 Validating {len(users)} user records...")
    
    batch_result = await validation_agent.batch_validate(users, validation_rules)
    
    print(f"\n📊 Batch Validation Results:")
    print(f"   Total Items: {batch_result['total_items']}")
    print(f"   ✅ Items Passed: {batch_result['items_passed']}")
    print(f"   ❌ Items Failed: {batch_result['total_items'] - batch_result['items_passed']}")
    print(f"   Total Validations: {batch_result['total_validations']}")
    print(f"   Passed: {batch_result['total_passed']}")
    print(f"   Failed: {batch_result['total_failed']}")
    
    return batch_result


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("🎯 MULTI-AGENT ORCHESTRATION - QUICK START EXAMPLES")
    print("="*80)
    print("\nThis demonstrates the complete multi-agent QA system with:")
    print("  • Orchestrator Agent (Test Lead)")
    print("  • UI Test Agent (Automation Engineer)")
    print("  • API Test Agent (API Tester)")
    print("  • Healing Agent (Flaky Test Fixer)")
    print("  • Validation Agent (Reviewer)")
    print("  • Report Agent (Analyst)")
    
    try:
        # Run examples
        await example_1_simple_ui_test()
        await example_2_api_with_validation()
        await example_3_full_suite_with_healing()
        await example_4_individual_agents()
        await example_5_performance_testing()
        await example_6_batch_validation()
        
        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Review the examples above")
        print("  2. Read docs/multi-agent-orchestration-guide.md")
        print("  3. Try creating your own test suites")
        print("  4. Integrate with the Agent Dashboard")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
