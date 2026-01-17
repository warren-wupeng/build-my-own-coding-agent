#!/usr/bin/env python3
"""
Demonstrate patch generation from agent message history

This script shows how file modifications in agent messages
are converted to git diff format patches.
"""

from swebench.patch_generator import (
    extract_file_modifications,
    generate_git_diff,
    generate_patch,
    extract_patch_from_messages
)


def main():
    print("=" * 80)
    print("PATCH GENERATION EXAMPLES")
    print("=" * 80)
    
    # Example 1: Single file write
    print("\n" + "#" * 80)
    print("# Example 1: New File Creation")
    print("#" * 80 + "\n")
    
    messages = [
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "write_file",
                        "arguments": '{"path": "hello.py", "content": "print(\\"Hello, World!\\")\\nprint(\\"This is a test\\")"}'
                    }
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "call_1",
            "name": "write_file",
            "content": "✅ Successfully written file hello.py"
        }
    ]
    
    patch = extract_patch_from_messages(messages)
    print("Agent Messages:")
    print("  - write_file('hello.py', 'print(\"Hello, World!\")\\nprint(\"This is a test\")')")
    print("\nGenerated Patch:")
    print("-" * 80)
    print(patch)
    print("-" * 80)
    
    # Example 2: File modification
    print("\n" + "#" * 80)
    print("# Example 2: File Modification")
    print("#" * 80 + "\n")
    
    original_content = "def old_function():\n    return 'old'\n"
    new_content = "def new_function():\n    return 'new'\n"
    
    diff = generate_git_diff("example.py", original_content, new_content)
    print("Original Content:")
    print(original_content)
    print("New Content:")
    print(new_content)
    print("\nGenerated Diff:")
    print("-" * 80)
    print(diff)
    print("-" * 80)
    
    # Example 3: Multiple files
    print("\n" + "#" * 80)
    print("# Example 3: Multiple File Modifications")
    print("#" * 80 + "\n")
    
    modifications = {
        "file1.py": "content1\nline2",
        "file2.py": "content2\nline2"
    }
    
    patch_multi = generate_patch(modifications)
    print("Modifications:")
    for path, content in modifications.items():
        print(f"  {path}: {len(content.splitlines())} lines")
    print("\nGenerated Multi-File Patch:")
    print("-" * 80)
    print(patch_multi)
    print("-" * 80)
    
    # Example 4: Edit file operation
    print("\n" + "#" * 80)
    print("# Example 4: Edit File Operation")
    print("#" * 80 + "\n")
    
    messages_edit = [
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_1",
                    "function": {
                        "name": "edit_file",
                        "arguments": '{"path": "test.py", "old_string": "old", "new_string": "new"}'
                    }
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "call_1",
            "name": "edit_file",
            "content": "✅ File edited successfully"
        }
    ]
    
    modifications_edit = extract_file_modifications(messages_edit)
    print("Edit Operation:")
    print("  edit_file('test.py', old_string='old', new_string='new')")
    print(f"\nExtracted Modifications: {modifications_edit}")


if __name__ == "__main__":
    main()
