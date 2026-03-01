#!/usr/bin/env python3
# execution/tool_executor.py - Tool execution handler
# V4 version: Extracted tool execution functionality

import json
from tools.registry import execute_tool


class ToolExecutor:
    """
    Tool Executor
    Responsible for executing tool calls, handling results, and tracking statistics
    """

    def __init__(self,
                 show_tool_calls=True,
                 show_results=True,
                 result_preview_length=300,
                 param_preview_length=50):
        """
        Initialize tool executor

        Args:
            show_tool_calls: Whether to display tool call information
            show_results: Whether to display tool execution results
            result_preview_length: Maximum length for result preview
            param_preview_length: Maximum length for parameter preview
        """
        self.show_tool_calls = show_tool_calls
        self.show_results = show_results
        self.result_preview_length = result_preview_length
        self.param_preview_length = param_preview_length

        # Execution statistics
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'tool_usage': {},
            'execution_times': []
        }

    def execute_tool_call(self, tool_call):
        """
        Execute single tool call

        Args:
            tool_call: Tool call object from LLM response

        Returns:
            Tool result message object
        """
        tool_name, tool_input, tool_id = self._parse_tool_call(tool_call)

        if self.show_tool_calls:
            self._show_tool_info(tool_name, tool_input)

        result = self._execute_single_tool(tool_name, tool_input)

        if self.show_results:
            self._show_result_preview(result)

        return self._build_tool_result(tool_id, tool_name, result)

    def execute_multiple_tools(self, tool_calls):
        """
        Execute multiple tool calls sequentially

        Args:
            tool_calls: List of tool call objects

        Returns:
            List of tool result message objects
        """
        tool_results = []

        for i, tool_call in enumerate(tool_calls, 1):
            print(f"   [{i}/{len(tool_calls)}]", end=" ")
            result = self.execute_tool_call(tool_call)
            tool_results.append(result)

        return tool_results

    def _parse_tool_call(self, tool_call):
        """
        Parse tool call object to extract name, input, and ID

        Args:
            tool_call: Tool call object from LLM response

        Returns:
            Tuple of (tool_name, tool_input, tool_id)
        """
        tool_name = tool_call["function"]["name"]
        tool_input = json.loads(tool_call["function"]["arguments"])
        tool_id = tool_call["id"]
        return tool_name, tool_input, tool_id

    def _show_tool_info(self, tool_name, tool_input):
        """
        Display tool call information

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
        """
        print(f"🔧 Calling tool '{tool_name}'")
        for key, value in tool_input.items():
            value_str = str(value)
            if len(value_str) > self.param_preview_length:
                preview = value_str[:self.param_preview_length] + "..."
            else:
                preview = value_str
            print(f"   📝 {key}: {preview}")

    def _execute_single_tool(self, tool_name, tool_input):
        """
        Execute a single tool and handle errors

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result (string)
        """
        import time
        start_time = time.time()

        try:
            result = execute_tool(tool_name, tool_input)

            # Update statistics
            self.execution_stats['total_executions'] += 1
            self.execution_stats['successful_executions'] += 1
            self.execution_stats['tool_usage'][tool_name] = \
                self.execution_stats['tool_usage'].get(tool_name, 0) + 1

            execution_time = time.time() - start_time
            self.execution_stats['execution_times'].append(execution_time)

            return result

        except Exception as e:
            # Update statistics
            self.execution_stats['total_executions'] += 1
            self.execution_stats['failed_executions'] += 1

            error_msg = f"Tool execution error: {e}"
            print(f"   ❌ {error_msg}")
            return error_msg

    def _show_result_preview(self, result):
        """
        Display tool execution result preview

        Args:
            result: Tool execution result string
        """
        if len(result) > self.result_preview_length:
            preview = result[:self.result_preview_length] + \
                     f"... (total {len(result)} characters)"
        else:
            preview = result
        print(f"   📤 Result: {preview}")

    def _build_tool_result(self, tool_id, tool_name, result):
        """
        Build tool result message object

        Args:
            tool_id: Tool call ID from original request
            tool_name: Name of the executed tool
            result: Tool execution result string

        Returns:
            Tool result message object
        """
        return {
            "tool_call_id": tool_id,
            "role": "tool",
            "name": tool_name,
            "content": result
        }

    def get_execution_statistics(self):
        """
        Get tool execution statistics

        Returns:
            Dictionary containing execution statistics
        """
        stats = self.execution_stats.copy()

        # Calculate average execution time
        if stats['execution_times']:
            stats['avg_execution_time'] = sum(stats['execution_times']) / len(stats['execution_times'])
            stats['max_execution_time'] = max(stats['execution_times'])
            stats['min_execution_time'] = min(stats['execution_times'])
        else:
            stats['avg_execution_time'] = 0
            stats['max_execution_time'] = 0
            stats['min_execution_time'] = 0

        # Remove detailed execution times list (keep only summary)
        stats.pop('execution_times', None)

        return stats

    def reset_statistics(self):
        """Reset execution statistics"""
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'tool_usage': {},
            'execution_times': []
        }
