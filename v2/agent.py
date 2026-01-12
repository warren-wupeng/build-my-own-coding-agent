#!/usr/bin/env python3
# V2 - Tool System Version (200+ lines of code)
# Introduce structured tool calling and modular design
# Inlined implementation - all functionality in single file

import json
import os
import sys
import urllib.request
import urllib.error
import subprocess
import re

# Tool definitions (OpenRouter format) - inlined from tools_definitions.py
TOOLS = [
    {
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
    },
    {
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
    },
    {
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
    },
    {
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
    },
    {
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
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "Run bash commands",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "command to run"}
                },
                "required": ["command"]
            }
        }
    }
]

# Dangerous operations that require user confirmation (like V1)
DANGEROUS_PATTERNS = [
    "rm -rf /", "sudo rm", "chmod 777", "curl.*|.*sh", "wget.*|.*sh",
    "dd if=", "mkfs.", "fdisk", "parted", "shutdown", "reboot", "init 0", "halt"
]

def _is_dangerous_command(command):
    """Check if a bash command contains dangerous patterns"""
    command_lower = command.lower()

    for pattern in DANGEROUS_PATTERNS:
        if pattern.endswith(".*"):
            if re.search(pattern.replace(".*", r".*?"), command_lower):
                return True, pattern
        else:
            if pattern.lower() in command_lower:
                return True, pattern

    # Additional pipe-to-shell check
    if "|" in command and ("sh" in command_lower or "bash" in command_lower):
        return True, "pipe to shell"

    return False, None

def _prompt_user_confirmation(tool_name, tool_input, dangerous_pattern):
    """Prompt user for confirmation of dangerous operations"""
    print(f"\n⚠️  Dangerous operation detected!", file=sys.stderr)

    if tool_name == "run_bash":
        command = tool_input.get("command", "")
        print(f"Command: {command}", file=sys.stderr)
        print(f"Matched pattern: '{dangerous_pattern}'", file=sys.stderr)
    else:
        print(f"Tool: {tool_name}", file=sys.stderr)
        print(f"Parameters: {json.dumps(tool_input, indent=2)}", file=sys.stderr)

    print("Allow execution? (y/n): ", end='', file=sys.stderr, flush=True)

    try:
        response = input().strip().lower()
        return response in ['y', 'yes']
    except (EOFError, KeyboardInterrupt):
        print("\nOperation cancelled by user", file=sys.stderr)
        return False

# Tool execution functions - inlined from tools_execution.py

def execute_tool(name, input_data):
    """Execute tool and return result"""
    try:
        if name == "read_file":
            return _execute_read_file(input_data)
        elif name == "write_file":
            return _execute_write_file(input_data)
        elif name == "edit_file":
            return _execute_edit_file(input_data)
        elif name == "glob":
            return _execute_glob(input_data)
        elif name == "grep":
            return _execute_grep(input_data)
        elif name == "run_bash":
            return _execute_run_bash(input_data)
        else:
            return f"❌ Error: Unknown tool: {name}"

    except Exception as e:
        return f"❌ Tool execution exception: {e}"

def _execute_read_file(input_data):
    """Execute file reading"""
    try:
        with open(input_data["path"], "r", encoding="utf-8") as f:
            content = f.read()
        return f"✅ Successfully read {input_data['path']} ({len(content)} characters):\n{content}"
    except Exception as e:
        return f"❌ Failed to read file: {e}"

def _execute_write_file(input_data):
    """Execute file writing"""
    try:
        with open(input_data["path"], "w", encoding="utf-8") as f:
            f.write(input_data["content"])
        return f"✅ Successfully written to {input_data['path']} ({len(input_data['content'])} characters)"
    except Exception as e:
        return f"❌ Failed to write file: {e}"

def _execute_edit_file(input_data):
    """Execute file editing"""
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

def _execute_glob(input_data):
    """Execute file pattern matching"""
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

def _execute_grep(input_data):
    """Execute text search"""
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

def _execute_run_bash(input_data):
    """Execute bash command (dangerous command checking moved to agent.py)"""
    try:
        command = input_data["command"]

        # Keep command length check as basic safety
        if len(command) > 1000:
            return f"❌ Error: Command too long (max 1000 characters)\n" \
                   f"Command length: {len(command)}\n" \
                   f"This may indicate a security risk or malformed command"

        # Execute the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = ""
        if result.stdout:
            output += f"stdout:\n{result.stdout}"
        if result.stderr:
            output += f"stderr:\n{result.stderr}"

        if result.returncode == 0:
            return f"✅ Command executed successfully (exit code: {result.returncode}):\n{output}"
        else:
            return f"⚠️  Command completed (exit code: {result.returncode}):\n{output}"

    except subprocess.TimeoutExpired:
        return "❌ Error: Command execution timeout (30 seconds)"
    except Exception as e:
        return f"❌ Command execution failed: {e}"

# Tool information summary
def get_tools_info():
    """Get tools information summary"""
    info = []
    for tool in TOOLS:
        func = tool["function"]
        info.append({
            "name": func["name"],
            "description": func["description"],
            "parameters": list(func["parameters"]["properties"].keys())
        })
    return info

def call_openrouter_api(messages, tools):
    """Call OpenRouter API"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("Please run: export OPENROUTER_API_KEY=\"your-key-here\"")
        sys.exit(1)

    # Build request data
    payload = {
        "model": "deepseek/deepseek-v3.2",
        "messages": messages,
        "tools": tools,
        "max_tokens": 4096
    }

    # Convert to JSON bytes
    data = json.dumps(payload).encode('utf-8')

    # Create request
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ API call failed ({e.code}): {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ API call failed: {e}")
        sys.exit(1)

def run_agent(task):
    """Main agent loop"""
    print(f"🚀 Starting AI Assistant (V2 - Tool System Version)")
    print(f"📝 Task: {task}")
    print(f"🛠️  Available tools: {len(TOOLS)}")
    print("")

    messages = [{"role": "user", "content": task}]
    step_count = 1

    while True:
        print(f"🔄 Step {step_count}...")

        try:
            response = call_openrouter_api(messages, TOOLS)
        except Exception as e:
            print(f"❌ API call exception: {e}")
            break

        # Get response message
        message = response["choices"][0]["message"]
        finish_reason = response["choices"][0]["finish_reason"]

        # Add assistant response to history
        messages.append(message)

        # Check if completed
        if finish_reason == "stop":
            if message.get("content"):
                print(f"✅ {message['content']}")
            print("")
            print(f"🎉 Task completed successfully! Total steps executed: {step_count}.")
            break

        # Handle tool usage
        elif finish_reason == "tool_calls" or message.get("tool_calls"):
            tool_results = []

            for tool_call in message.get("tool_calls", []):
                tool_name = tool_call["function"]["name"]
                tool_input = json.loads(tool_call["function"]["arguments"])
                tool_id = tool_call["id"]

                print(f"🔧 Using tool '{tool_name}': {json.dumps(tool_input, ensure_ascii=False)}")

                # Check for dangerous operations before execution (like V1)
                user_denied = False
                if tool_name == "run_bash":
                    command = tool_input.get("command", "")
                    is_dangerous, pattern = _is_dangerous_command(command)

                    if is_dangerous:
                        if not _prompt_user_confirmation(tool_name, tool_input, pattern):
                            result = f"❌ User denied execution of dangerous command: {command}"
                            user_denied = True

                # Execute tool only if not denied by user
                if not user_denied:
                    result = execute_tool(tool_name, tool_input)

                # Show result preview
                if len(result) > 200:
                    preview = result[:200] + "..."
                else:
                    preview = result

                print(f"   📤 Result: {preview}")

                tool_results.append({
                    "tool_call_id": tool_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result
                })

            # Add tool results to conversation
            messages.extend(tool_results)
            print("")

            # Prevent infinite loops
            step_count += 1
            if step_count > 30:
                print("⚠️  Executed 30 steps, stopping to prevent infinite loops")
                break

        else:
            print(f"❌ Unknown finish reason: {finish_reason}")
            break

def show_help():
    """Show help information"""
    print("V2 AI Assistant - Tool System Version")
    print("")
    print("Usage:")
    print("  python agent.py \"your task description\"")
    print("")
    print("Examples:")
    print("  python agent.py \"analyze Python files in current directory\"")
    print("  python agent.py \"create a hello.py and run it\"")
    print("  python agent.py \"search for all Python files containing 'class'\"")
    print("")
    print("Available tools:")
    for i, tool in enumerate(TOOLS, 1):
        name = tool["function"]["name"]
        desc = tool["function"]["description"]
        print(f"  {i}. {name}: {desc}")
    print("")
    print("Setup:")
    print("  export OPENROUTER_API_KEY=\"your-api-key\"")

def main():
    """Main function"""
    # Check for help flags first, regardless of argument count
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
        return

    # Then check if we have exactly one task argument
    if len(sys.argv) != 2:
        print("❌ Error: Please provide task description")
        print("Usage: python agent.py \"your task\"")
        print("Help: python agent.py --help")
        sys.exit(1)

    run_agent(sys.argv[1])

if __name__ == "__main__":
    main()