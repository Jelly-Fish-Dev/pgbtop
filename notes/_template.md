# [Topic Title]

<!-- One sentence describing what this note covers. -->

---

## Overview

<!-- What is the problem or question being addressed? -->

---

## Details

<!-- Main body. Use sub-headings as needed. -->

---

## Open Questions

<!-- Unresolved decisions or things that need more thought. -->

- [ ] 

---

## Decision / Outcome

<!-- If this note led to a decision, record it here. -->

---

## AI Disclosure

This note was produced with Claude (claude-sonnet-4-6) acting as a design and architecture assistant for the pgbtop project. The following rules govern how Claude contributes to this project:

- **No code generation.** Claude does not write, scaffold, or produce any executable or deployable code — including snippets, config files, or boilerplate. All notes are discussion and reasoning only.
- **Notes only.** All Claude output is written as Markdown into the `notes/` folder. Nothing is written outside this directory.
- **Server scope only.** Claude reasons about the pgbtop server component: PostgreSQL system table queries, WebSocket message design, TLS, token authentication, polling strategy, and connection handling. The React dashboard and TUI client are out of scope.
- **No deployment opinions.** Discussion is bounded to local development and the SSH tunnel access pattern. CI/CD, containerisation, and packaging are excluded.

These rules are defined in [CLAUDE.md](../CLAUDE.md) at the project root.
