"""IssueManager - Issue lifecycle management (Issue #6)

Issues are stored as Markdown files in .agent-team/issues/.
Each issue has a YAML-style frontmatter header for metadata.

File format:
    .agent-team/issues/{number}-{slug}.md

    ---
    id: 1
    title: Implement login
    status: open
    assignee: engineer
    priority: high
    created_by: pm
    created_at: 1709300000.0
    updated_at: 1709300000.0
    labels: [feature, auth]
    ---

    ## Description
    ...

    ## Acceptance Criteria
    ...
"""

import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


VALID_STATUSES = ("open", "in_progress", "review", "done", "closed")
VALID_PRIORITIES = ("low", "medium", "high", "critical")


@dataclass
class Issue:
    """A single project issue."""
    id: int
    title: str
    status: str = "open"
    assignee: Optional[str] = None
    priority: str = "medium"
    created_by: str = "system"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    labels: list[str] = field(default_factory=list)
    description: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)

    @property
    def slug(self) -> str:
        """Generate URL-safe slug from title."""
        s = self.title.lower()
        s = re.sub(r"[^a-z0-9\s-]", "", s)
        s = re.sub(r"[\s]+", "-", s)
        return s[:50].strip("-")

    @property
    def filename(self) -> str:
        return f"{self.id:03d}-{self.slug}.md"

    def to_markdown(self) -> str:
        """Serialize issue to Markdown with frontmatter."""
        lines = [
            "---",
            f"id: {self.id}",
            f"title: {self.title}",
            f"status: {self.status}",
            f"assignee: {self.assignee or 'unassigned'}",
            f"priority: {self.priority}",
            f"created_by: {self.created_by}",
            f"created_at: {self.created_at}",
            f"updated_at: {self.updated_at}",
            f"labels: [{', '.join(self.labels)}]",
            "---",
            "",
            f"# Issue #{self.id}: {self.title}",
            "",
        ]

        if self.description:
            lines.append("## Description")
            lines.append("")
            lines.append(self.description)
            lines.append("")

        if self.acceptance_criteria:
            lines.append("## Acceptance Criteria")
            lines.append("")
            for criterion in self.acceptance_criteria:
                lines.append(f"- [ ] {criterion}")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, text: str) -> "Issue":
        """Parse issue from Markdown with frontmatter."""
        # Extract frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            raise ValueError("Invalid issue format: no frontmatter found")

        frontmatter = fm_match.group(1)
        body = text[fm_match.end():].strip()

        # Parse frontmatter fields
        fields = {}
        for line in frontmatter.split("\n"):
            kv = re.match(r"^(\w+):\s*(.+)$", line.strip())
            if kv:
                key, value = kv.group(1), kv.group(2).strip()
                fields[key] = value

        # Parse labels
        labels_str = fields.get("labels", "[]")
        labels_match = re.match(r"\[(.*?)\]", labels_str)
        labels = []
        if labels_match and labels_match.group(1).strip():
            labels = [l.strip() for l in labels_match.group(1).split(",")]

        # Parse body sections
        description = ""
        acceptance_criteria = []

        desc_match = re.search(r"## Description\n\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()

        ac_match = re.search(r"## Acceptance Criteria\n\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
        if ac_match:
            for line in ac_match.group(1).strip().split("\n"):
                line = line.strip()
                # Remove checkbox prefix
                line = re.sub(r"^- \[[ x]\] ", "", line)
                if line:
                    acceptance_criteria.append(line)

        assignee = fields.get("assignee")
        if assignee == "unassigned":
            assignee = None

        return cls(
            id=int(fields.get("id", 0)),
            title=fields.get("title", ""),
            status=fields.get("status", "open"),
            assignee=assignee,
            priority=fields.get("priority", "medium"),
            created_by=fields.get("created_by", "system"),
            created_at=float(fields.get("created_at", 0)),
            updated_at=float(fields.get("updated_at", 0)),
            labels=labels,
            description=description,
            acceptance_criteria=acceptance_criteria,
        )


class IssueManager:
    """Create, assign, update, and close issues stored as Markdown files."""

    def __init__(self, base_dir: str):
        """Initialize issue manager.

        Args:
            base_dir: Root directory of the agent-team project
        """
        self.base_dir = Path(base_dir)
        self.issues_dir = self.base_dir / ".agent-team" / "issues"
        self.issues_dir.mkdir(parents=True, exist_ok=True)
        self._next_id = self._compute_next_id()

    def _compute_next_id(self) -> int:
        """Determine next available issue ID."""
        max_id = 0
        for f in self.issues_dir.glob("*.md"):
            match = re.match(r"^(\d+)-", f.name)
            if match:
                max_id = max(max_id, int(match.group(1)))
        return max_id + 1

    def create_issue(self, title: str, description: str = "",
                     priority: str = "medium", created_by: str = "pm",
                     labels: Optional[list[str]] = None,
                     acceptance_criteria: Optional[list[str]] = None) -> Issue:
        """Create a new issue.

        Args:
            title: Issue title
            description: Detailed description
            priority: low/medium/high/critical
            created_by: Agent that created this issue
            labels: Optional list of labels
            acceptance_criteria: Optional list of acceptance criteria

        Returns:
            Created Issue object
        """
        issue = Issue(
            id=self._next_id,
            title=title,
            description=description,
            priority=priority,
            created_by=created_by,
            labels=labels or [],
            acceptance_criteria=acceptance_criteria or [],
        )

        self._save_issue(issue)
        self._next_id += 1
        return issue

    def get_issue(self, issue_id: int) -> Optional[Issue]:
        """Get an issue by ID.

        Args:
            issue_id: The issue number

        Returns:
            Issue object or None
        """
        for f in self.issues_dir.glob(f"{issue_id:03d}-*.md"):
            text = f.read_text(encoding="utf-8")
            return Issue.from_markdown(text)
        return None

    def list_issues(self, status: Optional[str] = None,
                    assignee: Optional[str] = None) -> list[Issue]:
        """List issues with optional filters.

        Args:
            status: Filter by status
            assignee: Filter by assignee

        Returns:
            List of matching Issues, sorted by ID
        """
        issues = []
        for f in sorted(self.issues_dir.glob("*.md")):
            try:
                issue = Issue.from_markdown(f.read_text(encoding="utf-8"))
                if status and issue.status != status:
                    continue
                if assignee and issue.assignee != assignee:
                    continue
                issues.append(issue)
            except (ValueError, KeyError):
                continue
        return issues

    def update_issue(self, issue_id: int, **kwargs) -> Optional[Issue]:
        """Update an issue's fields.

        Args:
            issue_id: Issue to update
            **kwargs: Fields to update (status, assignee, priority, description, etc.)

        Returns:
            Updated Issue or None if not found
        """
        issue = self.get_issue(issue_id)
        if not issue:
            return None

        # Delete old file (slug might change if title changed)
        self._delete_file(issue)

        for key, value in kwargs.items():
            if hasattr(issue, key):
                setattr(issue, key, value)

        issue.updated_at = time.time()
        self._save_issue(issue)
        return issue

    def assign_issue(self, issue_id: int, assignee: str) -> Optional[Issue]:
        """Assign an issue to an agent.

        Args:
            issue_id: Issue to assign
            assignee: Agent name to assign to

        Returns:
            Updated Issue or None
        """
        return self.update_issue(issue_id, assignee=assignee, status="in_progress")

    def close_issue(self, issue_id: int) -> Optional[Issue]:
        """Close an issue (mark as done).

        Args:
            issue_id: Issue to close

        Returns:
            Updated Issue or None
        """
        return self.update_issue(issue_id, status="closed")

    def _save_issue(self, issue: Issue):
        """Write issue to disk."""
        filepath = self.issues_dir / issue.filename
        filepath.write_text(issue.to_markdown(), encoding="utf-8")

    def _delete_file(self, issue: Issue):
        """Delete issue file from disk."""
        for f in self.issues_dir.glob(f"{issue.id:03d}-*.md"):
            f.unlink()
