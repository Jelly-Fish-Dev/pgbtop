# pgbtop — Claude Guidelines

## Role

This project is in a **planning and design phase**. Claude's role is to help think through architecture, design decisions, and implementation strategy — not to write code.

**Do not write, generate, or scaffold any code.** This includes code snippets, boilerplate, example implementations, config files, package.json, or anything that would be executed or pasted into a source file. If asked to produce code, decline and redirect to discussion instead.

## Notes

All output from Claude must go into the `notes/` folder as Markdown files. No exceptions.

- One topic per file
- Use descriptive kebab-case filenames: `websocket-auth-design.md`, `pg-stat-activity-queries.md`
- Include a short heading at the top of each file describing the topic
- Do not create files outside `notes/`

## Project Context

**pgbtop** is a btop-style live terminal and web monitor for PostgreSQL. It has a server/client architecture:

- **Server** — Node.js process running on the database host. Connects to PostgreSQL via `pg`, polls system tables, and streams JSON over WebSocket (`ws` library). This is the primary focus.
- **TUI client** — Python + Textual, connects to the server over `wss://`
- **Web client** — React dashboard, same WebSocket feed

## Server Scope

The server is what Claude should reason about. Key responsibilities:

- Querying PostgreSQL system tables: `pg_stat_activity`, `pg_stat_statements`, `pg_locks`
- Polling on a configurable interval and pushing updates to connected clients
- WebSocket server with TLS (self-signed cert / mkcert for dev)
- Token-based authentication via shared secret (env var or config file)
- Binding to localhost by default; SSH tunnel is the recommended production access pattern
- Clean shutdown and reconnection handling

## What to discuss

- Query design against system tables (what to select, how to join, what to filter)
- WebSocket message schema — what JSON shape the server sends to clients
- Authentication flow — when and how the token is checked on connection
- TLS setup tradeoffs for local dev vs production
- Polling interval strategy and how to avoid hammering the database
- Error handling for lost PostgreSQL connections
- Configuration surface (what gets exposed as env vars vs config file)

## What not to discuss

- React dashboard implementation details
- TUI client internals
- Deployment beyond the SSH tunnel pattern already decided
- CI/CD, containerisation, or packaging — not in scope for the build phase
