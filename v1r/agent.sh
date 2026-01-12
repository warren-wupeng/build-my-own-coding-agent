#!/bin/bash
# V1_refactor - Bash to Python Architecture Migration
# 保持V1的用户接口，内部使用Python实现

# Check if we have any arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 \"task description\""
    echo ""
    echo "Examples:"
    echo "  $0 \"create a hello.py file and run it\""
    echo "  $0 \"list all Python files in current directory\""
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required for v1_refactor"
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