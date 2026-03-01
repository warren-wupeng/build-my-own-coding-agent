"""PM Agent tools - Issue and task management tools (Issue #7)

Tools specific to the PM role: create_issue, assign_task, check_progress, read_sop.
Follows V5 BaseTool pattern.
"""

from .base import BaseTool


class CreateIssueTool(BaseTool):
    """Create a new project issue."""

    def __init__(self):
        self.issue_manager = None  # Set by agent during initialization

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "create_issue",
                "description": "Create a new project issue with title, description, priority, and acceptance criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Issue title (concise, actionable)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of what needs to be done"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"],
                            "description": "Issue priority level"
                        },
                        "labels": {
                            "type": "string",
                            "description": "Comma-separated labels (e.g. 'feature,auth,backend')"
                        },
                        "acceptance_criteria": {
                            "type": "string",
                            "description": "Newline-separated acceptance criteria"
                        }
                    },
                    "required": ["title", "description"]
                }
            }
        }

    def execute(self, input_data):
        if not self.issue_manager:
            return "Error: IssueManager not initialized."

        labels = []
        if input_data.get("labels"):
            labels = [l.strip() for l in input_data["labels"].split(",")]

        criteria = []
        if input_data.get("acceptance_criteria"):
            criteria = [c.strip() for c in input_data["acceptance_criteria"].split("\n") if c.strip()]

        issue = self.issue_manager.create_issue(
            title=input_data["title"],
            description=input_data.get("description", ""),
            priority=input_data.get("priority", "medium"),
            created_by="pm",
            labels=labels,
            acceptance_criteria=criteria,
        )
        return f"Created Issue #{issue.id}: {issue.title} (priority: {issue.priority})"


class AssignTaskTool(BaseTool):
    """Assign an issue to an agent."""

    def __init__(self):
        self.issue_manager = None

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "assign_task",
                "description": "Assign an issue to an agent (engineer or strategist).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "integer",
                            "description": "Issue number to assign"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Agent to assign to ('engineer' or 'strategist')"
                        }
                    },
                    "required": ["issue_id", "assignee"]
                }
            }
        }

    def execute(self, input_data):
        if not self.issue_manager:
            return "Error: IssueManager not initialized."

        issue = self.issue_manager.assign_issue(
            input_data["issue_id"],
            input_data["assignee"],
        )
        if not issue:
            return f"Error: Issue #{input_data['issue_id']} not found."
        return f"Assigned Issue #{issue.id} to {issue.assignee} (status: {issue.status})"


class CheckProgressTool(BaseTool):
    """Check progress of all or specific issues."""

    def __init__(self):
        self.issue_manager = None

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "check_progress",
                "description": "Check progress of project issues. Can filter by status or assignee.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["open", "in_progress", "review", "done", "closed"],
                            "description": "Filter by status"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Filter by assignee"
                        }
                    },
                    "required": []
                }
            }
        }

    def execute(self, input_data):
        if not self.issue_manager:
            return "Error: IssueManager not initialized."

        issues = self.issue_manager.list_issues(
            status=input_data.get("status"),
            assignee=input_data.get("assignee"),
        )

        if not issues:
            return "No issues found matching filters."

        lines = [f"Found {len(issues)} issue(s):\n"]
        for issue in issues:
            assignee = issue.assignee or "unassigned"
            lines.append(
                f"  #{issue.id} [{issue.status}] {issue.title} "
                f"(assigned: {assignee}, priority: {issue.priority})"
            )
        return "\n".join(lines)


class ReadSOPTool(BaseTool):
    """Read and parse an SOP document."""

    def __init__(self):
        self.sop_parser = None
        self.sops_dir = None

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "read_sop",
                "description": "Read a Standard Operating Procedure document. Lists available SOPs or reads a specific one.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "SOP filename to read. Omit to list all available SOPs."
                        }
                    },
                    "required": []
                }
            }
        }

    def execute(self, input_data):
        if not self.sop_parser:
            return "Error: SOPParser not initialized."

        filename = input_data.get("filename")

        if not filename:
            # List available SOPs
            if not self.sops_dir:
                return "No SOPs directory configured."
            sops = self.sop_parser.list_sops(self.sops_dir)
            if not sops:
                return "No SOP files found."
            lines = ["Available SOPs:"]
            for path in sops:
                lines.append(f"  - {path.split('/')[-1]}")
            return "\n".join(lines)

        # Read specific SOP
        import os
        if self.sops_dir:
            filepath = os.path.join(self.sops_dir, filename)
        else:
            filepath = filename

        try:
            sop = self.sop_parser.parse_file(filepath)
            return sop.to_instruction_text()
        except FileNotFoundError:
            return f"SOP file not found: {filename}"
