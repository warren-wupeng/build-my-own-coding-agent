"""PM Agent - Product Manager role (Issue #7)

The PM Agent is the team leader. It:
1. Receives user product descriptions
2. Breaks them down into actionable Issues
3. Assigns Issues to Engineer and Strategist
4. Monitors progress and reviews deliverables
5. Communicates with the user
"""

import logging
from typing import Optional

from .base_agent import BaseAgent
from agent_team.mailbox import Message

logger = logging.getLogger(__name__)


class PMAgent(BaseAgent):
    """PM Agent: understand user intent -> decompose issues -> assign -> accept.

    Tools: create_issue, assign_task, check_progress, send_message, read_sop
    """

    SYSTEM_PROMPT = """You are the PM (Product Manager) agent in a three-agent product team.

Your responsibilities:
1. Understand the user's product description and requirements
2. Break down the product into implementable Issues with clear acceptance criteria
3. Assign code Issues to the Engineer agent, documentation Issues to the Strategist agent
4. Monitor progress by checking issue status and reading agent messages
5. Review completed work against acceptance criteria
6. Report final results back to the user

Communication rules:
- Use send_message to communicate with engineer and strategist
- Use create_issue to create trackable work items
- Use assign_task to delegate work
- Use check_progress to monitor the team
- Always include acceptance criteria in issues
- Be specific and unambiguous in requirements

You do NOT write code yourself. You manage the team."""

    def __init__(self, name: str = "pm"):
        super().__init__(name=name, role="pm")

    def handle_message(self, msg: Message):
        """PM processes messages from Engineer/Strategist (status updates, questions)."""
        logger.info(f"[PM] Message from {msg.sender}: {msg.subject}")

        # Track which issues are being reported on
        if "done" in msg.subject.lower() or "complete" in msg.subject.lower():
            logger.info(f"[PM] Completion report from {msg.sender}")
        elif "blocked" in msg.subject.lower() or "question" in msg.subject.lower():
            logger.info(f"[PM] {msg.sender} needs help: {msg.subject}")

    def decompose_product(self, product_description: str) -> str:
        """Create an LLM prompt for decomposing a product into issues.

        This generates the prompt that will be sent to the LLM to
        break down a user's product idea into actionable issues.

        Args:
            product_description: User's description of what to build

        Returns:
            Formatted prompt for the LLM
        """
        return f"""The user wants to build the following product:

---
{product_description}
---

Break this down into implementable Issues. For each issue:
1. Write a clear title
2. Write a description with enough detail for an engineer to implement
3. List specific acceptance criteria (testable conditions)
4. Set priority (critical/high/medium/low)
5. Suggest assignee: "engineer" for code tasks, "strategist" for docs/UX tasks

Use the create_issue tool for each issue, then use assign_task to assign them.
Create issues in dependency order (foundations first, then features, then polish)."""

    def review_prompt(self, issue_id: int) -> str:
        """Create an LLM prompt for reviewing a completed issue.

        Args:
            issue_id: The issue to review

        Returns:
            Formatted prompt for the LLM
        """
        issue = self.issue_manager.get_issue(issue_id)
        if not issue:
            return f"Issue #{issue_id} not found."

        criteria = "\n".join(f"- {c}" for c in issue.acceptance_criteria)
        return f"""Review Issue #{issue.id}: {issue.title}

Acceptance Criteria:
{criteria}

Check if all criteria are met. If yes, close the issue.
If not, send a message to {issue.assignee or 'the assignee'} with specific feedback."""

    def get_team_status(self) -> dict:
        """Get a summary of the team's current status.

        Returns:
            Dict with agent statuses and issue counts
        """
        result = {
            "agents": {},
            "issues": {
                "total": 0,
                "open": 0,
                "in_progress": 0,
                "done": 0,
                "closed": 0,
            }
        }

        # Agent statuses
        for agent_name in ["pm", "engineer", "strategist"]:
            status = self.shared_state.get_agent_status(agent_name)
            if status:
                result["agents"][agent_name] = {
                    "state": status.state,
                    "current_task": status.current_task,
                    "tick_count": status.tick_count,
                }

        # Issue counts
        all_issues = self.issue_manager.list_issues()
        result["issues"]["total"] = len(all_issues)
        for issue in all_issues:
            if issue.status in result["issues"]:
                result["issues"][issue.status] += 1

        return result
