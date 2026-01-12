# V2 - Tool System Version

**Introduce structured tool calling, 200+ lines of code showcasing modular architecture**

## Design Philosophy

V2 version represents the key turning point from simple scripts to modern AI assistants:
1. **Tool System**: Expand from single bash commands to 6 structured tools
2. **Module Separation**: Separate tool definitions and execution logic into different modules
3. **API Evolution**: Use OpenAI-compatible tool calling API
4. **Python Migration**: Move from bash to Python for better maintainability

## Core Architecture

### 📁 File Structure
```
v2/
├── agent.py              # Main program and conversation loop
├── tools_definitions.py  # Tool API definitions
├── tools_execution.py    # Tool execution implementation (with security)
├── test_safety.py        # Security mechanism test suite
└── README.md            # This document
```

### 🔧 Tool System
```python
Tool Definitions (tools_definitions.py)
    ↓ Provide API format
Main Agent (agent.py)
    ↓ Call tools
Tool Execution (tools_execution.py)
    ↓ Return results
```

### 🛠️ Available Tools (6 total)

| Tool Name | Function | Parameters | Safety Features |
|-----------|----------|------------|-----------------|
| `read_file` | Read file contents | path | UTF-8 safe, error handling |
| `write_file` | Create/overwrite files | path, content | UTF-8 safe, error handling |
| `edit_file` | Precise string replacement | path, old_string, new_string | Validation, uniqueness check |
| `glob` | File pattern matching | pattern, [path] | Timeout protection (30s) |
| `grep` | Text search | pattern, [path, file_pattern, case_sensitive] | Timeout protection (30s) |
| `run_bash` | Execute shell commands **with security** | command | **🔐 Enhanced safety checks** |

## Usage

```bash
# Set API key
export OPENROUTER_API_KEY="your-api-key"

# Run the assistant
cd v2
python agent.py "analyze Python files in current directory"
```

## 🔐 Security Features

V2 uses an **Interactive Safety Model** similar to V1, providing comprehensive security through user confirmation:

### Interactive Safety Checks for `run_bash` Tool

**Dangerous Command Detection (14 patterns):**
- **Root filesystem operations**: `rm -rf /`, `sudo rm`
- **Permission modifications**: `chmod 777`
- **Pipe to shell attacks**: `curl ... | sh`, `wget ... | bash`
- **System operations**: `shutdown`, `reboot`, `halt`, `init 0`
- **Disk operations**: `dd if=`, `mkfs.*`, `fdisk`, `parted`

**User Confirmation Process:**
- **Detection**: System identifies dangerous patterns automatically
- **User Prompt**: Interactive confirmation with command details
- **User Decision**: Final approval/denial rests with user
- **Clear Information**: Shows matched pattern and potential risks

**Additional Protections:**
- **Command length limiting**: Maximum 1000 characters (automatic)
- **Case-insensitive matching**: Detects dangerous patterns regardless of case
- **Timeout enforcement**: All commands limited to 30 seconds execution
- **Graceful cancellation**: Ctrl+C safely cancels confirmation prompts

### Interactive Safety Examples

```bash
# ⚠️ Dangerous commands trigger user confirmation:
$ python agent.py "delete temporary files with rm -rf /tmp/*"

⚠️  Dangerous operation detected!
Command: rm -rf /tmp/*
Matched pattern: 'rm -rf /'
Allow execution? (y/n): n

❌ User denied execution of dangerous command: rm -rf /tmp/*

# AI Response: "I understand you don't want to execute that command.
# Let me suggest safer alternatives like 'ls /tmp' to see what files
# are there first, or using more specific deletion commands."
```

```bash
# ✅ Safe commands execute without prompts:
$ python agent.py "list files with ls -la"

🔧 Using tool 'run_bash': {"command": "ls -la"}
📤 Result: ✅ Command executed successfully...
```

### Security Philosophy

- **Interactive Control**: User has final decision on dangerous operations
- **Informed Consent**: System provides clear information about detected risks
- **Comprehensive Detection**: Same extensive pattern matching as automatic systems
- **Non-Intrusive**: Safe operations continue without interruption
- **Collaborative Safety**: Combines system intelligence with human judgment
- **Educational**: Users learn about dangerous patterns through explanations

### Testing Security Features

#### Automated Tests

Run the automated test suite for dangerous command detection:

```bash
cd v2
python test_safety.py
```

**Expected Output:**
```
🔐 V2 INTERACTIVE SAFETY MECHANISM TEST SUITE
=======================================================
🔍 V2 Interactive Safety - Dangerous Command Detection Test
=================================================================
Testing 22 commands for dangerous pattern detection...

📊 Detection Test Results: 22/22 tests passed
Success rate: 100.0%
🎉 All detection tests passed! Command detection is working correctly.

🧪 V2 Safe Command Execution Test
========================================
✅ All automated tests passed!
   → Ready for manual testing with user confirmation
```

#### Manual Interactive Testing

The interactive safety model requires manual testing. The test suite provides detailed instructions for:

1. **Testing dangerous command confirmation** (deny scenario)
2. **Testing dangerous command confirmation** (allow scenario)
3. **Testing safe command execution** (no prompts)

Run `python test_safety.py` to see complete manual testing instructions with safety guidelines.

## Example Conversation

```
$ python3 agent.py "Create a Python file that calculates fibonacci numbers and run it"
🚀 Starting AI Assistant (V2 - Tool System Version)
📝 Task: Create a Python file that calculates fibonacci numbers and run it
🛠️  Available tools: 6

🔄 Step 1...
🔧 Using tool 'run_bash': {"command": "pwd && ls -la"}
   📤 Result: ✅ Command executed successfully (exit code: 0):
stdout:
/Users/wupeng/playground/my-coding-agents/v2
total 64
drwxr-xr-x@  4 wupeng  staff   128  1 12 13:29 __pycache__
drwxr-xr-x@  7 wupeng  staff   ...

🔄 Step 2...
🔧 Using tool 'write_file': {"path": "fibonacci.py", "content": "def fibonacci(n):\n    \"\"\"Calculate the nth Fibonacci number\"\"\"\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        a, b = 0, 1\n        for _ in range(2, n + 1):\n            a, b = b, a + b\n        return b\n\nif __name__ == \"__main__\":\n    # Test the function\n    test_cases = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\n    print(\"Fibonacci numbers:\")\n    for n in test_cases:\n        result = fibonacci(n)\n        print(f\"fibonacci({n}) = {result}\")"}
   📤 Result: ✅ Successfully written to fibonacci.py (472 characters)
🔧 Using tool 'run_bash': {"command": "python fibonacci.py"}
   📤 Result: ⚠️  Command completed (exit code: 127):
stderr:
/bin/sh: python: command not found


🔄 Step 3...
🔧 Using tool 'run_bash': {"command": "python3 --version && python3 fibonacci.py"}
   📤 Result: ✅ Command executed successfully (exit code: 0):
stdout:
Python 3.14.0
Fibonacci numbers:
fibonacci(0) = 0
fibonacci(1) = 1
fibonacci(2) = 1
fibonacci(3) = 2
fibonacci(4) = 3
fibonacci(5) = 5
fibonacci...

🔄 Step 4...
✅ Perfect! I've created a Python file `fibonacci.py` that calculates Fibonacci numbers and successfully executed it. Here's what I did:

1. **Created the file** with:
   - A `fibonacci(n)` function that calculates the nth Fibonacci number using an efficient iterative approach
   - A main section that tests the function with values from 0 to 10
   - Proper handling of edge cases (n <= 0 returns 0)

2. **Ran the program** using `python3 fibonacci.py` (after discovering that `python` command wasn't available, but `python3` was)

3. **Verified the output** shows the correct Fibonacci sequence:
   - fibonacci(0) = 0
   - fibonacci(1) = 1  
   - fibonacci(2) = 1
   - fibonacci(3) = 2
   - fibonacci(4) = 3
   - fibonacci(5) = 5
   - fibonacci(6) = 8
   - fibonacci(7) = 13
   - fibonacci(8) = 21
   - fibonacci(9) = 34
   - fibonacci(10) = 55

The program works correctly and demonstrates the Fibonacci sequence calculation. The file `fibonacci.py` is now available in your current directory.

🎉 Task completed successfully! Total steps executed: 4.
```

## Technical Highlights

### 1. Structured Tool Calling
```python
# OpenAI-compatible tool definition format
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
}
```

### 2. Modular Architecture
- **tools_definitions.py**: Pure declarative tool API definitions
- **tools_execution.py**: Implementation logic separated from definitions
- **agent.py**: Focuses on conversation loops and flow control

### 3. Enhanced Security and Safety
```python
# Dangerous command detection
dangerous_patterns = [
    "rm -rf /", "sudo rm", "chmod 777",
    "curl.*|.*sh", "wget.*|.*sh", "shutdown", ...
]

for pattern in dangerous_patterns:
    if pattern.lower() in command.lower():
        return f"⚠️ Dangerous command detected and blocked for safety"

# Additional pipe-to-shell protection
if "|" in command and ("sh" in command_lower or "bash" in command_lower):
    return f"⚠️ Pipe to shell blocked for safety"
```

### 4. Error Handling and Timeouts
```python
# Unified error handling with security
try:
    result = subprocess.run(command, timeout=30, ...)
    return f"✅ Command executed successfully: {result.stdout}"
except subprocess.TimeoutExpired:
    return "❌ Error: Command execution timeout"
```

### 5. Elegant Output Formatting
- Use emojis to identify different states
- Result preview to avoid overly long output
- Step counting and progress display

## Learning Points

1. **API Design**: How to design clear tool API interfaces
2. **Module Separation**: Principles of separating definitions from implementation
3. **Tool Calling**: Implementation of OpenAI tool calling protocol
4. **Security Implementation**: Comprehensive dangerous command detection and prevention
5. **Error Handling**: Production environment error handling strategies
6. **User Experience**: Clear output and feedback mechanisms
7. **Safety Testing**: Automated security validation and test suite development

## Code Quality Improvements

### V1 → V2 Improvements:
- ✅ Migrated from bash to Python for better maintainability
- ✅ Introduced typed tool system
- ✅ Separated concerns with modular design
- ✅ Richer feature set (6 tools vs 1 bash command)
- ✅ Better error handling and output formatting
- ✅ **Enhanced security**: Comprehensive dangerous command detection
- ✅ **Static safety**: Automatic blocking without user interaction required
- ✅ **Attack prevention**: Protection against pipe-to-shell and system damage

### V2 Limitations:
- Tool registration is still manual (hardcoded)
- Lacks object-oriented extensibility
- Tool execution logic concentrated in one large function
- No plugin mechanism for tools

## Evolution Direction

V2 → V3 Main Improvements:
- Object-oriented tool system
- Dynamic tool registration mechanism
- Better code organization and extensibility
- Complete production-grade error handling

This version demonstrates how to evolve from scripts to structured software systems.