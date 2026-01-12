#!/usr/bin/env python3
# V1_refactor - Core Agent Logic
# Migrated from bash to Python with inline implementation

import json
import sys
import urllib.request
import urllib.error
import os
import subprocess
import re

class AgentV1Refactor:
    """
    V1_refactor Agent - Python implementation with V1 functionality
    All logic is inlined for simplicity and better cohesion
    """

    def __init__(self):
        # V1兼容配置
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-v3.2"
        self.max_tokens = 1024
        self.max_steps = 20  # V1特性：20步限制
        self.timeout = 30

        # V1状态管理
        self.messages = []
        self.step_count = 1

        # V1提示模板 - 完全保持原有格式
        self.system_prompt = """You are a helpful assistant that can execute bash commands.

When a user gives you a task, reply with this JSON format:
{"action": "bash", "command": "your command"}

When the task is complete, reply:
{"action": "done", "message": "description of what was completed"}

Only reply with JSON, no other text."""

    def run(self, task):
        """主执行入口，保持V1的行为模式"""
        print("🚀 Starting AI assistant, beginning task processing...")
        print(f"📝 Task: {task}")
        print("")

        # 初始化消息历史
        self.messages = [{"role": "user", "content": task}]

        try:
            # V1的对话循环
            self._run_conversation_loop()
        except KeyboardInterrupt:
            print("\n⏹️  User interrupted execution")
        except Exception as e:
            print(f"\n💥 Execution failed: {e}")
            sys.exit(1)

    def _run_conversation_loop(self):
        """V1的对话循环逻辑，迁移到Python"""
        while self.step_count <= self.max_steps:
            print(f"🔄 Step {self.step_count}...")

            try:
                # API调用
                response = self._call_openrouter_api()
                ai_text = response["choices"][0]["message"]["content"]

                # 清理响应格式（V1特有的处理）
                ai_text = ai_text.replace('"(action)"', '"action"')

                # 添加AI响应到历史
                self.messages.append({"role": "assistant", "content": ai_text})

                # 解析JSON响应
                try:
                    ai_response = json.loads(ai_text)
                except json.JSONDecodeError:
                    print("❌ AI response is not valid JSON")
                    break

                action = ai_response.get("action")

                if action == "done":
                    # V1完成逻辑
                    message = ai_response.get("message", "Task completed")
                    print(f"✅ {message}")
                    print(f"🎉 Task successfully completed! Total steps executed: {self.step_count}.")
                    break

                elif action == "bash":
                    # V1的bash命令执行
                    command = ai_response.get("command")
                    if not command:
                        print("❌ Command is empty")
                        break

                    print(f"🔧 Preparing to execute: {command}")

                    # 直接执行bash命令
                    result = self._execute_bash_command(command)

                    # V1反馈格式
                    if result.startswith("Exit code: 0"):
                        print("📤 Output:")
                        output_part = result.split("Output: ", 1)[1] if "Output: " in result else ""
                        print(output_part)
                    else:
                        print(f"❌ Command execution failed")
                        print(result)

                    # 添加反馈到消息历史 - V1格式
                    feedback = f"Command '{command}' execution result:\n{result}"
                    self.messages.append({"role": "user", "content": feedback})

                    self.step_count += 1

                else:
                    print(f"❌ Unknown action: {action}")
                    break

            except Exception as e:
                print(f"❌ Step execution error: {e}")
                break

        if self.step_count > self.max_steps:
            print(f"⚠️  Executed {self.max_steps} steps, stopping to prevent infinite loops")

    def _call_openrouter_api(self):
        """API调用，迁移自V1逻辑"""
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "system", "content": self.system_prompt}] + self.messages
        }

        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            self.api_url,
            data=data,
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise RuntimeError(f"API call failed ({e.code}): {error_body}")
        except Exception as e:
            raise RuntimeError(f"API call failed: {e}")

    def _execute_bash_command(self, command):
        """
        执行bash命令 - 完全保持V1的逻辑和安全检查
        内联实现，无需额外模块
        """
        if not command:
            return "Error: No command provided"

        # V1安全检查 - 完全保持原有的检测模式
        if self._is_dangerous_command(command):
            # V1风格的用户确认 - 输出到stderr确保立即显示
            print(f"⚠️  Detected potentially dangerous command: {command}", file=sys.stderr)
            print("Allow execution? (y/n)", file=sys.stderr)

            try:
                confirm = input().strip().lower()
                if confirm != 'y':
                    return "User denied execution"
            except (EOFError, KeyboardInterrupt):
                return "User cancelled execution"

        try:
            # 执行命令并捕获输出 - 完全模拟V1的eval行为
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            # V1格式的结果返回 - 保持原有的格式
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += result.stderr

            # 如果没有输出，保持空字符串（V1行为）
            return f"Exit code: {result.returncode}\nOutput: {output}"

        except subprocess.TimeoutExpired:
            return "Error: Command execution timeout (30 seconds)"
        except Exception as e:
            return f"Error: Command execution failed: {e}"

    def _is_dangerous_command(self, command):
        """
        V1的危险命令检测逻辑
        完全保持原有的正则表达式模式
        """
        dangerous_patterns = [
            r'\brm\s',           # rm command
            r'\bsudo\s',         # sudo command
            r'\bchmod\s',        # chmod command
            r'curl.*\|.*sh',     # curl piped to sh
            r'wget.*\|.*sh'      # wget piped to sh (额外安全)
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

def main():
    """主入口函数"""
    if len(sys.argv) != 2:
        print("Usage: python agent.py \"task description\"")
        sys.exit(1)

    agent = AgentV1Refactor()
    agent.run(sys.argv[1])

if __name__ == "__main__":
    main()