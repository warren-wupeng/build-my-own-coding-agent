# V1_refactor - Architecture Migration Demo

**V1_refactor** demonstrates the migration from bash scripting to Python architecture while maintaining 100% functional compatibility with V1.

## Overview

V1_refactor is a bridge version that:
- **Preserves V1 functionality**: All V1 features work exactly the same
- **Adopts V2 architecture**: Uses Python with modular file structure
- **Maintains compatibility**: Same user interface (`agent.sh`)
- **Enables future growth**: Structured foundation for adding tools

## Key Features

### Preserved V1 Functionality
- ✅ **JSON Response Format**: AI returns `{"action": "bash", "command": "..."}` or `{"action": "done", "message": "..."}`
- ✅ **Safety Checks**: Detects dangerous commands (`rm`, `sudo`, `chmod`, `curl.*|.*sh`) with user confirmation
- ✅ **Conversation Loop**: Multi-step task execution with message history
- ✅ **Step Limit**: Maximum 20 steps to prevent infinite loops
- ✅ **Direct Bash Execution**: Commands executed directly in shell

### New Architectural Benefits
- 🏗️ **Modular Design**: Separated concerns (API, execution, safety)
- 🧪 **Testability**: Python implementation enables unit testing
- 🔧 **Maintainability**: Clear module boundaries and responsibilities
- 📈 **Extensibility**: V2-compatible structure for future tool additions

## File Structure

```
v1_refactor/
├── agent.sh              # Entry point (bash wrapper)
├── agent.py              # Core logic (V1 functionality in Python)
├── tools_definitions.py  # Empty tool framework (V2 compatibility)
├── tools_execution.py    # Bash execution and safety checks
└── README.md             # This documentation
```

## Usage

### Prerequisites
- Python 3.7+
- OpenRouter API key
- Unix-like environment (bash)

### Setup
```bash
export OPENROUTER_API_KEY="your-key-here"
cd v1_refactor
chmod +x agent.sh
```

### Examples

**Basic Usage:**
```bash
./agent.sh "create a hello.py file and print hello world"
```

**Multi-step Task:**
```bash
./agent.sh "list all Python files, then count the total lines of code"
```

**Safety Check Example:**
```bash
./agent.sh "clean up temporary files with rm command"
# Will prompt for confirmation on dangerous commands
```

## Architecture Comparison

| Aspect | V1 (Original) | V1_refactor | Benefits |
|--------|---------------|-------------|----------|
| **Language** | Bash | Python + Bash | Better error handling, testing |
| **Structure** | Single file | 4 modular files | Separation of concerns |
| **Entry Point** | agent.sh | agent.sh → agent.py | Backward compatibility |
| **Functionality** | Full V1 features | Identical V1 features | Zero functionality loss |
| **Architecture** | Monolithic | V2-compatible modules | Future extensibility |

## Migration Benefits

### 1. Language Migration Strategy
- **Gradual Migration**: Keeps user interface unchanged while upgrading internals
- **Compatibility Wrapper**: Bash script wraps Python implementation
- **Functional Parity**: Ensures migration doesn't affect user experience

### 2. Architecture Pattern Application
- **Modular Design**: From single file to structured multi-module organization
- **Separation of Concerns**: API calls, execution logic, safety checks are independent
- **Interface Standardization**: Foundation for future extensions

### 3. Code Quality Improvements
- **Enhanced Testability**: Python implementation allows unit testing
- **Better Error Handling**: More precise exception handling and user feedback
- **Improved Maintainability**: Clear module boundaries and responsibilities

## Technical Details

### API Compatibility
- **Same Model**: `deepseek/deepseek-v3.2`
- **Same Tokens**: 1024 max tokens
- **Same Timeout**: 30 seconds
- **Same Prompts**: Identical system prompt as V1

### Safety Implementation
Preserves exact V1 safety patterns:
```python
# Dangerous command patterns (same as V1)
dangerous_patterns = [
    r'\brm\s',           # rm command
    r'\bsudo\s',         # sudo command
    r'\bchmod\s',        # chmod command
    r'curl.*\|.*sh',     # curl piped to sh
    r'wget.*\|.*sh'      # wget piped to sh
]
```

### Error Handling
Enhanced error handling while maintaining V1 behavior:
- Network errors with detailed messages
- JSON parsing errors with fallback
- Command execution timeouts (30s limit)
- User interruption handling

## Development Evolution Path

V1_refactor serves as a crucial bridge in the architecture evolution:

```
V1 (bash script)
    ↓ [V1_refactor: Architecture upgrade]
V1_refactor (Python + V2 architecture)
    ↓ [Add tools]
V2 (Complete tool system)
    ↓ [Object-oriented]
V3 (OOP architecture)
    ↓ [Layered architecture]
V4 (Advanced features)
```

## Statistics

- **Total Lines**: ~240 lines (vs V1's 158 lines)
- **Files**: 4 files (vs V1's 1 file)
- **Architecture**: V2-compatible modular structure
- **Functionality**: 100% V1 feature parity
- **Dependencies**: Python 3 standard library only

## Testing

Verify functionality matches V1:

```bash
# Basic test
./agent.sh "echo hello world"

# Multi-step test
./agent.sh "create test.txt with content and show it"

# Safety test
./agent.sh "rm -rf /"  # Should prompt for confirmation

# Error test
./agent.sh "invalid_command_xyz"  # Should handle gracefully
```

## Future Extensions

V1_refactor's V2-compatible architecture enables:
- Adding actual tools to `tools_definitions.py`
- Extending `tools_execution.py` with more tool types
- Upgrading to V3's object-oriented patterns
- Integrating advanced features from V4

---

**V1_refactor demonstrates successful architecture migration while preserving complete functional compatibility.**