#!/usr/bin/env python3
# tools/registry.py - Tool registration and management center
# V3 version: Complete tool lifecycle management

from .base import registry, get_registry
from .file_tools import ReadFileTool, WriteFileTool, EditFileTool, ListFilesTool
from .file_search_tools import GlobTool, FindTool
from .text_search_tools import GrepTool
from .system_tools import RunBashTool, WhichTool, EnvTool, PwdTool


class ToolManager:
    """
    Tool Manager
    Responsible for tool registration, discovery, statistics and other advanced features
    """

    def __init__(self):
        self._registry = get_registry()
        self._initialized = False

    def initialize(self):
        """Initialize and register all tools"""
        if self._initialized:
            return

        print("🔧 Initializing tool system...")

        # File operation tools
        self._register_category("File Operations", [
            ReadFileTool(),
            WriteFileTool(),
            EditFileTool(),
            ListFilesTool()
        ])

        # Search and find tools
        self._register_category("Search and Find", [
            GlobTool(),
            GrepTool(),
            FindTool()
        ])

        # System tools
        self._register_category("System Operations", [
            RunBashTool(),
            WhichTool(),
            EnvTool(),
            PwdTool()
        ])

        self._initialized = True
        print(f"✅ Tool system initialization complete, registered {len(self._registry)} tools total")

    def _register_category(self, category_name, tools):
        """Register a category of tools"""
        print(f"  📦 Registering {category_name} tools...")
        for tool in tools:
            self._registry.register(tool)

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

    def list_tools_by_category(self):
        """List tools by category"""
        self.initialize()

        categories = {
            "File Operations": ["read_file", "write_file", "edit_file", "list_files"],
            "Search and Find": ["glob", "grep", "find"],
            "System Operations": ["run_bash", "which", "env", "pwd"]
        }

        result = {}
        all_tools_info = {tool["name"]: tool for tool in self.get_tools_info()}

        for category, tool_names in categories.items():
            category_tools = []
            for name in tool_names:
                if name in all_tools_info:
                    category_tools.append(all_tools_info[name])
            result[category] = category_tools

        return result

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

        issues = []
        tools_info = self.get_tools_info()

        # Check tool definitions
        for tool_info in tools_info:
            name = tool_info['name']
            try:
                # Try to get tool definition
                definitions = self.get_tools_definitions()
                tool_found = any(d['function']['name'] == name for d in definitions)
                if not tool_found:
                    issues.append(f"Tool {name} missing definition")

            except Exception as e:
                issues.append(f"Tool {name} definition error: {e}")

        if issues:
            return f"❌ Found {len(issues)} issues:\n" + "\n".join(f"  • {issue}" for issue in issues)
        else:
            return f"✅ Tool system validation passed, {len(tools_info)} tools normal"


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


def list_tools_by_category():
    """List tools by category"""
    return _tool_manager.list_tools_by_category()


def get_tool_help(tool_name):
    """Get tool help"""
    return _tool_manager.get_tool_help(tool_name)


def validate_tool_system():
    """Validate tool system"""
    return _tool_manager.validate_system()


# Convenience functions and backward compatibility
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
    # Test tool system
    print("🧪 Testing tool system...")

    # Initialize
    manager = ToolManager()
    print(f"\n{validate_tool_system()}")

    # Show tool information
    print(f"\n📊 Tool Statistics:")
    categories = list_tools_by_category()
    for category, tools in categories.items():
        print(f"  {category}: {len(tools)} tools")

    # Show tool list
    print(f"\n🛠️  All Tools:")
    for info in get_tools_info():
        print(f"  • {info['name']}: {info['description']}")

    print(f"\n✅ Testing complete")