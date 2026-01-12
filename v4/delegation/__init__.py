"""
Delegation module for V4 Agent

This module provides sub-agent delegation functionality, allowing the main agent
to delegate specific tasks to specialized sub-agents with restricted tool access.

Main components:
- SubAgentManager: Manages sub-agent lifecycle and configuration
- ToolSet & ToolSetManager: Defines and manages tool restrictions for sub-agents
- DelegationEventHandler: Handles events from sub-agents and bubbles to parent
"""

from .manager import SubAgentManager
from .tool_sets import ToolSet, ToolSetManager
from .events import DelegationEventHandler

__all__ = [
    'SubAgentManager',
    'ToolSet',
    'ToolSetManager',
    'DelegationEventHandler'
]