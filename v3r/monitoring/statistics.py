"""Statistics collection and reporting for AgentV4"""

import time
import json


class StatisticsCollector:
    """
    Statistics Collector
    Responsible for collecting and displaying execution statistics
    """

    def __init__(self,
                 level='basic',
                 track_performance=True,
                 export_enabled=False):
        """
        Initialize statistics collector

        Args:
            level: Statistics level ('basic' or 'detailed')
            track_performance: Whether to track performance metrics
            export_enabled: Whether to enable statistics export
        """
        self.level = level
        self.track_performance = track_performance
        self.export_enabled = export_enabled

        # Basic statistics
        self.step_count = 0
        self.api_calls = 0
        self.tool_usage = {}

        # Session timing
        self.start_time = None
        self.end_time = None

        # Compression tracking
        self.compression_events = []

    def start_session(self):
        """Start session timing"""
        self.start_time = time.time()

    def end_session(self):
        """End session timing"""
        self.end_time = time.time()

    def get_session_duration(self):
        """Get session duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return None

    def record_step(self):
        """Record execution step"""
        self.step_count += 1

    def record_api_call(self):
        """Record API call"""
        self.api_calls += 1

    def record_tool_usage(self, tool_name):
        """Record tool usage"""
        self.tool_usage[tool_name] = self.tool_usage.get(tool_name, 0) + 1

    def record_compression(self, old_count, new_count):
        """Record compression event"""
        self.compression_events.append({
            'timestamp': time.time(),
            'old_count': old_count,
            'new_count': new_count
        })

    def _show_basic_stats(self, messages):
        """Show basic execution statistics"""
        print(f"   • Total steps: {self.step_count}")
        print(f"   • Message count: {len(messages)}")

    def _show_compression_stats(self, compressor, messages=None):
        """Show compression statistics"""
        if compressor:
            print(f"   • Conversation compactions: {compressor.compressed_count}")

            # Enhanced statistics
            if messages:
                total_chars = sum(len(str(msg)) for msg in messages)
                estimated_tokens = total_chars // 4
                print(f"   • Estimated tokens: ~{estimated_tokens}")
            print(f"   • Compression threshold: {compressor.auto_compact_threshold} messages")
            print(f"   • Keep recent messages: {compressor.keep_recent_messages}")

    def _show_tool_stats(self, tool_executor):
        """Show tool execution statistics"""
        if tool_executor:
            tool_stats = tool_executor.get_execution_statistics()
            if tool_stats['total_executions'] > 0:
                print(f"   • Tool executions: {tool_stats['total_executions']} "
                      f"(✓ {tool_stats['successful_executions']}, "
                      f"✗ {tool_stats['failed_executions']})")
                if tool_stats.get('avg_execution_time', 0) > 0:
                    print(f"   • Avg execution time: {tool_stats['avg_execution_time']:.3f}s")
                if tool_stats['tool_usage']:
                    print("   • Tool usage:")
                    for tool_name, count in sorted(tool_stats['tool_usage'].items()):
                        print(f"     - {tool_name}: {count} times")

    def _show_performance_stats(self):
        """Show performance statistics"""
        duration = self.get_session_duration()
        if duration:
            print(f"   • Session duration: {duration:.2f}s")
            if self.step_count > 0:
                print(f"   • Steps per second: {self.step_count / duration:.3f}")
            if self.api_calls > 0:
                print(f"   • API calls: {self.api_calls}")
                print(f"   • API calls per minute: {(self.api_calls * 60) / duration:.2f}")

    def show_statistics(self, messages, compressor=None, tool_executor=None):
        """
        Show complete statistics information

        Args:
            messages: List of conversation messages
            compressor: ConversationCompressor instance (optional)
            tool_executor: ToolExecutor instance (optional)
        """
        print("")
        print("📊 Execution Statistics:")
        self._show_basic_stats(messages)
        self._show_compression_stats(compressor, messages)
        self._show_tool_stats(tool_executor)
        if self.track_performance:
            self._show_performance_stats()

    def get_performance_metrics(self):
        """Get performance metrics dictionary"""
        duration = self.get_session_duration()
        return {
            'session_duration': duration,
            'steps_per_second': self.step_count / duration if duration and duration > 0 else 0,
            'api_calls_per_minute': (self.api_calls * 60) / duration if duration and duration > 0 else 0,
            'average_tools_per_step': sum(self.tool_usage.values()) / self.step_count if self.step_count > 0 else 0
        }

    def get_statistics_dict(self, messages=None, compressor=None, tool_executor=None):
        """
        Get statistics as dictionary

        Args:
            messages: List of conversation messages (optional)
            compressor: ConversationCompressor instance (optional)
            tool_executor: ToolExecutor instance (optional)

        Returns:
            Dictionary containing all statistics
        """
        stats_data = {
            'session_info': {
                'start_time': self.start_time,
                'end_time': self.end_time,
                'duration': self.get_session_duration()
            },
            'execution_stats': {
                'total_steps': self.step_count,
                'api_calls': self.api_calls,
                'message_count': len(messages) if messages else 0,
                'tool_usage': self.tool_usage.copy()
            },
            'compression_stats': {
                'compression_count': len(self.compression_events),
                'compression_events': self.compression_events.copy()
            }
        }

        if compressor:
            stats_data['compression_stats']['compressed_count'] = compressor.compressed_count
            stats_data['compression_stats']['threshold'] = compressor.auto_compact_threshold
            stats_data['compression_stats']['keep_recent'] = compressor.keep_recent_messages

        if tool_executor:
            tool_stats = tool_executor.get_execution_statistics()
            stats_data['tool_execution_stats'] = tool_stats

        if self.track_performance:
            stats_data['performance_metrics'] = self.get_performance_metrics()

        return stats_data

    def export_statistics(self, filepath, messages=None, compressor=None, tool_executor=None, format='json'):
        """
        Export statistics to file

        Args:
            filepath: Path to export file
            messages: List of conversation messages (optional)
            compressor: ConversationCompressor instance (optional)
            tool_executor: ToolExecutor instance (optional)
            format: Export format ('json' or 'csv')
        """
        stats_data = self.get_statistics_dict(messages, compressor, tool_executor)

        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(stats_data, f, indent=2)
        elif format == 'csv':
            # CSV export could be implemented here
            raise NotImplementedError("CSV export not yet implemented")
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def reset(self):
        """Reset all statistics"""
        self.step_count = 0
        self.api_calls = 0
        self.tool_usage = {}
        self.start_time = None
        self.end_time = None
        self.compression_events = []
