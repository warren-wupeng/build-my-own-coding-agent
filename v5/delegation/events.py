"""
Event handling system for sub-agent delegation

This module provides event handling capabilities for monitoring sub-agent
activities and bubbling events to parent agents.
"""

from typing import Optional, Dict, Any, Callable
import time


class DelegationEventHandler:
    """
    Event handler for sub-agent delegation system.

    Manages events from sub-agents and can optionally forward them to a parent
    event handler. Provides delegation-specific event processing while
    maintaining compatibility with the existing event system.
    """

    def __init__(self, parent_handler: Optional[object] = None):
        """
        Initialize the delegation event handler.

        Args:
            parent_handler: Optional parent event handler to forward events to
        """
        self.parent_handler = parent_handler
        self.delegation_events = []  # Store delegation-specific events
        self.event_callbacks: Dict[str, Callable] = {}

    def handle_event(self, event_type: str, data: Any):
        """
        Handle an event from a sub-agent or delegation system.

        Args:
            event_type: Type of event (e.g., 'subagent_started', 'delegation_result')
            data: Event data (varies by event type)
        """
        # Record the event with timestamp
        event_record = {
            'event_type': event_type,
            'data': data,
            'timestamp': time.time()
        }

        # Handle delegation-specific events
        if event_type.startswith('subagent_') or event_type.startswith('delegation_'):
            self._handle_delegation_event(event_type, data, event_record)
        else:
            # Forward non-delegation events to parent if available
            if self.parent_handler and hasattr(self.parent_handler, 'handle_event'):
                self.parent_handler.handle_event(event_type, data)

        # Execute registered callbacks for this event type
        if event_type in self.event_callbacks:
            try:
                self.event_callbacks[event_type](event_type, data)
            except Exception as e:
                # Don't let callback errors break event handling
                print(f"Warning: Event callback for '{event_type}' failed: {e}")

    def _handle_delegation_event(self, event_type: str, data: Any, event_record: Dict):
        """
        Process delegation-specific events.

        Args:
            event_type: Type of delegation event
            data: Event data
            event_record: Complete event record with timestamp
        """
        # Store the event
        self.delegation_events.append(event_record)

        # Process specific delegation events
        if event_type == 'subagent_started':
            self._handle_subagent_started(data)
        elif event_type == 'subagent_completed':
            self._handle_subagent_completed(data)
        elif event_type == 'subagent_failed':
            self._handle_subagent_failed(data)
        elif event_type == 'delegation_result':
            self._handle_delegation_result(data)
        elif event_type == 'subagent_step_started':
            self._handle_subagent_step(data)
        elif event_type == 'subagent_tools_executing':
            self._handle_subagent_tools_executing(data)

        # Also forward to parent if it exists (for display purposes)
        if self.parent_handler and hasattr(self.parent_handler, 'handle_event'):
            self.parent_handler.handle_event(event_type, data)

    def _handle_subagent_started(self, data: Dict):
        """Handle sub-agent started event."""
        agent_id = data.get('agent_id', 'unknown')
        agent_type = data.get('agent_type', 'unknown')
        task = data.get('task', 'No task description')

        print(f"🤖 Sub-agent started: {agent_type} (ID: {agent_id})")
        print(f"   Task: {task}")

    def _handle_subagent_completed(self, data: Dict):
        """Handle sub-agent completed event."""
        agent_id = data.get('agent_id', 'unknown')
        agent_type = data.get('agent_type', 'unknown')
        duration = data.get('duration', 0)

        print(f"✅ Sub-agent completed: {agent_type} (ID: {agent_id})")
        if duration > 0:
            print(f"   Duration: {duration:.2f}s")

    def _handle_subagent_failed(self, data: Dict):
        """Handle sub-agent failure event."""
        agent_id = data.get('agent_id', 'unknown')
        agent_type = data.get('agent_type', 'unknown')
        error = data.get('error', 'Unknown error')

        print(f"❌ Sub-agent failed: {agent_type} (ID: {agent_id})")
        print(f"   Error: {error}")

    def _handle_delegation_result(self, data: Dict):
        """Handle delegation result event."""
        agent_type = data.get('agent_type', 'unknown')
        success = data.get('success', False)
        result = data.get('result', '')

        status = "✅" if success else "❌"
        print(f"{status} Delegation result from {agent_type}:")
        if result:
            # Truncate very long results for display
            display_result = result[:500] + "..." if len(result) > 500 else result
            print(f"   {display_result}")

    def _handle_subagent_step(self, data: Dict):
        """Handle sub-agent step started event."""
        agent_id = data.get('agent_id', 'unknown')
        step_count = data.get('step_count', 0)

        # Only show periodic updates for long-running sub-agents
        if step_count % 5 == 0:
            print(f"   Sub-agent {agent_id} step {step_count}...")

    def _handle_subagent_tools_executing(self, data: Dict):
        """Handle sub-agent tools executing event."""
        agent_id = data.get('agent_id', 'unknown')
        tools = data.get('tools', [])

        if tools:
            tool_names = [tool.get('function', {}).get('name', 'unknown') for tool in tools]
            print(f"   Sub-agent {agent_id} executing: {', '.join(tool_names)}")

    def register_event_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.

        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs (signature: callback(event_type, data))
        """
        self.event_callbacks[event_type] = callback

    def unregister_event_callback(self, event_type: str):
        """Remove a callback for a specific event type."""
        if event_type in self.event_callbacks:
            del self.event_callbacks[event_type]

    def get_delegation_events(self, event_type: Optional[str] = None) -> list:
        """
        Get delegation events, optionally filtered by event type.

        Args:
            event_type: Optional event type to filter by

        Returns:
            List of delegation events
        """
        if event_type:
            return [event for event in self.delegation_events if event['event_type'] == event_type]
        return self.delegation_events.copy()

    def get_delegation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about delegation events.

        Returns:
            Dictionary with delegation event statistics
        """
        if not self.delegation_events:
            return {
                'total_events': 0,
                'event_types': {},
                'recent_events': []
            }

        # Count events by type
        event_type_counts = {}
        for event in self.delegation_events:
            event_type = event['event_type']
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        # Get recent events (last 10)
        recent_events = sorted(
            self.delegation_events,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:10]

        return {
            'total_events': len(self.delegation_events),
            'event_types': event_type_counts,
            'recent_events': recent_events
        }

    def clear_delegation_events(self):
        """Clear all stored delegation events."""
        self.delegation_events.clear()

    def __str__(self) -> str:
        return f"DelegationEventHandler(events={len(self.delegation_events)}, callbacks={len(self.event_callbacks)})"

    def __repr__(self) -> str:
        return self.__str__()