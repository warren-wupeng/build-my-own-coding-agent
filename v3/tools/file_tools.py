#!/usr/bin/env python3
# tools/file_tools.py - 文件操作工具
# V3版本：增强的文件操作工具集

import os
from .base import BaseTool


class ReadFileTool(BaseTool):
    """
    读取文件内容工具
    支持UTF-8编码，提供详细的错误信息
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取文件内容，支持UTF-8编码",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "要读取的文件路径（支持相对路径和绝对路径）"
                        }
                    },
                    "required": ["path"]
                }
            }
        }

    def execute(self, input_data):
        file_path = input_data["path"]

        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return f"❌ 文件不存在: {file_path}"

            # 检查是否为文件
            if not os.path.isfile(file_path):
                return f"❌ 路径不是文件: {file_path}"

            # 读取文件
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 获取文件信息
            file_size = os.path.getsize(file_path)
            line_count = content.count('\n') + 1 if content else 0

            return f"✅ 成功读取文件 {file_path}\n" \
                   f"📊 文件信息: {file_size} 字节, {line_count} 行\n" \
                   f"📄 文件内容:\n{content}"

        except UnicodeDecodeError:
            return f"❌ 编码错误: 文件 {file_path} 不是UTF-8编码"
        except PermissionError:
            return f"❌ 权限错误: 无法读取文件 {file_path}"
        except Exception as e:
            return f"❌ 读取文件失败: {e}"


class WriteFileTool(BaseTool):
    """
    写入文件工具
    支持创建目录，原子写入操作
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "写入内容到文件，如果目录不存在会自动创建",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "目标文件路径"
                        },
                        "content": {
                            "type": "string",
                            "description": "要写入的文本内容"
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        }

    def execute(self, input_data):
        file_path = input_data["path"]
        content = input_data["content"]

        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                print(f"📁 创建目录: {directory}")

            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # 获取写入信息
            file_size = len(content.encode('utf-8'))
            line_count = content.count('\n') + 1 if content else 0

            return f"✅ 成功写入文件 {file_path}\n" \
                   f"📊 写入信息: {file_size} 字节, {line_count} 行"

        except PermissionError:
            return f"❌ 权限错误: 无法写入文件 {file_path}"
        except Exception as e:
            return f"❌ 写入文件失败: {e}"


class EditFileTool(BaseTool):
    """
    精确编辑文件工具
    支持唯一字符串替换，防止误操作
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "通过替换唯一字符串对文件进行精确编辑",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "要编辑的文件路径"
                        },
                        "old_string": {
                            "type": "string",
                            "description": "要替换的旧字符串（必须在文件中唯一存在）"
                        },
                        "new_string": {
                            "type": "string",
                            "description": "替换后的新字符串"
                        }
                    },
                    "required": ["path", "old_string", "new_string"]
                }
            }
        }

    def execute(self, input_data):
        file_path = input_data["path"]
        old_string = input_data["old_string"]
        new_string = input_data["new_string"]

        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return f"❌ 文件不存在: {file_path}"

            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # 检查旧字符串是否存在
            if old_string not in original_content:
                return f"❌ 在文件中未找到要替换的字符串\n" \
                       f"查找: {old_string[:100]}{'...' if len(old_string) > 100 else ''}"

            # 检查旧字符串是否唯一
            count = original_content.count(old_string)
            if count > 1:
                return f"❌ 要替换的字符串不唯一，在文件中找到 {count} 个匹配\n" \
                       f"字符串: {old_string[:100]}{'...' if len(old_string) > 100 else ''}\n" \
                       f"请使用更具体的字符串确保唯一性"

            # 执行替换
            new_content = original_content.replace(old_string, new_string)

            # 写回文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # 计算变化
            old_size = len(original_content)
            new_size = len(new_content)
            size_diff = new_size - old_size

            return f"✅ 成功编辑文件 {file_path}\n" \
                   f"📊 替换统计:\n" \
                   f"   • 旧字符串长度: {len(old_string)} 字符\n" \
                   f"   • 新字符串长度: {len(new_string)} 字符\n" \
                   f"   • 文件大小变化: {size_diff:+d} 字符"

        except PermissionError:
            return f"❌ 权限错误: 无法编辑文件 {file_path}"
        except Exception as e:
            return f"❌ 编辑文件失败: {e}"


class ListFilesTool(BaseTool):
    """
    列出目录内容工具
    V3新增功能
    """

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "列出目录中的文件和子目录",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "目录路径，默认为当前目录",
                            "default": "."
                        },
                        "show_hidden": {
                            "type": "boolean",
                            "description": "是否显示隐藏文件（以.开头的文件）",
                            "default": False
                        }
                    },
                    "required": []
                }
            }
        }

    def execute(self, input_data):
        directory = input_data.get("path", ".")
        show_hidden = input_data.get("show_hidden", False)

        try:
            # 检查目录是否存在
            if not os.path.exists(directory):
                return f"❌ 目录不存在: {directory}"

            if not os.path.isdir(directory):
                return f"❌ 路径不是目录: {directory}"

            # 获取目录内容
            items = os.listdir(directory)

            # 过滤隐藏文件
            if not show_hidden:
                items = [item for item in items if not item.startswith('.')]

            # 分类文件和目录
            files = []
            directories = []

            for item in items:
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    directories.append(item)
                else:
                    files.append(item)

            # 排序
            directories.sort()
            files.sort()

            # 构建输出
            result = f"📁 目录内容: {os.path.abspath(directory)}\n"

            if directories:
                result += f"\n📂 子目录 ({len(directories)} 个):\n"
                for d in directories:
                    result += f"   📂 {d}/\n"

            if files:
                result += f"\n📄 文件 ({len(files)} 个):\n"
                for f in files:
                    file_path = os.path.join(directory, f)
                    try:
                        size = os.path.getsize(file_path)
                        result += f"   📄 {f} ({size} 字节)\n"
                    except:
                        result += f"   📄 {f}\n"

            if not directories and not files:
                result += "\n📭 目录为空"

            return result

        except PermissionError:
            return f"❌ 权限错误: 无法访问目录 {directory}"
        except Exception as e:
            return f"❌ 列出目录失败: {e}"