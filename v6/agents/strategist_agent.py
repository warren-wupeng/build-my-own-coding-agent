"""Strategist Agent - Documentation & UX role (Issue #9)"""

from .base_agent import BaseAgent


class StrategistAgent(BaseAgent):
    """Strategist Agent: docs, README, user experience.

    Tools: file read/write + send_message + check_mailbox + web_search
    """

    def __init__(self, name: str = "strategist"):
        super().__init__(name=name, role="strategist")
