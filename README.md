# My Coding Agents

**A project demonstrating the evolution of Claude Code-like CLI programming assistants from simple to complex**

This project showcases how to build an AI programming assistant through four progressive versions, from the simplest 33-line bash script to a fully-featured 1,783-line object-oriented Python architecture. Each version represents different design philosophies and complexity levels, demonstrating a 5,303% code growth journey.

## Project Evolution Path

This project demonstrates four development stages of CLI programming assistants:

### 📖 Learning Path Recommendations
1. **v0 - Understanding Basic Concepts**: Start with the simplest implementation
2. **v1 - Adding Safety and Loops**: Understand necessary features for real-world applications
3. **v2 - Introducing Tool System**: Learn structured API design
4. **v3 - Complete Architecture**: Master extensible object-oriented design
5. **v4 - Advanced Conversation Management**: Learn token optimization and conversation compression

### 🎯 Core Value of Each Version
- **v0**: Proof of concept feasibility, minimal implementation
- **v1**: Practical considerations, safety protection
- **v2**: Architectural thinking, feature separation
- **v3**: Engineering practices, extensibility
- **v4**: Production optimization, token management, long conversation handling

## Version Overview

### 🚀 V0 - Proof of Concept (33 lines of code)
**Location**: `v0/` | **Complexity**: ⭐ | **Language**: Bash
- Simplest AI assistant implementation
- Single conversation, no loops
- Direct execution of AI-suggested commands
- **Learning Focus**: Understanding basic AI assistant principles

```bash
cd v0 && ./agent.sh "list all Python files"
```

### 🔄 V1 - Practical Enhancement (157 lines of code)
**Location**: `v1/` | **Complexity**: ⭐⭐ | **Language**: Bash
- Add conversation loops for multi-step tasks
- Dangerous command detection and user confirmation
- Error handling and retry mechanisms
- **Learning Focus**: Security considerations in real deployments

```bash
cd v1 && ./agent.sh "create a Python project structure"
```

### 🐍 V1 Refactor - Python Rewrite (260 lines of code)
**Location**: `v1r/` | **Complexity**: ⭐⭐ | **Language**: Python
- Keep V1 functionality but rewrite in Python
- Better error handling and code structure
- Bridge between Bash and Python paradigms
- **Learning Focus**: Language migration patterns and refactoring techniques

```bash
cd v1r && ./agent.sh "create a Python project structure"
```

### 🛠️ V2 - Tool System (558 lines of code)
**Location**: `v2/` | **Complexity**: ⭐⭐⭐ | **Language**: Python
- Introduce structured tool calling
- Separate tool definitions from execution logic
- Support file operations, search, system commands
- Enhanced safety mechanisms with comprehensive dangerous command detection
- **Learning Focus**: API design and feature modularization

```bash
cd v2 && ./agent.sh "analyze the codebase structure"
```

### 🏛️ V2 Refactor - Modern Architecture (1003 lines of code)
**Location**: `v2r/` | **Complexity**: ⭐⭐⭐ | **Language**: Python + Modern Patterns
- Keep V2's 6 tools but with improved architecture
- Adopt modern Python design patterns and best practices
- Better code organization and modular structure
- **Learning Focus**: Architecture refactoring without functional changes

```bash
cd v2r && ./agent.sh "analyze the codebase structure"
```

### 🏗️ V3 - Complete Architecture (1823 lines of code)
**Location**: `v3/` | **Complexity**: ⭐⭐⭐⭐ | **Language**: Python + OOP
- Object-oriented tool system
- Extensible tool registration mechanism
- Complete error handling and timeout control
- Comprehensive safety features matching V2 implementation
- **Learning Focus**: Maintainable software architecture design

```bash
cd v3 && ./agent.sh "create a hello.py file and run it"
```

### 🔄 V3 Refactor - V4 Architecture + V3 Functionality (2904 lines of code)
**Location**: `v3r/` | **Complexity**: ⭐⭐⭐⭐ | **Language**: Python + V4 Modular Architecture
- Use V4's complete modular architecture (core/execution/interface/llm/monitoring)
- Maintain V3's exact functionality (11 tools, no conversation compression)
- Demonstrate pure architectural refactoring best practices
- **Learning Focus**: How to refactor architecture while preserving functionality

```bash
cd v3r && ./agent.sh "create a hello.py file and run it"
```

### 💬 V4 - Advanced Conversation Management (3057 lines of code)
**Location**: `v4/` | **Complexity**: ⭐⭐⭐⭐⭐ | **Language**: Python + OOP + Layered Architecture
- Modular architecture with 7 core modules (Core, LLM, Execution, Interface, Monitoring, Conversation, Tools)
- Event-driven architecture with complete UI/business logic separation
- Intelligent conversation compression with 265-line compression engine
- Automatic compression at 25 message threshold with conservative context preservation
- Advanced statistics and monitoring system (221 lines)
- 13 tools including 2 conversation management tools
- Comprehensive test suite (406 lines across 2 test files)
- **Learning Focus**: Production-ready architecture and token optimization

```bash
cd v4 && ./agent.sh "create a complex multi-file project"
```

## 📊 Code Statistics

### Lines of Code Evolution (Excluding Tests)

| Version | Files | Lines | Language | Architecture | Growth |
|---------|-------|-------|----------|-------------|---------|
| **V0** | 1 | 33 | Bash | Linear script | — |
| **V1** | 1 | 157 | Bash | Loop-based | +376% |
| **V2** | 3 | 562 | Python | Modular system | +258% |
| **V3** | 8 | 1,783 | Python + OOP | Framework | +217% |
| **V4** | 21 | 3,416 | Python + OOP | Layered + Event-Driven | +92% |

### Growth Visualization

```
V0:         33 █
V1:        157 █████
V1r:       260 ████████
V2:        558 ███████████████████
V2r:      1003 ███████████████████████████████████
V3:       1823 ████████████████████████████████████████████████████████████████
V3r:      2904 █████████████████████████████████████████████████████████████████████████████████████████████████████████
V4:       3057 ████████████████████████████████████████████████████████████████████████████████████████████████████████████
```

### Key Metrics

#### Main Evolution Track
- **Total Growth**: 33 → 3,057 lines (**9,163% increase**)
- **V0→V1**: Added safety mechanisms and conversation loops (+124 lines)
- **V1→V2**: Language migration and tool system implementation (+401 lines)
- **V2→V3**: Full OOP architecture and comprehensive framework (+1,265 lines)
- **V3→V4**: Layered architecture with conversation management (+1,234 lines)
- **Tools Evolution**: 0 → 0 → 6 → 11 → 13 tools across versions

#### Refactoring Track
- **V1→V1r**: Bash to Python migration (+103 lines)
- **V2→V2r**: Modern architecture refactoring (+445 lines)
- **V3→V3r**: V4 architecture adoption (+1,081 lines)
- **Refactoring Impact**: Shows code quality improvement without feature changes
- **Architecture Value**: V3r demonstrates V4 patterns with V3 functionality

### File Breakdown

**V2 (558 lines total):**
- `agent.py`: 165 lines
- `tools_definitions.py`: 118 lines
- `tools_execution.py`: 275 lines

**V2r (1003 lines total):**
- Modern Python architecture with 7 modules
- Improved separation of concerns
- Enhanced error handling and validation
- Better code organization and maintainability

**V3 (1823 lines total):**
- `agent.py`: 278 lines
- `tools/base.py`: 191 lines
- `tools/registry.py`: 215 lines
- `tools/file_tools.py`: 300 lines
- `tools/file_search_tools.py`: 255 lines (glob, find)
- `tools/text_search_tools.py`: 172 lines (grep)
- `tools/system_tools.py`: 372 lines

**V3r (2904 lines total):**
- V4's complete modular architecture
- All V4 modules: core, execution, interface, llm, monitoring, conversation
- V3's exact functionality (11 tools, no conversation compression)
- Perfect demonstration of architecture refactoring best practices

**V4 (3057 lines total):**
- **Core Modules**:
  - `core/agent_core.py`: 138 lines (business logic)
  - `app.py`: 80 lines (application manager)
  - `agent.py`: 12 lines (entry point)
- **Tool System** (1,678 lines):
  - `tools/base.py`: 195 lines
  - `tools/registry.py`: 238 lines
  - `tools/file_tools.py`: 300 lines
  - `tools/file_search_tools.py`: 255 lines
  - `tools/text_search_tools.py`: 172 lines
  - `tools/system_tools.py`: 372 lines
  - `tools/conversation_tools.py`: 146 lines (NEW)
- **Architecture Modules**:
  - `conversation/compressor.py`: 265 lines (compression engine)
  - `llm/client.py`: 193 lines (API client)
  - `execution/tool_executor.py`: 218 lines (tool executor)
  - `monitoring/statistics.py`: 221 lines (statistics collector)
  - `interface/display.py`: 113 lines (output manager)
  - `interface/cli.py`: 60 lines (CLI parser)
- **Testing** (406 lines):
  - `test_conversation_compact.py`: 244 lines
  - `test_safety.py`: 162 lines

## Tools Available

| Tool | Description | Available In |
|------|-------------|--------------|
| `read_file` | Read file contents | V2, V3, V4 |
| `write_file` | Write content to file | V2, V3, V4 |
| `edit_file` | Make precise edits | V2, V3, V4 |
| `list_files` | List directory contents | V3, V4 |
| `glob` | Find files by pattern | V2, V3, V4 |
| `grep` | Search text in files | V2, V3, V4 |
| `find` | Advanced file search | V3, V4 |
| `run_bash` | Execute shell commands | V2, V3, V4 |
| `which` | Find command paths | V3, V4 |
| `env` | Environment variables | V3, V4 |
| `pwd` | Current directory info | V3, V4 |
| `compact_conversation` | Compact conversation history | V4 |
| `conversation_stats` | Get conversation statistics | V4 |

## Setup

### Prerequisites
- Python 3.7+
- bash (for shell agents)
- OpenRouter API key
- `jq` (for bash agents)

### Installation

1. Clone this repository
```bash
git clone https://github.com/yourusername/my-coding-agents.git
cd my-coding-agents
```

2. Set up your API key
```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

3. Make scripts executable
```bash
chmod +x v0/agent.sh v1/agent.sh v2/agent.py v3/agent.py
```

### Get OpenRouter API Key
1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Sign up and create an API key
3. Set the environment variable

## Usage Examples

### V0 - Basic Usage
```bash
cd v0
./agent.sh "find all Python files in current directory"
```

### V1 - Multi-step Tasks
```bash
cd v1
./agent.sh "create a Python project with tests directory and main.py"
```

### V2 - Structured Tools
```bash
cd v2
./agent.sh "read the README file and summarize the project"
./agent.sh "find all function definitions in Python files"
```

### V3 - Full-Featured (Recommended)
```bash
cd v3
./agent.sh "Create a Flask web application with proper structure"
./agent.sh "Analyze this codebase and generate a project report"
./agent.sh "Set up a new Python package with tests and documentation"
```

## Architecture

### V4 Layered Architecture (Recommended)

The advanced Python agent uses a layered, event-driven architecture with complete separation of concerns:

```
v4/
├── agent.py              # Compatibility entry point (12 lines)
├── app.py                # Application manager (80 lines)
├── core/
│   └── agent_core.py    # Pure business logic controller (138 lines)
├── llm/
│   └── client.py        # LLM API client (193 lines)
├── conversation/
│   └── compressor.py    # Intelligent compression engine (265 lines)
├── execution/
│   └── tool_executor.py # Tool execution handler (218 lines)
├── monitoring/
│   └── statistics.py    # Statistics collector (221 lines)
├── interface/
│   ├── cli.py          # Command line interface (60 lines)
│   └── display.py      # Display/output management (113 lines)
└── tools/              # Tool system (1,678 lines total)
    ├── base.py         # BaseTool class & ToolRegistry (195 lines)
    ├── registry.py     # ToolManager & registration (238 lines)
    ├── file_tools.py   # 4 file operation tools (300 lines)
    ├── file_search_tools.py  # 2 file search tools (255 lines)
    ├── text_search_tools.py  # 1 text search tool (172 lines)
    ├── system_tools.py # 4 system operation tools (372 lines)
    └── conversation_tools.py  # 2 conversation tools (146 lines)
```

### V3 Tool System (Legacy)

The V3 object-oriented tool architecture:

```
v3/
├── agent.py              # Main AgentV3 class
└── tools/
    ├── base.py          # BaseTool class & ToolRegistry
    ├── registry.py      # ToolManager & registration
    ├── file_tools.py    # 4 file operation tools
    ├── file_search_tools.py  # 2 file search tools (glob, find)
    ├── text_search_tools.py # 1 text search tool (grep)
    └── system_tools.py  # 4 system operation tools
```

#### V4 Key Features

**Event-Driven Architecture:**
- `AgentCore` emits events for UI communication
- `EventHandler` processes all display logic
- Complete separation of business logic and presentation

**Conversation Management:**
- Automatic compression at 25-message threshold
- Conservative strategy preserving 15 recent messages
- 40-60% token reduction in long conversations
- Manual compression tools available

**Advanced Monitoring:**
- Real-time statistics collection
- Performance metrics (steps/second, API calls/minute)
- Export capabilities (JSON format)
- Comprehensive session analytics

#### Adding New Tools (V4)

```python
# v4/tools/my_tools.py
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
        # Tool implementation here
        return f"HTTP {input_data['method']} to {input_data['url']}"

# Register in v4/tools/registry.py
from .my_tools import HttpTool
# Add to ToolManager.initialize()
```

## Safety Features

### Bash Agents (V0, V1)
- **V0**: No safety features (proof of concept)
- **V1**: Interactive dangerous command detection with user confirmation prompts
  - Patterns: `rm `, `sudo `, `chmod `, `curl.*|.*sh`
  - Manual user approval required for risky operations

### Python Agents (V2, V3)
- **Enhanced Security Implementation**: Comprehensive dangerous command detection
- **Static Protection**: Automatic blocking without user interaction
- **Command Patterns Detected**:
  - Root filesystem operations: `rm -rf /`, `sudo rm`
  - Permission modifications: `chmod 777`
  - Pipe to shell attacks: `curl ... | sh`, `wget ... | bash`
  - System operations: `shutdown`, `reboot`, `halt`, `init 0`
  - Disk operations: `dd if=`, `mkfs.*`, `fdisk`, `parted`
- **Additional Protections**:
  - Command length limiting (1000 characters max)
  - Timeout enforcement (30 seconds per operation)
  - Case-insensitive pattern matching
  - Clear safety messaging and recommendations

### Security Testing
Both V2 and V3 include comprehensive test suites:
```bash
# Test V2 safety features
cd v2 && ./agent.sh --test-safety

# Test V3 safety features
cd v3 && ./agent.sh --test-safety
```
Expected: 11/11 safety tests pass with 100% success rate

## Configuration

### Models
Currently using DeepSeek v3.2 via OpenRouter. You can modify the model in each version:
- **V0**: `v0/agent.sh` - edit model field in API call
- **V1**: `v1/agent.sh` - edit model field in API call
- **V2**: `v2/agent.py` - change `model` parameter
- **V3**: `v3/agent.py` - change `model` parameter

### Timeouts
- API calls: 60 seconds
- Tool execution: 30 seconds
- Command execution: 30 seconds

## Development

### Current Project Structure
```
my-coding-agents/
├── README.md              # This file
├── CLAUDE.md              # Claude Code guidance
├── LICENSE                # MIT License
├── .gitignore            # Git ignore rules
│
├── v0/                   # Proof of concept (33 lines)
│   ├── agent.sh         # Minimal bash implementation
│   └── README.md        # V0 documentation
│
├── v1/                   # Practical enhancement (157 lines)
│   ├── agent.sh         # Enhanced bash with safety loops
│   └── README.md        # V1 documentation
│
├── v2/                   # Tool system (562 lines)
│   ├── agent.py         # Python main program (165 lines)
│   ├── tools_definitions.py  # API definitions (118 lines)
│   ├── tools_execution.py    # Implementation with safety (279 lines)
│   ├── test_safety.py   # Security test suite
│   └── README.md        # V2 documentation
│
├── v3/                   # Complete architecture (1,783 lines)
│   ├── agent.py         # OOP implementation (278 lines)
│   ├── tools/           # Tool system package (1,496 lines)
│   │   ├── base.py      # Base classes (191 lines)
│   │   ├── registry.py  # Tool management (215 lines)
│   │   ├── file_tools.py     # File operations (300 lines)
│   │   ├── file_search_tools.py  # File search (glob, find) (255 lines)
│   │   ├── text_search_tools.py  # Text search (grep) (172 lines)
│   │   ├── system_tools.py   # System commands (372 lines)
│   │   └── __init__.py  # Package initialization
│   ├── test_safety.py   # Security test suite
│   └── README.md        # V3 documentation
│
└── v4/                   # Layered architecture (3,416 lines)
    ├── agent.py         # Compatibility entry point (12 lines)
    ├── app.py           # Application manager (80 lines)
    ├── core/            # Business logic (143 lines)
    │   ├── __init__.py
    │   └── agent_core.py
    ├── llm/             # LLM communication (198 lines)
    │   ├── __init__.py
    │   └── client.py
    ├── conversation/    # Compression engine (270 lines)
    │   ├── __init__.py
    │   └── compressor.py
    ├── execution/       # Tool execution (224 lines)
    │   ├── __init__.py
    │   └── tool_executor.py
    ├── monitoring/      # Statistics & analytics (226 lines)
    │   ├── __init__.py
    │   └── statistics.py
    ├── interface/       # CLI & display (179 lines)
    │   ├── __init__.py
    │   ├── cli.py
    │   └── display.py
    ├── tools/           # Tool system (1,678 lines)
    │   ├── __init__.py
    │   ├── base.py      # Base classes (195 lines)
    │   ├── registry.py  # Tool management (238 lines)
    │   ├── file_tools.py     # File operations (300 lines)
    │   ├── file_search_tools.py  # File search (255 lines)
    │   ├── text_search_tools.py  # Text search (172 lines)
    │   ├── system_tools.py   # System commands (372 lines)
    │   └── conversation_tools.py  # Conversation mgmt (146 lines)
    ├── test_safety.py   # Security test suite (162 lines)
    ├── test_conversation_compact.py  # Compression tests (244 lines)
    └── README.md        # V4 documentation
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add your tool or improvement
4. Test thoroughly with each version
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [OpenRouter](https://openrouter.ai) for AI model access
- Uses DeepSeek v3.2 for intelligent command generation
- Inspired by the need for safe, practical AI coding assistants

## Troubleshooting

### Common Issues

**API Key Not Set**
```
❌ Error: OPENROUTER_API_KEY environment variable not set
```
Solution: `export OPENROUTER_API_KEY="your-key"`

**jq Not Found (bash agents)**
```
command not found: jq
```
Solution: `brew install jq` (macOS) or `apt install jq` (Ubuntu)

**Permission Denied**
```
Permission denied: ./agent.sh
```
Solution: `chmod +x v*/agent.*`

### Getting Help

1. Check the error message carefully
2. Ensure API key is set correctly
3. Verify file permissions
4. Check network connectivity
5. Read the version-specific README.md files
6. Open an issue on GitHub

---

**Happy Coding with AI! 🤖✨**