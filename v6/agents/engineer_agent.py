"""Engineer Agent - Software Engineer role (Issue #8)

The Engineer Agent is the builder. It:
1. Receives assigned Issues from the PM
2. Reads issue description and acceptance criteria
3. Implements the solution using V5's full toolset (file ops, search, bash, etc.)
4. Runs tests and verifies acceptance criteria
5. Reports completion back to PM via mailbox
"""

import logging
from typing import Optional

from .base_agent import BaseAgent
from agent_team.mailbox import Message

logger = logging.getLogger(__name__)


class EngineerAgent(BaseAgent):
    """Engineer Agent: execute issues strictly within assigned scope.

    Tools: V5 all 15 tools + send_message + check_mailbox + reply_message
    """

    SYSTEM_PROMPT = """You are the Engineer agent in a three-agent product team.

Your responsibilities:
1. Pick up Issues assigned to you (check with check_progress)
2. Read the issue description and acceptance criteria carefully
3. Implement the solution using available tools (file operations, bash, search, etc.)
4. Test your implementation to verify acceptance criteria
5. Send a completion message to the PM when done

Strict rules:
- ONLY work on Issues assigned to you
- Do NOT change scope or add features not in the Issue
- If blocked or unclear, send a message to PM asking for clarification
- Always test before reporting completion
- Report ALL issues honestly — never hide failures

You are a disciplined engineer. You execute precisely what is asked."""

    def __init__(self, name: str = "engineer"):
        super().__init__(name=name, role="engineer")

    def handle_message(self, msg: Message):
        """Engineer processes messages from PM (assignments, feedback)."""
        logger.info(f"[Engineer] Message from {msg.sender}: {msg.subject}")

        if "assign" in msg.subject.lower():
            logger.info(f"[Engineer] New assignment from PM")
        elif "feedback" in msg.subject.lower() or "revision" in msg.subject.lower():
            logger.info(f"[Engineer] Revision request from PM")

    def work_on_issue_prompt(self, issue_id: int) -> str:
        """Create an LLM prompt for working on a specific issue.

        Args:
            issue_id: Issue to work on

        Returns:
            Formatted prompt for the LLM
        """
        issue = self.issue_manager.get_issue(issue_id)
        if not issue:
            return f"Issue #{issue_id} not found."

        criteria = "\n".join(f"- {c}" for c in issue.acceptance_criteria)

        return f"""You are working on Issue #{issue.id}: {issue.title}

Priority: {issue.priority}
Labels: {', '.join(issue.labels) if issue.labels else 'none'}

Description:
{issue.description}

Acceptance Criteria:
{criteria}

Instructions:
1. Read any existing code relevant to this issue
2. Implement the solution step by step
3. Test your implementation against each acceptance criterion
4. When all criteria pass, use send_message to notify PM that the issue is complete
5. Include a summary of what you built and how to verify it

Stay strictly within the scope of this issue. Do not add extra features."""

    def report_completion(self, issue_id: int, summary: str):
        """Report issue completion to PM via mailbox.

        Args:
            issue_id: Completed issue ID
            summary: Summary of work done
        """
        issue = self.issue_manager.get_issue(issue_id)
        if not issue:
            logger.warning(f"[Engineer] Cannot report: Issue #{issue_id} not found")
            return

        self.mailbox.send_message(
            recipient="pm",
            subject=f"Issue #{issue_id} complete: {issue.title}",
            body=f"Completed Issue #{issue_id}: {issue.title}\n\nSummary:\n{summary}",
        )

        # Update issue status
        self.issue_manager.update_issue(issue_id, status="review")
        logger.info(f"[Engineer] Reported Issue #{issue_id} complete, moved to review")

    def report_blocked(self, issue_id: int, reason: str):
        """Report that work on an issue is blocked.

        Args:
            issue_id: Blocked issue ID
            reason: Why the issue is blocked
        """
        self.mailbox.send_message(
            recipient="pm",
            subject=f"Blocked on Issue #{issue_id}",
            body=f"I'm blocked on Issue #{issue_id}.\n\nReason: {reason}\n\nPlease advise.",
        )
        logger.info(f"[Engineer] Reported blocked on Issue #{issue_id}: {reason}")
