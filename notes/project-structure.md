# Project Structure

A proposed directory layout for the pgbtop repository.

---

## Overview

The repo contains three discrete components — server, TUI client, and web client — plus shared documentation and tooling. Each component lives in its own top-level directory so they can evolve independently and be installed/run without pulling in the others.

---

## Details

```
pgbtop/
├── CLAUDE.md                   # AI assistant rules (this project)
├── README.md                   # Project overview, quickstart, architecture diagram
├── notes/                      # Design notes (Claude output lives here)
│
├── pgbtop-server/              # Node.js + TypeScript WebSocket server
│   ├── src/
│   │   ├── index.ts            # Entry point — starts server, handles shutdown
│   │   ├── config.ts           # Loads env vars / config file, validates required values
│   │   ├── db.ts               # pg client setup and connection management
│   │   ├── queries/
│   │   │   ├── activity.ts     # pg_stat_activity — live queries and connection states
│   │   │   ├── statements.ts   # pg_stat_statements — slow query history
│   │   │   └── locks.ts        # pg_locks — blocking detection
│   │   ├── poller.ts           # Polling loop — runs queries on interval, emits results
│   │   ├── ws-server.ts        # WebSocket server setup, auth handshake, broadcast
│   │   └── tls.ts              # Cert loading and TLS context
│   ├── dist/                   # .gitignored — compiled JS output
│   ├── certs/                  # .gitignored — local dev certs (mkcert or self-signed)
│   ├── .env.example            # Documents required environment variables
│   ├── tsconfig.json           # TypeScript compiler config
│   └── package.json
│
├── client-tui/                 # Python + Textual TUI client
│   ├── main.py
│   ├── widgets/
│   └── requirements.txt
│
├── client-web/                 # React dashboard
│   ├── src/
│   └── package.json
│
└── docs/
    ├── architecture.md         # Architecture diagram and narrative
    ├── security.md             # TLS setup, token auth, SSH tunnel guidance
    └── demo.md                 # How to run pgbench + Pagila for the demo GIF
```

---

## Key Structural Decisions

**`queries/` split by system table** — each file owns one data source (`pg_stat_activity`, `pg_stat_statements`, `pg_locks`). Keeps individual query logic isolated and easy to test or swap out without touching the polling or broadcast layers.

**`poller.js` separate from `ws-server.js`** — the poller doesn't know about WebSocket clients; it just emits data on an event emitter. The WS server subscribes to those events. This decouples the data pipeline from the transport layer, which makes it easier to add a second transport (HTTP SSE, for example) later without rewriting the poll logic.

**`config.ts` as single source of truth** — all env var reads happen here. Nothing else in the codebase calls `process.env` directly. Validates on startup and fails fast with a clear message if required values are missing.

**`dist/` gitignored** — TypeScript compiles to `dist/`. Only source files are committed. The run command targets `dist/index.js`.

**`certs/` gitignored** — dev certs are never committed. The README documents how to generate them with mkcert. Production relies on the SSH tunnel pattern, not a long-lived cert in the repo.

---

## Open Questions

- [x] Should `server/` be renamed `pgbtop-server/`? — Yes, matches the existing directory already in the repo.
- [ ] Does `pg_stat_statements` require the extension to be enabled on the target database — should the server handle the case where it's not installed gracefully?
- [ ] Where does the shared token secret live in the config — `.env` only, or also support a flat config file for users who don't want to manage env vars?

---

## Decision / Outcome

No final decision yet — this is a proposed structure for discussion.

---

## AI Disclosure

This note was produced with Claude (claude-sonnet-4-6) acting as a design and architecture assistant for the pgbtop project. The following rules govern how Claude contributes to this project:

- **No code generation.** Claude does not write, scaffold, or produce any executable or deployable code — including snippets, config files, or boilerplate. All notes are discussion and reasoning only.
- **Notes only.** All Claude output is written as Markdown into the `notes/` folder. Nothing is written outside this directory.
- **Server scope only.** Claude reasons about the pgbtop server component: PostgreSQL system table queries, WebSocket message design, TLS, token authentication, polling strategy, and connection handling. The React dashboard and TUI client are out of scope.
- **No deployment opinions.** Discussion is bounded to local development and the SSH tunnel access pattern. CI/CD, containerisation, and packaging are excluded.

These rules are defined in [CLAUDE.md](../CLAUDE.md) at the project root.
