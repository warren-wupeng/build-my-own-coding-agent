"""PM Agent - Product Manager role (Issue #7)"""

from .base_agent import BaseAgent


class PMAgent(BaseAgent):
    """PM Agent: understand user intent -> decompose issues -> assign -> accept.

    Tools: create_issue, assign_task, check_progress, send_message, read_sop
    """

    def __init__(self, name: str = "pm"):
        super().__init__(name=name, role="pm")
