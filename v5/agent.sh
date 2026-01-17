#!/bin/bash
# V4 - Advanced Conversation Management with Bash Entry Point
# 保持一致的用户接口，内部使用高级分层架构和对话压缩

# Check if we have any arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 \"task description\""
    echo ""
    echo "V4 - AI Assistant with Advanced Conversation Management"
    echo ""
    echo "Examples:"
    echo "  $0 \"create a complex multi-file project\""
    echo "  $0 \"analyze the entire codebase structure\""
    echo "  $0 \"implement a Flask web application with database\""
    echo "  $0 \"refactor this code and add comprehensive tests\""
    echo ""
    echo "V4 Features:"
    echo "  • 13 tools including conversation management (2 new tools)"
    echo "  • Layered architecture with 7 core modules"
    echo "  • Event-driven architecture with UI/business logic separation"
    echo "  • Intelligent conversation compression (auto at 25 messages)"
    echo "  • Advanced statistics and monitoring system"
    echo "  • Production-ready architecture and token optimization"
    echo ""
    echo "Advanced Features:"
    echo "  • Automatic compression preserving 15 recent messages"
    echo "  • 40-60% token reduction in long conversations"
    echo "  • Manual compression tools available"
    echo "  • Comprehensive session analytics"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required for V4"
    echo "Please install Python 3 to use this version"
    exit 1
fi

# 检查API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ Error: OPENROUTER_API_KEY environment variable not set"
    echo "Please run: export OPENROUTER_API_KEY=\"your-key-here\""
    exit 1
fi

# 调用Python核心逻辑 (V4 使用 agent.py 作为兼容入口点)
exec python3 "$(dirname "$0")/agent.py" "$@"