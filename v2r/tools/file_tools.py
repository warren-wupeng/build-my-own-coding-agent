#!/usr/bin/env python3
# tools/file_tools.py - File operation tools (V2 functionality in V3 architecture)

import os
from .base import BaseTool


class ReadFileTool(BaseTool):
    """Read file contents tool - V2 functionality"""

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read file contents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"}
                    },
                    "required": ["path"]
                }
            }
        }

    def execute(self, input_data):
        """Execute file reading - same logic as V2"""
        try:
            with open(input_data["path"], "r", encoding="utf-8") as f:
                content = f.read()
            return f"✅ Successfully read {input_data['path']} ({len(content)} characters):\n{content}"
        except Exception as e:
            return f"❌ Failed to read file: {e}"


class WriteFileTool(BaseTool):
    """Write content to file tool - V2 functionality"""

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            }
        }

    def execute(self, input_data):
        """Execute file writing - same logic as V2"""
        try:
            with open(input_data["path"], "w", encoding="utf-8") as f:
                f.write(input_data["content"])
            return f"✅ Successfully written to {input_data['path']} ({len(input_data['content'])} characters)"
        except Exception as e:
            return f"❌ Failed to write file: {e}"


class EditFileTool(BaseTool):
    """Make precise edits to files by replacing unique strings - V2 functionality"""

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "Make precise edits to files by replacing unique strings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "old_string": {"type": "string", "description": "Old string to replace"},
                        "new_string": {"type": "string", "description": "New string"}
                    },
                    "required": ["path", "old_string", "new_string"]
                }
            }
        }

    def execute(self, input_data):
        """Execute file editing - same logic as V2"""
        try:
            # Read file content
            with open(input_data["path"], "r", encoding="utf-8") as f:
                content = f.read()

            old_string = input_data["old_string"]
            new_string = input_data["new_string"]

            # Check if old string exists
            if old_string not in content:
                return f"❌ Error: String not found in file: {old_string[:50]}..."

            # Check if old string is unique
            count = content.count(old_string)
            if count > 1:
                return f"❌ Error: String not unique, found {count} matches: {old_string[:50]}..."

            # Execute replacement
            new_content = content.replace(old_string, new_string)

            # Write back to file
            with open(input_data["path"], "w", encoding="utf-8") as f:
                f.write(new_content)

            return f"✅ Successfully edited file {input_data['path']}: replaced {len(old_string)} characters"

        except Exception as e:
            return f"❌ Failed to edit file: {e}"