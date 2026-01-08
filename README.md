# State Transfer Protocol (STP)

**State Transfer Protocol (STP)** is a tiny HTTP convention for streaming and synchronizing changing state as an append-only change log — with **gap recovery**, **idempotency**, and **auditable ordering** via a monotonic sequence number.

It is designed to replace bespoke “poll JSON until it changes” patterns with a *minimal*, *standardizable* primitive that is easy to implement, cache, and reason about.

---

## Quick example (wire format)

```http
GET /table?since_id=42
Accept: application/stp+tsv; schema=endpoint_manifest; version=1
```

```text
Content-Type: application/stp+tsv; schema=endpoint_manifest; version=1

43\t2026-01-08T00:00:00Z\t+\tfhir_read\thttps://prov.com/fhir/read
44\t2026-01-08T00:00:01Z\t+\tdirect_message\thttps://prov.com/direct
```

Row format:

```
[SeqNo] \t [RFC3339 UTC Timestamp] \t [+/-] \t [Primary Key] \t [Record]
```

- `SeqNo` is the authoritative ordering (timestamps are informational)
- `+` add/replace, `-` delete
- Clients MUST tolerate duplicates and process rows idempotently

---

## Why STP (vs JSON polling)

**JSON polling is expensive and ambiguous:**
- forces full-state downloads or ad‑hoc “since” logic
- hard to audit (no canonical ordering)
- easy to lose updates during outages
- encourages per-API bespoke schemas and libraries

**STP is minimal but complete:**
- **Incremental replication:** `since_id=N` yields only new rows
- **Auditable change log:** monotonic `SeqNo` provides integrity and replay
- **Gap recovery:** reconnect with last seen `SeqNo`
- **Idempotent by design:** duplicates are harmless
- **Composable:** works with long-poll, caches, CDNs, or any transport layer
- **Easy to implement:** can be served by any web server + datastore

---

## STP is not a message bus

STP is not Kafka, NATS, or a pub/sub system.  
It is a minimal convention for exposing **change streams over HTTP**, with durable ordering and gap recovery.  
It composes with any distribution layer (CDN, long‑poll, notify POST, queues).

---

## Specification (at a glance)

### GET (stream rows)

```
GET <table_url>?since_id=N
```

Responses return TSV rows with:
- strictly increasing `SeqNo` per stream
- optional long‑poll/streaming until timeout or idle

**Required response header:**

```
Content-Type: application/stp+tsv; schema=<schema_id>; version=<n>
```

### Delta sync

- `?since_id=N` → rows with `SeqNo > N`
- `?since_id=-N` → last `N` rows (tail)

If absent, treat as `since_id=0`.

### Long‑poll / streaming (recommended)

Servers SHOULD stream rows until timeout (or idle), then close; clients reconnect using last seen `SeqNo`.

### Notify (optional mechanism)

Participants MAY expose **notify URLs** that peers can POST to in order to:
- announce a **new table** the recipient should begin monitoring, or
- signal that an existing table **has new rows**

```
POST <notify_url>
Content-Type: application/x-www-form-urlencoded

table=<STP_Table_URL>
```

Notify POSTs may be sent repeatedly and must be treated as idempotent.

---

## Docs

- **Implementer Quickstart:** `docs/quickstart.md`
- **STP Core Spec:** `docs/spec.md`
- **Schemas:** `schemas/`

---

## Contributing

PRs welcome. Suggested areas:
- reference implementations (Go, Python, JS)
- schema registry conventions
- test vectors + interop harness

---

## License

MIT (see `LICENSE`).
