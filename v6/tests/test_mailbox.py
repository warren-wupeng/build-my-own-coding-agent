"""Tests for the Mailbox communication system (Issue #2)"""

import json
import tempfile
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_team.mailbox import Mailbox, Message


class TestMessage:
    def test_to_dict_roundtrip(self):
        msg = Message(
            id="abc123",
            sender="pm",
            recipient="engineer",
            subject="Build feature",
            body="Please implement login",
            timestamp=1000.0,
        )
        d = msg.to_dict()
        restored = Message.from_dict(d)
        assert restored.id == msg.id
        assert restored.sender == msg.sender
        assert restored.body == msg.body

    def test_to_json_roundtrip(self):
        msg = Message(
            id="xyz789",
            sender="engineer",
            recipient="pm",
            subject="Done",
            body="Login implemented",
            timestamp=2000.0,
            reply_to="abc123",
        )
        json_str = msg.to_json()
        restored = Message.from_json(json_str)
        assert restored.reply_to == "abc123"
        assert restored.subject == "Done"


class TestMailbox:
    def _make_mailbox(self, tmpdir, name):
        return Mailbox(base_dir=str(tmpdir), agent_name=name)

    def test_send_and_receive(self, tmp_path):
        pm = self._make_mailbox(tmp_path, "pm")
        eng = self._make_mailbox(tmp_path, "engineer")

        pm.send_message("engineer", "Task", "Build login page")
        messages = eng.check_mailbox()
        assert len(messages) == 1
        assert messages[0].sender == "pm"
        assert messages[0].subject == "Task"
        assert messages[0].body == "Build login page"

    def test_unread_only(self, tmp_path):
        pm = self._make_mailbox(tmp_path, "pm")
        eng = self._make_mailbox(tmp_path, "engineer")

        msg = pm.send_message("engineer", "Task1", "Body1")
        pm.send_message("engineer", "Task2", "Body2")

        eng.mark_as_read(msg.id)

        unread = eng.check_mailbox(unread_only=True)
        assert len(unread) == 1
        assert unread[0].subject == "Task2"

        all_msgs = eng.check_mailbox(unread_only=False)
        assert len(all_msgs) == 2

    def test_reply(self, tmp_path):
        pm = self._make_mailbox(tmp_path, "pm")
        eng = self._make_mailbox(tmp_path, "engineer")

        original = pm.send_message("engineer", "Task", "Build it")
        messages = eng.check_mailbox()
        eng.reply_message(messages[0], "Done, it's built")

        replies = pm.check_mailbox()
        assert len(replies) == 1
        assert replies[0].subject == "Re: Task"
        assert replies[0].reply_to == original.id

    def test_unread_count(self, tmp_path):
        pm = self._make_mailbox(tmp_path, "pm")
        eng = self._make_mailbox(tmp_path, "engineer")

        pm.send_message("engineer", "A", "body")
        pm.send_message("engineer", "B", "body")
        pm.send_message("engineer", "C", "body")

        assert eng.get_unread_count() == 3
        msgs = eng.check_mailbox()
        eng.mark_as_read(msgs[0].id)
        assert eng.get_unread_count() == 2

    def test_empty_mailbox(self, tmp_path):
        eng = self._make_mailbox(tmp_path, "engineer")
        assert eng.check_mailbox() == []
        assert eng.get_unread_count() == 0

    def test_mark_nonexistent(self, tmp_path):
        eng = self._make_mailbox(tmp_path, "engineer")
        assert eng.mark_as_read("nonexistent") is False

    def test_message_ordering(self, tmp_path):
        pm = self._make_mailbox(tmp_path, "pm")
        eng = self._make_mailbox(tmp_path, "engineer")

        pm.send_message("engineer", "First", "1")
        pm.send_message("engineer", "Second", "2")
        pm.send_message("engineer", "Third", "3")

        messages = eng.check_mailbox()
        assert [m.subject for m in messages] == ["First", "Second", "Third"]
