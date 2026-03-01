"""Tests for the Heartbeat driver (Issue #3)"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_team.heartbeat import Heartbeat, TickResult


class TestTickResult:
    def test_success_when_no_errors(self):
        r = TickResult(tick_number=1, timestamp=time.time(), steps_completed=["git_pull"])
        assert r.success is True

    def test_failure_when_errors(self):
        r = TickResult(tick_number=1, timestamp=time.time(), errors=["git_pull: timeout"])
        assert r.success is False


class TestHeartbeat:
    def test_single_tick_no_callbacks(self):
        hb = Heartbeat(interval=1.0, agent_name="test")
        result = hb.tick()
        assert result.tick_number == 1
        assert result.success is True
        assert result.steps_completed == []

    def test_single_tick_with_callbacks(self):
        hb = Heartbeat(interval=1.0, agent_name="test")
        hb.register_step("git_pull", lambda: None)
        hb.register_step("check_mailbox", lambda: None)
        result = hb.tick()
        assert "git_pull" in result.steps_completed
        assert "check_mailbox" in result.steps_completed

    def test_tick_with_error_callback(self):
        hb = Heartbeat(interval=1.0, agent_name="test")
        hb.register_step("git_pull", lambda: "connection refused")
        result = hb.tick()
        assert result.success is False
        assert any("connection refused" in e for e in result.errors)

    def test_tick_with_exception(self):
        def explode():
            raise RuntimeError("boom")

        hb = Heartbeat(interval=1.0, agent_name="test")
        hb.register_step("execute_sop", explode)
        result = hb.tick()
        assert result.success is False
        assert any("boom" in e for e in result.errors)

    def test_tick_count_increments(self):
        hb = Heartbeat(interval=1.0, agent_name="test")
        hb.tick()
        hb.tick()
        hb.tick()
        assert hb.tick_count == 3

    def test_history(self):
        hb = Heartbeat(interval=1.0, agent_name="test")
        hb.tick()
        hb.tick()
        assert len(hb.history) == 2
        assert hb.last_tick.tick_number == 2

    def test_invalid_step_name(self):
        hb = Heartbeat(interval=1.0, agent_name="test")
        try:
            hb.register_step("invalid_step", lambda: None)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_start_stop(self):
        hb = Heartbeat(interval=0.1, agent_name="test")
        hb.register_step("git_pull", lambda: None)
        hb.start()
        assert hb.is_running is True
        time.sleep(0.35)
        hb.stop()
        assert hb.is_running is False
        assert hb.tick_count >= 2

    def test_last_tick_none_initially(self):
        hb = Heartbeat(interval=1.0, agent_name="test")
        assert hb.last_tick is None
