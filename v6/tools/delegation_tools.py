"""
Delegation tools for sub-agent functionality

This module provides tools that enable the main agent to delegate tasks
to specialized sub-agents with restricted tool access.
"""

import json
import sys
import os
from typing import Dict, Any

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from tools.base import BaseTool

# Import delegation components with error handling
try:
    from delegation.manager import SubAgentManager
except ImportError:
    # If imports fail, create a stub to prevent crashes
    class SubAgentManager:
        def __init__(self, *args, **kwargs):
            pass
        def get_agent_types(self):
            return ["file_agent", "search_agent", "system_agent", "analysis_agent"]
        def get_agent_type_info(self, name):
            return {"name": name, "description": "Delegation not available", "allowed_tools": []}
        def execute_delegated_task(self, *args, **kwargs):
            return {"success": False, "result": "Delegation system not available"}
        def get_delegation_statistics(self):
            return {"total_delegations": 0}
        def get_delegation_history(self):
            return []


class SubAgentTool(BaseTool):
    """
    Tool that allows the main agent to delegate tasks to specialized sub-agents.

    This tool wraps the SubAgentManager and provides a standard tool interface
    that can be called by the main agent through the normal tool execution system.
    """

    def __init__(self, agent_instance=None):
        """
        Initialize the SubAgentTool.

        Args:
            agent_instance: Reference to the parent agent instance for event handling
        """
        self.agent_instance = agent_instance
        self._manager = None  # Lazy initialization

    @property
    def manager(self) -> SubAgentManager:
        """Get or create the SubAgentManager instance."""
        if self._manager is None:
            # Get parent event handler if available
            parent_event_handler = None
            if self.agent_instance and hasattr(self.agent_instance, 'event_handler'):
                parent_event_handler = self.agent_instance.event_handler

            self._manager = SubAgentManager(parent_event_handler)
        return self._manager

    @property
    def definition(self) -> Dict[str, Any]:
        """Return the OpenAI tool definition for sub-agent delegation."""
        return {
            "type": "function",
            "function": {
                "name": "delegate_task",
                "description": "Delegate a task to a specialized sub-agent with restricted tool access",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_type": {
                            "type": "string",
                            "enum": ["file_agent", "search_agent", "system_agent", "analysis_agent"],
                            "description": "Type of specialized sub-agent to use for the task"
                        },
                        "task": {
                            "type": "string",
                            "description": "Clear description of the task to delegate to the sub-agent"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context, constraints, or requirements for the task (optional)"
                        }
                    },
                    "required": ["agent_type", "task"]
                }
            }
        }

    def execute(self, input_data: Dict[str, Any]) -> str:
        """
        Execute task delegation to a sub-agent.

        Args:
            input_data: Dictionary containing:
                - agent_type: Type of sub-agent to use
                - task: Task description to delegate
                - context: Optional additional context

        Returns:
            String representation of the delegation result
        """
        try:
            # Validate required parameters
            agent_type = input_data.get('agent_type')
            task = input_data.get('task')
            context = input_data.get('context')

            if not agent_type:
                return "❌ Error: agent_type parameter is required"

            if not task:
                return "❌ Error: task parameter is required"

            # Validate agent type
            available_types = self.manager.get_agent_types()
            if agent_type not in available_types:
                return f"❌ Error: Unknown agent type '{agent_type}'. Available types: {', '.join(available_types)}"

            # Get agent type info for display
            agent_info = self.manager.get_agent_type_info(agent_type)
            if agent_info:
                print(f"\n🤖 Delegating to {agent_type}:")
                print(f"   Description: {agent_info['description']}")
                print(f"   Available tools: {', '.join(agent_info['allowed_tools'])}")
                print(f"   Task: {task}")
                if context:
                    print(f"   Context: {context}")
                print()

            # Execute the delegation
            result = self.manager.execute_delegated_task(agent_type, task, context)

            # Format the result
            if result['success']:
                response_parts = [
                    f"✅ Sub-agent delegation completed successfully",
                    f"Agent type: {result['agent_type']}",
                    f"Duration: {result['duration']:.2f} seconds",
                    f"Messages processed: {result['message_count']}",
                    "",
                    "Result:",
                    result['result']
                ]
                return "\n".join(response_parts)
            else:
                return f"❌ Sub-agent delegation failed:\n{result['result']}"

        except Exception as e:
            return f"❌ Error during delegation: {str(e)}"


class DelegationInfoTool(BaseTool):
    """
    Tool that provides information about available sub-agents and delegation capabilities.

    This tool allows the main agent to query what types of sub-agents are available
    and what tools each type has access to.
    """

    def __init__(self, agent_instance=None):
        """
        Initialize the DelegationInfoTool.

        Args:
            agent_instance: Reference to the parent agent instance
        """
        self.agent_instance = agent_instance
        self._manager = None

    @property
    def manager(self) -> SubAgentManager:
        """Get or create the SubAgentManager instance."""
        if self._manager is None:
            parent_event_handler = None
            if self.agent_instance and hasattr(self.agent_instance, 'event_handler'):
                parent_event_handler = self.agent_instance.event_handler
            self._manager = SubAgentManager(parent_event_handler)
        return self._manager

    @property
    def definition(self) -> Dict[str, Any]:
        """Return the OpenAI tool definition for delegation information queries."""
        return {
            "type": "function",
            "function": {
                "name": "get_delegation_info",
                "description": "Get information about available sub-agents and delegation capabilities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "info_type": {
                            "type": "string",
                            "enum": ["agent_types", "statistics", "history"],
                            "description": "Type of delegation information to retrieve"
                        },
                        "agent_type": {
                            "type": "string",
                            "description": "Specific agent type to get information about (optional)"
                        }
                    },
                    "required": ["info_type"]
                }
            }
        }

    def execute(self, input_data: Dict[str, Any]) -> str:
        """
        Execute delegation information query.

        Args:
            input_data: Dictionary containing:
                - info_type: Type of information requested
                - agent_type: Optional specific agent type to query

        Returns:
            String representation of the requested information
        """
        try:
            info_type = input_data.get('info_type')
            agent_type = input_data.get('agent_type')

            if not info_type:
                return "❌ Error: info_type parameter is required"

            if info_type == "agent_types":
                return self._format_agent_types_info(agent_type)
            elif info_type == "statistics":
                return self._format_statistics_info()
            elif info_type == "history":
                return self._format_history_info()
            else:
                return f"❌ Error: Unknown info_type '{info_type}'"

        except Exception as e:
            return f"❌ Error retrieving delegation info: {str(e)}"

    def _format_agent_types_info(self, specific_type: str = None) -> str:
        """Format information about available agent types."""
        if specific_type:
            # Get info for specific agent type
            info = self.manager.get_agent_type_info(specific_type)
            if not info:
                return f"❌ Agent type '{specific_type}' not found"

            return f"""🤖 Agent Type: {info['name']}

Description: {info['description']}
Tool Set: {info['tool_set_name']}
Max Steps: {info['max_steps']}
Available Tools: {', '.join(info['allowed_tools'])}

This sub-agent can handle tasks that require: {', '.join(info['allowed_tools'])}"""

        else:
            # Get info for all agent types
            agent_types = self.manager.get_agent_types()
            if not agent_types:
                return "No sub-agent types are currently available."

            info_parts = ["🤖 Available Sub-Agent Types:\n"]

            for agent_type in agent_types:
                info = self.manager.get_agent_type_info(agent_type)
                if info:
                    info_parts.append(f"• {info['name']}: {info['description']}")
                    info_parts.append(f"  Tools: {', '.join(info['allowed_tools'])}")
                    info_parts.append("")

            return "\n".join(info_parts)

    def _format_statistics_info(self) -> str:
        """Format delegation statistics information."""
        stats = self.manager.get_delegation_statistics()

        if stats['total_delegations'] == 0:
            return "📊 No delegations have been performed yet."

        info_parts = [
            "📊 Delegation Statistics:",
            "",
            f"Total Delegations: {stats['total_delegations']}",
            f"Successful: {stats['successful_delegations']} ({stats['success_rate']:.1f}%)",
            f"Failed: {stats['failed_delegations']}",
            f"Average Duration: {stats['average_duration']:.2f} seconds",
            f"Total Time: {stats['total_duration']:.2f} seconds",
            ""
        ]

        # Agent type usage
        if stats['agent_type_usage']:
            info_parts.append("Agent Type Usage:")
            for agent_type, count in stats['agent_type_usage'].items():
                info_parts.append(f"  • {agent_type}: {count} times")
            info_parts.append("")

        # Recent delegations
        if stats['recent_delegations']:
            info_parts.append("Recent Delegations:")
            for delegation in stats['recent_delegations'][-3:]:  # Show last 3
                status = "✅" if delegation['success'] else "❌"
                info_parts.append(f"  {status} {delegation['agent_type']}: {delegation['task'][:50]}...")

        return "\n".join(info_parts)

    def _format_history_info(self) -> str:
        """Format delegation history information."""
        history = self.manager.get_delegation_history()

        if not history:
            return "📋 No delegation history available."

        info_parts = [
            f"📋 Delegation History ({len(history)} entries):",
            ""
        ]

        # Show last 5 delegations
        recent_history = history[-5:] if len(history) > 5 else history

        for i, delegation in enumerate(recent_history, 1):
            status = "✅" if delegation['success'] else "❌"
            duration = delegation['duration']
            agent_type = delegation['agent_type']
            task = delegation['task']

            # Truncate long tasks
            if len(task) > 60:
                task = task[:57] + "..."

            info_parts.append(f"{i}. {status} {agent_type} ({duration:.1f}s)")
            info_parts.append(f"   Task: {task}")
            info_parts.append("")

        if len(history) > 5:
            info_parts.append(f"... and {len(history) - 5} more entries")

        return "\n".join(info_parts)