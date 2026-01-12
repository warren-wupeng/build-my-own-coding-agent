#!/usr/bin/env python3
# V3 - Complete Architecture Version (300+ lines of code)
# Object-oriented tool system and extensible architecture

import json
import os
import sys
import urllib.request
import urllib.error
from tools.registry import get_tools, execute_tool, get_tools_info

class AgentV3:
    """V3 version AI assistant main class"""

    def __init__(self):
        self.messages = []
        self.tools = []
        self.step_count = 0
        self.max_steps = 50

    def initialize(self):
        """Initialize agent"""
        # Get tool definitions and information
        self.tools = get_tools()
        tools_info = get_tools_info()

        print("🚀 AI Assistant V3 - Complete Architecture Version")
        print("🏗️  Object-Oriented Tool System | Extensible Architecture")
        print("")
        print(f"🛠️  Loaded tools: {len(self.tools)}")
        for tool_info in tools_info:
            print(f"   • {tool_info['name']}: {tool_info['description']}")
        print("")

    def call_openrouter_api(self, messages, tools):
        """Call OpenRouter API"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("❌ Error: OPENROUTER_API_KEY environment variable not set")
            print("Please run: export OPENROUTER_API_KEY=\"your-key-here\"")
            print("Get API key: https://openrouter.ai/keys")
            sys.exit(1)

        # Build request data
        payload = {
            "model": "deepseek/deepseek-v3.2",
            "messages": messages,
            "tools": tools,
            "max_tokens": 4096
        }

        # Convert to JSON bytes
        data = json.dumps(payload).encode('utf-8')

        # Create request
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"❌ API call failed ({e.code}): {error_body}")
            raise
        except Exception as e:
            print(f"❌ API call failed: {e}")
            raise

    def execute_tool_call(self, tool_call):
        """Execute single tool call"""
        tool_name = tool_call["function"]["name"]
        tool_input = json.loads(tool_call["function"]["arguments"])
        tool_id = tool_call["id"]

        # Show tool call information
        print(f"🔧 Calling tool '{tool_name}'")
        for key, value in tool_input.items():
            if len(str(value)) > 50:
                preview = str(value)[:50] + "..."
            else:
                preview = str(value)
            print(f"   📝 {key}: {preview}")

        # Execute tool
        try:
            result = execute_tool(tool_name, tool_input)

            # Show result preview
            if len(result) > 300:
                preview = result[:300] + f"... (total {len(result)} characters)"
            else:
                preview = result
            print(f"   📤 Result: {preview}")

            return {
                "tool_call_id": tool_id,
                "role": "tool",
                "name": tool_name,
                "content": result
            }

        except Exception as e:
            error_msg = f"Tool execution error: {e}"
            print(f"   ❌ {error_msg}")
            return {
                "tool_call_id": tool_id,
                "role": "tool",
                "name": tool_name,
                "content": error_msg
            }

    def run_conversation_loop(self):
        """Run main conversation loop"""
        while self.step_count < self.max_steps:
            self.step_count += 1
            print(f"🔄 Execution Step {self.step_count}")

            try:
                # Call API
                response = self.call_openrouter_api(self.messages, self.tools)

                # Parse response
                message = response["choices"][0]["message"]
                finish_reason = response["choices"][0]["finish_reason"]

                # Add assistant response to history
                self.messages.append(message)

                # Handle different completion reasons
                if finish_reason == "stop":
                    # Task completed
                    if message.get("content"):
                        print(f"✅ {message['content']}")
                    print("")
                    print(f"🎉 Task completed successfully! Total steps executed: {self.step_count}.")
                    break

                elif finish_reason == "tool_calls" or message.get("tool_calls"):
                    # Need to execute tools
                    tool_calls = message.get("tool_calls", [])
                    if not tool_calls:
                        print("❌ Error: finish_reason is tool_calls but no tool calls found")
                        break

                    print(f"   🔗 Need to execute {len(tool_calls)} tools")

                    # Execute all tool calls
                    tool_results = []
                    for i, tool_call in enumerate(tool_calls, 1):
                        print(f"   [{i}/{len(tool_calls)}]", end=" ")
                        result = self.execute_tool_call(tool_call)
                        tool_results.append(result)

                    # Add tool results to conversation history
                    self.messages.extend(tool_results)
                    print("")

                elif finish_reason == "length":
                    print("⚠️  Response length exceeded, continuing...")

                else:
                    print(f"❌ Unknown finish reason: {finish_reason}")
                    print(f"   Response content: {message}")
                    break

            except Exception as e:
                print(f"❌ Step execution failed: {e}")
                break

        # Check if maximum steps reached
        if self.step_count >= self.max_steps:
            print(f"⚠️  Reached maximum step limit ({self.max_steps}), stopping execution")
            print("   This usually means the task is too complex or there's a loop")

    def run(self, task):
        """Run AI assistant to process specified task"""
        print(f"📝 Task: {task}")
        print("")

        # Initialize conversation
        self.messages = [{"role": "user", "content": task}]

        # Run conversation loop
        self.run_conversation_loop()

    def show_statistics(self):
        """Show runtime statistics"""
        print("")
        print("📊 Execution Statistics:")
        print(f"   • Total steps: {self.step_count}")
        print(f"   • Message count: {len(self.messages)}")

        # Count tool usage
        tool_usage = {}
        for msg in self.messages:
            if msg.get("role") == "tool":
                tool_name = msg.get("name")
                if tool_name:
                    tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        if tool_usage:
            print("   • Tool usage:")
            for tool_name, count in sorted(tool_usage.items()):
                print(f"     - {tool_name}: {count} times")

def show_help():
    """Show help information"""
    print("🏗️  AI Assistant V3 - Complete Architecture Version")
    print("")
    print("💡 Features:")
    print("   • Object-oriented tool system")
    print("   • Extensible tool registration mechanism")
    print("   • Complete error handling and timeout control")
    print("   • Detailed execution statistics and logging")
    print("")
    print("📖 Usage:")
    print("   python agent.py \"your task description\"")
    print("")
    print("🌟 Examples:")
    print("   python agent.py \"Create a Python file that calculates Fibonacci numbers and run it\"")
    print("   python agent.py \"Analyze function definitions in all Python files in the current directory\"")
    print("   python agent.py \"Search for all files containing 'TODO' in the project\"")
    print("")
    print("⚙️  Configuration:")
    print("   export OPENROUTER_API_KEY=\"your-api-key\"")
    print("   Get API key: https://openrouter.ai/keys")
    print("")

    # Show available tools
    try:
        tools_info = get_tools_info()
        print("🛠️  Available Tools:")
        for i, tool_info in enumerate(tools_info, 1):
            print(f"   {i}. {tool_info['name']}: {tool_info['description']}")
            if tool_info.get('parameters'):
                print(f"      Parameters: {', '.join(tool_info['parameters'])}")
    except:
        print("🛠️  (Tool information loading failed)")

def main():
    """Main function"""
    # Handle help arguments
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help", "help"]):
        show_help()
        return

    if len(sys.argv) != 2:
        print("❌ Error: Please provide task description")
        print("Usage: python agent.py \"your task\"")
        print("Help: python agent.py --help")
        sys.exit(1)

    # Create and run agent
    agent = AgentV3()

    try:
        agent.initialize()
        agent.run(sys.argv[1])
        agent.show_statistics()

    except KeyboardInterrupt:
        print("\n⏹️  User interrupted execution")
        agent.show_statistics()

    except Exception as e:
        print(f"\n💥 Program exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()