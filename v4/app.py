"""Application entry point - 应用程序入口"""

import sys
from core.agent_core import AgentCore
from interface.display import DisplayManager, EventHandler
from interface.cli import CommandLineInterface


class AgentApplication:
    """应用程序主类，管理完整的应用生命周期"""

    def __init__(self):
        self.core = AgentCore()
        self.display = DisplayManager()
        self.cli = CommandLineInterface()

        # 设置事件处理
        event_handler = EventHandler(self.display)
        self.core.set_event_handler(event_handler)

    def run(self):
        """运行应用程序"""
        try:
            # 解析命令行参数
            action, data = self.cli.parse_arguments()

            if action == "help":
                self.cli.show_help()
                return

            if action == "error":
                print(f"❌ Error: {data}")
                print("Usage: python agent.py \"your task\"")
                print("Help: python agent.py --help")
                sys.exit(1)

            # 初始化和执行任务
            self._execute_task(data)

        except KeyboardInterrupt:
            print("\n⏹️  User interrupted execution")
            self._show_final_statistics()

        except Exception as e:
            print(f"\n💥 Program exception: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _execute_task(self, task):
        """执行任务的完整流程"""
        # 初始化
        tools_info = self.core.initialize_tools()
        self.display.show_initialization(tools_info)

        # 显示任务开始
        self.display.show_task_start(task)

        # 执行任务
        success = self.core.execute_task(task)

        # 显示最终统计
        self._show_final_statistics()

        return success

    def _show_final_statistics(self):
        """显示最终统计信息"""
        stats_data = self.core.get_statistics_data()
        self.display.show_statistics(stats_data)


def main():
    """主入口函数"""
    app = AgentApplication()
    app.run()


if __name__ == "__main__":
    main()
