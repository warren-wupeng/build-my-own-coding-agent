#!/usr/bin/env python3
# tools/system_tools.py - 系统操作工具
# V3版本：增强的系统命令和进程管理

import subprocess
import os
import shutil
from .base import BaseTool


class RunBashTool(BaseTool):
    """
    bash命令执行工具
    支持安全检查、超时控制、详细输出
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "run_bash",
                "description": "安全地执行bash命令，支持超时控制和详细输出",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "要执行的bash命令"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "命令超时时间（秒），默认30秒",
                            "default": 30
                        },
                        "working_dir": {
                            "type": "string",
                            "description": "命令执行的工作目录，默认为当前目录"
                        }
                    },
                    "required": ["command"]
                }
            }
        }

    def execute(self, input_data):
        command = input_data["command"]
        timeout = input_data.get("timeout", 30)
        working_dir = input_data.get("working_dir")

        # Safety check - detect dangerous commands
        dangerous_patterns = [
            "rm -rf /",      # Delete root filesystem
            "sudo rm",       # Privileged deletion
            "chmod 777",     # Dangerous permissions
            "curl.*|.*sh",   # Pipe curl to shell
            "wget.*|.*sh",   # Pipe wget to shell
            "dd if=",        # Disk operations
            "mkfs.",         # Format filesystem
            "fdisk",         # Partition operations
            "parted",        # Partition operations
            "shutdown",      # System shutdown
            "reboot",        # System reboot
            "init 0",        # System halt
            "halt"           # System halt
        ]

        # Check for dangerous patterns (case-insensitive)
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            # Handle regex patterns and simple string patterns
            if pattern.endswith(".*"):
                # For regex-like patterns, use more sophisticated matching
                import re
                if re.search(pattern.replace(".*", r".*?"), command_lower):
                    return f"⚠️  Dangerous command detected and blocked for safety\n" \
                           f"Command: {command}\n" \
                           f"Matched pattern: '{pattern}'\n" \
                           f"Reason: This command could potentially harm the system\n" \
                           f"If you need to execute this command, please run it manually with proper precautions"
            else:
                # For simple string patterns
                if pattern.lower() in command_lower:
                    return f"⚠️  Dangerous command detected and blocked for safety\n" \
                           f"Command: {command}\n" \
                           f"Matched pattern: '{pattern}'\n" \
                           f"Reason: This command could potentially harm the system\n" \
                           f"If you need to execute this command, please run it manually with proper precautions"

        # Additional check for pipe to shell commands
        if "|" in command and ("sh" in command_lower or "bash" in command_lower):
            return f"⚠️  Dangerous command detected and blocked for safety\n" \
                   f"Command: {command}\n" \
                   f"Matched pattern: 'pipe to shell'\n" \
                   f"Reason: Piping external content to shell can be dangerous\n" \
                   f"If you need to execute this command, please run it manually with proper precautions"

        # Additional safety checks
        if len(command) > 1000:
            return f"❌ Error: Command too long (max 1000 characters)\n" \
                   f"Command length: {len(command)}\n" \
                   f"This may indicate a security risk or malformed command"

        try:
            # Check working directory
            if working_dir and not os.path.exists(working_dir):
                return f"❌ Working directory does not exist: {working_dir}"

            # Limit timeout
            timeout = min(timeout, 300)  # Maximum 5 minutes

            print(f"🔧 Executing command: {command}")
            if working_dir:
                print(f"📁 Working directory: {working_dir}")
            print(f"⏱️  Timeout: {timeout} seconds")

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir
            )

            output = ""
            if result.stdout:
                output += f"stdout:\n{result.stdout}"
            if result.stderr:
                output += f"stderr:\n{result.stderr}"

            if result.returncode == 0:
                return f"✅ Command executed successfully (exit code: {result.returncode}):\n{output}"
            else:
                return f"⚠️  Command completed (exit code: {result.returncode}):\n{output}"

        except subprocess.TimeoutExpired:
            return "❌ Error: Command execution timeout (30 seconds)"
        except Exception as e:
            return f"❌ Command execution failed: {e}"


class WhichTool(BaseTool):
    """
    命令查找工具
    V3新增：查找系统命令位置
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "which",
                "description": "查找系统命令的完整路径",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "要查找的命令名称"
                        }
                    },
                    "required": ["command"]
                }
            }
        }

    def execute(self, input_data):
        command = input_data["command"]

        try:
            # 使用shutil.which查找命令
            path = shutil.which(command)

            if path:
                # 获取命令信息
                try:
                    stat = os.stat(path)
                    size = stat.st_size
                    executable = os.access(path, os.X_OK)

                    return f"✅ 找到命令: {command}\n" \
                           f"📍 路径: {path}\n" \
                           f"📊 大小: {size} 字节\n" \
                           f"🔐 可执行: {'是' if executable else '否'}"
                except:
                    return f"✅ 找到命令: {command}\n📍 路径: {path}"
            else:
                # 尝试使用which命令
                result = subprocess.run(
                    f"which {command}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0 and result.stdout.strip():
                    return f"✅ 找到命令: {command}\n📍 路径: {result.stdout.strip()}"
                else:
                    return f"❌ 未找到命令: {command}\n" \
                           f"请检查:\n" \
                           f"• 命令是否已安装\n" \
                           f"• 命令是否在PATH环境变量中\n" \
                           f"• 命令名拼写是否正确"

        except Exception as e:
            return f"❌ 查找命令失败: {e}"


class EnvTool(BaseTool):
    """
    环境变量工具
    V3新增：环境变量查看和管理
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "env",
                "description": "查看或搜索环境变量",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "variable": {
                            "type": "string",
                            "description": "要查看的环境变量名称，不指定则显示所有"
                        },
                        "search_pattern": {
                            "type": "string",
                            "description": "搜索环境变量的模式（不区分大小写）"
                        },
                        "show_path": {
                            "type": "boolean",
                            "description": "是否详细显示PATH变量内容",
                            "default": False
                        }
                    },
                    "required": []
                }
            }
        }

    def execute(self, input_data):
        variable = input_data.get("variable")
        search_pattern = input_data.get("search_pattern")
        show_path = input_data.get("show_path", False)

        try:
            if variable:
                # 查看特定环境变量
                value = os.environ.get(variable)
                if value is not None:
                    if variable.upper() == "PATH" or show_path:
                        # 特殊处理PATH变量
                        paths = value.split(os.pathsep)
                        result = f"✅ 环境变量 {variable}:\n"
                        result += f"📊 包含 {len(paths)} 个路径:\n"
                        for i, path in enumerate(paths, 1):
                            exists = "✓" if os.path.exists(path) else "✗"
                            result += f"  {i:2d}. {exists} {path}\n"
                        return result
                    else:
                        return f"✅ 环境变量 {variable}: {value}"
                else:
                    return f"❌ 环境变量不存在: {variable}"

            elif search_pattern:
                # 搜索环境变量
                matches = []
                pattern_lower = search_pattern.lower()

                for key, value in os.environ.items():
                    if pattern_lower in key.lower() or pattern_lower in value.lower():
                        matches.append((key, value))

                if matches:
                    result = f"🔍 找到 {len(matches)} 个匹配的环境变量:\n"
                    for key, value in sorted(matches):
                        # 限制显示长度
                        display_value = value[:100] + "..." if len(value) > 100 else value
                        result += f"  • {key}={display_value}\n"
                    return result
                else:
                    return f"❌ 未找到匹配 '{search_pattern}' 的环境变量"

            else:
                # 显示所有环境变量概览
                env_vars = list(os.environ.items())
                important_vars = ["PATH", "HOME", "USER", "SHELL", "PWD", "LANG"]

                result = f"🌐 环境变量概览 (总共 {len(env_vars)} 个)\n\n"

                # 显示重要变量
                result += "📌 重要变量:\n"
                for var in important_vars:
                    if var in os.environ:
                        value = os.environ[var]
                        display_value = value[:60] + "..." if len(value) > 60 else value
                        result += f"  • {var}: {display_value}\n"

                result += f"\n💡 提示:\n"
                result += f"  • 查看特定变量: 使用 variable 参数\n"
                result += f"  • 搜索变量: 使用 search_pattern 参数\n"
                result += f"  • 查看PATH详情: 使用 show_path=true"

                return result

        except Exception as e:
            return f"❌ 环境变量操作失败: {e}"


class PwdTool(BaseTool):
    """
    当前目录工具
    V3新增：显示当前工作目录信息
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "pwd",
                "description": "显示当前工作目录的详细信息",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }

    def execute(self, input_data):
        try:
            current_dir = os.getcwd()
            abs_path = os.path.abspath(current_dir)

            # 获取目录信息
            result = f"📍 当前工作目录:\n{abs_path}\n\n"

            # 检查权限
            readable = os.access(current_dir, os.R_OK)
            writable = os.access(current_dir, os.W_OK)
            executable = os.access(current_dir, os.X_OK)

            result += f"🔐 权限:\n"
            result += f"  • 读取: {'✓' if readable else '✗'}\n"
            result += f"  • 写入: {'✓' if writable else '✗'}\n"
            result += f"  • 执行: {'✓' if executable else '✗'}\n"

            # 统计目录内容
            try:
                items = os.listdir(current_dir)
                files = sum(1 for item in items if os.path.isfile(os.path.join(current_dir, item)))
                dirs = sum(1 for item in items if os.path.isdir(os.path.join(current_dir, item)))

                result += f"\n📊 目录内容:\n"
                result += f"  • 文件: {files} 个\n"
                result += f"  • 子目录: {dirs} 个\n"
                result += f"  • 总计: {len(items)} 个项目"

            except PermissionError:
                result += f"\n❌ 无法读取目录内容（权限不足）"

            return result

        except Exception as e:
            return f"❌ 获取当前目录失败: {e}"