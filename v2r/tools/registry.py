#!/usr/bin/env python3
# tools/registry.py - Tool registration and management center
# V2 Refactor: V2 tools (6 total) in V3 architecture

from .base import registry, get_registry
from .file_tools import ReadFileTool, WriteFileTool, EditFileTool
from .search_tools import GlobTool, GrepTool
from .system_tools import RunBashTool


class ToolManager:
    """
    Tool Manager for V2 Refactor
    Manages the 6 tools from V2: read_file, write_file, edit_file, glob, grep, run_bash
    """

    def __init__(self):
        self._registry = get_registry()
        self._initialized = False

    def initialize(self):
        """Initialize and register all V2 tools"""
        if self._initialized:
            return

        print("🔧 Initializing V2 Refactor tool system...")

        # V2 tools (same 6 tools as original V2)
        tools_to_register = [
            ReadFileTool(),     # read_file
            WriteFileTool(),    # write_file
            EditFileTool(),     # edit_file
            GlobTool(),         # glob
            GrepTool(),         # grep
            RunBashTool()       # run_bash
        ]

        print("  📦 Registering V2 tools...")
        for tool in tools_to_register:
            self._registry.register(tool)

        self._initialized = True
        print(f"✅ V2 Refactor tool system initialization complete, registered {len(self._registry)} tools total")

        # Show registered tools
        print("🛠️  Available V2 tools:")
        for tool_info in self.get_tools_info():
            print(f"   • {tool_info['name']}: {tool_info['description']}")

    def get_tools_definitions(self):
        """Get API definitions for all tools"""
        self.initialize()
        return self._registry.get_definitions()

    def execute_tool(self, name, input_data):
        """Execute specified tool"""
        self.initialize()
        return self._registry.execute_tool(name, input_data)

    def get_tools_info(self):
        """Get information summary for all tools"""
        self.initialize()
        return self._registry.get_all_tools_info()

    def get_statistics(self):
        """Get tool usage statistics"""
        return self._registry.get_statistics()

    def get_tool_help(self, tool_name):
        """Get help information for specific tool"""
        self.initialize()
        info = self._registry.get_tool_info(tool_name)
        if info:
            return f"🛠️  Tool: {info['name']}\n" \
                   f"📝 Description: {info['description']}\n" \
                   f"📋 Parameters: {', '.join(info['parameters']) if info['parameters'] else 'None'}"
        else:
            available = ", ".join(self._registry.list_tools())
            return f"❌ Tool does not exist: {tool_name}\nAvailable tools: {available}"

    def validate_system(self):
        """Validate tool system integrity"""
        self.initialize()

        expected_tools = ["read_file", "write_file", "edit_file", "glob", "grep", "run_bash"]
        issues = []
        tools_info = self.get_tools_info()
        actual_tools = [tool["name"] for tool in tools_info]

        # Check if we have exactly the 6 V2 tools
        if len(actual_tools) != 6:
            issues.append(f"Expected 6 tools, found {len(actual_tools)}")

        # Check each expected tool exists
        for expected_tool in expected_tools:
            if expected_tool not in actual_tools:
                issues.append(f"Missing V2 tool: {expected_tool}")

        # Check for unexpected tools
        for actual_tool in actual_tools:
            if actual_tool not in expected_tools:
                issues.append(f"Unexpected tool found: {actual_tool}")

        if issues:
            return f"❌ Found {len(issues)} issues:\n" + "\n".join(f"  • {issue}" for issue in issues)
        else:
            return f"✅ V2 Refactor tool system validation passed, {len(tools_info)} tools normal"


# Global tool manager instance
_tool_manager = ToolManager()


def get_tools():
    """Get all tool definitions - main API function"""
    return _tool_manager.get_tools_definitions()


def execute_tool(name, input_data):
    """Execute tool - main API function"""
    return _tool_manager.execute_tool(name, input_data)


def get_tools_info():
    """Get tool information - main API function"""
    return _tool_manager.get_tools_info()


def get_tool_statistics():
    """Get tool usage statistics"""
    return _tool_manager.get_statistics()


def get_tool_help(tool_name):
    """Get tool help"""
    return _tool_manager.get_tool_help(tool_name)


def validate_tool_system():
    """Validate tool system"""
    return _tool_manager.validate_system()


# Convenience functions for backward compatibility
def register_all_tools():
    """Register all tools - backward compatibility function"""
    _tool_manager.initialize()


# For backward compatibility
TOOLS = None


def get_tools_lazy():
    """Lazy load tool definitions - backward compatibility function"""
    global TOOLS
    if TOOLS is None:
        TOOLS = get_tools()
    return TOOLS


if __name__ == "__main__":
    # Test V2 Refactor tool system
    print("🧪 Testing V2 Refactor tool system...")

    # Initialize
    manager = ToolManager()
    print(f"\n{validate_tool_system()}")

    # Show tool information
    print(f"\n📊 V2 Refactor Tools:")
    for info in get_tools_info():
        print(f"  • {info['name']}: {info['description']}")

    print(f"\n✅ Testing complete")