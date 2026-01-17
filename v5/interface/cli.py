"""Command line interface - 命令行界面管理"""

import sys
from tools.registry import get_tools_info
from llm.client import LLMClient


class CommandLineInterface:
    """命令行界面管理"""

    @staticmethod
    def show_help():
        """显示帮助信息"""
        print("🏗️  AI Assistant V4 - Advanced Conversation Management")
        print("")
        print("💡 Features:")
        print("   • Object-oriented tool system")
        print("   • Extensible tool registration mechanism")
        print("   • Complete error handling and timeout control")
        print("   • Detailed execution statistics and logging")
        print("")
        print("📖 Usage:")
        print("   python agent.py \"your task description\"")
        print("")
        print("🌟 Examples:")
        print("   python agent.py \"Create a Python file that calculates Fibonacci numbers and run it\"")
        print("   python agent.py \"Analyze function definitions in all Python files in the current directory\"")
        print("   python agent.py \"Search for all files containing 'TODO' in the project\"")
        print("")

        # Get configuration help from LLM client
        for line in LLMClient.get_configuration_help():
            print(line)

        # Show available tools
        CommandLineInterface._show_available_tools()

    @staticmethod
    def _show_available_tools():
        """显示可用工具"""
        try:
            tools_info = get_tools_info()
            print("🛠️  Available Tools:")
            for i, tool_info in enumerate(tools_info, 1):
                print(f"   {i}. {tool_info['name']}: {tool_info['description']}")
                if tool_info.get('parameters'):
                    print(f"      Parameters: {', '.join(tool_info['parameters'])}")
        except:
            print("🛠️  (Tool information loading failed)")

    @staticmethod
    def parse_arguments():
        """解析命令行参数"""
        if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help", "help"]):
            return "help", None

        if len(sys.argv) != 2:
            return "error", "Please provide task description"

        return "task", sys.argv[1]
