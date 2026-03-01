"""BaseAgent - Common base for all V6 agent roles

Extends AgentCore with team infrastructure: mailbox, heartbeat, shared state,
SOP execution, and issue awareness. All agent roles inherit from this.
"""

import logging
from typing import Optional

from core.agent_core import AgentCore
from agent_team.mailbox import Mailbox
from agent_team.heartbeat import Heartbeat
from agent_team.shared_state import SharedState
from agent_team.sop_parser import SOPParser, SOP
from agent_team.issue_manager import IssueManager

logger = logging.getLogger(__name__)


class BaseAgent(AgentCore):
    """Base class for V6 agent roles (PM, Engineer, Strategist).

    Extends AgentCore with:
    - Agent identity (name, role)
    - Mailbox integration (async messaging)
    - Heartbeat participation (periodic tick)
    - Shared state access (git-based coordination)
    - SOP awareness (procedure-driven behavior)
    - Issue tracking (task management)
    """

    # Subclasses define their system prompt
    SYSTEM_PROMPT: str = "You are an AI agent."

    def __init__(self, name: str, role: str):
        # Skip AgentCore.__init__() to avoid requiring OPENROUTER_API_KEY at construction.
        # LLM/tools are initialized lazily when actually needed for task execution.
        self.messages = []
        self.tools = []
        self.max_steps = 50
        self.event_handler = None

        self.agent_name = name
        self.role = role

        # Team infrastructure (initialized via setup())
        self.mailbox: Optional[Mailbox] = None
        self.heartbeat: Optional[Heartbeat] = None
        self.shared_state: Optional[SharedState] = None
        self.sop_parser: Optional[SOPParser] = None
        self.issue_manager: Optional[IssueManager] = None

        # Current state
        self.current_sop: Optional[SOP] = None
        self.current_sop_step: int = 0

    def setup(self, project_dir: str, heartbeat_interval: float = 30.0):
        """Initialize team infrastructure for this agent.

        Args:
            project_dir: Root directory of the git project
            heartbeat_interval: Seconds between heartbeat ticks
        """
        self.mailbox = Mailbox(base_dir=project_dir, agent_name=self.agent_name)
        self.heartbeat = Heartbeat(interval=heartbeat_interval, agent_name=self.agent_name)
        self.shared_state = SharedState(project_dir=project_dir)
        self.sop_parser = SOPParser()
        self.issue_manager = IssueManager(base_dir=project_dir)

        # Register heartbeat steps
        self.heartbeat.register_step("git_pull", self._on_git_pull)
        self.heartbeat.register_step("check_mailbox", self._on_check_mailbox)
        self.heartbeat.register_step("check_tasks", self._on_check_tasks)
        self.heartbeat.register_step("execute_sop", self._on_execute_sop)
        self.heartbeat.register_step("push_progress", self._on_push_progress)

        # Update status
        self.shared_state.update_agent_status(
            self.agent_name, state="idle", last_heartbeat=0
        )

        logger.info(f"[{self.agent_name}] Setup complete for project: {project_dir}")

    def _on_git_pull(self) -> Optional[str]:
        """Heartbeat step: pull latest changes."""
        success, output = self.shared_state.git_pull()
        if not success:
            return f"git pull failed: {output}"
        return None

    def _on_check_mailbox(self) -> Optional[str]:
        """Heartbeat step: check for new messages."""
        messages = self.mailbox.check_mailbox(unread_only=True)
        if messages:
            logger.info(f"[{self.agent_name}] {len(messages)} new message(s)")
            for msg in messages:
                self.handle_message(msg)
                self.mailbox.mark_as_read(msg.id)
        return None

    def _on_check_tasks(self) -> Optional[str]:
        """Heartbeat step: check assigned issues."""
        issues = self.issue_manager.list_issues(assignee=self.agent_name)
        active = [i for i in issues if i.status in ("open", "in_progress")]
        if active:
            logger.info(f"[{self.agent_name}] {len(active)} active issue(s)")
        return None

    def _on_execute_sop(self) -> Optional[str]:
        """Heartbeat step: execute current SOP step if any."""
        if self.current_sop and self.current_sop_step < self.current_sop.step_count:
            step = self.current_sop.steps[self.current_sop_step]
            logger.info(f"[{self.agent_name}] Executing SOP step {step.number}: {step.title}")
            self.current_sop_step += 1
        return None

    def _on_push_progress(self) -> Optional[str]:
        """Heartbeat step: commit and push changes."""
        import time
        self.shared_state.update_agent_status(
            self.agent_name,
            last_heartbeat=time.time(),
            tick_count=self.heartbeat.tick_count,
        )
        success, output = self.shared_state.git_commit(
            f"[{self.agent_name}] heartbeat tick #{self.heartbeat.tick_count}"
        )
        if not success and "Nothing to commit" not in output:
            return f"commit failed: {output}"
        return None

    def handle_message(self, msg):
        """Handle an incoming message. Override in subclasses for role-specific behavior.

        Args:
            msg: Message object from the mailbox
        """
        logger.info(
            f"[{self.agent_name}] Received from {msg.sender}: {msg.subject}"
        )

    def load_sop(self, sop_path: str):
        """Load an SOP document to guide this agent's behavior.

        Args:
            sop_path: Path to the .md SOP file
        """
        self.current_sop = self.sop_parser.parse_file(sop_path)
        self.current_sop_step = 0
        logger.info(
            f"[{self.agent_name}] Loaded SOP: {self.current_sop.title} "
            f"({self.current_sop.step_count} steps)"
        )

    def get_assigned_issues(self, status: Optional[str] = None):
        """Get issues assigned to this agent.

        Args:
            status: Optional status filter

        Returns:
            List of Issue objects
        """
        issues = self.issue_manager.list_issues(assignee=self.agent_name)
        if status:
            issues = [i for i in issues if i.status == status]
        return issues

    def start(self):
        """Start this agent's heartbeat."""
        self.shared_state.update_agent_status(self.agent_name, state="working")
        self.heartbeat.start()

    def stop(self):
        """Stop this agent's heartbeat."""
        self.heartbeat.stop()
        self.shared_state.update_agent_status(self.agent_name, state="idle")

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.agent_name!r} role={self.role!r}>"
