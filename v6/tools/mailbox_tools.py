"""Mailbox tools - Agent-to-agent communication tools (Issue #2)

Follows V5 BaseTool pattern for tool definition and registration.
"""

from .base import BaseTool


class SendMessageTool(BaseTool):
    """Send a message to another agent via the mailbox system."""

    def __init__(self):
        self.mailbox = None  # Set by agent during initialization

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "send_message",
                "description": "Send a message to another agent in the team. Use this to communicate tasks, updates, questions, or results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Target agent name (e.g. 'pm', 'engineer', 'strategist')"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Message subject line"
                        },
                        "body": {
                            "type": "string",
                            "description": "Message body content"
                        },
                        "reply_to": {
                            "type": "string",
                            "description": "Optional: message ID this is replying to"
                        }
                    },
                    "required": ["recipient", "subject", "body"]
                }
            }
        }

    def execute(self, input_data):
        if not self.mailbox:
            return "Error: Mailbox not initialized. Agent setup required."

        recipient = input_data["recipient"]
        subject = input_data["subject"]
        body = input_data["body"]
        reply_to = input_data.get("reply_to")

        msg = self.mailbox.send_message(
            recipient=recipient,
            subject=subject,
            body=body,
            reply_to=reply_to,
        )
        return f"Message sent to {recipient}: [{msg.id}] {subject}"


class CheckMailboxTool(BaseTool):
    """Check the agent's mailbox for new messages."""

    def __init__(self):
        self.mailbox = None

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "check_mailbox",
                "description": "Check your mailbox for new (unread) messages from other agents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_read": {
                            "type": "boolean",
                            "description": "If true, also include already-read messages. Default: false"
                        }
                    },
                    "required": []
                }
            }
        }

    def execute(self, input_data):
        if not self.mailbox:
            return "Error: Mailbox not initialized. Agent setup required."

        include_read = input_data.get("include_read", False)
        messages = self.mailbox.check_mailbox(unread_only=not include_read)

        if not messages:
            return "No new messages."

        lines = [f"You have {len(messages)} message(s):\n"]
        for msg in messages:
            status = ""
            read_marker = self.mailbox.mailbox_root / self.mailbox.agent_name / f"{msg.id}.json.read"
            if read_marker.exists():
                status = " [read]"
            lines.append(
                f"  [{msg.id}]{status} From: {msg.sender} | Subject: {msg.subject}\n"
                f"    {msg.body[:200]}{'...' if len(msg.body) > 200 else ''}"
            )

        return "\n".join(lines)


class ReplyMessageTool(BaseTool):
    """Reply to a specific message."""

    def __init__(self):
        self.mailbox = None

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "reply_message",
                "description": "Reply to a specific message by its ID. The reply is sent back to the original sender.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "The ID of the message to reply to"
                        },
                        "body": {
                            "type": "string",
                            "description": "Reply body content"
                        }
                    },
                    "required": ["message_id", "body"]
                }
            }
        }

    def execute(self, input_data):
        if not self.mailbox:
            return "Error: Mailbox not initialized. Agent setup required."

        message_id = input_data["message_id"]
        body = input_data["body"]

        # Find the original message
        all_msgs = self.mailbox.get_all_messages()
        original = None
        for msg in all_msgs:
            if msg.id == message_id:
                original = msg
                break

        if not original:
            return f"Error: Message {message_id} not found in mailbox."

        reply = self.mailbox.reply_message(original, body)
        self.mailbox.mark_as_read(message_id)
        return f"Reply sent to {original.sender}: [{reply.id}] {reply.subject}"
