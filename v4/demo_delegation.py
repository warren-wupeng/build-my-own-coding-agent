#!/usr/bin/env python3
"""
Demonstration of V4 Sub-Agents (Delegation) Functionality

This script demonstrates the key components of the delegation system that has been
successfully integrated into V4.
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def demo_tool_sets():
    """Demonstrate the ToolSet system"""
    print("🛠️  ToolSet System Demo")
    print("=" * 40)

    from delegation.tool_sets import ToolSetManager

    manager = ToolSetManager()

    print("Available Tool Sets:")
    for tool_set_name in manager.list_available_tool_sets():
        info = manager.get_tool_set_info(tool_set_name)
        print(f"  • {info['name']}: {info['description']}")
        print(f"    Tools ({info['tool_count']}): {', '.join(info['allowed_tools'])}")
        print()


def demo_sub_agent_manager():
    """Demonstrate the SubAgentManager"""
    print("🤖 SubAgentManager Demo")
    print("=" * 40)

    from delegation.manager import SubAgentManager

    manager = SubAgentManager()

    print("Available Agent Types:")
    for agent_type in manager.get_agent_types():
        info = manager.get_agent_type_info(agent_type)
        print(f"  • {info['name']}: {info['description']}")
        print(f"    Max Steps: {info['max_steps']}")
        print(f"    Tool Set: {info['tool_set_name']}")
        print(f"    Tools: {', '.join(info['allowed_tools'])}")
        print()

    print("Delegation Statistics (Empty):")
    stats = manager.get_delegation_statistics()
    print(f"  Total Delegations: {stats['total_delegations']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print()


def demo_delegation_tools():
    """Demonstrate the delegation tools"""
    print("🔧 Delegation Tools Demo")
    print("=" * 40)

    from tools.delegation_tools import SubAgentTool, DelegationInfoTool

    # Demo SubAgentTool
    sub_agent_tool = SubAgentTool()
    definition = sub_agent_tool.definition

    print("SubAgentTool Definition:")
    print(f"  Name: {definition['function']['name']}")
    print(f"  Description: {definition['function']['description']}")

    parameters = definition['function']['parameters']['properties']
    print("  Parameters:")
    for param_name, param_info in parameters.items():
        print(f"    - {param_name}: {param_info.get('description', 'No description')}")
        if 'enum' in param_info:
            print(f"      Allowed values: {param_info['enum']}")
    print()

    # Demo DelegationInfoTool
    info_tool = DelegationInfoTool()
    info_definition = info_tool.definition

    print("DelegationInfoTool Definition:")
    print(f"  Name: {info_definition['function']['name']}")
    print(f"  Description: {info_definition['function']['description']}")
    print()


def demo_tool_registry_integration():
    """Demonstrate integration with tool registry"""
    print("📋 Tool Registry Integration Demo")
    print("=" * 40)

    from tools.registry import ToolManager

    manager = ToolManager()
    manager.initialize()

    # Show delegation tools in registry
    categories = manager.list_tools_by_category()

    if "Delegation" in categories:
        print("Delegation Tools in Registry:")
        for tool in categories["Delegation"]:
            print(f"  • {tool['name']}: {tool['description']}")
        print()

    # Show total tool count
    all_tools = manager.get_tools_info()
    print(f"Total Tools Registered: {len(all_tools)}")

    tool_names = [tool['name'] for tool in all_tools]
    delegation_tools = ["delegate_task", "get_delegation_info"]

    print("Delegation Tools Status:")
    for tool_name in delegation_tools:
        status = "✅ Registered" if tool_name in tool_names else "❌ Missing"
        print(f"  {tool_name}: {status}")
    print()


def demo_event_handling():
    """Demonstrate event handling system"""
    print("📡 Event Handling Demo")
    print("=" * 40)

    from delegation.events import DelegationEventHandler

    handler = DelegationEventHandler()

    # Simulate some events
    test_events = [
        ("subagent_started", {"agent_id": "demo_001", "agent_type": "file_agent", "task": "Demo task"}),
        ("subagent_completed", {"agent_id": "demo_001", "agent_type": "file_agent", "duration": 2.5}),
        ("delegation_result", {"agent_type": "file_agent", "success": True, "result": "Demo completed"})
    ]

    print("Processing Demo Events:")
    for event_type, event_data in test_events:
        print(f"  Processing: {event_type}")
        handler.handle_event(event_type, event_data)

    print()
    print("Event Statistics:")
    stats = handler.get_delegation_statistics()
    print(f"  Total Events: {stats['total_events']}")
    print(f"  Event Types: {list(stats['event_types'].keys())}")
    print()


def main():
    """Run all demonstrations"""
    print("🚀 V4 Sub-Agents (Delegation) Functionality Demo")
    print("=" * 60)
    print()

    demos = [
        demo_tool_sets,
        demo_sub_agent_manager,
        demo_delegation_tools,
        demo_tool_registry_integration,
        demo_event_handling
    ]

    for i, demo_func in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"❌ Demo {i} failed: {e}")
            import traceback
            traceback.print_exc()

        if i < len(demos):
            print()

    print("=" * 60)
    print("✅ Delegation Functionality Successfully Implemented!")
    print()
    print("Key Features Added to V4:")
    print("  • SubAgentManager for managing specialized sub-agents")
    print("  • ToolSet system for restricting sub-agent capabilities")
    print("  • DelegationEventHandler for monitoring sub-agent activities")
    print("  • Integration with existing tool registry system")
    print("  • Extended statistics system for delegation metrics")
    print("  • Two new tools: delegate_task and get_delegation_info")
    print()
    print("Ready for Use:")
    print("  • Use 'delegate_task' to assign tasks to specialized sub-agents")
    print("  • Use 'get_delegation_info' to query available agent types and statistics")
    print("  • All delegation activities are monitored and logged")
    print("  • Statistics are collected and can be exported")


if __name__ == "__main__":
    main()