# June 12 Sprint Plan

Four-day plan to reach a functional v1 by June 12. One medium session per day.

**Scope cut for this sprint:** TLS and client decomposition are deferred — they don't affect core functionality and can follow v1. Everything else ships.

---

## Day 1 — June 9 ✅

**Done:**
- `pg` + `@types/pg` installed
- `src/db.ts` — Pool + `verifyConnection()`
- `src/config.ts` — all db vars, token, port
- `package.json` — `build` + `start` scripts; ESLint config fixed (`dist/` ignored, `eslint.config.mjs`)
- `src/index.ts` — calls `verifyConnection()` on startup
- `npm run start` → "Listening on ws://localhost:4242" + "Connected" ✓

**Carried to Day 2:**

- Fix `.env.example` — still shows `DATABASE_URL` format; update to individual vars
- Add startup validation to `config.ts` — fail fast if any required var is missing

---

## Day 2 — June 10 — First Real Data

**Goal:** Replace synthetic random payload with live `pg_stat_activity` rows.

- Create `src/queries/activity.ts` — query `pg_stat_activity`, return typed rows (pid, state, query, wait_event_type, application_name, duration)
- Call it from `ws-server.ts` inside the poll interval — replace the `Math.random()` payload
- Recompile and connect the Python client — confirm real rows appear in the terminal output
- Fix the three Python client bugs: `call_from_thread`, `data_received` typo, remove dead `update()` method

**Done when:** Running `pgbench` against the test DB produces visible activity rows in the client output.

---

## Day 3 — June 11 — Auth + Remaining Queries

**Goal:** Secure the connection and fill out the data model.

- Implement token auth in `ws-server.ts` — check `PGBTOP_TOKEN` on the WebSocket upgrade request; reject unauthenticated connections with close code `4401`
- Wire token into the Python client's `websockets.connect()` call (pass as a query-string param or `Authorization` header)
- Create `src/queries/statements.ts` — query `pg_stat_statements`; catch the "relation does not exist" error and return an empty result rather than crashing
- Create `src/queries/locks.ts` — join `pg_locks` to `pg_stat_activity` to surface blocking pairs
- Add all three query types to the broadcast payload
- Add reconnection logic to the Python client WebSocket worker (retry with exponential backoff on disconnect)

**Done when:** Client connects only with the correct token; all three data types appear in the payload; client recovers from a server restart.

---

## Day 4 — June 12 — Ship

**Goal:** Production-ready enough to call v1.

- Handle `SIGTERM`/`SIGINT` in `src/index.ts` — drain the poll loop, close the WebSocket server, end the `pg` pool, exit cleanly
- Add client `.env.example` documenting `PGBTOP_TOKEN`, `PGBTOP_HOST`, `PGBTOP_PORT`
- Write README quickstart: generate test DB, set env vars, `npm run build && npm run start`, run Python client
- Resolve open question: token via `.env` only (close it — yes, env only for now)
- Resolve open question: `pg_stat_statements` absent — close it as silent empty result (already handled in Day 3)
- Final end-to-end smoke test: server + client + pgbench load + lock contention

**Done when:** A new contributor can follow the README from scratch and see live PostgreSQL data in the terminal.

---

## Deferred (post-June 12)

- TLS (`tls.ts`, mkcert setup, wss:// wiring)
- `poller.ts` abstraction (decouple data layer from ws-server)
- Full client decomposition (`app.py`, `connection.py`, `messages.py`, widget files)
- Message schema design note
