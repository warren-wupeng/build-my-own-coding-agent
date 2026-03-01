"""SharedState - Git-based shared state management (Issue #4)

Manages the .agent-team/ directory structure within a git repository.
Provides auto commit/push/pull operations for team coordination.

Directory layout:
    .agent-team/
        config.json          # Team configuration
        mailbox/{agent}/     # Agent mailboxes (managed by Mailbox)
        issues/              # Issue files (managed by IssueManager)
        status/{agent}.json  # Agent status files
        logs/                # Shared logs
"""

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class TeamConfig:
    """Team configuration stored in .agent-team/config.json."""
    project_name: str
    description: str
    agents: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TeamConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AgentStatus:
    """Status of a single agent."""
    agent_name: str
    state: str = "idle"  # idle, working, waiting, error
    current_task: Optional[str] = None
    last_heartbeat: float = 0.0
    tick_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentStatus":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class SharedState:
    """Manages .agent-team/ directory structure with git operations.

    Provides:
    - Directory initialization
    - Team config read/write
    - Agent status read/write
    - Git pull/commit/push wrappers
    """

    def __init__(self, project_dir: str):
        """Initialize shared state manager.

        Args:
            project_dir: Root directory of the git repository
        """
        self.project_dir = Path(project_dir)
        self.team_dir = self.project_dir / ".agent-team"

    def initialize(self, project_name: str, description: str,
                   agents: Optional[list[str]] = None) -> TeamConfig:
        """Initialize .agent-team/ directory structure.

        Args:
            project_name: Name of the project
            description: Project description
            agents: List of agent names to register

        Returns:
            The created TeamConfig
        """
        agents = agents or ["pm", "engineer", "strategist"]

        # Create directory structure
        dirs = [
            self.team_dir,
            self.team_dir / "mailbox",
            self.team_dir / "issues",
            self.team_dir / "status",
            self.team_dir / "logs",
        ]
        for agent in agents:
            dirs.append(self.team_dir / "mailbox" / agent)

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # Write config
        config = TeamConfig(
            project_name=project_name,
            description=description,
            agents=agents,
        )
        self._write_json(self.team_dir / "config.json", config.to_dict())

        # Initialize agent status files
        for agent in agents:
            status = AgentStatus(agent_name=agent)
            self._write_json(
                self.team_dir / "status" / f"{agent}.json",
                status.to_dict(),
            )

        logger.info(f"Initialized .agent-team/ for project: {project_name}")
        return config

    def get_config(self) -> Optional[TeamConfig]:
        """Read team configuration."""
        config_path = self.team_dir / "config.json"
        if not config_path.exists():
            return None
        data = self._read_json(config_path)
        return TeamConfig.from_dict(data) if data else None

    def get_agent_status(self, agent_name: str) -> Optional[AgentStatus]:
        """Read an agent's status."""
        status_path = self.team_dir / "status" / f"{agent_name}.json"
        if not status_path.exists():
            return None
        data = self._read_json(status_path)
        return AgentStatus.from_dict(data) if data else None

    def update_agent_status(self, agent_name: str, **kwargs) -> AgentStatus:
        """Update an agent's status fields.

        Args:
            agent_name: Agent to update
            **kwargs: Fields to update (state, current_task, last_heartbeat, tick_count)

        Returns:
            Updated AgentStatus
        """
        status = self.get_agent_status(agent_name)
        if not status:
            status = AgentStatus(agent_name=agent_name)

        for key, value in kwargs.items():
            if hasattr(status, key):
                setattr(status, key, value)

        self._write_json(
            self.team_dir / "status" / f"{agent_name}.json",
            status.to_dict(),
        )
        return status

    def git_pull(self) -> tuple[bool, str]:
        """Pull latest changes from remote.

        Returns:
            (success, output) tuple
        """
        return self._run_git("pull", "--rebase")

    def git_commit(self, message: str) -> tuple[bool, str]:
        """Stage all .agent-team/ changes and commit.

        Args:
            message: Commit message

        Returns:
            (success, output) tuple
        """
        # Stage .agent-team/ changes
        success, output = self._run_git("add", ".agent-team/")
        if not success:
            return False, f"git add failed: {output}"

        # Check if there are staged changes
        success, output = self._run_git("diff", "--cached", "--quiet")
        if success:
            return True, "Nothing to commit"

        return self._run_git("commit", "-m", message)

    def git_push(self) -> tuple[bool, str]:
        """Push changes to remote.

        Returns:
            (success, output) tuple
        """
        return self._run_git("push")

    def sync(self, commit_message: Optional[str] = None) -> tuple[bool, str]:
        """Full sync cycle: pull -> commit -> push.

        Args:
            commit_message: Optional commit message (default: auto-generated)

        Returns:
            (success, output) tuple
        """
        # Pull first
        success, pull_output = self.git_pull()
        if not success:
            return False, f"Pull failed: {pull_output}"

        # Commit if there's a message
        if commit_message:
            success, commit_output = self.git_commit(commit_message)
            if not success:
                return False, f"Commit failed: {commit_output}"

            # Push only if we committed
            if "Nothing to commit" not in commit_output:
                success, push_output = self.git_push()
                if not success:
                    return False, f"Push failed: {push_output}"

        return True, "Sync complete"

    def _run_git(self, *args) -> tuple[bool, str]:
        """Run a git command in the project directory.

        Returns:
            (success, output) tuple
        """
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout.strip() or result.stderr.strip()
            return result.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, "Git command timed out"
        except FileNotFoundError:
            return False, "Git not found"
        except Exception as e:
            return False, str(e)

    def _write_json(self, path: Path, data: dict):
        """Write JSON data to a file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _read_json(self, path: Path) -> Optional[dict]:
        """Read JSON data from a file."""
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return None
