# V5 - SWE-bench Evaluation Integration Version

> **Note**: This is V5, extending V4 with SWE-bench evaluation capabilities.  
> See [PLAN.md](./PLAN.md) for the complete development plan.

## Quick Start

### Prerequisites

- Python >= 3.10
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Installation

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies**:
   ```bash
   cd v5
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   export OPENROUTER_API_KEY="your-api-key"
   ```

### Running the Agent

```bash
# Using uv (recommended)
uv run python agent.py "your task description"

# Or activate virtual environment manually
source .venv/bin/activate
python agent.py "your task description"
```

### Development

```bash
# Run all tests (unit tests only, skips integration tests)
uv run pytest

# Run integration tests (requires network access to HuggingFace)
uv run pytest -m integration

# Run all tests including integration tests
uv run pytest -m "not integration"  # unit tests only
uv run pytest -m integration        # integration tests only
uv run pytest                       # all tests

# Run with coverage
uv run pytest --cov=swebench --cov-report=term-missing

# Add new dependency
uv add <package-name>

# Add development dependency
uv add --dev <package-name>

# Sync environment
uv sync
```

### Dependencies

- **Core**: `datasets`, `unidiff`
- **Development**: `pytest`, `pytest-cov`
- **Optional (Evaluation)**: `docker` (for local SWE-bench evaluation)

See `pyproject.toml` for complete dependency list.

---

# V4 - Advanced Conversation Management Version (Base)

**Object-oriented tool system with intelligent conversation compression, 400+ lines of code**

## Design Philosophy

V4 version extends V3 with advanced conversation management capabilities:
1. **Object-Oriented Design**: Each tool is an independent class, easy to extend and maintain
2. **Intelligent Compression**: Automatic conversation compression to manage token usage
3. **Conservative Approach**: Preserves context while reducing token consumption
4. **Production Quality**: Comprehensive error handling, statistics, validation mechanisms
5. **User Experience**: Detailed execution feedback, progress display, help system

## Core Architecture

### 🏗️ System Architecture
```
AgentV4 (Main Agent Class with Compression)
    ↓
ToolManager (Tool Manager)
    ↓
ToolRegistry (Tool Registry)
    ↓
BaseTool (Base Tool Class)
    ↓
Concrete Tool Implementation (13 tools)
```

### 📁 Complete File Structure
```
v4/
├── agent.py                 # Main agent program with compression
├── tools/                   # Tool system package
│   ├── __init__.py         # Package initialization
│   ├── base.py             # Tool base class and registration system
│   ├── registry.py         # Tool management and registration center
│   ├── file_tools.py       # File operation tools (4 tools)
│   ├── file_search_tools.py # File search tools (2 tools: glob, find)
│   ├── text_search_tools.py # Text search tools (1 tool: grep)
│   ├── system_tools.py     # System operation tools (4 tools)
│   └── conversation_tools.py # Conversation management tools (2 tools)
└── README.md               # This document
```

## New Features in V4

### 🧬 Intelligent Conversation Compression
- **Automatic Compression**: Triggers when message count exceeds threshold (25 messages)
- **Conservative Settings**: Keeps 15 recent messages, compresses to max 18 messages
- **Context Preservation**: Always preserves first message and recent context
- **Block-based Compression**: Groups messages by type for intelligent summarization
- **Token Management**: Reduces token usage by 40-60% in long conversations

### 🛠️ Rich Tool Set (13 tools)

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

#### 💬 Conversation Management (2 tools) - NEW
- `compact_conversation`: Manually compact conversation history with customizable settings
- `conversation_stats`: Get statistics about conversation length and token usage

### 🎛️ Advanced Features
- **Execution Statistics**: Tool usage frequency and total count statistics
- **Compression Statistics**: Track compression count and token estimates
- **Error Recovery**: Comprehensive exception handling and user-friendly error messages
- **Progress Display**: Detailed step tracking and status feedback
- **System Validation**: Tool system integrity checking
- **Category Management**: Tools displayed by functional categories

## Conversation Compression Details

### Conservative Compression Strategy
- **Threshold**: 25 messages (higher threshold, less frequent compression)
- **Keep Recent**: 15 messages (generous context preservation)
- **Max Length**: 18 messages after compression
- **Block Size**: 6 messages per compression block

### Compression Process
1. **Preserve First Message**: Always keeps the initial user request
2. **Keep Recent Messages**: Preserves last 15 messages for immediate context
3. **Compress Middle Section**: Analyzes and compresses messages in the middle
4. **Block Grouping**: Groups messages by type (user, assistant, tool) for intelligent summarization
5. **Smart Summarization**: Creates concise summaries while preserving key information

### Automatic vs Manual Compression
- **Automatic**: Triggers automatically when message count > 25
- **Manual**: Use `compact_conversation` tool for on-demand compression
- **Statistics**: Use `conversation_stats` tool to monitor conversation state

## Usage

```bash
# Set API key
export OPENROUTER_API_KEY="your-api-key"

# Run the assistant
cd v4
python agent.py "Create a Python web application project structure"
```

### Command Options
```bash
# Show help and tool list
python agent.py --help

# Execute task
python agent.py "your task description"
```

## Example Conversation with Compression

```
$ python agent.py "Create a complex multi-file project with many steps"

🚀 AI Assistant V4 - Advanced Conversation Management
🏗️  Object-Oriented Tool System | Intelligent Compression

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
  📦 Registering Conversation Management tools...
✅ Registered tool: compact_conversation
✅ Registered tool: conversation_stats
✅ Tool system initialization complete, registered 13 tools total

🛠️  Loaded tools: 13
   • read_file: Read file contents with UTF-8 encoding support
   • write_file: Write content to file, auto-create directories if they don't exist
   ...
   • compact_conversation: Compact conversation history to reduce token usage
   • conversation_stats: Get statistics about current conversation length

📝 Task: Create a complex multi-file project...

🔄 Execution Step 1
   🔗 Need to execute 1 tool
   [1/1] 🔧 Calling tool 'write_file'
   ...

... (many steps later) ...

🔄 Execution Step 26
📦 Auto-compacting conversation (26 messages → preserving context)
   ✅ Conservative compression: 26 → 18 messages

🔄 Execution Step 27
   🔗 Need to execute 1 tool
   ...

🎉 Task completed successfully! Total steps executed: 30.

📊 Execution Statistics:
   • Total steps: 30
   • Message count: 22
   • Conversation compactions: 1
   • Estimated tokens: ~4523
   • Compression threshold: 25 messages
   • Keep recent messages: 15
   • Tool usage:
     - write_file: 8 times
     - read_file: 3 times
```

## Technical Highlights

### 1. Conversation Compression Algorithm
```python
def _compact_messages_conservative(self, keep_recent=15, max_total=18):
    """Conservative compression logic"""
    # Preserve first message
    # Keep recent messages
    # Analyze and compress middle section
    # Group by message type
    # Create intelligent summaries
```

### 2. Automatic Compression Trigger
```python
# In run_conversation_loop
if len(self.messages) > self.auto_compact_threshold:
    self._auto_compact_conversation()
```

### 3. Message Analysis and Grouping
```python
def _analyze_message_structure(self, messages):
    """Analyze messages to identify compressible blocks"""
    # Groups messages by type (user, assistant, tool)
    # Identifies blocks of 6+ messages for compression
```

### 4. Tool Integration
```python
# Conversation tools can access agent instance
compact_tool = get_tool_instance("compact_conversation")
compact_tool.agent_instance = self
```

## V3 → V4 Major Improvements

- ✅ **Conversation Compression**: Automatic and manual compression capabilities
- ✅ **Token Management**: 40-60% token reduction in long conversations
- ✅ **Context Preservation**: Conservative approach maintains conversation quality
- ✅ **13 tools** vs V3's 11 tools (added 2 conversation management tools)
- ✅ **Enhanced Statistics**: Compression metrics and token estimates
- ✅ **Extended Conversations**: Can handle 50+ step conversations efficiently
- ✅ **Production-Ready**: Robust compression with error handling

## Benefits

### Token Efficiency
- **Before (V3)**: Linear growth (50 steps = ~50+ messages per API call)
- **After (V4)**: Bounded growth (max ~18 messages per API call)
- **Savings**: 40-60% token reduction in long conversations

### Conversation Quality
- **Context Retention**: Recent messages preserved for immediate context
- **Key Information**: Important results and decisions retained in summaries
- **Continuity**: Conversation flow maintained through intelligent summarization

### User Experience
- **Transparent Operation**: Automatic compression runs seamlessly at 25 message threshold
- **Manual Control**: Users can trigger compression via conversation tools
- **Enhanced Statistics**: Clear display of conversation metrics and compression status
- **Performance**: Faster API responses due to reduced token usage while maintaining context quality

## Extension Guide

### Adding New Tool Classes
1. Inherit from `BaseTool` base class
2. Implement `definition` and `execute` methods
3. Register in `registry.py`
4. Add to appropriate category

### Example: Conversation Tool
```python
class ConversationTool(BaseTool):
    def __init__(self, agent_instance=None):
        self.agent_instance = agent_instance

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "Tool description",
                "parameters": {...}
            }
        }

    def execute(self, input_data):
        # Access agent instance if needed
        if self.agent_instance:
            # Use self.agent_instance.messages, etc.
            pass
        return "Result"
```

This version demonstrates how to build a production-grade AI assistant system with intelligent conversation management for handling extended dialogues efficiently.
