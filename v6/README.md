# V6 — Agent Team

**Describe your product. Your AI team builds it.**

*From Solo Coder to Product Team*

---

## What is this?

V6 transforms the coding agent from a single AI programmer into a **three-agent product team** that autonomously builds software from a natural language description.

You describe what you want. The team builds it — continuously, without you having to babysit every step.

| Agent | Role | Responsibility |
|-------|------|---------------|
| **PM** | Product Manager | Understands user intent, breaks down into Issues, assigns tasks, reviews deliverables |
| **Engineer** | Software Engineer | Writes production code, fixes bugs, runs tests — strictly within assigned scope |
| **Strategist** | Documentation Lead | Writes README, docs, changelogs, demo scripts; proactively finds quality gaps |

---

## Why Agent Team?

V0–V5 were **single-agent** architectures: one AI, one conversation, one task at a time. This hits a ceiling when you want to build a real product — code, docs, project management, and quality assurance all compete for the same context window.

V6 separates concerns. Each agent has its own role, its own SOP, its own context. They communicate through Git (shared state) and a Mailbox (async messages). This mirrors how real product teams work.

### The Evolution

```
V0  (33 lines)      — Bash script, proof of concept
V1  (157 lines)     — Safety + loops
V2  (742 lines)     — Tool system
V3  (1,962 lines)   — OOP architecture
V4  (5,546 lines)   — Sub-agent delegation
V5  (9,266 lines)   — SWE-bench evaluation
V6  (Agent Team)    — Multi-agent product team
```

The jump from V5 to V6 isn't about more lines of code. It's about a fundamental shift: from **one agent doing everything** to **a team of specialists collaborating**.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    User                          │
│              "Build me a Todo App"                │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│                  PM Agent                        │
│  · Receives user request                         │
│  · Breaks down into Issues                       │
│  · Assigns to Engineer / Strategist              │
│  · Reviews and accepts deliverables              │
└──────┬───────────────────────┬───────────────────┘
       │ Mailbox               │ Mailbox
       ▼                       ▼
┌──────────────┐    ┌──────────────────────┐
│  Engineer    │    │    Strategist         │
│  Agent       │    │    Agent              │
│              │    │                       │
│  · Codes     │    │  · Writes README      │
│  · Tests     │    │  · Writes docs        │
│  · Fixes     │    │  · Designs demos      │
└──────┬───────┘    └──────────┬────────────┘
       │                       │
       └───────────┬───────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │   Git Repository      │
       │   (Shared State)      │
       │                       │
       │  .agent-team/         │
       │  ├── issues/          │
       │  ├── mailbox/         │
       │  ├── status.json      │
       │  └── sops/            │
       └───────────────────────┘
```

### Key Design Decisions

1. **Git as the single source of truth** — All state lives in the repo. No external database, no message broker. If you can read the repo, you can understand everything.

2. **Heartbeat-driven execution** — Each agent runs on a configurable timer. Every tick: pull → check mail → check tasks → execute → push. This enables asynchronous collaboration without a central scheduler.

3. **Mailbox for communication** — Agents don't call each other directly. They leave messages. This is intentionally asynchronous — just like real teams using Slack or email.

4. **SOP-driven behavior** — Each agent's behavior is defined by a Markdown SOP file, not hardcoded logic. Change the SOP, change the agent's behavior. This makes the system inspectable and customizable.

5. **Strict role boundaries** — PM never writes code. Engineer never creates Issues. Strategist never changes application logic. This prevents the chaos of "everyone does everything."

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/warren-wupeng/build-my-own-coding-agent.git
cd build-my-own-coding-agent/v6

# Install dependencies
uv sync

# Initialize a new product project
agent-team init my-todo-app

# Start the team
agent-team start

# Tell them what to build
agent-team chat "Build a command-line Todo app in Python with add, list, complete, and delete commands"

# Watch them work
agent-team status
```

---

## Project Structure

```
v6/
├── sops/                    # Standard Operating Procedures
│   ├── pm.md               # PM Agent behavior definition
│   ├── engineer.md         # Engineer Agent behavior definition
│   └── strategist.md       # Strategist Agent behavior definition
├── agent_team/             # Core framework
│   ├── core/               # Shared infrastructure
│   │   ├── mailbox.py      # Async message system
│   │   ├── heartbeat.py    # Tick-based execution driver
│   │   ├── shared_state.py # Git-based state management
│   │   ├── issue_manager.py# Issue lifecycle (create/assign/close)
│   │   └── sop_parser.py   # Markdown SOP → executable steps
│   ├── agents/             # Agent implementations
│   │   ├── pm.py           # PM Agent
│   │   ├── engineer.py     # Engineer Agent
│   │   └── strategist.py   # Strategist Agent
│   └── orchestrator.py     # Team lifecycle manager
├── cli.py                  # agent-team CLI entrypoint
├── README.md               # This file
├── CHANGELOG.md            # Version history
└── pyproject.toml          # Dependencies
```

---

## How It Differs from V5

| | V5 | V6 |
|---|---|---|
| **Agents** | 1 main + sub-agents (ephemeral) | 3 persistent specialists |
| **Communication** | Function calls | Git + Mailbox (async) |
| **State** | In-memory conversation | Git repository (durable) |
| **Task management** | Ad-hoc delegation | Issue-based lifecycle |
| **Behavior** | Hardcoded prompts | SOP-driven (Markdown) |
| **User interaction** | Continuous chat | Describe once, team executes |

---

## Educational Value

This project is an **open-source educational resource** demonstrating how to build multi-agent AI systems. Each version teaches different concepts:

- **V0-V1**: How LLMs can execute commands
- **V2-V3**: How to structure AI tools and conversations
- **V4**: How to delegate between agents
- **V5**: How to evaluate agent performance
- **V6**: How to build autonomous agent teams with real-world collaboration patterns

The Agent Team architecture mirrors patterns used in production systems like [Claude Code](https://claude.ai/claude-code), [Devin](https://devin.ai), and [OpenHands](https://github.com/All-Hands-AI/OpenHands) — but distilled to its essence for learning.

---

## Status

🚧 **Under active development**

- [x] SOP templates (PM, Engineer, Strategist)
- [ ] Core infrastructure (Mailbox, Heartbeat, SharedState)
- [ ] Agent role implementations
- [ ] Team Orchestrator
- [ ] CLI tool
- [ ] End-to-end demo
