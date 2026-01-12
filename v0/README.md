# V0 - Proof of Concept Version

**Simplest AI assistant implementation, 24 lines of code demonstrating core concepts**

## Design Philosophy

V0 version focuses on demonstrating the most basic AI assistant workflow:
1. User provides a task description
2. Call AI API to get suggested commands
3. User confirms and executes commands

## Core Features

- **Minimal Design**: Only 24 lines of code, easy to understand
- **Single Interaction**: One task corresponds to one API call
- **Direct Execution**: No complex tool system, direct bash command execution
- **Basic Safety**: Requires manual user confirmation before execution

## Usage

```bash
# Set API key
export OPENROUTER_API_KEY="your-api-key"

# Run the assistant
chmod +x agent.sh
./agent.sh "list all Python files in current directory"
```

## Example Conversation

```
$ ./agent.sh "find all shell files in current dir"
🤖 AI suggests executing: find . -maxdepth 1 -type f -name "*.sh"
Confirm to run this command? (y/n) y
./agent.sh
```

## Learning Points

1. **API Call Basics**: How to construct HTTP requests to call OpenRouter
2. **JSON Processing**: Using jq to parse API responses
3. **User Interaction**: Simple confirmation mechanism
4. **Command Execution**: Usage of eval in bash

## Limitations

- No conversation history, cannot handle multi-step tasks
- No error handling mechanism
- Lacks protection against dangerous commands
- Does not support complex file operations

## Evolution Direction

V0 → V1 main improvements:
- Add conversation loops
- Increase safety checks
- Improve error handling
- Support multi-step tasks

This version is suitable for beginners to understand the basic working principles of AI assistants.