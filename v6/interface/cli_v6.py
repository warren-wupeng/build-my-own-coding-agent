"""agent-team CLI — Command-line interface for V6 Agent Team (Issue #11)

Commands:
    agent-team init <name> <description>  — Initialize a new project
    agent-team start [--description]      — Start all agents
    agent-team stop                       — Stop all agents
    agent-team status                     — Show team status
    agent-team chat <message>             — Send a message to PM
"""

import argparse
import json
import os
import sys

# Ensure v6/ is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.team_orchestrator import TeamOrchestrator


def cmd_init(args):
    """Initialize a new agent-team project."""
    project_dir = args.dir or os.getcwd()
    orch = TeamOrchestrator(project_dir)
    result = orch.init_project(args.name, args.description)

    print(f"Project '{result['project_name']}' initialized.")
    print(f"  Agents: {', '.join(result['agents'])}")
    print(f"  Directory: {project_dir}/.agent-team/")
    print(f"\nNext: agent-team start --description \"your product idea\"")


def cmd_start(args):
    """Start all agent heartbeats."""
    project_dir = args.dir or os.getcwd()
    orch = TeamOrchestrator(project_dir, heartbeat_interval=args.interval)

    # Load existing config
    config = orch.shared_state.get_config()
    if not config:
        print("Error: No .agent-team/ found. Run 'agent-team init' first.")
        sys.exit(1)

    orch.init_project(config.project_name, config.description)
    result = orch.start(product_description=args.description)

    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)

    print(f"Team started for project: {config.project_name}")
    for agent, state in result.get("agents", {}).items():
        print(f"  {agent}: {state}")

    if args.description:
        print(f"\nProduct request sent to PM: {args.description[:80]}...")

    # Run until interrupted
    print("\nPress Ctrl+C to stop...")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        stop_result = orch.stop()
        print(f"Stopped. PM: {stop_result.get('pm_ticks', 0)} ticks, "
              f"Engineer: {stop_result.get('engineer_ticks', 0)} ticks, "
              f"Strategist: {stop_result.get('strategist_ticks', 0)} ticks")


def cmd_stop(args):
    """Stop all agents (sends stop signal)."""
    project_dir = args.dir or os.getcwd()
    # In a real implementation, this would signal a running daemon.
    # For now, show status.
    orch = TeamOrchestrator(project_dir)
    config = orch.shared_state.get_config()
    if not config:
        print("Error: No .agent-team/ found.")
        sys.exit(1)

    # Update status to idle
    for agent in ["pm", "engineer", "strategist"]:
        orch.shared_state.update_agent_status(agent, state="idle")
    print("Stop signal sent. All agents marked as idle.")


def cmd_status(args):
    """Show team status."""
    project_dir = args.dir or os.getcwd()
    orch = TeamOrchestrator(project_dir)

    config = orch.shared_state.get_config()
    if not config:
        print("Error: No .agent-team/ found. Run 'agent-team init' first.")
        sys.exit(1)

    # Re-init to get issue counts
    orch.init_project(config.project_name, config.description)
    status = orch.status()

    print(f"Project: {status.get('project_name', 'unknown')}")
    print(f"Running: {status['running']}")
    print()

    # Agents
    print("Agents:")
    for name, info in status.get("agents", {}).items():
        task = info.get("current_task") or "none"
        print(f"  {name:12s}  state: {info['state']:10s}  task: {task}  ticks: {info['tick_count']}")

    # Issues
    issues = status.get("issues", {})
    print(f"\nIssues: {issues.get('total', 0)} total")
    for s in ["open", "in_progress", "review", "done", "closed"]:
        count = issues.get(s, 0)
        if count:
            print(f"  {s}: {count}")


def cmd_chat(args):
    """Send a message to PM."""
    project_dir = args.dir or os.getcwd()
    orch = TeamOrchestrator(project_dir)

    config = orch.shared_state.get_config()
    if not config:
        print("Error: No .agent-team/ found.")
        sys.exit(1)

    orch.init_project(config.project_name, config.description)
    message = " ".join(args.message)
    result = orch.send_chat(message)
    print(result)


def main():
    parser = argparse.ArgumentParser(
        prog="agent-team",
        description="V6 Agent Team CLI - Multi-agent product team framework",
    )
    parser.add_argument(
        "--dir", "-d",
        help="Project directory (default: current directory)",
        default=None,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = subparsers.add_parser("init", help="Initialize a new project")
    p_init.add_argument("name", help="Project name")
    p_init.add_argument("description", help="Project description")

    # start
    p_start = subparsers.add_parser("start", help="Start all agents")
    p_start.add_argument(
        "--description", "-d",
        help="Product description to send to PM",
        default=None,
    )
    p_start.add_argument(
        "--interval", "-i",
        type=float,
        help="Heartbeat interval in seconds (default: 30)",
        default=30.0,
    )

    # stop
    subparsers.add_parser("stop", help="Stop all agents")

    # status
    subparsers.add_parser("status", help="Show team status")

    # chat
    p_chat = subparsers.add_parser("chat", help="Send a message to PM")
    p_chat.add_argument("message", nargs="+", help="Message text")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "init": cmd_init,
        "start": cmd_start,
        "stop": cmd_stop,
        "status": cmd_status,
        "chat": cmd_chat,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
