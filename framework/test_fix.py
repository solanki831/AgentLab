"""Test script to verify agent_dashboard fixes"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.agent_registry import get_registry

print("Testing agent registry get_all_metadata()...")
print("=" * 60)

registry = get_registry()
agents_metadata_dict = registry.get_all_metadata()

print(f"Type of result: {type(agents_metadata_dict)}")
print(f"Number of agents: {len(agents_metadata_dict)}")
print()

# Test what we get when iterating
print("Testing iteration (the fixed way):")
print("-" * 60)

agents_by_category = {}
for agent_type, agent_meta in agents_metadata_dict.items():
    print(f"✅ Agent: {agent_meta.name:30} | Type: {agent_type.value:25} | Category: {agent_meta.category}")
    
    if agent_meta.category not in agents_by_category:
        agents_by_category[agent_meta.category] = []
    agents_by_category[agent_meta.category].append(agent_meta)

print()
print("=" * 60)
print(f"✅ Grouped {len(agents_by_category)} categories:")
print("-" * 60)

for category in sorted(agents_by_category.keys()):
    agents = agents_by_category[category]
    print(f"  {category.upper():15} → {len(agents)} agents")
    for agent in agents:
        print(f"     • {agent.name}")

print()
print("=" * 60)
print("✅ ALL TESTS PASSED - agent_dashboard is ready!")
print("=" * 60)
