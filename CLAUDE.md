# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **My Coding Agents** - a comprehensive demonstration of how to build CLI coding assistants similar to Claude Code, showing the evolution from simple 24-line bash scripts to production-ready Python architectures. The project is structured as a learning journey through four progressive versions, each representing different design philosophies and complexity levels.

## Common Commands

### Running Different Versions

**V0 - Proof of Concept (33 lines):**
```bash
cd v0
./agent.sh "list all Python files"
```

**V1 - Practical Enhancement (157 lines):**
```bash
cd v1
./agent.sh "create a Python project structure"
```

**V1 Refactor - Python Rewrite (260 lines):**
```bash
cd v1r
./agent.sh "create a Python project structure"
```

**V2 - Tool System (558 lines):**
```bash
cd v2
./agent.sh "analyze the codebase structure"
```

**V2 Refactor - Modern Architecture (1000+ lines):**
```bash
cd v2r
./agent.sh "analyze the codebase structure"
```

**V3 - Complete Architecture (1823 lines) - Recommended:**
```bash
cd v3
./agent.sh "create a hello.py file and run it"
```

**V3 Refactor - V4 Architecture + V3 Functionality (2904 lines):**
```bash
cd v3r
./agent.sh "create a hello.py file and run it"
```

**V4 - Advanced Conversation Management (3057 lines):**
```bash
cd v4
./agent.sh "create a hello.py file and run it"
```

### Setup Requirements

**Environment Setup:**
```bash
export OPENROUTER_API_KEY="your-key-here"
chmod +x v*/agent.*
```

**Prerequisites:**
- Python 3.7+
- `jq` command (for bash agents): `brew install jq` or `apt install jq`
- OpenRouter API key from https://openrouter.ai/keys

### Testing Different Versions

**V0 Tests (Basic - 33 lines):**
```bash
cd v0
./agent.sh "find all .py files"
```

**V1 Tests (Multi-step - 157 lines):**
```bash
cd v1
./agent.sh "create a Python project with tests directory"
```

**V1 Refactor Tests (Python Rewrite - 260 lines):**
```bash
cd v1r
./agent.sh "create a Python project with tests directory"
```

**V2 Tests (Structured Tools - 558 lines):**
```bash
cd v2
./agent.sh "read the README file and summarize it"
./agent.sh "search for 'class' definitions in all Python files"
```

**V2 Refactor Tests (Modern Architecture - 1003 lines):**
```bash
cd v2r
./agent.sh "read the README file and summarize it"
./agent.sh "search for 'class' definitions in all Python files"
```

**V3 Tests (Complete Architecture - 1823 lines) - Recommended:**
```bash
cd v3
./agent.sh "Create a Python script that calculates fibonacci numbers and run it"
./agent.sh "Find all Python files and show me the function definitions"
./agent.sh "Create a Flask web application project structure"
```

**V3 Refactor Tests (V4 Architecture + V3 Functionality - 2904 lines):**
```bash
cd v3r
./agent.sh "Create a Python script that calculates fibonacci numbers and run it"
./agent.sh "Find all Python files and show me the function definitions"
# Also supports help mode:
./agent.sh --help
```

**V4 Tests (Advanced Conversation Management - 3057 lines):**
```bash
cd v4
./agent.sh "Create a Python script that calculates fibonacci numbers and run it"
./agent.sh "Find all Python files and show me the function definitions"
./agent.sh "Create a Flask web application project structure"
```

**No formal test suite** - testing is done manually. Generated test files are gitignored (`test_*.py`, `hello.py`, `fibonacci.py`).

## Architecture Evolution

### Version Structure

| Version | Location | Complexity | Lines | Description |
|---------|----------|------------|-------|-------------|
| **V4** | `v4/` | ⭐⭐⭐⭐⭐ | 3057 | Advanced conversation management (13 tools) |
| **V3 Refactor** | `v3r/` | ⭐⭐⭐⭐ | 2904 | V4 architecture + V3 functionality (11 tools) |
| **V3** | `v3/` | ⭐⭐⭐⭐ | 1823 | **Recommended** - Complete OOP architecture (11 tools) |
| **V2 Refactor** | `v2r/` | ⭐⭐⭐ | 1003 | Modern Python architecture (6 tools) |
| **V2** | `v2/` | ⭐⭐⭐ | 558 | Structured tool system (6 tools) |
| **V1 Refactor** | `v1r/` | ⭐⭐ | 260 | Python rewrite of V1 functionality |
| **V1** | `v1/` | ⭐⭐ | 157 | Enhanced bash with safety (bash commands only) |
| **V0** | `v0/` | ⭐ | 24 | Minimal proof of concept (bash commands only) |

### Learning Path

#### Main Evolution Track
1. **Start with V0**: Understand basic AI assistant concepts
2. **Progress to V1**: Learn safety considerations and multi-step tasks
3. **Study V2**: Understand structured tool systems and API design
4. **Master V3**: Production-ready architecture and extensibility
5. **Explore V4**: Advanced conversation management and compression

#### Refactoring Study Track
- **V1 → V1r**: Learn Bash to Python migration patterns
- **V2 → V2r**: Study modern Python architecture practices
- **V3 → V3r**: Understand modular architecture without feature changes
- **Compare V3r vs V4**: See architecture vs feature evolution

### V3 Tool System Architecture (Recommended)

Complete object-oriented tool system in `v3/`:

```
v3/
├── agent.py              # Main AgentV3 class
└── tools/
    ├── base.py          # BaseTool class & ToolRegistry
    ├── registry.py      # ToolManager & registration
    ├── file_tools.py    # 4 file operation tools
    ├── file_search_tools.py  # 2 file search tools (glob, find)
    ├── text_search_tools.py  # 1 text search tool (grep)
    └── system_tools.py  # 4 system operation tools
```

**V3 Tools (11 total):**

**File Operations (4):**
- `read_file` - Enhanced file reading with encoding detection
- `write_file` - Auto-create directories, atomic writes
- `edit_file` - Safe string replacement with validation
- `list_files` - Directory listing with file details

**Search & Find (3):**
- `glob` - Pattern matching with recursive support
- `grep` - Regex text search with context
- `find` - Advanced file search by size/time/permissions

**System Operations (4):**
- `run_bash` - Safe command execution with danger detection
- `which` - Command path finder
- `env` - Environment variable management
- `pwd` - Current directory information

### Communication Flow

```
User Input → Agent Main Loop → OpenRouter API (with tool definitions)
    ↓
Parse Response → If tool_calls: Execute tools → Add results to history → Loop back
    ↓
If stop: Print response and exit
```

**API Configuration:**
- **Model:** `deepseek/deepseek-v3.2` (configurable in agent files)
- **Endpoint:** `https://openrouter.ai/api/v1/chat/completions`
- **Timeout:** 60 seconds for API calls, 30 seconds for tool execution
- **Max tokens:** 4096

### Safety Features

**Bash Agents (V0, V1):**
- Dangerous command detection via regex: `rm |sudo |chmod |curl.*\|.*sh`
- User manual confirmation prompts for risky operations
- Command preview before execution
- Prevention of infinite loops (max 20 steps in V1)

**Python Agents (V2, V3):**
- 30-second timeout on all tool operations
- File operation error handling with descriptive messages
- No privilege escalation (no sudo support)
- UTF-8 safe file handling

## Development Patterns

### Adding New Tools (V3 Architecture)

1. Create a class inheriting from `BaseTool` in `v3/tools/`
2. Implement `definition` property (OpenAI tool format)
3. Implement `execute(input_data)` method
4. Register in `v3/tools/registry.py`

Example:
```python
# v3/tools/my_tools.py
from .base import BaseTool

class HttpTool(BaseTool):
    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "http_request",
                "description": "Send HTTP requests",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Request URL"},
                        "method": {"type": "string", "default": "GET"}
                    },
                    "required": ["url"]
                }
            }
        }

    def execute(self, input_data):
        # Implementation here
        return f"HTTP {input_data['method']} to {input_data['url']}"

# Register in registry.py
from .my_tools import HttpTool
# Add to ToolManager.initialize()
```

### Configuration Points

**Change AI Model:**
- V3: `v3/agent.py` line ~40: `"model": "deepseek/deepseek-v3.2"`
- V2: `v2/agent.py` line ~20: `"model": "deepseek/deepseek-v3.2"`
- V1: `v1/agent.sh` line ~45: model field in API call
- V0: `v0/agent.sh` line ~15: model field in API call

**Modify Timeouts:**
- V3 API timeout: `v3/agent.py` (~60 seconds)
- V3 tool execution: `v3/tools/system_tools.py` (~30 seconds)
- V2 timeouts: `v2/agent.py` and `v2/tools_execution.py`
- V1/V0 timeouts: shell script timeout parameters

**Safety Rules:**
- V3: `v3/tools/system_tools.py` - `RunBashTool.execute()` danger patterns
- V2: `v2/tools_execution.py` - `_execute_run_bash()` function
- V1: `v1/agent.sh` - regex pattern around line 21
- V0: No safety rules (minimal implementation)

## Important Notes

- **Educational Purpose:** This is a learning project showing CLI agent evolution
- **Language:** All code and comments are in English for international accessibility
- **Dependencies:** Only Python standard library (no pip install needed)
- **State:** All agents are stateless - conversation history in memory only
- **No Build System:** Pure runtime execution, no configuration files or databases
- **Permissions:** Executable files need 755 permissions (`chmod +x v*/agent.*`)

## Quick Start Recommendation

**For Learning:** Start with V0 and progress through each version
**For Usage:** Jump directly to V3 for the most complete experience
**For Understanding:** Read each version's README.md for detailed explanations

## Architecture Evolution Summary

### Main Evolution Track
| Feature | V0 | V1 | V2 | V3 | V4 |
|---------|----|----|----|----|----|----|
| **Lines of Code** | 33 | 157 | 558 | 1823 | 3057 |
| **Language** | Bash | Bash | Python | Python | Python |
| **Tools** | 0 | 0 | 6 | 11 | 13 |
| **Safety** | None | Basic | Timeout | Complete | Complete |
| **Architecture** | Linear | Loop | Modular | OOP | Modular OOP |
| **Extensibility** | None | None | Manual | Automatic | Advanced |
| **Special Features** | - | Multi-step | Tool System | Production Ready | Conversation Mgmt |

### Refactoring Evolution
| Feature | V1 | V1 Refactor | V2 | V2 Refactor | V3 | V3 Refactor |
|---------|----|-----------|----|------------|----|-----------
| **Lines of Code** | 157 | 260 | 558 | 1003 | 1823 | 2904 |
| **Language** | Bash | Python | Python | Python | Python | Python |
| **Architecture** | Loop | OOP | Modular | Modern OOP | OOP | V4 Modular |
| **Purpose** | Original | Python Port | Original | Architecture | Original | Architecture Demo |

### Recommendations
- **For Learning**: Start with V0 → V1 → V2 → V3 → V4
- **For Refactoring Study**: Compare original vs refactor versions
- **For Production**: Use V3 (`v3/agent.py`) or V4 (`v4/app.py`)
- **For Architecture Study**: Use V3 Refactor (`v3r/app.py`)