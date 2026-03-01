"""BaseAgent - Common base for all V6 agent roles"""

from core.agent_core import AgentCore


class BaseAgent(AgentCore):
    """Base class for V6 agent roles (PM, Engineer, Strategist).

    Extends AgentCore with:
    - Agent identity (name, role)
    - Mailbox integration
    - Heartbeat participation
    - Shared state access
    """

    def __init__(self, name: str, role: str):
        super().__init__()
        self.agent_name = name
        self.role = role

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.agent_name!r} role={self.role!r}>"
