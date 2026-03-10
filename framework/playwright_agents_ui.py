"""
🎭 PLAYWRIGHT AGENTS UI
Interactive dashboard for Planner, Generator, and Healer agents

Features:
- Create test plans from requirements
- Generate test code from plans
- Analyze and heal test failures
- Workflow visualization
- Export generated code
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.playwright_agents import (
    PlannerAgent, GeneratorAgent, HealerAgent,
    create_test_plan, generate_test_code, heal_test_failure
)

# Page configuration
st.set_page_config(
    page_title="🎭 Playwright Agents Dashboard",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Cards */
    .agent-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    
    /* Badges */
    .badge-planner { 
        background-color: #3b82f6; 
        color: white; 
        padding: 5px 12px; 
        border-radius: 15px; 
        font-size: 0.9em;
        display: inline-block;
        margin: 5px;
    }
    .badge-generator { 
        background-color: #10b981; 
        color: white; 
        padding: 5px 12px; 
        border-radius: 15px; 
        font-size: 0.9em;
        display: inline-block;
        margin: 5px;
    }
    .badge-healer { 
        background-color: #f59e0b; 
        color: white; 
        padding: 5px 12px; 
        border-radius: 15px; 
        font-size: 0.9em;
        display: inline-block;
        margin: 5px;
    }
    
    /* Status indicators */
    .status-success { color: #10b981; font-weight: bold; }
    .status-warning { color: #f59e0b; font-weight: bold; }
    .status-error { color: #ef4444; font-weight: bold; }
    
    /* Workflow visualization */
    .workflow-step {
        background: white;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }
    
    /* Code blocks */
    .code-container {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'planner_agent' not in st.session_state:
    st.session_state.planner_agent = PlannerAgent()
if 'generator_agent' not in st.session_state:
    st.session_state.generator_agent = GeneratorAgent()
if 'healer_agent' not in st.session_state:
    st.session_state.healer_agent = HealerAgent()
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'workflow_history' not in st.session_state:
    st.session_state.workflow_history = []


def main():
    """Main application"""
    
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: white; border-radius: 12px; margin-bottom: 20px;'>
        <h1>🎭 Playwright Agents Dashboard</h1>
        <p style='color: #666; font-size: 1.1em;'>
            Intelligent Test Automation with Planner, Generator & Healer
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.radio(
        "Select Agent",
        ["🏠 Overview", "📋 Planner", "🔧 Generator", "🔨 Healer", "📊 Analytics", "⚙️ Workflow"]
    )
    
    # Display metrics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Quick Stats")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Plans", len(st.session_state.planner_agent.plans_created))
        st.metric("Generated", len(st.session_state.generator_agent.generated_tests))
    with col2:
        st.metric("Healed", len(st.session_state.healer_agent.healing_history))
        healing_rate = st.session_state.healer_agent.success_rate
        st.metric("Success", f"{healing_rate:.0f}%")
    
    # LangChain status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧠 LangChain Status")
    
    planner_lc = "✅" if st.session_state.planner_agent.use_langchain else "❌"
    generator_lc = "✅" if st.session_state.generator_agent.use_langchain else "❌"
    healer_lc = "✅" if st.session_state.healer_agent.use_langchain else "❌"
    
    st.sidebar.markdown(f"""
    - Planner Memory: {planner_lc}
    - Generator Memory: {generator_lc}
    - Healer RAG: {healer_lc}
    """)
    
    # Route to pages
    if page == "🏠 Overview":
        show_overview()
    elif page == "📋 Planner":
        show_planner()
    elif page == "🔧 Generator":
        show_generator()
    elif page == "🔨 Healer":
        show_healer()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "⚙️ Workflow":
        show_workflow()


def show_overview():
    """Show overview page"""
    
    st.markdown("## 🎯 Playwright Agents Overview")
    
    # Agent cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='agent-card'>
            <h3>📋 Planner Agent</h3>
            <span class='badge-planner'>Planning</span>
            <p>Analyzes requirements and creates comprehensive test plans with scenarios, priorities, and coverage analysis.</p>
            <ul>
                <li>Requirement analysis</li>
                <li>Test scenario creation</li>
                <li>Coverage planning</li>
                <li>Risk assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='agent-card'>
            <h3>🔧 Generator Agent</h3>
            <span class='badge-generator'>Generation</span>
            <p>Generates executable test code from test plans supporting multiple frameworks and languages.</p>
            <ul>
                <li>Code generation</li>
                <li>Page object creation</li>
                <li>Test data factories</li>
                <li>Multiple frameworks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='agent-card'>
            <h3>🔨 Healer Agent</h3>
            <span class='badge-healer'>Healing</span>
            <p>Detects and automatically fixes test failures with intelligent analysis and recommendations.</p>
            <ul>
                <li>Failure analysis</li>
                <li>Flaky test detection</li>
                <li>Auto-healing</li>
                <li>Fix suggestions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Workflow visualization
    st.markdown("## 🔄 Complete Testing Workflow")
    
    st.markdown("""
    <div class='workflow-step'>
        <h4>Step 1: 📋 Plan</h4>
        <p>Define requirements → Planner Agent creates comprehensive test plan</p>
    </div>
    <div style='text-align: center; font-size: 2em; margin: 10px;'>⬇️</div>
    <div class='workflow-step'>
        <h4>Step 2: 🔧 Generate</h4>
        <p>Test plan → Generator Agent creates executable test code</p>
    </div>
    <div style='text-align: center; font-size: 2em; margin: 10px;'>⬇️</div>
    <div class='workflow-step'>
        <h4>Step 3: ▶️ Execute</h4>
        <p>Run generated tests → Collect results and failures</p>
    </div>
    <div style='text-align: center; font-size: 2em; margin: 10px;'>⬇️</div>
    <div class='workflow-step'>
        <h4>Step 4: 🔨 Heal</h4>
        <p>Failed tests → Healer Agent analyzes and fixes issues</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("---")
    st.markdown("## ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Create New Plan", use_container_width=True):
            st.session_state.page = "📋 Planner"
            st.rerun()
    with col2:
        if st.button("🔧 Generate Code", use_container_width=True):
            st.session_state.page = "🔧 Generator"
            st.rerun()
    with col3:
        if st.button("🔨 Heal Failure", use_container_width=True):
            st.session_state.page = "🔨 Healer"
            st.rerun()


def show_planner():
    """Show planner agent page"""
    
    st.markdown("## 📋 Planner Agent")
    st.markdown("Create comprehensive test plans from requirements")
    
    # Input form
    with st.form("planner_form"):
        st.markdown("### 📝 Input Requirements")
        
        target = st.text_input(
            "Target Application/Feature",
            placeholder="e.g., E-commerce checkout flow",
            help="What are you planning to test?"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            test_type = st.selectbox(
                "Test Type",
                ["functional", "integration", "e2e", "regression", "smoke", "user_acceptance"]
            )
        with col2:
            priority_focus = st.selectbox(
                "Priority Focus",
                ["balanced", "critical_first", "user_journey"]
            )
        
        st.markdown("#### Requirements")
        requirements_text = st.text_area(
            "Enter requirements (one per line)",
            placeholder="User can login\nUser can add items to cart\nUser can checkout",
            height=150
        )
        
        st.markdown("#### User Stories (Optional)")
        user_stories_text = st.text_area(
            "Enter user stories (one per line)",
            placeholder="As a user, I want to login so that I can access my account",
            height=100
        )
        
        st.markdown("#### Acceptance Criteria (Optional)")
        acceptance_text = st.text_area(
            "Enter acceptance criteria (one per line)",
            placeholder="Login should work with valid credentials\nInvalid credentials should show error",
            height=100
        )
        
        submitted = st.form_submit_button("🚀 Create Test Plan", use_container_width=True)
        
        if submitted:
            if not target or not requirements_text:
                st.error("⚠️ Please provide target and at least one requirement")
            else:
                with st.spinner("🔄 Creating test plan..."):
                    # Parse inputs
                    requirements = [r.strip() for r in requirements_text.split('\n') if r.strip()]
                    user_stories = [u.strip() for u in user_stories_text.split('\n') if u.strip()]
                    acceptance = [a.strip() for a in acceptance_text.split('\n') if a.strip()]
                    
                    # Create plan
                    config = {
                        'requirements': requirements,
                        'user_stories': user_stories,
                        'acceptance_criteria': acceptance,
                        'test_type': test_type
                    }
                    
                    result = asyncio.run(st.session_state.planner_agent.execute(target, config))
                    st.session_state.current_plan = result
                    st.session_state.workflow_history.append({
                        'step': 'plan',
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    st.success("✅ Test plan created successfully!")
                    st.rerun()
    
    # Display current plan
    if st.session_state.current_plan:
        st.markdown("---")
        st.markdown("### 📊 Generated Test Plan")
        
        plan = st.session_state.current_plan
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Scenarios", plan['summary']['total_scenarios'])
        with col2:
            st.metric("High Priority", plan['summary']['priority_high'])
        with col3:
            st.metric("Coverage", f"{plan['test_plan']['coverage']}%")
        with col4:
            st.metric("Est. Time", plan['summary']['estimated_time'])
        
        # LangChain insights
        if 'langchain_insights' in plan and plan['langchain_insights']['vectordb_enabled']:
            st.markdown("#### 🧠 LangChain Insights")
            insights = plan['langchain_insights']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Similar Plans Found", insights['similar_plans_found'])
            with col2:
                st.metric("Vector DB", "✅ Enabled" if insights['vectordb_enabled'] else "❌ Disabled")
            with col3:
                st.metric("Memory", "✅ Enabled" if insights['memory_enabled'] else "❌ Disabled")
            
            if insights.get('similar_plans'):
                st.markdown("**Similar Past Plans:**")
                for similar in insights['similar_plans'][:3]:
                    st.info(f"📋 {similar['metadata']['target']} - Similarity: {similar['similarity_score']:.2f}")
        
        # Test scenarios
        st.markdown("#### 📝 Test Scenarios")
        for scenario in plan['test_plan']['test_scenarios']:
            with st.expander(f"**{scenario['id']}**: {scenario['title']} ({scenario['priority']})", expanded=False):
                st.markdown(f"**Description:** {scenario['description']}")
                st.markdown(f"**Priority:** {scenario['priority']}")
                st.markdown(f"**Type:** {scenario['test_type']}")
                
                st.markdown("**Preconditions:**")
                for pre in scenario['preconditions']:
                    st.markdown(f"- {pre}")
                
                st.markdown("**Test Steps:**")
                for i, step in enumerate(scenario['steps'], 1):
                    st.markdown(f"{i}. {step}")
                
                st.markdown(f"**Expected Result:** {scenario['expected_result']}")
                st.markdown(f"**Duration:** {scenario['estimated_duration']}")
        
        # Export plan
        col1, col2 = st.columns(2)
        with col1:
            plan_json = json.dumps(plan, indent=2)
            st.download_button(
                "📥 Download Plan (JSON)",
                plan_json,
                file_name=f"test_plan_{plan['plan_id']}.json",
                mime="application/json",
                use_container_width=True
            )
        with col2:
            if st.button("➡️ Generate Code from Plan", use_container_width=True):
                st.session_state.page = "🔧 Generator"
                st.rerun()
    
    # List previous plans
    if st.session_state.planner_agent.plans_created:
        st.markdown("---")
        st.markdown("### 📚 Previous Plans")
        
        plans = st.session_state.planner_agent.list_plans()
        for p in plans:
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.markdown(f"**{p['target']}**")
            with col2:
                st.markdown(f"Scenarios: {p['scenarios']}")
            with col3:
                st.markdown(f"{p['status']}")
            with col4:
                if st.button("Load", key=f"load_{p['plan_id']}"):
                    st.session_state.current_plan = st.session_state.planner_agent.get_plan(p['plan_id'])
                    st.rerun()


def show_generator():
    """Show generator agent page"""
    
    st.markdown("## 🔧 Generator Agent")
    st.markdown("Generate executable test code from test plans")
    
    if not st.session_state.current_plan:
        st.warning("⚠️ No test plan available. Please create a plan first.")
        if st.button("📋 Go to Planner"):
            st.session_state.page = "📋 Planner"
            st.rerun()
        return
    
    # Configuration
    with st.form("generator_form"):
        st.markdown("### ⚙️ Code Generation Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            framework = st.selectbox(
                "Framework",
                ["playwright", "selenium", "cypress", "puppeteer"],
                help="Select test framework"
            )
        with col2:
            language = st.selectbox(
                "Language",
                ["python", "typescript", "javascript", "java"],
                help="Select programming language"
            )
        
        col3, col4 = st.columns(2)
        with col3:
            include_page_objects = st.checkbox("Generate Page Objects", value=True)
        with col4:
            include_fixtures = st.checkbox("Generate Test Fixtures", value=True)
        
        submitted = st.form_submit_button("🚀 Generate Code", use_container_width=True)
        
        if submitted:
            with st.spinner("🔄 Generating test code..."):
                config = {
                    'test_plan': st.session_state.current_plan['test_plan'],
                    'framework': framework,
                    'language': language
                }
                
                result = asyncio.run(st.session_state.generator_agent.execute('code_generation', config))
                st.session_state.generated_code = result
                st.session_state.workflow_history.append({
                    'step': 'generate',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
                st.success("✅ Test code generated successfully!")
                st.rerun()
    
    # Display generated code
    if st.session_state.generated_code:
        st.markdown("---")
        st.markdown("### 📦 Generated Files")
        
        gen = st.session_state.generated_code
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Test Files", gen['summary']['main_tests'])
        with col2:
            st.metric("Helper Files", gen['summary']['helper_files'])
        with col3:
            st.metric("Total Lines", gen['summary']['total_lines'])
        
        # Display each file
        for filename, code in gen['generated_files'].items():
            with st.expander(f"📄 {filename}", expanded=(filename == 'test_main.py')):
                st.code(code, language=gen['language'])
                
                # Download button for each file
                st.download_button(
                    f"📥 Download {filename}",
                    code,
                    file_name=filename,
                    mime="text/plain",
                    key=f"download_{filename}"
                )
        
        # Download all as ZIP (simulated)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📦 Download All Files (ZIP)", use_container_width=True):
                st.info("ZIP download would be implemented here")
        with col2:
            st.markdown("**Framework:** " + gen['framework'])
            st.markdown("**Language:** " + gen['language'])


def show_healer():
    """Show healer agent page"""
    
    st.markdown("## 🔨 Healer Agent")
    st.markdown("Analyze and fix test failures automatically")
    
    # Input form
    with st.form("healer_form"):
        st.markdown("### 🔍 Test Failure Information")
        
        test_name = st.text_input(
            "Failed Test Name",
            placeholder="test_user_login",
            help="Name of the failed test"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            error_type = st.selectbox(
                "Error Type",
                ["TimeoutError", "ElementNotFound", "AssertionError", "NetworkError", "StaleElement", "Other"]
            )
        with col2:
            auto_fix = st.checkbox("Enable Auto-Fix", value=False, help="Automatically apply high-confidence fixes")
        
        error_message = st.text_area(
            "Error Message",
            placeholder="TimeoutError: Locator 'button#submit' not found within timeout",
            height=100
        )
        
        test_code = st.text_area(
            "Test Code (Optional)",
            placeholder="def test_example(page):\n    page.goto('/')\n    page.click('#submit')",
            height=150
        )
        
        logs = st.text_area(
            "Logs (Optional)",
            placeholder="Enter test execution logs",
            height=100
        )
        
        submitted = st.form_submit_button("🔍 Analyze Failure", use_container_width=True)
        
        if submitted:
            if not test_name or not error_message:
                st.error("⚠️ Please provide test name and error message")
            else:
                with st.spinner("🔄 Analyzing failure..."):
                    error_info = {
                        'message': error_message,
                        'type': error_type,
                        'stack_trace': ''
                    }
                    
                    config = {
                        'error_info': error_info,
                        'test_code': test_code,
                        'logs': logs.split('\n') if logs else [],
                        'auto_fix': auto_fix
                    }
                    
                    result = asyncio.run(st.session_state.healer_agent.execute(test_name, config))
                    
                    st.session_state.workflow_history.append({
                        'step': 'heal',
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    st.success("✅ Analysis complete!")
                    
                    # Display results
                    st.markdown("---")
                    st.markdown("### 🔍 Analysis Results")
                    
                    analysis = result['analysis']
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Confidence", f"{analysis['confidence']}%")
                    with col2:
                        st.metric("Success Probability", f"{analysis['success_probability']}%")
                    with col3:
                        st.metric("Fixes Suggested", len(result['recommended_fixes']))
                    with col4:
                        flaky_status = "Yes" if analysis['is_flaky'] else "No"
                        st.metric("Flaky Test", flaky_status)
                    
                    # LangChain RAG insights
                    if 'langchain_insights' in result and result['langchain_insights']['vectordb_enabled']:
                        st.markdown("#### 🧠 LangChain RAG Insights")
                        insights = result['langchain_insights']
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Similar Failures", insights['similar_failures_found'])
                        with col2:
                            st.metric("RAG Suggestions", insights['rag_suggestions'])
                        with col3:
                            st.metric("Vector DB", "✅" if insights['vectordb_enabled'] else "❌")
                        with col4:
                            st.metric("Memory", "✅" if insights['memory_enabled'] else "❌")
                        
                        if insights.get('past_fixes_referenced'):
                            st.markdown("**Similar Past Failures:**")
                            for past in insights['past_fixes_referenced'][:3]:
                                st.info(f"🔧 {past.get('root_cause', 'Unknown')} - Test: {past.get('test_id', 'N/A')}")
                    
                    # Analysis details
                    st.markdown("#### 📊 Failure Analysis")
                    st.markdown(f"**Type:** {analysis['failure_type']}")
                    st.markdown(f"**Root Cause:** {analysis['root_cause']}")
                    
                    if analysis['is_flaky']:
                        st.warning("⚠️ This appears to be a flaky test that may pass/fail intermittently")
                    
                    # Recommendations
                    st.markdown("#### 💡 Recommendations")
                    for rec in analysis['recommendations']:
                        st.markdown(f"- {rec}")
                    
                    # Fixes
                    st.markdown("#### 🔧 Suggested Fixes")
                    for fix in result['recommended_fixes']:
                        with st.expander(f"**{fix['type']}** (Confidence: {fix['confidence']}%)", expanded=True):
                            st.markdown(f"**Description:** {fix['description']}")
                            st.code(fix['code_change'], language='python')
                    
                    # Applied fixes
                    if result['applied_fixes']:
                        st.markdown("#### ✅ Applied Fixes")
                        for fix in result['applied_fixes']:
                            st.success(f"✓ {fix['description']}")
    
    # Healing statistics
    if st.session_state.healer_agent.healing_history:
        st.markdown("---")
        st.markdown("### 📊 Healing Statistics")
        
        stats = st.session_state.healer_agent.get_healing_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Healings", stats['total_healings'])
        with col2:
            st.metric("Success Rate", f"{stats['success_rate']}%")
        with col3:
            st.metric("Avg Confidence", f"{stats['average_confidence']}%")
        
        st.markdown("#### Most Common Failures")
        for failure_type, count in stats['common_failures']:
            st.markdown(f"- **{failure_type}**: {count} occurrences")


def show_analytics():
    """Show analytics page"""
    
    st.markdown("## 📊 Analytics & Insights")
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>{}</h3>
            <p>Test Plans</p>
        </div>
        """.format(len(st.session_state.planner_agent.plans_created)), unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>{}</h3>
            <p>Generated Tests</p>
        </div>
        """.format(len(st.session_state.generator_agent.generated_tests)), unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>{}</h3>
            <p>Healed Failures</p>
        </div>
        """.format(len(st.session_state.healer_agent.healing_history)), unsafe_allow_html=True)
    with col4:
        success_rate = st.session_state.healer_agent.success_rate
        st.markdown("""
        <div class='metric-card'>
            <h3>{:.0f}%</h3>
            <p>Healing Success</p>
        </div>
        """.format(success_rate), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Workflow history
    if st.session_state.workflow_history:
        st.markdown("### 🔄 Workflow History")
        
        for i, item in enumerate(reversed(st.session_state.workflow_history[-10:]), 1):
            step_emoji = {
                'plan': '📋',
                'generate': '🔧',
                'heal': '🔨'
            }
            
            with st.expander(f"{step_emoji.get(item['step'], '📍')} {item['step'].title()} - {item['timestamp']}", expanded=False):
                st.json(item['result'])
    else:
        st.info("No workflow history yet. Start by creating a test plan!")


def show_workflow():
    """Show end-to-end workflow page"""
    
    st.markdown("## ⚙️ Complete Workflow")
    st.markdown("Execute the full testing workflow: Plan → Generate → Execute → Heal")
    
    st.markdown("""
    <div class='agent-card'>
        <h3>🔄 Automated Testing Workflow</h3>
        <p>This workflow automates the complete testing lifecycle:</p>
        <ol>
            <li><strong>Plan:</strong> Analyze requirements and create test scenarios</li>
            <li><strong>Generate:</strong> Create executable test code</li>
            <li><strong>Execute:</strong> Run tests (external)</li>
            <li><strong>Heal:</strong> Analyze failures and apply fixes</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Workflow execution
    st.markdown("### 🚀 Execute Workflow")
    
    with st.form("workflow_form"):
        target = st.text_input("Target Application", placeholder="My Application")
        requirements = st.text_area("Requirements (one per line)", height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            framework = st.selectbox("Framework", ["playwright", "selenium"])
        with col2:
            language = st.selectbox("Language", ["python", "typescript"])
        
        execute_workflow = st.form_submit_button("🚀 Execute Complete Workflow", use_container_width=True)
        
        if execute_workflow:
            if not target or not requirements:
                st.error("Please provide target and requirements")
            else:
                # Step 1: Plan
                with st.spinner("📋 Step 1: Creating test plan..."):
                    reqs = [r.strip() for r in requirements.split('\n') if r.strip()]
                    plan_result = asyncio.run(create_test_plan(target, reqs))
                    st.success(f"✅ Created {len(plan_result['test_plan']['test_scenarios'])} test scenarios")
                
                # Step 2: Generate
                with st.spinner("🔧 Step 2: Generating test code..."):
                    gen_result = asyncio.run(generate_test_code(
                        plan_result['test_plan'],
                        framework=framework,
                        language=language
                    ))
                    st.success(f"✅ Generated {len(gen_result['generated_files'])} test files")
                
                # Step 3: Placeholder for execution
                st.info("ℹ️ Step 3: Execute tests using your test runner (pytest, npm test, etc.)")
                
                # Step 4: Placeholder for healing
                st.info("ℹ️ Step 4: If tests fail, use the Healer agent to analyze and fix issues")
                
                st.balloons()
                st.success("🎉 Workflow completed successfully!")


# Run the app
if __name__ == "__main__":
    main()
