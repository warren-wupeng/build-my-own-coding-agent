"""Tests for the Issue lifecycle management (Issue #6)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_team.issue_manager import IssueManager, Issue


class TestIssue:
    def test_slug(self):
        issue = Issue(id=1, title="Implement User Login")
        assert issue.slug == "implement-user-login"

    def test_filename(self):
        issue = Issue(id=3, title="Add Tests")
        assert issue.filename == "003-add-tests.md"

    def test_markdown_roundtrip(self):
        issue = Issue(
            id=5,
            title="Build API",
            status="in_progress",
            assignee="engineer",
            priority="high",
            created_by="pm",
            labels=["feature", "api"],
            description="Build the REST API endpoints.",
            acceptance_criteria=["GET /users works", "POST /users works"],
        )
        md = issue.to_markdown()
        restored = Issue.from_markdown(md)

        assert restored.id == 5
        assert restored.title == "Build API"
        assert restored.status == "in_progress"
        assert restored.assignee == "engineer"
        assert restored.priority == "high"
        assert restored.labels == ["feature", "api"]
        assert "REST API" in restored.description
        assert len(restored.acceptance_criteria) == 2

    def test_unassigned_roundtrip(self):
        issue = Issue(id=1, title="Test", assignee=None)
        md = issue.to_markdown()
        restored = Issue.from_markdown(md)
        assert restored.assignee is None


class TestIssueManager:
    def _make_manager(self, tmp_path):
        (tmp_path / ".agent-team" / "issues").mkdir(parents=True)
        return IssueManager(str(tmp_path))

    def test_create_issue(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        issue = mgr.create_issue("Login Feature", description="OAuth login")
        assert issue.id == 1
        assert issue.title == "Login Feature"
        assert issue.status == "open"

    def test_auto_increment_id(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        i1 = mgr.create_issue("First")
        i2 = mgr.create_issue("Second")
        i3 = mgr.create_issue("Third")
        assert i1.id == 1
        assert i2.id == 2
        assert i3.id == 3

    def test_get_issue(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        mgr.create_issue("Test Issue", description="A test")
        issue = mgr.get_issue(1)
        assert issue is not None
        assert issue.title == "Test Issue"

    def test_get_nonexistent(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        assert mgr.get_issue(999) is None

    def test_list_issues(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        mgr.create_issue("A")
        mgr.create_issue("B")
        mgr.create_issue("C")
        issues = mgr.list_issues()
        assert len(issues) == 3

    def test_list_filter_by_status(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        mgr.create_issue("Open1")
        mgr.create_issue("Open2")
        i3 = mgr.create_issue("Done1")
        mgr.close_issue(i3.id)

        open_issues = mgr.list_issues(status="open")
        assert len(open_issues) == 2
        closed = mgr.list_issues(status="closed")
        assert len(closed) == 1

    def test_list_filter_by_assignee(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        i1 = mgr.create_issue("Task1")
        i2 = mgr.create_issue("Task2")
        mgr.assign_issue(i1.id, "engineer")
        mgr.assign_issue(i2.id, "strategist")

        eng_issues = mgr.list_issues(assignee="engineer")
        assert len(eng_issues) == 1
        assert eng_issues[0].title == "Task1"

    def test_update_issue(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        mgr.create_issue("Original Title")
        updated = mgr.update_issue(1, title="New Title", priority="critical")
        assert updated.title == "New Title"
        assert updated.priority == "critical"

        # Verify persistence
        reloaded = mgr.get_issue(1)
        assert reloaded.title == "New Title"

    def test_assign_issue(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        mgr.create_issue("Task")
        assigned = mgr.assign_issue(1, "engineer")
        assert assigned.assignee == "engineer"
        assert assigned.status == "in_progress"

    def test_close_issue(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        mgr.create_issue("Task")
        closed = mgr.close_issue(1)
        assert closed.status == "closed"

    def test_acceptance_criteria(self, tmp_path):
        mgr = self._make_manager(tmp_path)
        issue = mgr.create_issue(
            "API",
            acceptance_criteria=["Returns 200", "Has JSON body"],
        )
        reloaded = mgr.get_issue(issue.id)
        assert len(reloaded.acceptance_criteria) == 2
        assert "Returns 200" in reloaded.acceptance_criteria
