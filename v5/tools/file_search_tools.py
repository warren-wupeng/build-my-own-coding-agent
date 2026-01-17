#!/usr/bin/env python3
# tools/file_search_tools.py - File search and find tools
# V3: File search functionality based on file attributes

import subprocess
import os
from .base import BaseTool


class GlobTool(BaseTool):
    """
    File search tool
    Supports glob pattern matching and recursive search
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "glob",
                "description": "Find matching files using glob patterns, supports wildcards and recursive search",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern, e.g.: '*.py'(Python files), '**/*.txt'(recursively find txt files), 'test_*.py'(test files)"
                        },
                        "path": {
                            "type": "string",
                            "description": "Search root path, defaults to current directory",
                            "default": "."
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results, default 100",
                            "default": 100
                        }
                    },
                    "required": ["pattern"]
                }
            }
        }

    def execute(self, input_data):
        pattern = input_data["pattern"]
        search_path = input_data.get("path", ".")
        max_results = input_data.get("max_results", 100)

        try:
            # Check if search path exists
            if not os.path.exists(search_path):
                return f"❌ Search path does not exist: {search_path}"

            # Build find command
            if "**" in pattern:
                # Recursive search
                clean_pattern = pattern.replace("**/", "").replace("**", "*")
                command = f"find '{search_path}' -name '{clean_pattern}' -type f"
            else:
                # Non-recursive search
                command = f"find '{search_path}' -maxdepth 1 -name '{pattern}' -type f"

            # Add result limit
            command += f" | head -{max_results}"

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0 and result.stderr:
                return f"❌ Search error: {result.stderr}"

            files = result.stdout.strip()
            if not files:
                return f"🔍 No files found matching pattern '{pattern}'\n" \
                       f"Search path: {os.path.abspath(search_path)}"

            file_list = files.split('\n')
            file_count = len(file_list)

            # Build detailed results
            result_text = f"🔍 Found {file_count} matching files\n" \
                         f"Pattern: {pattern}\n" \
                         f"Path: {os.path.abspath(search_path)}\n\n"

            # Add file information
            for i, file_path in enumerate(file_list, 1):
                try:
                    size = os.path.getsize(file_path)
                    result_text += f"{i:3d}. {file_path} ({size} bytes)\n"
                except:
                    result_text += f"{i:3d}. {file_path}\n"

            # If max results reached, add warning
            if file_count == max_results:
                result_text += f"\n⚠️  Results limited to {max_results}, there may be more matching files"

            return result_text

        except subprocess.TimeoutExpired:
            return f"❌ Search timeout (30 seconds), please narrow the search scope"
        except Exception as e:
            return f"❌ File search failed: {e}"


class FindTool(BaseTool):
    """
    Advanced find tool
    V3 new: Combined file attribute search
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "find",
                "description": "Advanced file search, supports searching by file size, modification time, permissions and other attributes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Search path",
                            "default": "."
                        },
                        "name_pattern": {
                            "type": "string",
                            "description": "Filename pattern, e.g.: '*.py', 'test_*'"
                        },
                        "file_type": {
                            "type": "string",
                            "description": "File type: 'f'(file), 'd'(directory), 'l'(symbolic link)",
                            "enum": ["f", "d", "l"]
                        },
                        "min_size": {
                            "type": "string",
                            "description": "Minimum file size, e.g.: '1k', '1M', '100'"
                        },
                        "max_size": {
                            "type": "string",
                            "description": "Maximum file size, e.g.: '10M', '1G'"
                        },
                        "newer_than_days": {
                            "type": "integer",
                            "description": "Modification time later than N days ago"
                        },
                        "older_than_days": {
                            "type": "integer",
                            "description": "Modification time earlier than N days ago"
                        }
                    },
                    "required": []
                }
            }
        }

    def execute(self, input_data):
        search_path = input_data.get("path", ".")

        try:
            # Check search path
            if not os.path.exists(search_path):
                return f"❌ Search path does not exist: {search_path}"

            # Build find command
            command_parts = [f"find '{search_path}'"]

            # Filename pattern
            if "name_pattern" in input_data:
                command_parts.append(f"-name '{input_data['name_pattern']}'")

            # File type
            if "file_type" in input_data:
                command_parts.append(f"-type {input_data['file_type']}")

            # File size
            if "min_size" in input_data:
                command_parts.append(f"-size +{input_data['min_size']}")
            if "max_size" in input_data:
                command_parts.append(f"-size -{input_data['max_size']}")

            # Modification time
            if "newer_than_days" in input_data:
                command_parts.append(f"-mtime -{input_data['newer_than_days']}")
            if "older_than_days" in input_data:
                command_parts.append(f"-mtime +{input_data['older_than_days']}")

            # Combine command
            command = " ".join(command_parts)

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0 and result.stderr:
                return f"❌ Find error: {result.stderr}"

            output = result.stdout.strip()
            if not output:
                return f"🔍 No files found matching conditions\nSearch conditions: {input_data}"

            files = output.split('\n')
            result_text = f"🔍 Advanced find results ({len(files)} matches)\n"

            # Add search condition summary
            conditions = []
            if "name_pattern" in input_data:
                conditions.append(f"Name: {input_data['name_pattern']}")
            if "file_type" in input_data:
                type_names = {"f": "file", "d": "directory", "l": "symbolic link"}
                conditions.append(f"Type: {type_names.get(input_data['file_type'])}")
            if "min_size" in input_data or "max_size" in input_data:
                size_range = []
                if "min_size" in input_data:
                    size_range.append(f">{input_data['min_size']}")
                if "max_size" in input_data:
                    size_range.append(f"<{input_data['max_size']}")
                conditions.append(f"Size: {' '.join(size_range)}")

            if conditions:
                result_text += f"Conditions: {', '.join(conditions)}\n"

            result_text += f"Path: {os.path.abspath(search_path)}\n\n"

            # List file details
            for i, file_path in enumerate(files, 1):
                try:
                    stat = os.stat(file_path)
                    size = stat.st_size
                    is_dir = os.path.isdir(file_path)
                    icon = "📂" if is_dir else "📄"
                    result_text += f"{i:3d}. {icon} {file_path}"
                    if not is_dir:
                        result_text += f" ({size} bytes)"
                    result_text += "\n"
                except:
                    result_text += f"{i:3d}. {file_path}\n"

            return result_text

        except subprocess.TimeoutExpired:
            return f"❌ Find timeout (30 seconds)"
        except Exception as e:
            return f"❌ Advanced find failed: {e}"
