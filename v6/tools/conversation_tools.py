#!/usr/bin/env python3
# tools/conversation_tools.py - Conversation management tools
# V4 version: Tools for conversation compression and statistics

from .base import BaseTool
import json


class CompactConversationTool(BaseTool):
    """
    Compact conversation history to reduce token usage and manage context
    """

    def __init__(self, agent_instance=None):
        """
        Initialize with optional agent instance reference for accessing messages
        """
        self.agent_instance = agent_instance

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "compact_conversation",
                "description": "Compact conversation history to reduce token usage and manage context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keep_recent": {
                            "type": "integer",
                            "description": "Number of recent uncompressed messages to keep",
                            "default": 10
                        },
                        "max_total": {
                            "type": "integer",
                            "description": "Maximum total messages after compression",
                            "default": 15
                        },
                        "force_compact": {
                            "type": "boolean",
                            "description": "Force compression even if within limits",
                            "default": False
                        }
                    }
                }
            }
        }

    def execute(self, input_data):
        if not self.agent_instance:
            return "❌ Error: Agent instance not available for conversation compaction"

        keep_recent = input_data.get("keep_recent", 10)
        max_total = input_data.get("max_total", 15)
        force_compact = input_data.get("force_compact", False)

        old_count = len(self.agent_instance.messages)

        if not force_compact and old_count <= max_total:
            return f"ℹ️  Conversation length ({old_count}) is within limits ({max_total}). Use force_compact=true to compress anyway."

        # Use agent's compression method
        compacted = self.agent_instance._compact_messages_conservative(
            keep_recent=keep_recent,
            max_total=max_total
        )

        if compacted and len(compacted) < old_count:
            self.agent_instance.messages = compacted
            self.agent_instance.compressed_count += 1
            return f"✅ Conversation compacted: {old_count} → {len(compacted)} messages (kept {keep_recent} recent, max {max_total})"
        else:
            return f"ℹ️  No compression performed. Current: {old_count} messages"


class ConversationStatsTool(BaseTool):
    """
    Get statistics about current conversation length and token usage
    """

    def __init__(self, agent_instance=None):
        """
        Initialize with optional agent instance reference for accessing messages
        """
        self.agent_instance = agent_instance

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "conversation_stats",
                "description": "Get statistics about current conversation length and token usage",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }

    def execute(self, input_data):
        if not self.agent_instance:
            return "❌ Error: Agent instance not available for conversation statistics"

        messages = self.agent_instance.messages
        message_count = len(messages)

        # Count by role
        role_counts = {}
        for msg in messages:
            role = msg.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1

        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        total_chars = sum(len(json.dumps(msg)) for msg in messages)
        estimated_tokens = total_chars // 4

        # Get compression settings
        threshold = self.agent_instance.auto_compact_threshold
        keep_recent = self.agent_instance.keep_recent_messages
        compressed_count = self.agent_instance.compressed_count

        stats = {
            "message_count": message_count,
            "estimated_tokens": estimated_tokens,
            "role_distribution": role_counts,
            "compression_threshold": threshold,
            "keep_recent_messages": keep_recent,
            "compression_count": compressed_count,
            "above_threshold": message_count > threshold
        }

        # Format output
        result = f"📊 Conversation Statistics:\n"
        result += f"   • Total messages: {message_count}\n"
        result += f"   • Estimated tokens: ~{estimated_tokens}\n"
        result += f"   • Role distribution:\n"
        for role, count in sorted(role_counts.items()):
            result += f"     - {role}: {count}\n"
        result += f"   • Compression threshold: {threshold} messages\n"
        result += f"   • Keep recent: {keep_recent} messages\n"
        result += f"   • Compressions performed: {compressed_count}\n"
        result += f"   • Above threshold: {'Yes' if stats['above_threshold'] else 'No'}"

        return result
