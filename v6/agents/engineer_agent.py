"""Engineer Agent - Software Engineer role (Issue #8)"""

from .base_agent import BaseAgent


class EngineerAgent(BaseAgent):
    """Engineer Agent: execute issues strictly, use V5 full toolset + messaging.

    Tools: V5 all 15 tools + send_message + check_mailbox
    """

    def __init__(self, name: str = "engineer"):
        super().__init__(name=name, role="engineer")
