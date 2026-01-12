#!/usr/bin/env python3
# tools/search_tools.py - Search tools (V2 functionality in V3 architecture)

import subprocess
from .base import BaseTool


class GlobTool(BaseTool):
    """Find files matching glob patterns tool - V2 functionality"""

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "glob",
                "description": "Find files matching glob patterns",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "glob pattern (like '*.py', '**/*.txt')"},
                        "path": {"type": "string", "description": "search path, defaults to current directory", "default": "."}
                    },
                    "required": ["pattern"]
                }
            }
        }

    def execute(self, input_data):
        """Execute file pattern matching - same logic as V2"""
        try:
            pattern = input_data["pattern"]
            search_path = input_data.get("path", ".")

            # Use find command to implement glob functionality
            if "**" in pattern:
                # Recursive search
                clean_pattern = pattern.replace("**/", "").replace("**", "*")
                command = f"find {search_path} -name '{clean_pattern}' -type f"
            else:
                # Non-recursive search
                command = f"find {search_path} -maxdepth 1 -name '{pattern}' -type f"

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return f"❌ Search error: {result.stderr}"

            files = result.stdout.strip()
            if not files:
                return f"📂 No files found matching '{pattern}'"

            file_list = files.split('\n')
            return f"📂 Found {len(file_list)} matching files:\n{files}"

        except Exception as e:
            return f"❌ Glob search failed: {e}"


class GrepTool(BaseTool):
    """Search for matching text in files tool - V2 functionality"""

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "grep",
                "description": "Search for matching text in files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "search pattern (regular expression)"},
                        "path": {"type": "string", "description": "search path (file or directory), defaults to current directory", "default": "."},
                        "file_pattern": {"type": "string", "description": "filename filter pattern (like '*.py')", "default": "*"},
                        "case_sensitive": {"type": "boolean", "description": "whether to match case", "default": True},
                        "show_line_numbers": {"type": "boolean", "description": "whether to show line numbers", "default": True}
                    },
                    "required": ["pattern"]
                }
            }
        }

    def execute(self, input_data):
        """Execute text search - same logic as V2"""
        try:
            search_pattern = input_data["pattern"]
            search_path = input_data.get("path", ".")
            file_pattern = input_data.get("file_pattern", "*")
            case_sensitive = input_data.get("case_sensitive", True)
            show_line_numbers = input_data.get("show_line_numbers", True)

            # Build grep command
            grep_opts = []
            if not case_sensitive:
                grep_opts.append("-i")
            if show_line_numbers:
                grep_opts.append("-n")

            grep_opts.append("-r")  # Recursive search

            # Use find with grep
            if file_pattern != "*":
                command = f"find {search_path} -name '{file_pattern}' -type f -exec grep {' '.join(grep_opts)} '{search_pattern}' {{}} +"
            else:
                command = f"grep {' '.join(grep_opts)} '{search_pattern}' {search_path}/* 2>/dev/null || true"

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout.strip()
            if not output:
                return f"🔍 No content found matching '{search_pattern}' in '{search_path}'"

            lines = output.split('\n')
            return f"🔍 Found {len(lines)} matches:\n{output}"

        except Exception as e:
            return f"❌ Grep search failed: {e}"