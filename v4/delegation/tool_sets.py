"""
Tool set management for sub-agent delegation

This module defines tool sets that can be assigned to specialized sub-agents,
allowing precise control over which tools each type of sub-agent can access.
"""

from typing import List, Dict, Set, Optional


class ToolSet:
    """
    Represents a collection of tools that can be assigned to a sub-agent.

    Each ToolSet defines:
    - A name and description for the tool set
    - A list of allowed tool names
    - Methods to filter tools based on the allowed set
    """

    def __init__(self, name: str, allowed_tools: List[str], description: str):
        """
        Initialize a ToolSet.

        Args:
            name: Unique identifier for this tool set
            allowed_tools: List of tool names that are allowed in this set
            description: Human-readable description of the tool set's purpose
        """
        self.name = name
        self.allowed_tools = set(allowed_tools)  # Use set for O(1) lookups
        self.description = description

    def filter_tools(self, all_tools: List[Dict]) -> List[Dict]:
        """
        Filter a list of tool definitions to only include allowed tools.

        Args:
            all_tools: List of tool definitions (with 'function' -> 'name' structure)

        Returns:
            List of tool definitions that are allowed by this tool set
        """
        filtered_tools = []
        for tool in all_tools:
            tool_name = tool.get('function', {}).get('name')
            if tool_name in self.allowed_tools:
                filtered_tools.append(tool)
        return filtered_tools

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a specific tool is allowed in this tool set."""
        return tool_name in self.allowed_tools

    def get_allowed_tools(self) -> Set[str]:
        """Get the set of allowed tool names."""
        return self.allowed_tools.copy()

    def __str__(self) -> str:
        return f"ToolSet(name='{self.name}', tools={len(self.allowed_tools)}, description='{self.description}')"

    def __repr__(self) -> str:
        return self.__str__()


class ToolSetManager:
    """
    Manages all available tool sets for sub-agent delegation.

    Provides predefined tool sets for common sub-agent specializations
    and allows registration of custom tool sets.
    """

    def __init__(self):
        """Initialize with predefined tool sets for common specializations."""
        self.tool_sets: Dict[str, ToolSet] = {}
        self._initialize_default_tool_sets()

    def _initialize_default_tool_sets(self):
        """Set up the default tool sets for common sub-agent types."""

        # File Operations Agent - Can manipulate files but not execute system commands
        self.register_tool_set(ToolSet(
            name="file_operations",
            allowed_tools=[
                "read_file",
                "write_file",
                "edit_file",
                "list_files"
            ],
            description="File manipulation and management operations"
        ))

        # Search and Find Agent - Can search but not modify
        self.register_tool_set(ToolSet(
            name="search_and_find",
            allowed_tools=[
                "glob",
                "grep",
                "find"
            ],
            description="File and content search operations"
        ))

        # System Operations Agent - Can execute system commands but no file access
        self.register_tool_set(ToolSet(
            name="system_operations",
            allowed_tools=[
                "run_bash",
                "which",
                "env",
                "pwd"
            ],
            description="System command execution and environment queries"
        ))

        # Analysis Agent - Read-only operations for code analysis
        self.register_tool_set(ToolSet(
            name="analysis_only",
            allowed_tools=[
                "read_file",
                "list_files",
                "glob",
                "grep",
                "find"
            ],
            description="Read-only analysis and exploration operations"
        ))

        # Full Access Agent - All tools except conversation management
        # (Conversation tools should remain exclusive to the main agent)
        self.register_tool_set(ToolSet(
            name="full_access",
            allowed_tools=[
                "read_file",
                "write_file",
                "edit_file",
                "list_files",
                "glob",
                "grep",
                "find",
                "run_bash",
                "which",
                "env",
                "pwd"
            ],
            description="Full access to all tools except conversation management"
        ))

    def register_tool_set(self, tool_set: ToolSet):
        """
        Register a new tool set.

        Args:
            tool_set: ToolSet instance to register

        Raises:
            ValueError: If a tool set with the same name already exists
        """
        if tool_set.name in self.tool_sets:
            raise ValueError(f"ToolSet with name '{tool_set.name}' already exists")

        self.tool_sets[tool_set.name] = tool_set

    def get_tool_set(self, name: str) -> Optional[ToolSet]:
        """
        Get a tool set by name.

        Args:
            name: Name of the tool set to retrieve

        Returns:
            ToolSet instance if found, None otherwise
        """
        return self.tool_sets.get(name)

    def list_available_tool_sets(self) -> List[str]:
        """Get a list of all available tool set names."""
        return list(self.tool_sets.keys())

    def get_tool_set_info(self, name: str) -> Optional[Dict[str, any]]:
        """
        Get information about a tool set.

        Args:
            name: Name of the tool set

        Returns:
            Dictionary with tool set information, or None if not found
        """
        tool_set = self.get_tool_set(name)
        if not tool_set:
            return None

        return {
            'name': tool_set.name,
            'description': tool_set.description,
            'allowed_tools': list(tool_set.allowed_tools),
            'tool_count': len(tool_set.allowed_tools)
        }

    def validate_tool_set(self, name: str, available_tools: List[str]) -> Dict[str, any]:
        """
        Validate that a tool set's allowed tools are actually available.

        Args:
            name: Name of the tool set to validate
            available_tools: List of tool names that are actually available

        Returns:
            Dictionary with validation results
        """
        tool_set = self.get_tool_set(name)
        if not tool_set:
            return {
                'valid': False,
                'error': f"ToolSet '{name}' not found"
            }

        available_set = set(available_tools)
        missing_tools = tool_set.allowed_tools - available_set

        return {
            'valid': len(missing_tools) == 0,
            'missing_tools': list(missing_tools),
            'available_tools': list(tool_set.allowed_tools & available_set),
            'total_allowed': len(tool_set.allowed_tools),
            'total_available': len(tool_set.allowed_tools & available_set)
        }

    def get_all_tool_sets_info(self) -> Dict[str, Dict[str, any]]:
        """Get information about all registered tool sets."""
        return {
            name: self.get_tool_set_info(name)
            for name in self.tool_sets.keys()
        }

    def __str__(self) -> str:
        return f"ToolSetManager(tool_sets={len(self.tool_sets)})"

    def __repr__(self) -> str:
        return self.__str__()