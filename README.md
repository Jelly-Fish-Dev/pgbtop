# pgbtop

A btop-style live terminal and web monitor for PostgreSQL.

## Overview

pgbtop streams real-time data from PostgreSQL system tables to connected clients over WebSocket. It is designed to run on the database host and be accessed remotely via SSH tunnel.

```
pgbtop-server  ──wss://──►  client-tui   (Python + Textual, terminal UI)
                       └──►  client-web   (React dashboard)
```

## Components

| Directory | Description |
|---|---|
| `pgbtop-server/` | Node.js WebSocket server — polls PostgreSQL and broadcasts JSON to clients |
| `pgbtop-client/` | Python + Textual TUI client |
| `client-web/` | React web dashboard |

## What it monitors

- **Active queries** — live sessions from `pg_stat_activity`
- **Slow queries** — aggregated history from `pg_stat_statements`
- **Locks** — blocking detection from `pg_locks`

## Architecture

The server runs on the machine hosting PostgreSQL. It connects to the database via the `pg` library, polls system tables on a configurable interval, and pushes JSON updates to all connected WebSocket clients.

Clients authenticate with a shared token passed at connection time. TLS is used for the WebSocket transport; for local development, [mkcert](https://github.com/FiloSottile/mkcert) or a self-signed cert is used. In production, the recommended pattern is an SSH tunnel — no public port exposure required.

## Access pattern

```
your machine  ──SSH tunnel──►  database host  ──localhost──►  pgbtop-server
```

The server binds to `localhost` by default. Forward the port over SSH:

```
ssh -L 4242:localhost:4242 user@db-host
```

Then connect your client to `wss://localhost:4242`.

## Configuration

The server is configured via environment variables (or a `.env` file). See `pgbtop-server/.env.example` for the full list. Required values:

| Variable | Description |
|---|---|
| `PGBTOP_TOKEN` | Shared secret — clients must present this to connect |
| `DATABASE_URL` | PostgreSQL connection string |
| `PGBTOP_PORT` | Port to bind the WebSocket server (default: `4242`) |

## Status

Early development. Architecture and message schema are being designed.
