#!/bin/bash
# V3 - Complete OOP Architecture with Bash Entry Point
# 保持一致的用户接口，内部使用完整面向对象架构

# Check if we have any arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 \"task description\""
    echo ""
    echo "V3 - AI Assistant with Complete OOP Architecture"
    echo ""
    echo "Examples:"
    echo "  $0 \"create a hello.py file and run it\""
    echo "  $0 \"analyze this codebase and generate a project report\""
    echo "  $0 \"set up a new Python package with tests and documentation\""
    echo "  $0 \"find all function definitions in Python files\""
    echo ""
    echo "V3 Features:"
    echo "  • 11 comprehensive tools across 4 categories"
    echo "  • Object-oriented tool system with extensible registry"
    echo "  • Complete error handling and timeout control"
    echo "  • Comprehensive safety features"
    echo "  • Maintainable software architecture design"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required for V3"
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