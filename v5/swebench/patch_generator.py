"""
SWE-bench patch generator

This module extracts file modifications from agent message history
and generates git diff format patches.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from difflib import unified_diff


def extract_file_modifications(messages: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Extract file modifications from agent message history.
    
    Tracks write_file and edit_file tool calls to build a map of
    file paths to their final content.
    
    Args:
        messages: List of agent conversation messages
    
    Returns:
        Dictionary mapping file paths to their final content
    """
    modifications = {}
    file_contents = {}  # Track current content of files
    
    for message in messages:
        # Check for tool calls (write_file, edit_file)
        if message.get("role") == "assistant" and message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                func_name = tool_call.get("function", {}).get("name", "")
                func_args_str = tool_call.get("function", {}).get("arguments", "{}")
                
                try:
                    func_args = json.loads(func_args_str)
                except (json.JSONDecodeError, TypeError):
                    continue
                
                if func_name == "write_file":
                    file_path = func_args.get("path")
                    content = func_args.get("content", "")
                    if file_path:
                        modifications[file_path] = content
                        file_contents[file_path] = content
                
                elif func_name == "edit_file":
                    file_path = func_args.get("path")
                    old_string = func_args.get("old_string", "")
                    new_string = func_args.get("new_string", "")
                    
                    if file_path:
                        # Get current content or use old_string as base
                        current_content = file_contents.get(file_path, old_string)
                        
                        # Apply edit: replace old_string with new_string
                        if old_string in current_content:
                            new_content = current_content.replace(old_string, new_string, 1)
                        else:
                            # If old_string not found, append new_string
                            new_content = current_content + "\n" + new_string
                        
                        modifications[file_path] = new_content
                        file_contents[file_path] = new_content
        
        # Also check tool results for read_file to track original content
        elif message.get("role") == "tool":
            tool_name = message.get("name", "")
            if tool_name == "read_file":
                # Extract file path and content from read_file result
                # This helps us track original file content
                content = message.get("content", "")
                # Try to extract file path from content (format: "✅ 成功读取文件 {path}")
                path_match = re.search(r'成功读取文件 (.+?)\n', content)
                if path_match:
                    file_path = path_match.group(1).strip()
                    # Extract actual file content (after "📄 文件内容:\n")
                    content_match = re.search(r'📄 文件内容:\n(.*)', content, re.DOTALL)
                    if content_match:
                        file_content = content_match.group(1)
                        # Store original content if we haven't modified it yet
                        if file_path not in file_contents:
                            file_contents[file_path] = file_content
    
    return modifications


def generate_git_diff(
    file_path: str,
    old_content: Optional[str],
    new_content: Optional[str]
) -> str:
    """
    Generate git diff format for a single file.
    
    Args:
        file_path: Path to the file
        old_content: Original file content (None for new files)
        new_content: New file content (None for deleted files)
    
    Returns:
        Git diff format string
    """
    # Handle file deletion
    if new_content is None and old_content is not None:
        old_lines = old_content.splitlines(keepends=True)
        if not old_lines:
            old_lines = [""]
        
        diff_lines = [
            f"diff --git a/{file_path} b/{file_path}",
            f"deleted file mode 100644",
            f"index {'0' * 40}..{'0' * 40}",
            f"--- a/{file_path}",
            f"+++ /dev/null",
            f"@@ -1,{len(old_lines)} +0,0 @@"
        ]
        for line in old_lines:
            diff_lines.append(f"-{line.rstrip()}")
        
        return "\n".join(diff_lines) + "\n"
    
    # Handle new file
    if old_content is None and new_content is not None:
        new_lines = new_content.splitlines(keepends=True)
        if not new_lines:
            new_lines = [""]
        
        diff_lines = [
            f"diff --git a/{file_path} b/{file_path}",
            f"new file mode 100644",
            f"index {'0' * 40}..{'0' * 40}",
            f"--- /dev/null",
            f"+++ b/{file_path}",
            f"@@ -0,0 +1,{len(new_lines)} @@"
        ]
        for line in new_lines:
            # Ensure line ends with newline for proper diff format
            line_content = line if line.endswith('\n') else line + '\n'
            diff_lines.append(f"+{line_content.rstrip()}")
        
        return "\n".join(diff_lines) + "\n"
    
    # Handle file modification
    if old_content is not None and new_content is not None:
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        # Use unified_diff to generate proper diff
        diff = list(unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        ))
        
        # Convert to git diff format
        if not diff:
            return ""  # No changes
        
        # Replace unified diff header with git diff header
        git_diff_lines = [f"diff --git a/{file_path} b/{file_path}"]
        
        # Skip unified diff header lines and process the rest
        skip_count = 2  # Skip "---" and "+++" from unified_diff
        for i, line in enumerate(diff):
            if i < skip_count:
                # Replace unified diff file markers with git format
                if line.startswith("---"):
                    git_diff_lines.append(f"--- a/{file_path}")
                elif line.startswith("+++"):
                    git_diff_lines.append(f"+++ b/{file_path}")
            else:
                git_diff_lines.append(line)
        
        return "\n".join(git_diff_lines) + "\n"
    
    # No change
    return ""


def generate_patch(
    modifications: Dict[str, str],
    original_contents: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate a complete patch from file modifications.
    
    Args:
        modifications: Dictionary mapping file paths to their new content
        original_contents: Optional dictionary mapping file paths to original content.
                         If not provided, assumes all files are new.
    
    Returns:
        Complete git diff patch string
    """
    if not modifications:
        return ""
    
    patches = []
    
    for file_path, new_content in modifications.items():
        old_content = original_contents.get(file_path) if original_contents else None
        file_diff = generate_git_diff(file_path, old_content, new_content)
        if file_diff:
            patches.append(file_diff)
    
    return "\n".join(patches)


def extract_patch_from_messages(
    messages: List[Dict[str, Any]],
    original_contents: Optional[Dict[str, str]] = None
) -> str:
    """
    Extract patch from agent message history.
    
    This is the main function that combines extraction and patch generation.
    
    Args:
        messages: List of agent conversation messages
        original_contents: Optional dictionary of original file contents
    
    Returns:
        Git diff format patch string
    """
    modifications = extract_file_modifications(messages)
    
    # If original_contents not provided, try to extract from messages
    if original_contents is None:
        original_contents = _extract_original_contents(messages)
    
    return generate_patch(modifications, original_contents)


def _extract_original_contents(messages: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Extract original file contents from read_file tool calls in messages.
    
    Args:
        messages: List of agent conversation messages
    
    Returns:
        Dictionary mapping file paths to their original content
    """
    original_contents = {}
    
    for message in messages:
        if message.get("role") == "tool" and message.get("name") == "read_file":
            content = message.get("content", "")
            # Extract file path
            path_match = re.search(r'成功读取文件 (.+?)\n', content)
            if path_match:
                file_path = path_match.group(1).strip()
                # Extract file content
                content_match = re.search(r'📄 文件内容:\n(.*)', content, re.DOTALL)
                if content_match:
                    file_content = content_match.group(1)
                    original_contents[file_path] = file_content
    
    return original_contents
