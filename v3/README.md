# V3 - Complete Architecture Version

**Object-oriented tool system, 300+ lines of code showcasing production-grade architecture**

## Design Philosophy

V3 version represents the final form of AI assistant architecture:
1. **Object-Oriented Design**: Each tool is an independent class, easy to extend and maintain
2. **Tool Registration Mechanism**: Dynamic discovery and management of tools, supports plugin architecture
3. **Production Quality**: Comprehensive error handling, statistics, validation mechanisms
4. **User Experience**: Detailed execution feedback, progress display, help system

## Core Architecture

### 🏗️ System Architecture
```
AgentV3 (Main Agent Class)
    ↓
ToolManager (Tool Manager)
    ↓
ToolRegistry (Tool Registry)
    ↓
BaseTool (Base Tool Class)
    ↓
Concrete Tool Implementation (11 tools)
```

### 📁 Complete File Structure
```
v3/
├── agent.py                 # Main agent program (object-oriented)
├── tools/                   # Tool system package
│   ├── __init__.py         # Package initialization
│   ├── base.py             # Tool base class and registration system
│   ├── registry.py         # Tool management and registration center
│   ├── file_tools.py       # File operation tools (4 tools)
│   ├── file_search_tools.py # File search tools (2 tools: glob, find)
│   ├── text_search_tools.py # Text search tools (1 tool: grep)
│   └── system_tools.py     # System operation tools (4 tools)
└── README.md               # This document
```

## New Features

### 🧬 Object-Oriented Tool System
- **BaseTool Base Class**: Unified tool interface and lifecycle
- **Tool Registry**: Dynamic tool discovery and management
- **Tool Manager**: Advanced features like categorization, statistics, validation
- **Plugin Design**: Easy addition of new tools

### 🛠️ Rich Tool Set (11 tools)

#### 📄 File Operations (4 tools)
- `read_file`: Enhanced file reading with encoding detection
- `write_file`: Auto-create directories for file writing
- `edit_file`: Unique string replacement to prevent misoperations
- `list_files`: Directory content listing with file information statistics

#### 🔍 Search and Find (3 tools)
- `glob`: glob pattern file finding with recursive support
- `grep`: Regular expression text search with context display
- `find`: Advanced file finding supporting size, time, and other conditions

#### ⚙️ System Operations (4 tools)
- `run_bash`: Safe command execution with dangerous command detection
- `which`: System command finder
- `env`: Environment variable management
- `pwd`: Current directory information

### 🎛️ Advanced Features
- **Execution Statistics**: Tool usage frequency and total count statistics
- **Error Recovery**: Comprehensive exception handling and user-friendly error messages
- **Progress Display**: Detailed step tracking and status feedback
- **System Validation**: Tool system integrity checking
- **Category Management**: Tools displayed by functional categories

## Usage

```bash
# Set API key
export OPENROUTER_API_KEY="your-api-key"

# Run the assistant
cd v3
python agent.py "Create a Python web application project structure"
```

### Command Options
```bash
# Show help and tool list
python agent.py --help

# Execute task
python agent.py "your task description"
```

## Example Conversation

```
$ python agent.py "Create a Flask application Python project including tests and documentation"

🚀 AI Assistant V3 - Complete Architecture Version
🏗️  Object-Oriented Tool System | Extensible Architecture

🔧 Initializing tool system...
  📦 Registering File Operations tools...
✅ Registered tool: read_file
✅ Registered tool: write_file
✅ Registered tool: edit_file
✅ Registered tool: list_files
  📦 Registering Search and Find tools...
✅ Registered tool: glob
✅ Registered tool: grep
✅ Registered tool: find
  📦 Registering System Operations tools...
✅ Registered tool: run_bash
✅ Registered tool: which
✅ Registered tool: env
✅ Registered tool: pwd
✅ Tool system initialization complete, registered 11 tools total

🛠️  Loaded tools: 11
   • read_file: Read file contents with UTF-8 encoding support
   • write_file: Write content to file, auto-create directories if they don't exist
   • edit_file: Make precise edits by replacing unique strings
   • list_files: List files and subdirectories in a directory
   • glob: Find matching files using glob patterns with wildcard and recursive search support
   • grep: Search matching text content in files with regex and multiple search options support
   • find: Advanced file search supporting file size, modification time, permissions and other attributes
   • run_bash: Safely execute bash commands with timeout control and detailed output
   • which: Find the complete path of system commands
   • env: View or search environment variables
   • pwd: Display detailed information about the current working directory

📝 Task: Create a Flask application Python project including tests and documentation

🔄 Execution Step 1
   🔗 Need to execute 1 tool
   [1/1] 🔧 Calling tool 'run_bash'
   📝 command: mkdir -p flask_project/{app,tests,docs,static,templates}
🔧 Executing command: mkdir -p flask_project/{app,tests,docs,static,templates}
⏱️  Timeout: 30 seconds
   📤 Result: 🔧 Command: mkdir -p flask_project/{app,tests,docs,static,templates}
✅ Execution successful (exit code: 0)

📭 No output

🔄 Execution Step 2
   🔗 Need to execute 1 tool
   [1/1] 🔧 Calling tool 'write_file'
   📝 path: flask_project/app/__init__.py
   📝 content: from flask import Flask

def create_app():
    app = Flask(__name__)

    from . import routes
    app.register_blueprint(routes.bp)

    return app...
   📤 Result: ✅ Successfully written file flask_project/app/__init__.py
📊 Write info: 178 bytes, 8 lines

🔄 Execution Step 3
✅ Flask project structure creation complete! The project includes complete directory structure, Flask application code, test files, and documentation. You can start the application by running `python run.py`.

🎉 Task completed successfully! Total steps executed: 3.

📊 Execution Statistics:
   • Total steps: 3
   • Message count: 9
   • Tool usage:
     - run_bash: 1 time
     - write_file: 6 times
```

## Technical Highlights

### 1. Object-Oriented Tool Architecture
```python
class MyTool(BaseTool):
    @property
    def definition(self):
        return {...}  # OpenAI format definition

    def execute(self, input_data):
        return "Result"  # Tool logic
```

### 2. Dynamic Tool Registration
```python
# Automatic tool discovery and registration
manager = ToolManager()
manager.initialize()  # Auto-register all tools

# Add new tools at runtime
registry.register(NewTool())
```

### 3. Detailed Execution Feedback
```python
# Tool call details
🔧 Calling tool 'write_file'
   📝 path: example.py
   📝 content: print("Hello")...
   📤 Result: ✅ Successfully written file example.py (28 bytes)
```

### 4. Production-Grade Error Handling
- Input parameter validation
- File permission checking
- Timeout control
- User-friendly error messages
- Dangerous operation detection

### 5. Statistics and Monitoring
```python
# Get usage statistics
stats = get_tool_statistics()
# {"total_executions": 42, "tool_usage": {"write_file": 15, ...}}

# Tool system validation
validation = validate_tool_system()
# "✅ Tool system validation passed, 11 tools normal"
```

## Learning Points

1. **Object-Oriented Design**: How to design an extensible tool system
2. **Registry Pattern**: Implementation of plugin architecture
3. **Error Handling Strategy**: Best practices for error handling in production environments
4. **User Experience Design**: Detailed feedback and progress display
5. **Code Organization**: Modular structure for large Python projects
6. **API Design**: Balance of consistency and usability

## Code Quality

### V2 → V3 Major Improvements:
- ✅ Completely object-oriented, each tool is an independent class
- ✅ Automatic tool discovery and registration mechanism
- ✅ 11 tools vs V2's 6 tools, more comprehensive functionality
- ✅ Production-grade error handling and user experience
- ✅ Detailed statistics and system validation
- ✅ Complete documentation and help system
- ✅ Extensible plugin architecture

### Production Features:
- 🚀 Performance: Tool lazy loading and caching mechanisms
- 🛡️ Security: Dangerous command detection and parameter validation
- 📊 Monitoring: Usage statistics and system health checks
- 🔧 Maintenance: Clear code structure and complete documentation
- 🧪 Testing: Built-in validation and consistency checks

## Extension Guide

### Adding New Tool Classes
1. Inherit from `BaseTool` base class
2. Implement `definition` and `execute` methods
3. Register in `registry.py`
4. Add to appropriate category

### Example New Tool
```python
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
                        "url": {"type": "string"},
                        "method": {"type": "string", "default": "GET"}
                    },
                    "required": ["url"]
                }
            }
        }

    def execute(self, input_data):
        # Implement HTTP request logic
        return "HTTP response result"
```

This version demonstrates how to build a production-grade, extensible AI assistant system.