"""Strategist Agent - Documentation & UX role (Issue #9)

The Strategist Agent handles everything user-facing that isn't code:
1. README and documentation
2. CHANGELOG and release notes
3. Demo scripts and walkthroughs
4. User experience review
5. Proactive quality gap identification
"""

import logging
from typing import Optional

from .base_agent import BaseAgent
from agent_team.mailbox import Message

logger = logging.getLogger(__name__)


class StrategistAgent(BaseAgent):
    """Strategist Agent: docs, README, user experience, quality.

    Tools: file read/write + send_message + check_mailbox + reply_message + web_search
    """

    SYSTEM_PROMPT = """You are the Strategist agent in a three-agent product team.

Your responsibilities:
1. Write and maintain README.md with clear usage instructions
2. Create and update documentation (API docs, architecture, guides)
3. Write CHANGELOG entries for completed features
4. Create demo scripts that showcase the product
5. Review user-facing text for clarity and professionalism
6. Proactively identify quality gaps (missing docs, unclear instructions, UX issues)

Communication rules:
- Receive doc tasks from PM via assigned Issues
- Send completion reports to PM when done
- Proactively send suggestions to PM when you spot quality gaps
- Coordinate with Engineer when you need to understand code behavior

You do NOT write application code. You write everything that surrounds the code:
documentation, guides, demos, and user-facing text."""

    def __init__(self, name: str = "strategist"):
        super().__init__(name=name, role="strategist")

    def handle_message(self, msg: Message):
        """Strategist processes messages from PM/Engineer."""
        logger.info(f"[Strategist] Message from {msg.sender}: {msg.subject}")

        if msg.sender == "engineer":
            logger.info(f"[Strategist] Engineer update — may need doc refresh")

    def doc_task_prompt(self, issue_id: int) -> str:
        """Create an LLM prompt for a documentation task.

        Args:
            issue_id: Issue to work on

        Returns:
            Formatted prompt for the LLM
        """
        issue = self.issue_manager.get_issue(issue_id)
        if not issue:
            return f"Issue #{issue_id} not found."

        criteria = "\n".join(f"- {c}" for c in issue.acceptance_criteria)

        return f"""You are working on documentation Issue #{issue.id}: {issue.title}

Description:
{issue.description}

Acceptance Criteria:
{criteria}

Guidelines:
- Write clear, concise documentation
- Use code examples where appropriate
- Structure with headers for scannability
- Target audience: developers using this product for the first time
- When done, use send_message to notify PM"""

    def audit_docs_prompt(self, project_dir: str) -> str:
        """Create an LLM prompt for auditing project documentation quality.

        Args:
            project_dir: Root project directory

        Returns:
            Formatted prompt for the LLM
        """
        return f"""Audit the documentation quality of this project at {project_dir}.

Check for:
1. README.md exists and has: description, installation, quick start, usage examples
2. All public APIs/features are documented
3. No broken links or references to nonexistent files
4. Code examples are runnable and up-to-date
5. CHANGELOG exists with recent entries

For each gap found, send a message to PM with a suggested Issue to create.
Be specific about what's missing and where."""

    def report_completion(self, issue_id: int, summary: str):
        """Report doc task completion to PM.

        Args:
            issue_id: Completed issue ID
            summary: What was written/updated
        """
        issue = self.issue_manager.get_issue(issue_id)
        if not issue:
            return

        self.mailbox.send_message(
            recipient="pm",
            subject=f"Docs complete: Issue #{issue_id} {issue.title}",
            body=f"Documentation for Issue #{issue_id} is ready.\n\nSummary:\n{summary}",
        )
        self.issue_manager.update_issue(issue_id, status="review")
        logger.info(f"[Strategist] Reported Issue #{issue_id} docs complete")

    def suggest_improvement(self, area: str, suggestion: str):
        """Proactively suggest a quality improvement to PM.

        Args:
            area: Area of concern (e.g., "README", "API docs", "demo")
            suggestion: What should be improved
        """
        self.mailbox.send_message(
            recipient="pm",
            subject=f"Quality suggestion: {area}",
            body=f"I noticed a quality gap in {area}.\n\nSuggestion:\n{suggestion}",
        )
        logger.info(f"[Strategist] Sent quality suggestion about {area}")
