"""Mailbox - File-system based async messaging between agents (Issue #2)

Messages are stored as JSON files in .agent-team/mailbox/{recipient}/.
Each message has a unique ID, sender, recipient, subject, body, and timestamp.
Messages are marked as read by renaming the file with a .read suffix.
"""

import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class Message:
    """A single mailbox message."""
    id: str
    sender: str
    recipient: str
    subject: str
    body: str
    timestamp: float
    reply_to: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, text: str) -> "Message":
        return cls.from_dict(json.loads(text))


class Mailbox:
    """Async message passing between agents via filesystem JSON files.

    Directory layout:
        .agent-team/mailbox/{agent_name}/
            {message_id}.json       # unread message
            {message_id}.json.read  # read message (marker file)
    """

    def __init__(self, base_dir: str, agent_name: str):
        """Initialize mailbox for a specific agent.

        Args:
            base_dir: Root directory of the agent-team project (contains .agent-team/)
            agent_name: Name of this agent (e.g. "pm", "engineer", "strategist")
        """
        self.base_dir = Path(base_dir)
        self.agent_name = agent_name
        self.mailbox_root = self.base_dir / ".agent-team" / "mailbox"
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Ensure mailbox directories exist for this agent."""
        inbox = self.mailbox_root / self.agent_name
        inbox.mkdir(parents=True, exist_ok=True)

    def _ensure_recipient_dir(self, recipient: str):
        """Ensure mailbox directory exists for recipient."""
        (self.mailbox_root / recipient).mkdir(parents=True, exist_ok=True)

    def send_message(self, recipient: str, subject: str, body: str,
                     reply_to: Optional[str] = None,
                     metadata: Optional[dict] = None) -> Message:
        """Send a message to another agent.

        Args:
            recipient: Target agent name
            subject: Message subject
            body: Message body
            reply_to: Optional message ID this is replying to
            metadata: Optional extra metadata

        Returns:
            The sent Message object
        """
        self._ensure_recipient_dir(recipient)

        msg = Message(
            id=str(uuid.uuid4())[:8],
            sender=self.agent_name,
            recipient=recipient,
            subject=subject,
            body=body,
            timestamp=time.time(),
            reply_to=reply_to,
            metadata=metadata or {},
        )

        msg_path = self.mailbox_root / recipient / f"{msg.id}.json"
        msg_path.write_text(msg.to_json(), encoding="utf-8")
        return msg

    def check_mailbox(self, unread_only: bool = True) -> list[Message]:
        """Check this agent's inbox for messages.

        Args:
            unread_only: If True, only return unread messages

        Returns:
            List of Message objects, sorted by timestamp (oldest first)
        """
        inbox = self.mailbox_root / self.agent_name
        if not inbox.exists():
            return []

        messages = []
        for f in inbox.iterdir():
            if f.name.endswith(".read"):
                continue
            if not f.name.endswith(".json"):
                continue
            if unread_only:
                read_marker = inbox / f"{f.name}.read"
                if read_marker.exists():
                    continue
            try:
                msg = Message.from_json(f.read_text(encoding="utf-8"))
                messages.append(msg)
            except (json.JSONDecodeError, TypeError, KeyError):
                continue

        messages.sort(key=lambda m: m.timestamp)
        return messages

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read by creating a .read marker file.

        Args:
            message_id: The message ID to mark as read

        Returns:
            True if successfully marked, False if message not found
        """
        inbox = self.mailbox_root / self.agent_name
        msg_path = inbox / f"{message_id}.json"
        read_marker = inbox / f"{message_id}.json.read"

        if msg_path.exists():
            read_marker.touch()
            return True
        return False

    def reply_message(self, original_msg: Message, body: str,
                      subject: Optional[str] = None) -> Message:
        """Reply to a received message.

        Args:
            original_msg: The message being replied to
            body: Reply body
            subject: Optional subject override (defaults to "Re: {original_subject}")

        Returns:
            The sent reply Message
        """
        reply_subject = subject or f"Re: {original_msg.subject}"
        return self.send_message(
            recipient=original_msg.sender,
            subject=reply_subject,
            body=body,
            reply_to=original_msg.id,
        )

    def get_all_messages(self) -> list[Message]:
        """Get all messages (read and unread) in this agent's inbox."""
        return self.check_mailbox(unread_only=False)

    def get_unread_count(self) -> int:
        """Get count of unread messages."""
        return len(self.check_mailbox(unread_only=True))
