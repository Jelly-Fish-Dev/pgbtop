# TypeScript Server to Python Client — WebSocket Connection

How the pgbtop server and TUI client establish and maintain a connection over WebSocket.

---

## Overview

The TypeScript server owns the WebSocket listener. The Python Textual client is a consumer — it initiates the connection, authenticates, then passively receives JSON payloads on each poll tick. Neither side needs to know the other's language; the protocol is JSON over `wss://`.

---

## Details

### Connection lifecycle

```md
Python client                          TypeScript server
     |                                        |
     |------- TCP + TLS handshake ----------->|
     |                                        |  (TLS established)
     |------- WebSocket upgrade request ----->|
     |<------ 101 Switching Protocols --------|
     |                                        |  (WebSocket open)
     |------- { type: "auth", token: "..." }->|
     |                                        |  (token validated)
     |<------ { type: "activity", data: [] }--|  (first poll tick)
     |<------ { type: "locks",    data: [] }--|
     |<------ { type: "activity", data: [] }--|  (next tick, N seconds later)
     |                                        |
     |  ... steady state: server pushes,      |
     |      client renders ...                |
     |                                        |
     |        (client disconnects or          |
     |         server shuts down)             |
     |------- close frame ------------------->|
```

### TypeScript server side — what it does

1. Creates an HTTPS server using Node's built-in `https` module, loading the TLS cert and key from `certs/`
2. Passes the HTTPS server to `new WebSocketServer({ server })` from the `ws` package — the WebSocket listener rides on top of the existing HTTPS server, same port
3. On each new connection, immediately waits for the first message
4. First message must be `{ type: "auth", token: "<secret>" }` — if the token doesn't match the configured secret, the socket is closed with code 4401 and nothing further happens
5. Authenticated connections are added to a Set of active clients
6. The poller runs on a configurable interval (e.g. 2000ms). On each tick it runs the PostgreSQL queries and calls `broadcast()`, which iterates the Set and sends the payload to every open socket
7. On connection close, the socket is removed from the Set
8. On process SIGTERM/SIGINT, the server drains: stops the poller, closes all sockets cleanly, then closes the PostgreSQL pool

### Python client side — what it does

1. Textual app starts, creates an async worker on startup
2. Worker opens a WebSocket connection using the `websockets` library — passes a custom SSL context pointing at the same cert (dev) or system trust store (prod via SSH tunnel)
3. Immediately sends `{ "type": "auth", "token": os.environ["PGBTOP_TOKEN"] }`
4. Enters a receive loop — awaits each incoming message, parses JSON, posts a Textual message to the app's message queue
5. Textual widgets subscribe to those messages and update their display
6. If the connection drops, the worker catches the exception and schedules a reconnect after a backoff delay

### Message schema

Each server-to-client payload follows the same envelope:

```
{
  "type": "<string>",   // identifies the data source
  "ts":   <epoch ms>,   // server timestamp of the poll
  "data": [ ...rows ]   // array of row objects
}
```

Known types for this project:

| type         | source table                    | key fields                                    |
| --------------| ---------------------------------| -----------------------------------------------|
| `activity`   | `pg_stat_activity`              | pid, query, state, duration, wait_event       |
| `statements` | `pg_stat_statements`            | query, calls, mean_exec_time, total_exec_time |
| `locks`      | `pg_locks` + `pg_stat_activity` | pid, relation, mode, granted, blocking_pid    |

The server sends one message per type per tick. The client doesn't need to request anything — it just receives.

### TLS in development

Both sides must trust the same certificate.

- Server loads `certs/cert.pem` and `certs/key.pem` — generated with mkcert or openssl
- Python client creates an `ssl.SSLContext`, calls `context.load_verify_locations("certs/cert.pem")`, and passes the context to `websockets.connect()`
- In production via SSH tunnel, the connection is `ws://localhost:<forwarded-port>` with no TLS needed — TLS is provided by the SSH tunnel itself, so the SSL context is omitted

### Auth token flow

- Server reads the token from `PGBTOP_TOKEN` env var on startup. If the var is missing, it refuses to start.
- Client reads the same env var and sends it as the first message after the WebSocket handshake completes
- The server does not send any data before auth is confirmed — the client sits in silence until the auth message is sent, then immediately receives the first poll tick

### What happens on disconnect

| Scenario | Server behaviour | Client behaviour |
|---|---|---|
| Client closes tab / kills process | Socket emits `close` event, removed from Set | N/A |
| Server restarts | All sockets receive close frame | Worker catches disconnect, waits backoff, reconnects |
| PostgreSQL goes away | Poller catches error, logs it, skips that tick | Client sees stale data (last received payload stays on screen) |
| Network blip | WebSocket close event fires on both sides | Client reconnects after backoff |

---

## Open Questions

- [ ] What is the poll interval? 2s feels right for a live monitor without hammering the database — but should it be configurable per client or fixed server-side?
- [ ] Should the server send a `{ type: "error", message: "..." }` payload when a query fails, so the client can display a status indicator rather than silently showing stale data?
- [ ] Should the auth token be sent as a WebSocket subprotocol header instead of the first message? More standard, but more complex on the Python side.

---

## Decision / Outcome

No decisions recorded yet.

---

## AI Disclosure

This note was produced with Claude (claude-sonnet-4-6) acting as a design and architecture assistant for the pgbtop project. The following rules govern how Claude contributes to this project:

- **No code generation.** Claude does not write, scaffold, or produce any executable or deployable code — including snippets, config files, or boilerplate. All notes are discussion and reasoning only.
- **Notes only.** All Claude output is written as Markdown into the `notes/` folder. Nothing is written outside this directory.
- **Server scope only.** Claude reasons about the pgbtop server component: PostgreSQL system table queries, WebSocket message design, TLS, token authentication, polling strategy, and connection handling. The React dashboard and TUI client are out of scope.
- **No deployment opinions.** Discussion is bounded to local development and the SSH tunnel access pattern. CI/CD, containerisation, and packaging are excluded.

These rules are defined in [CLAUDE.md](../CLAUDE.md) at the project root.
