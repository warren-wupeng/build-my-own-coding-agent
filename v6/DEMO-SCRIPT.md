# V6 Demo Script — Todo App in 5 Minutes

> End-to-end demonstration of Agent Team building a CLI Todo app from a single description.

---

## Setup (30 seconds)

```bash
cd build-my-own-coding-agent/v6
agent-team init demo-todo-app
agent-team start
```

Expected output:
```
[agent-team] Initialized project: demo-todo-app
[agent-team] Starting team...
[PM]         Online. Waiting for user input.
[Engineer]   Online. Waiting for tasks.
[Strategist] Online. Waiting for tasks.
```

---

## Step 1: User Describes the Product (10 seconds)

```bash
agent-team chat "Build a command-line Todo app in Python. Features: add task, list tasks, mark complete, delete task. Store tasks in a JSON file."
```

---

## Step 2: PM Breaks Down the Request (auto, ~30 seconds)

PM receives the message and creates Issues:

```
[PM] Received user request. Breaking down into Issues...
[PM] Created Issue #1: "Project setup — create todo_app/ with __main__.py and storage.py"
     → Assigned to: Engineer (Size: S, Priority: P0)
[PM] Created Issue #2: "Implement core CRUD operations (add/list/complete/delete)"
     → Assigned to: Engineer (Size: M, Priority: P0)
[PM] Created Issue #3: "JSON file storage with load/save"
     → Assigned to: Engineer (Size: S, Priority: P0)
[PM] Created Issue #4: "CLI argument parsing with argparse"
     → Assigned to: Engineer (Size: S, Priority: P1)
[PM] Created Issue #5: "README with usage examples"
     → Assigned to: Strategist (Size: M, Priority: P1)
[PM] Sent task assignments via mailbox.
```

### What to Highlight

- PM understood the user intent and created 5 atomic Issues
- Each Issue has a clear scope, acceptance criteria, and assignee
- Code tasks → Engineer; documentation → Strategist
- Dependencies are implicit: #2 and #3 need #1 first

---

## Step 3: Engineer Builds (auto, ~2-3 minutes)

Engineer picks up Issues in priority order:

### Issue #1: Project Setup
```
[Engineer] Picked up Issue #1: Project setup
[Engineer] Creating demo-todo-app/todo_app/__main__.py
[Engineer] Creating demo-todo-app/todo_app/storage.py
[Engineer] git commit: "engineer: #1 project setup with __main__ and storage module"
[Engineer] Issue #1 → done. Notifying PM.
```

### Issue #3: JSON Storage (picked before #2 — smaller)
```
[Engineer] Picked up Issue #3: JSON file storage
[Engineer] Implementing TodoStorage class in storage.py
           - load_tasks(): read from tasks.json
           - save_tasks(): write to tasks.json
           - handles missing file gracefully
[Engineer] git commit: "engineer: #3 JSON storage with load/save"
[Engineer] Issue #3 → done. Notifying PM.
```

### Issue #2: Core CRUD
```
[Engineer] Picked up Issue #2: Core CRUD operations
[Engineer] Implementing in todo_app/core.py:
           - add_task(title) → creates task with id, title, completed=False
           - list_tasks() → prints all tasks with status
           - complete_task(id) → marks task as done
           - delete_task(id) → removes task
[Engineer] git commit: "engineer: #2 core CRUD operations"
[Engineer] Issue #2 → done. Notifying PM.
```

### Issue #4: CLI
```
[Engineer] Picked up Issue #4: CLI argument parsing
[Engineer] Implementing argparse in __main__.py:
           - python -m todo_app add "Buy groceries"
           - python -m todo_app list
           - python -m todo_app complete 1
           - python -m todo_app delete 1
[Engineer] Self-review: all commands work ✓
[Engineer] git commit: "engineer: #4 CLI with argparse"
[Engineer] Issue #4 → done. Notifying PM.
```

### What to Highlight

- Engineer works one Issue at a time, smallest first when priority is equal
- Each commit references the Issue number
- Self-review before marking done
- Notifies PM after each completion

---

## Step 4: Strategist Documents (auto, parallel with Engineer)

Strategist picks up Issue #5 once there's enough code to document:

```
[Strategist] Picked up Issue #5: README with usage examples
[Strategist] Reading codebase to understand architecture...
[Strategist] Writing demo-todo-app/README.md:
             - What is this? (1-line description)
             - Quick start (3 commands)
             - Usage examples (add/list/complete/delete)
             - File structure
[Strategist] git commit: "strategist: #5 README with usage examples"
[Strategist] Issue #5 → done. Notifying PM.
```

### Proactive Quality Scan
```
[Strategist] Running quality scan...
[Strategist] Found: No docstrings in core.py functions.
[Strategist] → Sent suggestion to PM: "Consider adding Issue for docstrings in core.py"
```

### What to Highlight

- Strategist works in parallel with Engineer (different files, no conflicts)
- Documentation is based on actual code, not guesses
- Proactive scanning identifies improvements PM didn't ask for

---

## Step 5: PM Reviews and Accepts (auto, ~30 seconds)

```
[PM] Engineer completed Issue #1 → Reviewing...
     ✓ __main__.py exists with proper structure
     ✓ storage.py exists
     → Accepted. Issue #1 closed.

[PM] Engineer completed Issue #3 → Reviewing...
     ✓ TodoStorage class implements load/save
     ✓ Handles missing file case
     → Accepted. Issue #3 closed.

[PM] Engineer completed Issue #2 → Reviewing...
     ✓ All 4 CRUD operations implemented
     ✓ Functions use storage module correctly
     → Accepted. Issue #2 closed.

[PM] Engineer completed Issue #4 → Reviewing...
     ✓ argparse setup with 4 subcommands
     ✓ python -m todo_app works
     → Accepted. Issue #4 closed.

[PM] Strategist completed Issue #5 → Reviewing...
     ✓ README covers all commands
     ✓ Code examples match actual CLI
     → Accepted. Issue #5 closed.

[PM] All 5 Issues completed. Reporting to user.
```

---

## Step 6: User Gets the Result (5 seconds)

```
[PM] Project "demo-todo-app" is complete.

     Delivered:
     - CLI Todo app with add/list/complete/delete commands
     - JSON file persistence
     - README with usage documentation

     5 Issues created → 5 completed → 0 rejected

     Try it:
     $ cd demo-todo-app
     $ python -m todo_app add "Try Agent Team"
     $ python -m todo_app list
```

User tries it:
```bash
$ cd demo-todo-app
$ python -m todo_app add "Buy groceries"
Added: "Buy groceries" (id: 1)

$ python -m todo_app add "Write blog post"
Added: "Write blog post" (id: 2)

$ python -m todo_app list
  1. [ ] Buy groceries
  2. [ ] Write blog post

$ python -m todo_app complete 1
Completed: "Buy groceries"

$ python -m todo_app list
  1. [x] Buy groceries
  2. [ ] Write blog post
```

---

## Final Project Structure

```
demo-todo-app/
├── .agent-team/            # Agent Team state (auto-generated)
│   ├── issues/             # 5 closed Issues
│   ├── mailbox/            # Message history
│   └── status.json         # Project status: complete
├── todo_app/
│   ├── __init__.py
│   ├── __main__.py         # CLI entry point (argparse)
│   ├── core.py             # CRUD operations
│   └── storage.py          # JSON file storage
├── tasks.json              # Data file (created on first use)
└── README.md               # Auto-generated documentation
```

---

## Timing Summary

| Phase | Duration | Agent |
|-------|----------|-------|
| User input | 10s | User |
| PM breakdown | 30s | PM |
| Engineering (4 Issues) | 2-3 min | Engineer |
| Documentation (1 Issue) | 1 min | Strategist (parallel) |
| PM review (5 Issues) | 30s | PM |
| **Total** | **~5 min** | |

---

## Presentation Notes

**Key talking points during demo:**

1. **"One description, full product."** — The user said one sentence. The team produced working code + docs.

2. **"Real team dynamics."** — PM breaks down, Engineer builds, Strategist documents. Just like a real team.

3. **"Async by design."** — Agents don't wait for each other. Engineer and Strategist work in parallel. PM reviews as things complete.

4. **"SOP-driven, not hardcoded."** — Change the SOP Markdown file, change the agent's behavior. No code changes needed.

5. **"Git is the only infrastructure."** — No database, no message broker, no external services. Just a Git repo. You can inspect everything.

6. **"The Strategist proactively found an issue."** — It wasn't asked to check for docstrings. It scanned the code and surfaced a suggestion. This is the quality conscience at work.
