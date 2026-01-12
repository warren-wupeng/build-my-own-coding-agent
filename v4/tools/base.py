#!/usr/bin/env python3
# tools/base.py - Tool base class and registration system
# V3 version: Complete object-oriented tool architecture

class BaseTool:
    """
    Tool base class, all tools should inherit from this class

    Design principles:
    1. Each tool is an independent class
    2. Tool definition and implementation are separated but in the same class
    3. Unified error handling and interface
    4. Support for tool metadata and documentation
    """

    @property
    def definition(self):
        """
        Return the OpenRouter API definition for the tool
        Must return a dictionary conforming to OpenAI tool calling format
        """
        raise NotImplementedError("Subclass must implement definition property")

    def execute(self, input_data):
        """
        Execute tool and return result

        Args:
            input_data (dict): Tool input parameters

        Returns:
            str: Tool execution result
        """
        raise NotImplementedError("Subclass must implement execute method")

    @property
    def name(self):
        """Return tool name, defaults to getting from definition"""
        return self.definition["function"]["name"]

    @property
    def description(self):
        """Return tool description, defaults to getting from definition"""
        return self.definition["function"]["description"]

    def validate_input(self, input_data):
        """
        Validate input parameters
        Subclasses can override this method to add custom validation
        """
        required = self.definition["function"]["parameters"].get("required", [])
        for param in required:
            if param not in input_data:
                raise ValueError(f"Missing required parameter: {param}")

    def safe_execute(self, input_data):
        """
        Safely execute tool with validation and error handling
        This is the recommended method for external calls
        """
        try:
            self.validate_input(input_data)
            return self.execute(input_data)
        except Exception as e:
            return f"❌ Tool '{self.name}' execution failed: {e}"

    def get_info(self):
        """Get tool information summary"""
        definition = self.definition["function"]
        parameters = list(definition.get("parameters", {}).get("properties", {}).keys())
        return {
            "name": definition["name"],
            "description": definition["description"],
            "parameters": parameters
        }


class ToolRegistry:
    """
    Tool registry that manages all tool instances

    Features:
    1. Dynamic tool registration
    2. Tool discovery and management
    3. Unified tool calling interface
    4. Tool information aggregation
    """

    def __init__(self):
        self._tools = {}
        self._stats = {
            "total_executions": 0,
            "tool_usage": {}
        }

    def register(self, tool_instance):
        """
        Register a tool instance

        Args:
            tool_instance: Subclass instance of BaseTool
        """
        if not isinstance(tool_instance, BaseTool):
            raise TypeError(f"Tool must inherit from BaseTool class, received: {type(tool_instance)}")

        name = tool_instance.name
        if name in self._tools:
            print(f"⚠️  Warning: Tool '{name}' already exists, will be overwritten")

        self._tools[name] = tool_instance
        print(f"✅ Registered tool: {name}")

    def get_definitions(self):
        """Get OpenRouter API definition list for all tools"""
        return [tool.definition for tool in self._tools.values()]

    def execute_tool(self, name, input_data):
        """
        Execute tool with specified name

        Args:
            name (str): Tool name
            input_data (dict): Tool input parameters

        Returns:
            str: Tool execution result
        """
        if name not in self._tools:
            available_tools = ", ".join(self._tools.keys())
            return f"❌ Error: Unknown tool '{name}'\nAvailable tools: {available_tools}"

        # Update statistics
        self._update_stats(name)

        # Execute tool
        return self._tools[name].safe_execute(input_data)

    def list_tools(self):
        """List all registered tool names"""
        return list(self._tools.keys())

    def get_tool_info(self, name):
        """Get detailed information for specified tool"""
        if name not in self._tools:
            return None
        return self._tools[name].get_info()

    def get_tool_instance(self, name):
        """Get tool instance by name"""
        return self._tools.get(name)

    def get_all_tools_info(self):
        """Get information for all tools"""
        return [tool.get_info() for tool in self._tools.values()]

    def get_statistics(self):
        """Get tool usage statistics"""
        return self._stats.copy()

    def _update_stats(self, tool_name):
        """Update tool usage statistics"""
        self._stats["total_executions"] += 1
        self._stats["tool_usage"][tool_name] = self._stats["tool_usage"].get(tool_name, 0) + 1

    def reset_statistics(self):
        """Reset statistics information"""
        self._stats = {
            "total_executions": 0,
            "tool_usage": {}
        }

    def __len__(self):
        """Return number of registered tools"""
        return len(self._tools)

    def __contains__(self, name):
        """Check if tool is registered"""
        return name in self._tools

    def __str__(self):
        """Return string representation of registry"""
        tool_list = ", ".join(self._tools.keys())
        return f"ToolRegistry({len(self._tools)} tools: {tool_list})"


# Global tool registry instance
registry = ToolRegistry()

# Convenience functions
def get_registry():
    """Get global tool registry instance"""
    return registry

def register_tool(tool_instance):
    """Convenience function for registering tools"""
    return registry.register(tool_instance)