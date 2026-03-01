"""Tests for Git-based shared state (Issue #4)"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_team.shared_state import SharedState, TeamConfig, AgentStatus


class TestTeamConfig:
    def test_roundtrip(self):
        config = TeamConfig(project_name="test", description="A test project", agents=["pm", "eng"])
        d = config.to_dict()
        restored = TeamConfig.from_dict(d)
        assert restored.project_name == "test"
        assert restored.agents == ["pm", "eng"]


class TestAgentStatus:
    def test_defaults(self):
        s = AgentStatus(agent_name="pm")
        assert s.state == "idle"
        assert s.current_task is None

    def test_roundtrip(self):
        s = AgentStatus(agent_name="eng", state="working", current_task="Issue #1")
        d = s.to_dict()
        restored = AgentStatus.from_dict(d)
        assert restored.state == "working"
        assert restored.current_task == "Issue #1"


class TestSharedState:
    def test_initialize(self, tmp_path):
        ss = SharedState(str(tmp_path))
        config = ss.initialize("myproject", "Test project", ["pm", "engineer"])

        assert config.project_name == "myproject"
        assert (tmp_path / ".agent-team" / "config.json").exists()
        assert (tmp_path / ".agent-team" / "mailbox" / "pm").is_dir()
        assert (tmp_path / ".agent-team" / "mailbox" / "engineer").is_dir()
        assert (tmp_path / ".agent-team" / "issues").is_dir()
        assert (tmp_path / ".agent-team" / "status").is_dir()
        assert (tmp_path / ".agent-team" / "logs").is_dir()

    def test_get_config(self, tmp_path):
        ss = SharedState(str(tmp_path))
        ss.initialize("myproject", "desc")
        config = ss.get_config()
        assert config.project_name == "myproject"
        assert "pm" in config.agents

    def test_get_config_missing(self, tmp_path):
        ss = SharedState(str(tmp_path))
        assert ss.get_config() is None

    def test_agent_status(self, tmp_path):
        ss = SharedState(str(tmp_path))
        ss.initialize("proj", "desc", ["pm"])

        status = ss.get_agent_status("pm")
        assert status.state == "idle"

        ss.update_agent_status("pm", state="working", current_task="Issue #5")
        status = ss.get_agent_status("pm")
        assert status.state == "working"
        assert status.current_task == "Issue #5"

    def test_agent_status_missing(self, tmp_path):
        ss = SharedState(str(tmp_path))
        assert ss.get_agent_status("nonexistent") is None

    def test_update_creates_if_missing(self, tmp_path):
        ss = SharedState(str(tmp_path))
        (tmp_path / ".agent-team" / "status").mkdir(parents=True)
        status = ss.update_agent_status("new_agent", state="working")
        assert status.agent_name == "new_agent"
        assert status.state == "working"

    def test_default_agents(self, tmp_path):
        ss = SharedState(str(tmp_path))
        config = ss.initialize("proj", "desc")
        assert config.agents == ["pm", "engineer", "strategist"]
