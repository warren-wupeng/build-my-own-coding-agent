# Changelog — V6 Agent Team

All notable changes to V6 will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### Added
- **SOP Templates** — Standard Operating Procedures for all three Agent roles:
  - `sops/pm.md` — PM Agent: Issue management, task assignment, acceptance review
  - `sops/engineer.md` — Engineer Agent: code implementation, self-review, scope discipline
  - `sops/strategist.md` — Strategist Agent: documentation, quality scanning, brand voice
- **V6 README** — Project vision, architecture diagram, quick start guide
- **V6 CHANGELOG** — This file

### Architecture Decisions
- Git repository as single source of truth (no external DB)
- Heartbeat-driven async execution model
- File-based Mailbox for inter-agent communication
- Markdown SOPs as agent behavior definitions (inspectable, customizable)
- Strict role separation (PM/Engineer/Strategist never cross boundaries)
