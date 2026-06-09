# Local PostgreSQL Test Setup

How to spin up a realistic PostgreSQL environment for testing pgbtop during development — covering database setup, load generation, lock contention, and `pg_stat_statements`.

---

## Option A — Docker (recommended for dev)

The fastest path: no system PostgreSQL install needed, fully disposable.

```
docker run --name pgbtop-test \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_USER=pgbtop \
  -e POSTGRES_DB=testdb \
  -p 5432:5432 \
  -d postgres:16
```

`DATABASE_URL` for `.env`:
```
DATABASE_URL="postgres://pgbtop:password@localhost:5432/testdb"
```

Stop and destroy cleanly when done:
```
docker stop pgbtop-test && docker rm pgbtop-test
```

---

## Option B — System PostgreSQL

If PostgreSQL is already installed locally, create a dedicated role and database:

```sql
CREATE ROLE pgbtop WITH LOGIN PASSWORD 'password';
CREATE DATABASE testdb OWNER pgbtop;
GRANT pg_monitor TO pgbtop;   -- needed to see other users' sessions in pg_stat_activity
```

`DATABASE_URL`:
```
DATABASE_URL="postgres://pgbtop:password@localhost:5432/testdb"
```

The `pg_monitor` role grant is important — without it, `pg_stat_activity` queries will only show the pgbtop user's own sessions, which makes testing the activity monitor useless.

---

## Enable `pg_stat_statements`

`pg_stat_statements` requires a one-time setup. It must be loaded at server start via `postgresql.conf`, then created as an extension per-database.

**Step 1 — add to `postgresql.conf`:**
```
shared_preload_libraries = 'pg_stat_statements'
```
Then restart PostgreSQL (Docker: `docker restart pgbtop-test`).

**Step 2 — create the extension in your test database:**
```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

**Verify it's working:**
```sql
SELECT query, calls, total_exec_time FROM pg_stat_statements LIMIT 5;
```

If this returns rows, the extension is live. If the server gets a relation-not-found error, it means the extension wasn't created or `shared_preload_libraries` wasn't set — this is exactly the degradation case the server needs to handle gracefully.

---

## Generating Activity — pgbench

`pgbench` ships with PostgreSQL and is the easiest way to produce realistic `pg_stat_activity` rows.

**Initialise the pgbench schema (run once):**
```
pgbench -h localhost -U pgbtop -d testdb -i -s 10
```
`-s 10` sets scale factor — 10 gives ~1 M rows in `pgbench_accounts`, enough for queries to take a visible amount of time.

**Run a load test (generates live sessions):**
```
pgbench -h localhost -U pgbtop -d testdb -c 10 -j 2 -T 60
```
- `-c 10` — 10 concurrent clients (shows up as 10 rows in `pg_stat_activity`)
- `-j 2` — 2 worker threads
- `-T 60` — run for 60 seconds

While this is running, `pg_stat_activity` will have live `active` and `idle in transaction` rows to read.

---

## Generating Lock Contention

To test the locks monitor, you need two sessions that block each other. Open two `psql` sessions:

**Session 1 — hold a row lock:**
```sql
BEGIN;
UPDATE pgbench_accounts SET abalance = abalance + 1 WHERE aid = 1;
-- do not COMMIT yet
```

**Session 2 — try to update the same row:**
```sql
UPDATE pgbench_accounts SET abalance = abalance - 1 WHERE aid = 1;
-- this will hang, waiting on session 1's lock
```

Now `pg_locks` joined to `pg_stat_activity` will show a blocking/waiting pair — exactly what the locks query should detect. COMMIT session 1 to release the lock.

---

## Pagila (optional — richer schema)

Pagila is a sample DVD rental database with a realistic schema, foreign keys, and pre-loaded data. More representative than pgbench's flat tables if you want to test slow query detection with `pg_stat_statements`.

```
git clone https://github.com/devrimgunduz/pagila.git
psql -h localhost -U pgbtop -d testdb -f pagila/pagila-schema.sql
psql -h localhost -U pgbtop -d testdb -f pagila/pagila-data.sql
```

Then run ad-hoc queries against it (joins across `film`, `inventory`, `rental`, `payment`) to populate `pg_stat_statements` with interesting entries.

---

## Verifying the Server Sees Real Data

Once `db.ts` and a query module exist, a quick sanity check before wiring the full broadcast:

1. Start the server with the `.env` in place
2. Run `pgbench` load test in the background
3. Connect a WebSocket client (the Python client, or `wscat`, or the Node snippet used during the run audit)
4. Confirm the JSON payload contains real `pg_stat_activity` rows — `pid`, `state`, `query`, `wait_event_type` — not random values

`wscat` install if needed: `npm install -g wscat`, then `wscat -c ws://localhost:4242`.

---

## Open Questions

- Should test setup instructions (Docker command, pgbench init) live in a `docs/demo.md` or the README quickstart? The README already mentions `docs/demo.md` in the proposed structure.
- Does the CI environment need a PostgreSQL service for integration tests, or is unit testing the query-building logic sufficient at this stage?
