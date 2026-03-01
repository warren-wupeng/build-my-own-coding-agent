"""Team Orchestrator - Agent lifecycle manager (Issue #10)

The Team Orchestrator is the top-level controller that:
1. Initializes the project's .agent-team/ directory
2. Creates and configures all three agent instances
3. Starts/stops agent heartbeats
4. Monitors agent health and handles recovery
5. Provides a unified interface for the CLI
"""

import logging
import time
from typing import Optional

from agent_team.shared_state import SharedState
from .pm_agent import PMAgent
from .engineer_agent import EngineerAgent
from .strategist_agent import StrategistAgent

logger = logging.getLogger(__name__)


class TeamOrchestrator:
    """Manages lifecycle of PM/Engineer/Strategist agents.

    This is the entry point for creating and running an agent team.
    The CLI (Issue #11) will interact with this class.
    """

    def __init__(self, project_dir: str, heartbeat_interval: float = 30.0):
        """Initialize the orchestrator.

        Args:
            project_dir: Root directory of the git project
            heartbeat_interval: Seconds between heartbeat ticks for all agents
        """
        self.project_dir = project_dir
        self.heartbeat_interval = heartbeat_interval
        self.shared_state = SharedState(project_dir)

        # Agent instances
        self.pm: Optional[PMAgent] = None
        self.engineer: Optional[EngineerAgent] = None
        self.strategist: Optional[StrategistAgent] = None

        self._initialized = False
        self._running = False

    def init_project(self, project_name: str, description: str) -> dict:
        """Initialize a new agent-team project.

        Creates .agent-team/ directory structure and agent instances.

        Args:
            project_name: Name of the project
            description: Project description (user's product idea)

        Returns:
            Dict with initialization status
        """
        # Initialize shared state
        config = self.shared_state.initialize(
            project_name=project_name,
            description=description,
            agents=["pm", "engineer", "strategist"],
        )

        # Create agent instances
        self.pm = PMAgent()
        self.engineer = EngineerAgent()
        self.strategist = StrategistAgent()

        # Setup each agent with project infrastructure
        for agent in [self.pm, self.engineer, self.strategist]:
            agent.setup(
                project_dir=self.project_dir,
                heartbeat_interval=self.heartbeat_interval,
            )

        self._initialized = True

        logger.info(f"Project '{project_name}' initialized with 3 agents")
        return {
            "project_name": project_name,
            "description": description,
            "agents": ["pm", "engineer", "strategist"],
            "status": "initialized",
        }

    def start(self, product_description: Optional[str] = None) -> dict:
        """Start all agent heartbeats.

        Args:
            product_description: Optional initial product description to kick off PM

        Returns:
            Dict with start status
        """
        if not self._initialized:
            return {"error": "Project not initialized. Run init_project() first."}

        if self._running:
            return {"error": "Team is already running."}

        # Start all heartbeats
        for agent in [self.pm, self.engineer, self.strategist]:
            agent.start()

        self._running = True

        # If product description provided, send it to PM as the initial task
        if product_description:
            self.pm.mailbox.send_message(
                recipient="pm",
                subject="New Product Request",
                body=product_description,
                metadata={"type": "user_request"},
            )

        logger.info("All agents started")
        return {
            "status": "running",
            "agents": {
                "pm": "running",
                "engineer": "running",
                "strategist": "running",
            }
        }

    def stop(self) -> dict:
        """Stop all agent heartbeats.

        Returns:
            Dict with stop status
        """
        if not self._running:
            return {"status": "already stopped"}

        for agent in [self.pm, self.engineer, self.strategist]:
            if agent:
                agent.stop()

        self._running = False
        logger.info("All agents stopped")

        return {
            "status": "stopped",
            "pm_ticks": self.pm.heartbeat.tick_count if self.pm else 0,
            "engineer_ticks": self.engineer.heartbeat.tick_count if self.engineer else 0,
            "strategist_ticks": self.strategist.heartbeat.tick_count if self.strategist else 0,
        }

    def status(self) -> dict:
        """Get current team status.

        Returns:
            Dict with team status overview
        """
        result = {
            "running": self._running,
            "initialized": self._initialized,
            "agents": {},
            "issues": {"total": 0, "open": 0, "in_progress": 0, "review": 0, "done": 0, "closed": 0},
        }

        # Agent statuses
        for name in ["pm", "engineer", "strategist"]:
            agent_status = self.shared_state.get_agent_status(name)
            if agent_status:
                result["agents"][name] = {
                    "state": agent_status.state,
                    "current_task": agent_status.current_task,
                    "tick_count": agent_status.tick_count,
                    "last_heartbeat": agent_status.last_heartbeat,
                }

        # Issue summary
        if self._initialized and self.pm:
            all_issues = self.pm.issue_manager.list_issues()
            result["issues"]["total"] = len(all_issues)
            for issue in all_issues:
                if issue.status in result["issues"]:
                    result["issues"][issue.status] += 1

        # Config
        config = self.shared_state.get_config()
        if config:
            result["project_name"] = config.project_name
            result["description"] = config.description

        return result

    def send_chat(self, message: str) -> str:
        """Send a user message to the PM agent.

        Args:
            message: User's message text

        Returns:
            Confirmation string
        """
        if not self._initialized:
            return "Error: Project not initialized."

        self.pm.mailbox.send_message(
            recipient="pm",
            subject="User message",
            body=message,
            metadata={"type": "user_chat"},
        )
        return f"Message sent to PM: {message[:100]}{'...' if len(message) > 100 else ''}"

    def get_agent(self, name: str):
        """Get an agent by name.

        Args:
            name: Agent name ('pm', 'engineer', 'strategist')

        Returns:
            Agent instance or None
        """
        return {"pm": self.pm, "engineer": self.engineer, "strategist": self.strategist}.get(name)
