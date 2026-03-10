#!/usr/bin/env python
"""
🚀 Quick Start Examples
Real-world examples for using the testing framework
"""

import asyncio
import logging
from typing import List
from framework.agent_registry import get_registry, AgentType
from framework.agentFactory import AgentFactory, AgentFactoryError
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestingFramework:
    """High-level testing framework wrapper"""
    
    def __init__(self, model_client):
        """Initialize testing framework"""
        self.factory = AgentFactory(model_client)
        self.registry = get_registry()
        self.registry.set_factory(self.factory)
        logger.info("Testing framework initialized")
    
    def get_agent(self, agent_type: AgentType):
        """Get an agent by type"""
        try:
            agent = self.registry.get_agent_instance(agent_type)
            logger.info(f"Retrieved agent: {agent_type.value}")
            return agent
        except Exception as e:
            logger.error(f"Failed to get agent {agent_type.value}: {str(e)}")
            raise
    
    def list_available_agents(self) -> List[str]:
        """List all available agents"""
        return self.registry.list_agents()
    
    def get_agents_by_category(self, category: str):
        """Get agents for a specific testing category"""
        agents = self.registry.get_agents_by_category(category)
        return {
            agent_type: metadata.name 
            for agent_type, metadata in agents.items()
        }


def example_1_list_agents():
    """Example 1: List all available agents"""
    print("\n" + "="*60)
    print("EXAMPLE 1: List All Available Agents")
    print("="*60 + "\n")
    
    registry = get_registry()
    
    print("Total Agents: {}\n".format(len(registry.get_all_metadata())))
    
    # Group by category
    categories = {}
    for agent_type, metadata in registry.get_all_metadata().items():
        if metadata.category not in categories:
            categories[metadata.category] = []
        categories[metadata.category].append(metadata)
    
    for category, agents in sorted(categories.items()):
        print(f"\n🏷️  {category.upper()}")
        print("-" * 60)
        for agent in agents:
            print(f"  • {agent.name:<30} {agent.description}")


def example_2_get_agent_info():
    """Example 2: Get detailed information about an agent"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Get Agent Detailed Information")
    print("="*60 + "\n")
    
    registry = get_registry()
    
    # Get info for API Contract Testing Agent
    agent_type = AgentType.API_CONTRACT_TESTING
    metadata = registry.get_metadata(agent_type)
    
    print(f"Agent Name: {metadata.name}")
    print(f"Description: {metadata.description}")
    print(f"Category: {metadata.category}")
    print(f"\nCapabilities:")
    for cap in metadata.capabilities:
        print(f"  ✓ {cap}")
    print(f"\nMCP Tools Required:")
    for tool in metadata.mcp_tools:
        print(f"  • {tool}")
    print(f"\nConfiguration:")
    print(f"  Requires Auth: {metadata.requires_auth}")
    print(f"  Min Timeout: {metadata.min_timeout}s")
    print(f"  Max Concurrent: {metadata.max_concurrent}")


def example_3_agents_by_category():
    """Example 3: Get all agents for a specific testing category"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Get Agents by Category")
    print("="*60 + "\n")
    
    registry = get_registry()
    
    # Get all security testing agents
    security_agents = registry.get_agents_by_category("security")
    print(f"🔒 Security Testing Agents ({len(security_agents)}):")
    for agent_type, metadata in security_agents.items():
        print(f"  • {metadata.name}")
        print(f"    └─ {metadata.description}")
    
    # Get all UI testing agents
    ui_agents = registry.get_agents_by_category("ui")
    print(f"\n🎨 UI Testing Agents ({len(ui_agents)}):")
    for agent_type, metadata in ui_agents.items():
        print(f"  • {metadata.name}")
        print(f"    └─ {metadata.description}")
    
    # Get all API testing agents
    api_agents = registry.get_agents_by_category("api")
    print(f"\n🔌 API Testing Agents ({len(api_agents)}):")
    for agent_type, metadata in api_agents.items():
        print(f"  • {metadata.name}")
        print(f"    └─ {metadata.description}")


def example_4_create_agent_with_ollama():
    """Example 4: Create an agent using Ollama (local LLM)"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Create Agent with Ollama")
    print("="*60 + "\n")
    
    try:
        # Create Ollama client
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from autogen_core.models import ModelInfo
        
        client = OpenAIChatCompletionClient(
            model="llama3.2:latest",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model_info=ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                family="unknown"
            )
        )
        
        # Create factory
        factory = AgentFactory(client)
        
        # Create agents
        api_agent = factory.create_api_contract_testing_agent()
        print(f"✓ Created: {api_agent.name}")
        
        ui_agent = factory.create_ui_visual_regression_agent()
        print(f"✓ Created: {ui_agent.name}")
        
        acc_agent = factory.create_accessibility_testing_agent()
        print(f"✓ Created: {acc_agent.name}")
        
        print("\n✅ All agents created successfully!")
        
    except Exception as e:
        print(f"\n❌ Failed to create agents: {str(e)}")
        print("\nMake sure Ollama is running:")
        print("  ollama serve")
        print("\nIn another terminal:")
        print("  ollama run llama3.2")


def example_5_testing_framework_wrapper():
    """Example 5: Use the TestingFramework wrapper"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Using TestingFramework Wrapper")
    print("="*60 + "\n")
    
    try:
        # Create a mock client for demonstration
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from autogen_core.models import ModelInfo
        
        client = OpenAIChatCompletionClient(
            model="llama3.2:latest",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
            model_info=ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                family="unknown"
            )
        )
        
        # Initialize framework
        framework = TestingFramework(client)
        
        # List agents
        print("Available agents:")
        for agent_name in framework.list_available_agents():
            print(f"  • {agent_name}")
        
        # Get agents by category
        print("\nSecurity agents:")
        security_agents = framework.get_agents_by_category("security")
        for agent_type, agent_name in security_agents.items():
            print(f"  • {agent_name} ({agent_type.value})")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("🚀 Testing Framework Quick Start Examples")
    print("="*60)
    
    # Run examples
    example_1_list_agents()
    example_2_get_agent_info()
    example_3_agents_by_category()
    
    # These examples require Ollama to be running
    # Uncomment to test:
    # example_4_create_agent_with_ollama()
    # example_5_testing_framework_wrapper()
    
    print("\n" + "="*60)
    print("✅ Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
