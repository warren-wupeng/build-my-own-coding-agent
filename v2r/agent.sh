#!/bin/bash
# V2 - Tool System with Bash Entry Point
# 保持一致的用户接口，内部使用Python工具系统

# Check if we have any arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 \"task description\""
    echo ""
    echo "V2 - AI Assistant with Tool System"
    echo ""
    echo "Examples:"
    echo "  $0 \"create a hello.py file and run it\""
    echo "  $0 \"list all Python files and count lines\""
    echo "  $0 \"search for 'class' definitions in all Python files\""
    echo "  $0 \"read README.md and summarize the project\""
    echo ""
    echo "V2 Features:"
    echo "  • 6 structured tools (file ops, search, system commands)"
    echo "  • Enhanced safety with comprehensive dangerous command detection"
    echo "  • Modular Python architecture"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required for V2"
    echo "Please install Python 3 to use this version"
    exit 1
fi

# 检查API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ Error: OPENROUTER_API_KEY environment variable not set"
    echo "Please run: export OPENROUTER_API_KEY=\"your-key-here\""
    exit 1
fi

# 调用Python核心逻辑
exec python3 "$(dirname "$0")/agent.py" "$@"