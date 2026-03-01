# V6 - Agent Team

Multi-agent product team framework. Three agent roles (PM, Engineer, Strategist) collaborate through a Git repository with shared state, heartbeat-driven autonomy, and async mailbox communication.

## Architecture

```
v6/
├── core/              # Inherited from V5 - AgentCore business logic
├── tools/             # Inherited from V5 - 15 tools (file/search/system/conversation/delegation)
├── conversation/      # Inherited from V5 - Context compression
├── delegation/        # Inherited from V5 - Sub-agent delegation
├── execution/         # Inherited from V5 - Tool executor
├── llm/               # Inherited from V5 - LLM client (OpenRouter)
├── monitoring/        # Inherited from V5 - Statistics
├── interface/         # Inherited from V5 - CLI display
├── agent_team/        # NEW - Team infrastructure
│   ├── mailbox.py     # Async file-based messaging
│   ├── heartbeat.py   # Periodic tick driver
│   ├── shared_state.py # Git-based state management
│   ├── sop_parser.py  # Markdown SOP -> executable steps
│   └── issue_manager.py # Issue CRUD + lifecycle
├── agents/            # NEW - Agent roles
│   ├── base_agent.py  # BaseAgent extends AgentCore
│   ├── pm_agent.py    # Product Manager
│   ├── engineer_agent.py # Software Engineer
│   ├── strategist_agent.py # Documentation & UX
│   └── team_orchestrator.py # Lifecycle manager
├── tests/             # Unit tests
├── docs/              # Documentation
└── sops/              # SOP templates (Markdown)
```

## Quick Start

```bash
cd v6
uv sync
agent-team init my-project "Build a todo app"
agent-team start
agent-team status
agent-team stop
```

## Design Principles

1. **Inherit, don't rewrite** - V5 core modules are copied verbatim
2. **Agents are processes** - Each role runs as an independent process
3. **Git is the bus** - All communication flows through the Git repository
4. **Heartbeat drives autonomy** - Agents self-activate on configurable intervals
5. **SOP guides behavior** - Agent actions are governed by Markdown SOP documents
