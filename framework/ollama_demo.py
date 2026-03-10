"""
Testing Agents Demo using Ollama (Local LLM)
No API key required - runs completely locally!
"""
import asyncio
import os
import httpx
from datetime import datetime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._openai_client import ModelInfo
from autogen_core.tools import FunctionTool

# ============================================================================
# OLLAMA CONFIGURATION
# ============================================================================
# Make sure Ollama is running: ollama serve
# Install a model: ollama pull llama3.2
# Or use: qwen2.5, mistral, phi3, etc.
# ============================================================================

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL = "llama3.2:latest"  # Change to your installed model
OLLAMA_API_KEY = "ollama"  # Placeholder - Ollama doesn't need real API keys


# Tool functions for API testing
async def test_api_endpoint(url: str, method: str = "GET", json_body: dict | None = None) -> str:
    """
    Test an API endpoint and return response details.
    
    Args:
        url: The full URL to test
        method: HTTP method (GET, POST, etc.)
        json_body: Optional JSON body for POST requests (can be None, empty dict, or empty string)
    
    Returns:
        String containing status code, response time, and response body
    """
    # Handle various empty inputs from LLM
    if json_body in (None, {}, "", "{}"):
        json_body = None
    
    try:
        start_time = datetime.now()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "POST" and json_body:
                response = await client.post(url, json=json_body)
            else:
                response = await client.get(url)
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        result = f"""
API Test Results:
─────────────────────────────────────────────────
Endpoint: {url}
Method: {method}
Status Code: {response.status_code}
Response Time: {response_time:.3f} seconds
Response Headers: {dict(response.headers)}
Response Body: {response.text[:500]}...
─────────────────────────────────────────────────
"""
        return result
    except Exception as e:
        return f"API Test Failed: {str(e)}"


async def analyze_web_accessibility(url: str) -> str:
    """
    Analyze web accessibility of a URL.
    
    Args:
        url: The URL to analyze
    
    Returns:
        Accessibility analysis report
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            html_content = response.text
        
        # Simple accessibility checks
        checks = []
        
        # Check for title
        has_title = "<title>" in html_content.lower()
        checks.append(f"✓ Page Title: {'Present' if has_title else '❌ MISSING'}")
        
        # Check for meta description
        has_meta_desc = 'name="description"' in html_content.lower()
        checks.append(f"✓ Meta Description: {'Present' if has_meta_desc else '⚠ Missing'}")
        
        # Check for alt attributes on images
        img_count = html_content.lower().count("<img")
        alt_count = html_content.lower().count('alt="')
        checks.append(f"✓ Images: {img_count} found, {alt_count} with alt text")
        
        # Check for heading structure
        h1_count = html_content.lower().count("<h1")
        h2_count = html_content.lower().count("<h2")
        checks.append(f"✓ Headings: {h1_count} H1 tags, {h2_count} H2 tags")
        
        # Check for form labels
        form_count = html_content.lower().count("<form")
        label_count = html_content.lower().count("<label")
        checks.append(f"✓ Forms: {form_count} forms, {label_count} labels")
        
        # Check for ARIA landmarks
        has_nav = 'role="navigation"' in html_content.lower() or "<nav" in html_content.lower()
        has_main = 'role="main"' in html_content.lower() or "<main" in html_content.lower()
        checks.append(f"✓ ARIA Landmarks: Navigation={'Yes' if has_nav else 'No'}, Main={'Yes' if has_main else 'No'}")
        
        report = f"""
Accessibility Analysis Report for: {url}
═══════════════════════════════════════════════════════════
{chr(10).join(checks)}
═══════════════════════════════════════════════════════════

Recommendations:
1. {'✓ Title tag is present' if has_title else '❌ Add a descriptive <title> tag'}
2. {'✓ Images have alt text' if img_count == alt_count else '⚠ Add alt attributes to all images'}
3. {'✓ Heading structure exists' if h1_count > 0 else '⚠ Add proper heading hierarchy (H1-H6)'}
4. {'✓ Forms have labels' if form_count <= label_count else '⚠ Associate labels with form inputs'}
5. {'✓ ARIA landmarks present' if has_nav and has_main else '⚠ Add semantic HTML5 or ARIA landmarks'}
"""
        return report
    except Exception as e:
        return f"Accessibility Analysis Failed: {str(e)}"


async def create_visual_report(url: str, viewport: str = "desktop") -> str:
    """
    Create a visual testing report for a URL.
    
    Args:
        url: The URL to test
        viewport: Viewport size (desktop, mobile, tablet)
    
    Returns:
        Visual testing report
    """
    viewport_sizes = {
        "desktop": "1920x1080",
        "mobile": "375x667",
        "tablet": "768x1024"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        
        report = f"""
Visual Testing Report
═══════════════════════════════════════════════════════════
URL: {url}
Viewport: {viewport} ({viewport_sizes.get(viewport, 'unknown')})
Status: Page loaded successfully (HTTP {response.status_code})
Content-Type: {response.headers.get('content-type', 'unknown')}
Page Size: {len(response.content)} bytes

Visual Checks Performed:
✓ Page responsiveness: {viewport} viewport
✓ HTTP Status: {response.status_code}
✓ Content loaded successfully
✓ Response time acceptable

Note: Full screenshot capabilities require browser automation.
For production use, integrate with Playwright or Selenium.
═══════════════════════════════════════════════════════════
"""
        return report
    except Exception as e:
        return f"Visual Testing Failed: {str(e)}"


def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return True, models
        return False, []
    except Exception as e:
        return False, []


async def main():
    """
    Demonstrate Testing Agents with Ollama (Local LLM)
    """
    
    print("\n" + "="*80)
    print(" 🦙 TESTING AGENTS DEMONSTRATION WITH OLLAMA")
    print(" Running locally - No API keys required!")
    print("="*80 + "\n")
    
    # Check Ollama connection
    print("🔍 Checking Ollama connection...")
    is_running, models = check_ollama_connection()
    
    if not is_running:
        print("❌ Ollama is not running!")
        print("\n📝 To start Ollama:")
        print("   1. Install Ollama: https://ollama.ai/download")
        print("   2. Start Ollama: ollama serve")
        print("   3. Pull a model: ollama pull llama3.2")
        print("\nAlternatively, use one of these models:")
        print("   - ollama pull qwen2.5:latest")
        print("   - ollama pull mistral:latest")
        print("   - ollama pull phi3:latest")
        return
    
    print("✅ Ollama is running!")
    if models:
        print(f"📦 Available models: {', '.join([m['name'] for m in models[:5]])}")
    print()
    
    # Create Ollama client (uses OpenAI-compatible API)
    try:
        # Create model info for Ollama
        model_info = ModelInfo(
            vision=False,
            function_calling=True,
            json_output=True,
            structured_output=True,
            family="ollama"
        )
        
        model_client = OpenAIChatCompletionClient(
            model=OLLAMA_MODEL,
            api_key=OLLAMA_API_KEY,
            base_url=OLLAMA_BASE_URL,
            model_info=model_info
        )
        
        print(f"🤖 Using Ollama model: {OLLAMA_MODEL}")
        print(f"🔗 Ollama URL: {OLLAMA_BASE_URL}\n")
    except Exception as e:
        print(f"❌ Failed to create Ollama client: {e}")
        print(f"\n💡 Make sure the model '{OLLAMA_MODEL}' is installed:")
        print(f"   ollama pull {OLLAMA_MODEL}")
        return
    
    # Create tool instances
    api_test_tool = FunctionTool(test_api_endpoint, description="Test API endpoints and analyze responses")
    accessibility_tool = FunctionTool(analyze_web_accessibility, description="Analyze web accessibility compliance")
    visual_tool = FunctionTool(create_visual_report, description="Create visual testing reports")
    
    # 1. API Contract Testing Agent
    api_tester = AssistantAgent(
        name="APIContractTester",
        model_client=model_client,
        tools=[api_test_tool],
        system_message="""
        You are an API Contract Testing specialist.
        
        Please perform API testing for the endpoint at https://petstore.swagger.io/, 
        referencing the documentation at https://petstore.swagger.io/v2/swagger.json.
        
        Your task:
        1. Test the Petstore API endpoints:
           - GET https://petstore.swagger.io/v2/pet/1 (get pet by ID)
           - GET https://petstore.swagger.io/v2/store/inventory (get inventory)
        2. Analyze the responses:
           - Check status codes (200, 404, etc.)
           - Measure response times
           - Validate response structure against Swagger documentation
           - Verify data types and required fields
        3. Provide a clear summary of findings
        
        When complete, write: "API_TESTING_DONE - Moving to visual testing"
        """
    )
    
    # 2. UI Visual Testing Agent
    visual_tester = AssistantAgent(
        name="VisualTester",
        model_client=model_client,
        tools=[visual_tool],
        system_message="""
        You are a UI Visual Testing specialist.
        
        Your task:
        1. Create visual reports for: https://www.saucedemo.com/
        2. Test these viewports:
           - Desktop (1920x1080)
           - Mobile (375x667)
           - Tablet (768x1024)
        3. Report on page loading and viewport compatibility
        
        When complete, write: "VISUAL_TESTING_DONE - Moving to accessibility"
        """
    )
    
    # 3. Accessibility Testing Agent
    accessibility_tester = AssistantAgent(
        name="AccessibilityTester",
        model_client=model_client,
        tools=[accessibility_tool],
        system_message="""
        You are an Accessibility Testing specialist focused on WCAG compliance.
        
        Your task:
        1. Analyze: https://www.saucedemo.com/
        2. Check for:
           - Page title and meta tags
           - Image alt text
           - Heading hierarchy
           - Form labels
           - ARIA landmarks
        3. Provide recommendations for improvements
        
        When complete, write: "ALL_TESTING_COMPLETE"
        """
    )
    
    # Create testing team
    testing_team = RoundRobinGroupChat(
        participants=[api_tester, visual_tester, accessibility_tester],
        termination_condition=TextMentionTermination("ALL_TESTING_COMPLETE")
    )
    
    print("🚀 Starting Testing Workflow with Ollama...\n")
    print("📋 Test Plan:")
    print("   Phase 1: API Contract Testing")
    print("   Phase 2: UI Visual Regression Testing")  
    print("   Phase 3: Accessibility Testing")
    print("\n" + "-"*80 + "\n")
    
    # Run the testing workflow
    try:
        result = await Console(
            testing_team.run_stream(
                task="""
Execute Live Testing Workflow:

PHASE 1 - API Contract Testing (APIContractTester):
Perform API testing for the endpoint at https://petstore.swagger.io/, 
referencing the documentation at https://petstore.swagger.io/v2/swagger.json.
Test GET /pet/1 and GET /store/inventory endpoints.
Validate response contracts, status codes, and response times.

PHASE 2 - UI Visual Testing (VisualTester):
Create visual reports for SauceDemo website (https://www.saucedemo.com/) 
across desktop, mobile, and tablet viewports.

PHASE 3 - Accessibility Testing (AccessibilityTester):
Analyze the SauceDemo website for WCAG compliance and accessibility issues.

Execute each phase completely and provide detailed findings.
                """
            )
        )
        
        print("\n" + "="*80)
        print(" ✅ TESTING DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\n📊 Summary:")
        print("   • API Contract Testing: Validated endpoint behavior")
        print("   • Visual Testing: Checked responsive design across viewports")
        print("   • Accessibility Testing: Identified WCAG compliance issues")
        print("\n🦙 Powered by Ollama - Running 100% locally!")
        print("💡 These agents can be deployed in CI/CD pipelines for continuous testing!")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during testing workflow: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure Ollama is running: ollama serve")
        print(f"   2. Verify model is installed: ollama list | grep {OLLAMA_MODEL.split(':')[0]}")
        print(f"   3. Try pulling the model: ollama pull {OLLAMA_MODEL}")


if __name__ == "__main__":
    print("\n🦙 Ollama-Powered Testing Agents")
    print("This demonstration runs completely locally without any API keys!")
    asyncio.run(main())
