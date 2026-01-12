"""Pure business logic controller - 纯业务逻辑控制器"""

from tools.registry import get_tools, get_tools_info, get_tool_instance
from conversation.compressor import ConversationCompressor
from llm.client import LLMClient
from execution.tool_executor import ToolExecutor
from monitoring.statistics import StatisticsCollector


class AgentCore:
    """Pure business logic controller - 纯业务逻辑控制器"""

    def __init__(self):
        # 核心状态
        self.messages = []
        self.tools = []
        self.max_steps = 50

        # 功能模块
        self.compressor = ConversationCompressor()
        self.llm = LLMClient()
        self.tool_executor = ToolExecutor()
        self.statistics = StatisticsCollector()

        # 事件处理器（用于UI通信）
        self.event_handler = None

    def set_event_handler(self, handler):
        """设置事件处理器，用于与UI通信"""
        self.event_handler = handler

    def initialize_tools(self):
        """初始化工具系统"""
        self.tools = get_tools()
        # 设置工具实例
        compact_tool = get_tool_instance("compact_conversation")
        stats_tool = get_tool_instance("conversation_stats")
        if compact_tool:
            compact_tool.agent_instance = self
        if stats_tool:
            stats_tool.agent_instance = self

        self.statistics.start_session()
        return get_tools_info()

    def execute_task(self, task):
        """执行任务的核心业务逻辑"""
        self.messages = [{"role": "user", "content": task}]
        return self._run_conversation_loop()

    def _run_conversation_loop(self):
        """纯粹的对话循环逻辑，无UI依赖"""
        while self.statistics.step_count < self.max_steps:
            self.statistics.record_step()

            # 触发步骤开始事件
            self._emit_event('step_started', self.statistics.step_count)

            try:
                # 压缩检查
                if self.compressor.should_compact(self.messages):
                    old_count = len(self.messages)
                    compacted, compressed = self.compressor.auto_compact(self.messages)
                    if compressed:
                        self.messages = compacted
                        self.statistics.record_compression(old_count, len(self.messages))
                        self._emit_event('conversation_compressed', {
                            'old_count': old_count,
                            'new_count': len(self.messages)
                        })

                # LLM生成
                self.statistics.record_api_call()
                response = self.llm.generate(self.messages, self.tools)

                # 解析响应
                message = response["choices"][0]["message"]
                finish_reason = response["choices"][0]["finish_reason"]
                self.messages.append(message)

                # 处理完成情况
                if finish_reason == "stop":
                    self._emit_event('task_completed', {
                        'message': message.get("content"),
                        'total_steps': self.statistics.step_count
                    })
                    return True

                elif finish_reason == "tool_calls" or message.get("tool_calls"):
                    tool_calls = message.get("tool_calls", [])
                    if not tool_calls:
                        self._emit_event('error', 'No tool calls found')
                        return False

                    # 记录工具使用并执行
                    for tool_call in tool_calls:
                        tool_name = tool_call["function"]["name"]
                        self.statistics.record_tool_usage(tool_name)

                    self._emit_event('tools_executing', {
                        'count': len(tool_calls),
                        'tools': [tc["function"]["name"] for tc in tool_calls]
                    })

                    tool_results = self.tool_executor.execute_multiple_tools(tool_calls)
                    self.messages.extend(tool_results)

                elif finish_reason == "length":
                    self._emit_event('response_length_exceeded', None)

                else:
                    self._emit_event('unknown_finish_reason', {
                        'reason': finish_reason,
                        'message': message
                    })
                    return False

            except Exception as e:
                self._emit_event('step_failed', str(e))
                return False

        # 达到最大步骤数
        self._emit_event('max_steps_reached', self.max_steps)
        return False

    def _emit_event(self, event_type, data):
        """发出事件，供UI层处理"""
        if self.event_handler:
            self.event_handler.handle_event(event_type, data)

    def get_statistics_data(self):
        """获取统计数据"""
        self.statistics.end_session()
        return self.statistics.get_statistics_dict(
            self.messages,
            compressor=self.compressor,
            tool_executor=self.tool_executor
        )
