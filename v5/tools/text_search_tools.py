#!/usr/bin/env python3
# tools/text_search_tools.py - Text search tools
# V3: Text content search functionality

import subprocess
import os
from .base import BaseTool


class GrepTool(BaseTool):
    """
    Text search tool
    Supports regular expressions and multiple search options
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "grep",
                "description": "Search for matching text content in files, supports regular expressions and multiple search options",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern (supports regular expressions), e.g.: 'def.*function', 'class\\s+\\w+', 'TODO|FIXME'"
                        },
                        "path": {
                            "type": "string",
                            "description": "Search path (file or directory), defaults to current directory",
                            "default": "."
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "Filename filter pattern, e.g.: '*.py'(Python files), '*.js'(JavaScript files), '*.md'(Markdown files)",
                            "default": "*"
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Whether to be case sensitive",
                            "default": True
                        },
                        "show_line_numbers": {
                            "type": "boolean",
                            "description": "Whether to show line numbers for matching lines",
                            "default": True
                        },
                        "context_lines": {
                            "type": "integer",
                            "description": "Number of context lines before and after matching lines (0-5)",
                            "default": 0
                        },
                        "max_matches": {
                            "type": "integer",
                            "description": "Maximum number of matches, default 50",
                            "default": 50
                        }
                    },
                    "required": ["pattern"]
                }
            }
        }

    def execute(self, input_data):
        search_pattern = input_data["pattern"]
        search_path = input_data.get("path", ".")
        file_pattern = input_data.get("file_pattern", "*")
        case_sensitive = input_data.get("case_sensitive", True)
        show_line_numbers = input_data.get("show_line_numbers", True)
        context_lines = input_data.get("context_lines", 0)
        max_matches = input_data.get("max_matches", 50)

        try:
            # Check if search path exists
            if not os.path.exists(search_path):
                return f"❌ Search path does not exist: {search_path}"

            # Build grep command options
            grep_opts = []

            # Case sensitivity option
            if not case_sensitive:
                grep_opts.append("-i")

            # Line number option
            if show_line_numbers:
                grep_opts.append("-n")

            # Context lines
            if context_lines > 0:
                context_lines = min(context_lines, 5)  # Limit maximum context lines
                grep_opts.append(f"-C {context_lines}")

            # Recursive search
            grep_opts.append("-r")

            # Show filename
            grep_opts.append("-H")

            # Build complete command
            grep_options = " ".join(grep_opts)

            if file_pattern != "*":
                # Use find with grep to filter file types
                command = f"find '{search_path}' -name '{file_pattern}' -type f -exec grep {grep_options} '{search_pattern}' {{}} +"
            else:
                # Directly use grep for recursive search
                command = f"grep {grep_options} '{search_pattern}' '{search_path}' 2>/dev/null || true"

            # Limit result count
            command += f" | head -{max_matches}"

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout.strip()
            if not output:
                return f"🔍 No matching content found\n" \
                       f"Pattern: {search_pattern}\n" \
                       f"Path: {os.path.abspath(search_path)}\n" \
                       f"File type: {file_pattern if file_pattern != '*' else 'All files'}"

            # Parse results
            lines = output.split('\n')
            match_count = len(lines)

            # Count matching files
            files = set()
            for line in lines:
                if ':' in line:
                    files.add(line.split(':', 1)[0])

            # Build result report
            result_text = f"🔍 Text search results\n" \
                         f"Pattern: {search_pattern}\n" \
                         f"Path: {os.path.abspath(search_path)}\n" \
                         f"File type: {file_pattern if file_pattern != '*' else 'All files'}\n" \
                         f"Matches: {match_count} lines, {len(files)} files\n\n"

            # Add match details
            current_file = None
            for line in lines:
                if ':' in line:
                    file_part, content_part = line.split(':', 1)
                    if file_part != current_file:
                        current_file = file_part
                        result_text += f"\n📄 {current_file}:\n"

                    # Handle line numbers
                    if ':' in content_part and show_line_numbers:
                        line_num, content = content_part.split(':', 1)
                        result_text += f"  {line_num:>4}: {content}\n"
                    else:
                        result_text += f"       {content_part}\n"

            # If max matches reached, add warning
            if match_count == max_matches:
                result_text += f"\n⚠️  Results limited to {max_matches} lines, there may be more matches"

            return result_text

        except subprocess.TimeoutExpired:
            return f"❌ Search timeout (30 seconds), please narrow the search scope or use a more specific pattern"
        except Exception as e:
            return f"❌ Text search failed: {e}"
