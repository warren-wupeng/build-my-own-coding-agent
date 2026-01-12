#!/usr/bin/env python3
# tools/system_tools.py - System operation tools (V2 functionality in V3 architecture)

import subprocess
import re
import sys
import json
from .base import BaseTool


class RunBashTool(BaseTool):
    """Run bash commands tool - V2 functionality with dangerous command checking"""

    # Dangerous operations that require user confirmation (from V2)
    DANGEROUS_PATTERNS = [
        "rm -rf /", "sudo rm", "chmod 777", "curl.*|.*sh", "wget.*|.*sh",
        "dd if=", "mkfs.", "fdisk", "parted", "shutdown", "reboot", "init 0", "halt"
    ]

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": "run_bash",
                "description": "Run bash commands",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "command to run"}
                    },
                    "required": ["command"]
                }
            }
        }

    def _is_dangerous_command(self, command):
        """Check if a bash command contains dangerous patterns - same logic as V2"""
        command_lower = command.lower()

        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.endswith(".*"):
                if re.search(pattern.replace(".*", r".*?"), command_lower):
                    return True, pattern
            else:
                if pattern.lower() in command_lower:
                    return True, pattern

        # Additional pipe-to-shell check
        if "|" in command and ("sh" in command_lower or "bash" in command_lower):
            return True, "pipe to shell"

        return False, None

    def _prompt_user_confirmation(self, command, dangerous_pattern):
        """Prompt user for confirmation of dangerous operations - same logic as V2"""
        print(f"\n⚠️  Dangerous operation detected!", file=sys.stderr)
        print(f"Command: {command}", file=sys.stderr)
        print(f"Matched pattern: '{dangerous_pattern}'", file=sys.stderr)
        print("Allow execution? (y/n): ", end='', file=sys.stderr, flush=True)

        try:
            response = input().strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled by user", file=sys.stderr)
            return False

    def execute(self, input_data):
        """Execute bash command - same logic as V2 with dangerous command checking"""
        try:
            command = input_data["command"]

            # Check for dangerous operations before execution (like V2)
            is_dangerous, pattern = self._is_dangerous_command(command)
            if is_dangerous:
                if not self._prompt_user_confirmation(command, pattern):
                    return f"❌ User denied execution of dangerous command: {command}"

            # Keep command length check as basic safety
            if len(command) > 1000:
                return f"❌ Error: Command too long (max 1000 characters)\n" \
                       f"Command length: {len(command)}\n" \
                       f"This may indicate a security risk or malformed command"

            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
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