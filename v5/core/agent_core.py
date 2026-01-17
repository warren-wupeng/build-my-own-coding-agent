"""Pure business logic controller - 纯业务逻辑控制器"""

import logging

from tools.registry import get_tools, get_tools_info, get_tool_instance
from conversation.compressor import ConversationCompressor
from llm.client import LLMClient
from execution.tool_executor import ToolExecutor
from monitoring.statistics import StatisticsCollector

logger = logging.getLogger(__name__)


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
        delegate_tool = get_tool_instance("delegate_task")
        delegation_info_tool = get_tool_instance("get_delegation_info")

        # Set agent instance for conversation management tools
        if compact_tool:
            compact_tool.agent_instance = self
        if stats_tool:
            stats_tool.agent_instance = self

        # Set agent instance for delegation tools
        if delegate_tool:
            delegate_tool.agent_instance = self
        if delegation_info_tool:
            delegation_info_tool.agent_instance = self

        self.statistics.start_session()
        return get_tools_info()

    def execute_task(self, task):
        """执行任务的核心业务逻辑"""
        logger.info(f"Starting task execution. Max steps: {self.max_steps}")
        logger.debug(f"Task content (first 300 chars): {task[:300]}...")
        self.messages = [{"role": "user", "content": task}]
        result = self._run_conversation_loop()
        logger.info(f"Task execution completed. Result: {result}, Total steps: {self.statistics.step_count}")
        return result

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

                # 记录详细的 LLM 响应信息
                message_content = message.get("content", "")
                message_preview = message_content[:200] if message_content else "(empty)"
                tool_calls = message.get("tool_calls", [])
                
                logger.info(
                    f"Step {self.statistics.step_count}: LLM Response - "
                    f"finish_reason={finish_reason}, "
                    f"has_content={bool(message_content)}, "
                    f"content_preview='{message_preview}...', "
                    f"tool_calls_count={len(tool_calls)}"
                )

                # 处理完成情况
                if finish_reason == "stop":
                    logger.info(
                        f"Task completed: LLM returned finish_reason='stop' at step {self.statistics.step_count}. "
                        f"Final message: '{message_preview}...'"
                    )
                    self._emit_event('task_completed', {
                        'message': message.get("content"),
                        'total_steps': self.statistics.step_count
                    })
                    return True

                elif finish_reason == "tool_calls" or message.get("tool_calls"):
                    tool_calls = message.get("tool_calls", [])
                    if not tool_calls:
                        logger.warning(f"Step {self.statistics.step_count}: finish_reason='tool_calls' but no tool_calls found in message")
                        self._emit_event('error', 'No tool calls found')
                        return False

                    # 记录工具使用并执行
                    tool_names = []
                    for tool_call in tool_calls:
                        tool_name = tool_call["function"]["name"]
                        tool_names.append(tool_name)
                        self.statistics.record_tool_usage(tool_name)
                    
                    logger.info(
                        f"Step {self.statistics.step_count}: Executing {len(tool_calls)} tool(s): {', '.join(tool_names)}"
                    )

                    self._emit_event('tools_executing', {
                        'count': len(tool_calls),
                        'tools': tool_names
                    })

                    tool_results = self.tool_executor.execute_multiple_tools(tool_calls)
                    self.messages.extend(tool_results)

                elif finish_reason == "length":
                    logger.warning(
                        f"Step {self.statistics.step_count}: Response length exceeded (finish_reason='length')"
                    )
                    self._emit_event('response_length_exceeded', None)

                else:
                    logger.warning(
                        f"Step {self.statistics.step_count}: Unknown finish_reason='{finish_reason}'. "
                        f"Message: {message}"
                    )
                    self._emit_event('unknown_finish_reason', {
                        'reason': finish_reason,
                        'message': message
                    })
                    return False

            except Exception as e:
                logger.error(f"Step {self.statistics.step_count}: Exception occurred: {e}", exc_info=True)
                self._emit_event('step_failed', str(e))
                return False

        # 达到最大步骤数
        logger.warning(
            f"Task stopped: Reached max_steps={self.max_steps} at step {self.statistics.step_count}"
        )
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
