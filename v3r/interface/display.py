"""Display management - 输出显示管理"""


class DisplayManager:
    """管理所有输出显示逻辑"""

    def __init__(self, verbose=True):
        self.verbose = verbose

    def show_initialization(self, tools_info):
        """显示初始化信息"""
        print("🚀 AI Assistant V4 - Advanced Conversation Management")
        print("🏗️  Object-oriented Tool System | Intelligent Compression")
        print("")
        print(f"🛠️  Loaded tools: {len(tools_info)}")
        for tool_info in tools_info:
            print(f"   • {tool_info['name']}: {tool_info['description']}")
        print("")

    def show_task_start(self, task):
        """显示任务开始"""
        print(f"📝 Task: {task}")
        print("")

    def show_step_start(self, step_number):
        """显示步骤开始"""
        print(f"🔄 Execution Step {step_number}")

    def show_compression(self, old_count, new_count):
        """显示压缩信息"""
        print(f"📦 Auto-compacting: {old_count} → {new_count} messages")

    def show_task_completed(self, message, total_steps):
        """显示任务完成"""
        if message:
            print(f"✅ {message}")
        print("")
        print(f"🎉 Task completed successfully! Total steps executed: {total_steps}.")

    def show_tools_executing(self, count, tools):
        """显示工具执行信息"""
        print(f"   🔗 Need to execute {count} tools")
        if self.verbose:
            print(f"   Tools: {', '.join(tools)}")
        print("")

    def show_error(self, error_message):
        """显示错误信息"""
        print(f"❌ Error: {error_message}")

    def show_warning(self, warning_message):
        """显示警告信息"""
        print(f"⚠️  {warning_message}")

    def show_statistics(self, stats_data):
        """显示统计信息"""
        print("")
        print("📊 Execution Statistics:")
        
        # 从嵌套结构中提取数据
        execution_stats = stats_data.get('execution_stats', {})
        compression_stats = stats_data.get('compression_stats', {})
        
        print(f"   • Total steps: {execution_stats.get('total_steps', 0)}")
        print(f"   • Message count: {execution_stats.get('message_count', 0)}")
        print(f"   • Conversation compactions: {compression_stats.get('compression_count', 0)}")

        if 'estimated_tokens' in stats_data:
            print(f"   • Estimated tokens: ~{stats_data['estimated_tokens']}")

        tool_usage = execution_stats.get('tool_usage', {})
        if tool_usage:
            print("   • Tool usage:")
            for tool_name, count in sorted(tool_usage.items()):
                print(f"     - {tool_name}: {count} times")


class EventHandler:
    """处理AgentCore发出的事件"""

    def __init__(self, display_manager):
        self.display = display_manager

    def handle_event(self, event_type, data):
        """处理各种事件"""
        if event_type == 'step_started':
            self.display.show_step_start(data)

        elif event_type == 'conversation_compressed':
            self.display.show_compression(data['old_count'], data['new_count'])

        elif event_type == 'task_completed':
            self.display.show_task_completed(data['message'], data['total_steps'])

        elif event_type == 'tools_executing':
            self.display.show_tools_executing(data['count'], data['tools'])

        elif event_type == 'response_length_exceeded':
            self.display.show_warning("Response length exceeded, continuing...")

        elif event_type == 'max_steps_reached':
            self.display.show_warning(f"Reached maximum step limit ({data}), stopping execution")
            self.display.show_warning("This usually means the task is too complex or there's a loop")

        elif event_type == 'error':
            self.display.show_error(data)

        elif event_type == 'step_failed':
            self.display.show_error(f"Step execution failed: {data}")

        elif event_type == 'unknown_finish_reason':
            self.display.show_error(f"Unknown finish reason: {data['reason']}")
            self.display.show_error(f"Response content: {data['message']}")
