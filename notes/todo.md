# Todo — pgbtop Implementation Checklist

Outstanding work to get from the current scaffold to a functional v1.

---

## Already Done

- [x] Repository structure (`pgbtop-server/`, `pgbtop-client/`, `notes/`)
- [x] `.gitignore` — covers `dist/`, `certs/`, `node_modules/`, `.venv/`, `.env`, OS/editor noise
- [x] `README.md` — architecture overview, access pattern (SSH tunnel), config table, component table
- [x] `tsconfig.json` — strict mode, `commonjs` output, `es2022` target, source maps, declarations
- [x] `package.json` — `ws` + `@types/ws` + TypeScript toolchain; ESLint + Prettier configured
- [x] `src/config.ts` — env-var config skeleton (PORT only so far)
- [x] `src/ws-server.ts` — WebSocket server starts, tracks connected clients, broadcasts every 2 s, handles client disconnect
- [x] `src/index.ts` — entry point calls `startServer()`
- [x] Server compiles cleanly with `tsc` and runs via `node dist/index.js`
- [x] `requirements.txt` — all Python deps pinned (textual, websockets, textual-plot, numpy, etc.)
- [x] `.venv` set up and functional
- [x] `pgbtop-client/src/main.py` — Textual app skeleton: `PlotWidget` composed, WebSocket worker started on mount, JSON parsed, plot buffer populated and rendered

---

## Outstanding

### Server — Foundation

- [ ] **Correction needed:** README documents port `4242` but `config.ts` defaults to `8080` — align them
- [ ] Add `pg` to `dependencies` in `package.json`
- [ ] Create `src/db.ts` — `pg` client setup, connection lifecycle, and reconnect handling for lost PostgreSQL connections
- [ ] Expand `src/config.ts` — add `DATABASE_URL`, `PGBTOP_TOKEN`, `PGBTOP_PORT`; validate required vars on startup and fail fast with a clear error message
- [ ] Add `.env.example` to `pgbtop-server/` documenting `DATABASE_URL`, `PGBTOP_TOKEN`, `PGBTOP_PORT` (README already references this file but it doesn't exist yet)
- [ ] Add `build` and `start` scripts to `package.json` (`tsc` + `node dist/index.js`)

### Server — Queries

- [ ] Create `src/queries/activity.ts` — query `pg_stat_activity`; decide columns and filters (exclude idle, exclude own backend)
- [ ] Create `src/queries/statements.ts` — query `pg_stat_statements`; degrade gracefully if the extension is not installed
- [ ] Create `src/queries/locks.ts` — query `pg_locks` joined to `pg_stat_activity` for blocking detection

### Server — Polling & Message Schema

- [ ] Create `src/poller.ts` — polling loop on configurable interval; emit results via `EventEmitter`, no direct knowledge of WebSocket clients
- [ ] Refactor `src/ws-server.ts` — subscribe to poller events; remove the synthetic random-data placeholder
- [ ] Define and document the WebSocket message schema (JSON shape, field names, type discriminants) — see `notes/` for the design discussion

### Server — Authentication

- [ ] Implement token auth in `src/ws-server.ts` — verify `PGBTOP_TOKEN` on the connection upgrade request (header or query-string); reject with close code `4401` if missing or invalid

### Server — TLS

- [ ] Create `src/tls.ts` — load cert and key from `pgbtop-server/certs/`; document mkcert setup in README
- [ ] Wire TLS into the WebSocket server; keep plain `ws://` available via a flag for dev without certs

### Server — Shutdown

- [ ] Handle `SIGTERM`/`SIGINT` in `src/index.ts` — stop the poll loop, close the WebSocket server, end the `pg` client, then exit

### Client

- [ ] **Bug:** UI updates are called directly from the WebSocket worker thread — must go through `self.call_from_thread(...)` or a Textual custom `Message` to be thread-safe; this will crash under real load
- [ ] **Typo:** `data_recived` → `data_received`
- [ ] **Dead code:** `update()` method just calls `print(data)` and is never invoked — remove or wire up properly
- [ ] Add reconnection logic to the WebSocket worker (retry with backoff on disconnect)
- [ ] Wire auth token into the `websockets.connect()` call once server auth is in place
- [ ] Decompose `main.py` into the module structure from `notes/project-structure.md`: `app.py`, `connection.py`, `messages.py`, `widgets/activity.py`, `widgets/locks.py`, `widgets/statements.py`
- [ ] Add `.env.example` to `pgbtop-client/` documenting `PGBTOP_TOKEN`, `PGBTOP_HOST`, `PGBTOP_PORT`

### Shared / Housekeeping

- [ ] Resolve open question: shared token via `.env` only, or also support a flat config file?
- [ ] Resolve open question: graceful degradation when `pg_stat_statements` is not installed — silently omit the panel, or show an explicit "extension unavailable" state?
- [ ] README quickstart section — step-by-step: generate certs, set env vars, run server, run client

---

## Suggested Path

The goal of this sequence is to get a real end-to-end data flow — actual PostgreSQL rows visible in the client — as early as possible, then harden around it.

**1. Fix the port discrepancy**
Trivial but blocks everything else from matching the docs. Pick `4242` (what README says) and update `config.ts`.

**2. Server foundation — `pg` + `db.ts` + config expansion**
Add the `pg` package and write `db.ts`. Expand `config.ts` to read `DATABASE_URL` and fail fast. This is the prerequisite for any real query work. Add `.env.example` at the same time.

**3. First real query — `pg_stat_activity` only**
Write `queries/activity.ts` and call it directly from `ws-server.ts` (inline, before poller abstraction). Replace the random-data payload with real rows. This proves the full data path works — PostgreSQL → Node → WebSocket — without the complexity of the poller architecture.

**4. Fix the client thread-safety bug**
Before investing more in the client, fix the `call_from_thread` issue and the `data_received` typo so the client doesn't crash. This keeps the client viable as a test harness while the server evolves.

**5. Add token auth**
Short, self-contained. Once in place both ends are secured and the auth wiring in the client can be done. Add client `.env.example` at the same time.

**6. Poller abstraction**
Introduce `poller.ts` with `EventEmitter`. Move the query calls there and have `ws-server.ts` subscribe. This decouples the data layer from transport and makes it straightforward to add the remaining queries.

**7. Remaining queries — `pg_stat_statements` + `pg_locks`**
Add the other two query modules. Handle the `pg_stat_statements` extension-absent case.

**8. Client decomposition**
Split `main.py` into `app.py`, `connection.py`, `messages.py`, and the three widget files. Replace the single `PlotWidget` with the real activity/locks/statements widgets. Add reconnection logic.

**9. TLS**
Add `tls.ts` and wire it in. Document `mkcert` setup in README. Keep plain `ws://` available via env flag for dev.

**10. Shutdown handling**
`SIGTERM`/`SIGINT` handler in `index.ts`. Low risk, worth doing before any real-world use.

**11. README quickstart + housekeeping**
Fill in the quickstart section, resolve the open config-file question, and close out any remaining open questions from `notes/project-structure.md`.

---

## Current State (as of 2026-06-09)

The WebSocket plumbing is end-to-end functional: the server starts, broadcasts a JSON message every 2 s, and the Python client connects, parses the payload, and feeds the plot buffer. No PostgreSQL queries exist yet — the data stream is entirely synthetic random values. Port mismatch between README (`4242`) and server default (`8080`).
