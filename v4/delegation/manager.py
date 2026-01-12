"""
Sub-agent manager for delegation functionality

This module provides the core SubAgentManager class that handles the lifecycle
of sub-agents, including creation, configuration, execution, and monitoring.
"""

import uuid
import time
import sys
import os
from typing import Dict, Any, Optional, List

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.agent_core import AgentCore
from execution.tool_executor import ToolExecutor
from llm.client import LLMClient
from monitoring.statistics import StatisticsCollector
from delegation.tool_sets import ToolSetManager, ToolSet
from delegation.events import DelegationEventHandler


class SubAgentManager:
    """
    Manages the lifecycle and execution of sub-agents for task delegation.

    The SubAgentManager handles:
    - Registration and configuration of sub-agent types
    - Creation of sub-agents with restricted tool access
    - Execution of delegated tasks
    - Monitoring and event handling for sub-agents
    - Statistics collection for delegation activities
    """

    def __init__(self, parent_event_handler: Optional[object] = None):
        """
        Initialize the SubAgentManager.

        Args:
            parent_event_handler: Optional parent event handler for event bubbling
        """
        self.tool_set_manager = ToolSetManager()
        self.agent_types: Dict[str, Dict[str, Any]] = {}
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.delegation_history: List[Dict[str, Any]] = []

        # Event handling
        self.event_handler = DelegationEventHandler(parent_event_handler)

        # Initialize default agent types
        self._initialize_default_agent_types()

    def _initialize_default_agent_types(self):
        """Set up default sub-agent types based on available tool sets."""
        # File Operations Agent
        self.register_agent_type(
            name="file_agent",
            tool_set_name="file_operations",
            description="Specialized for file manipulation and management",
            max_steps=20  # Shorter limit for focused tasks
        )

        # Search and Analysis Agent
        self.register_agent_type(
            name="search_agent",
            tool_set_name="search_and_find",
            description="Specialized for searching files and content",
            max_steps=15
        )

        # System Operations Agent
        self.register_agent_type(
            name="system_agent",
            tool_set_name="system_operations",
            description="Specialized for system commands and environment queries",
            max_steps=25
        )

        # Analysis Agent (read-only)
        self.register_agent_type(
            name="analysis_agent",
            tool_set_name="analysis_only",
            description="Read-only analysis and exploration agent",
            max_steps=30
        )

    def register_agent_type(self, name: str, tool_set_name: str, description: str, max_steps: int = 25):
        """
        Register a new sub-agent type.

        Args:
            name: Unique name for the agent type
            tool_set_name: Name of the tool set this agent type should use
            description: Human-readable description of the agent type
            max_steps: Maximum number of conversation steps for this agent type

        Raises:
            ValueError: If agent type already exists or tool set not found
        """
        if name in self.agent_types:
            raise ValueError(f"Agent type '{name}' already exists")

        tool_set = self.tool_set_manager.get_tool_set(tool_set_name)
        if not tool_set:
            raise ValueError(f"ToolSet '{tool_set_name}' not found")

        self.agent_types[name] = {
            'name': name,
            'tool_set_name': tool_set_name,
            'description': description,
            'max_steps': max_steps,
            'tool_set': tool_set
        }

    def get_agent_types(self) -> List[str]:
        """Get list of available agent type names."""
        return list(self.agent_types.keys())

    def get_agent_type_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific agent type.

        Args:
            name: Name of the agent type

        Returns:
            Dictionary with agent type information, or None if not found
        """
        agent_type = self.agent_types.get(name)
        if not agent_type:
            return None

        return {
            'name': agent_type['name'],
            'description': agent_type['description'],
            'tool_set_name': agent_type['tool_set_name'],
            'max_steps': agent_type['max_steps'],
            'allowed_tools': list(agent_type['tool_set'].allowed_tools)
        }

    def create_sub_agent(self, agent_type: str, parent_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new sub-agent instance.

        Args:
            agent_type: Type of agent to create
            parent_context: Optional context from parent agent (working directory, etc.)

        Returns:
            Unique agent ID for the created sub-agent

        Raises:
            ValueError: If agent type is not found
        """
        if agent_type not in self.agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent_config = self.agent_types[agent_type]
        agent_id = str(uuid.uuid4())[:8]  # Short unique ID

        # Create sub-agent with restricted tools
        sub_agent = AgentCore()
        sub_agent.max_steps = agent_config['max_steps']

        # Set up event handling for sub-agent
        sub_agent.set_event_handler(self.event_handler)

        # Create restricted tool executor
        tool_executor = ToolExecutor()

        # Store agent configuration
        agent_instance = {
            'id': agent_id,
            'type': agent_type,
            'agent_core': sub_agent,
            'tool_executor': tool_executor,
            'tool_set': agent_config['tool_set'],
            'created_at': time.time(),
            'parent_context': parent_context or {}
        }

        self.active_agents[agent_id] = agent_instance
        return agent_id

    def execute_delegated_task(self, agent_type: str, task: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using a specialized sub-agent.

        Args:
            agent_type: Type of sub-agent to use
            task: Task description to execute
            context: Optional additional context for the task

        Returns:
            Dictionary with execution results and metadata
        """
        start_time = time.time()

        try:
            # Create sub-agent
            agent_id = self.create_sub_agent(agent_type)
            agent_instance = self.active_agents[agent_id]
            sub_agent = agent_instance['agent_core']
            tool_set = agent_instance['tool_set']

            # Emit delegation started event
            self.event_handler.handle_event('subagent_started', {
                'agent_id': agent_id,
                'agent_type': agent_type,
                'task': task
            })

            # Initialize sub-agent with restricted tools
            self._setup_sub_agent_tools(sub_agent, tool_set)

            # Prepare task with context
            full_task = task
            if context:
                full_task = f"{task}\n\nAdditional context: {context}"

            # Execute the task
            success = sub_agent.execute_task(full_task)
            end_time = time.time()
            duration = end_time - start_time

            # Get the result from sub-agent messages
            result = self._extract_result_from_messages(sub_agent.messages)

            # Emit completion event
            if success:
                self.event_handler.handle_event('subagent_completed', {
                    'agent_id': agent_id,
                    'agent_type': agent_type,
                    'duration': duration
                })
            else:
                self.event_handler.handle_event('subagent_failed', {
                    'agent_id': agent_id,
                    'agent_type': agent_type,
                    'error': 'Task execution failed'
                })

            # Store in delegation history
            delegation_record = {
                'agent_id': agent_id,
                'agent_type': agent_type,
                'task': task,
                'context': context,
                'success': success,
                'result': result,
                'duration': duration,
                'timestamp': start_time,
                'message_count': len(sub_agent.messages)
            }
            self.delegation_history.append(delegation_record)

            # Emit delegation result event
            self.event_handler.handle_event('delegation_result', {
                'agent_type': agent_type,
                'success': success,
                'result': result
            })

            # Cleanup
            self._cleanup_agent(agent_id)

            return {
                'success': success,
                'result': result,
                'duration': duration,
                'agent_id': agent_id,
                'agent_type': agent_type,
                'message_count': len(sub_agent.messages)
            }

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            error_msg = str(e)
            self.event_handler.handle_event('subagent_failed', {
                'agent_id': 'unknown',
                'agent_type': agent_type,
                'error': error_msg
            })

            # Store failure in delegation history
            delegation_record = {
                'agent_id': 'unknown',
                'agent_type': agent_type,
                'task': task,
                'context': context,
                'success': False,
                'result': f"Error: {error_msg}",
                'duration': duration,
                'timestamp': start_time,
                'message_count': 0
            }
            self.delegation_history.append(delegation_record)

            return {
                'success': False,
                'result': f"Error: {error_msg}",
                'duration': duration,
                'agent_id': 'unknown',
                'agent_type': agent_type,
                'message_count': 0
            }

    def _setup_sub_agent_tools(self, sub_agent: AgentCore, tool_set: ToolSet):
        """
        Set up the sub-agent with filtered tools based on its tool set.

        Args:
            sub_agent: The AgentCore instance to configure
            tool_set: ToolSet defining allowed tools
        """
        # Get all available tools from the main registry
        from tools.registry import ToolManager
        tool_manager = ToolManager()

        # Initialize tools if not already done
        if not hasattr(tool_manager, '_initialized') or not tool_manager._initialized:
            tool_manager.initialize()

        # Get all tool definitions
        all_tools = tool_manager.get_tools_definitions()

        # Filter tools based on the tool set
        filtered_tools = tool_set.filter_tools(all_tools)

        # Set the filtered tools on the sub-agent
        sub_agent.tools = filtered_tools

    def _extract_result_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        """
        Extract the final result from sub-agent conversation messages.

        Args:
            messages: List of conversation messages from sub-agent

        Returns:
            String representation of the sub-agent's result
        """
        if not messages:
            return "No output generated"

        # Look for the last assistant message
        for message in reversed(messages):
            if message.get('role') == 'assistant' and message.get('content'):
                return message['content']

        # If no assistant message found, look for tool outputs
        tool_results = []
        for message in messages:
            if message.get('role') == 'tool' and message.get('content'):
                tool_results.append(f"{message.get('name', 'tool')}: {message['content']}")

        if tool_results:
            return "Tool outputs:\n" + "\n".join(tool_results)

        return "No meaningful output found"

    def _cleanup_agent(self, agent_id: str):
        """
        Clean up a completed sub-agent.

        Args:
            agent_id: ID of the agent to clean up
        """
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]

    def get_active_agents(self) -> List[str]:
        """Get list of currently active agent IDs."""
        return list(self.active_agents.keys())

    def get_delegation_history(self) -> List[Dict[str, Any]]:
        """Get the complete delegation history."""
        return self.delegation_history.copy()

    def get_delegation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about delegation activities.

        Returns:
            Dictionary with delegation statistics
        """
        if not self.delegation_history:
            return {
                'total_delegations': 0,
                'success_rate': 0,
                'agent_type_usage': {},
                'average_duration': 0,
                'total_duration': 0
            }

        total_delegations = len(self.delegation_history)
        successful = sum(1 for d in self.delegation_history if d['success'])
        success_rate = (successful / total_delegations) * 100

        # Agent type usage
        agent_type_usage = {}
        for delegation in self.delegation_history:
            agent_type = delegation['agent_type']
            agent_type_usage[agent_type] = agent_type_usage.get(agent_type, 0) + 1

        # Duration statistics
        durations = [d['duration'] for d in self.delegation_history]
        total_duration = sum(durations)
        average_duration = total_duration / len(durations) if durations else 0

        return {
            'total_delegations': total_delegations,
            'successful_delegations': successful,
            'failed_delegations': total_delegations - successful,
            'success_rate': success_rate,
            'agent_type_usage': agent_type_usage,
            'average_duration': average_duration,
            'total_duration': total_duration,
            'recent_delegations': self.delegation_history[-5:] if self.delegation_history else []
        }

    def __str__(self) -> str:
        return f"SubAgentManager(types={len(self.agent_types)}, active={len(self.active_agents)}, history={len(self.delegation_history)})"

    def __repr__(self) -> str:
        return self.__str__()