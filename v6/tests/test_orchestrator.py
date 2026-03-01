"""Tests for Team Orchestrator (Issue #10)"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.team_orchestrator import TeamOrchestrator


class TestTeamOrchestrator:
    def test_init_project(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path))
        result = orch.init_project("todo-app", "Build a todo app")

        assert result["project_name"] == "todo-app"
        assert result["status"] == "initialized"
        assert orch.pm is not None
        assert orch.engineer is not None
        assert orch.strategist is not None
        assert (tmp_path / ".agent-team" / "config.json").exists()

    def test_start_stop(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path), heartbeat_interval=0.1)
        orch.init_project("test", "Test project")

        start_result = orch.start()
        assert start_result["status"] == "running"
        assert orch._running is True

        time.sleep(0.25)

        stop_result = orch.stop()
        assert stop_result["status"] == "stopped"
        assert orch._running is False
        assert stop_result["pm_ticks"] >= 1

    def test_start_without_init(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path))
        result = orch.start()
        assert "error" in result

    def test_double_start(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path), heartbeat_interval=60)
        orch.init_project("test", "Test")
        orch.start()
        result = orch.start()
        assert "error" in result
        orch.stop()

    def test_status(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path))
        orch.init_project("myapp", "A web app")

        status = orch.status()
        assert status["initialized"] is True
        assert status["running"] is False
        assert "pm" in status["agents"]
        assert status["project_name"] == "myapp"

    def test_send_chat(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path))
        orch.init_project("test", "Test")

        result = orch.send_chat("Add a login page")
        assert "Message sent" in result

        # Verify PM received it
        msgs = orch.pm.mailbox.check_mailbox()
        assert len(msgs) == 1
        assert "login page" in msgs[0].body

    def test_send_chat_without_init(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path))
        result = orch.send_chat("hello")
        assert "Error" in result

    def test_get_agent(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path))
        orch.init_project("test", "Test")

        assert orch.get_agent("pm") is orch.pm
        assert orch.get_agent("engineer") is orch.engineer
        assert orch.get_agent("strategist") is orch.strategist
        assert orch.get_agent("nonexistent") is None

    def test_start_with_product_description(self, tmp_path):
        orch = TeamOrchestrator(str(tmp_path), heartbeat_interval=60)
        orch.init_project("todo", "Todo app")
        orch.start(product_description="Build a todo app with React")
        orch.stop()

        msgs = orch.pm.mailbox.check_mailbox(unread_only=False)
        assert any("todo app" in m.body.lower() for m in msgs)
