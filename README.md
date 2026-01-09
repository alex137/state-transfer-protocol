# State Transfer Protocol (STP)

**State Transfer Protocol (STP)** is a tiny HTTP convention for synchronizing changing **state** as an append-only change log — with **gap recovery**, **idempotency**, and **auditable ordering** via a monotonic sequence number.

STP is to state synchronization what HTTP is to hypertext: a simple, universal substrate for linking and transferring state.  
It is designed to replace bespoke “poll JSON until it changes” patterns with a *minimal*, *standardizable* primitive that is easy to implement, cache, and reason about — especially across **independent systems** that do not share infrastructure.

---

## Quick example (wire format)

```http
GET /table?since_id=42
Accept: text/sequence; schema=endpoint_manifest; version=1
```

```text
Content-Type: text/sequence; charset=utf-8; schema=endpoint_manifest; version=1

43	2026-01-08T00:00:00Z	+	fhir_read	https://prov.com/fhir/read
44	2026-01-08T00:00:01Z	+	direct_message	https://prov.com/direct
```

Row format:

```
[SeqNo] \t [RFC3339 UTC Timestamp] \t [+/-] \t [Primary Key] \t [Record]
```

- `SeqNo` is the authoritative ordering (timestamps are informational)
- `+` add/replace, `-` delete
- Clients MUST tolerate duplicates and process rows idempotently

---

## Why STP exists

Many systems need to share or synchronize **changing state** (tables, mappings, approval lists, subscriptions, routing entries, manifests, etc.) without:

- building a bespoke “delta sync” API for every endpoint,
- transferring full datasets repeatedly,
- relying on a shared broker, queue, or database,
- losing updates during outages,
- or sacrificing auditability and replay.

**STP defines a tiny, inspectable, cacheable convention for doing this over HTTP.**

It represents state as an **append-only change log** with monotonic sequence numbers, enabling:
- **delta sync** (`since_id`)
- **gap recovery** (replay from last seen SeqNo)
- **idempotent processing**
- **auditable ordering**

---

## Why STP includes Notify (NURLs)

In real systems, “poll until it changes” isn’t enough.  
You also need a way to **bootstrap relationships** and **signal updates** across distributed components.

Historically, webhooks and JSON polling exist largely because HTTP itself has no built‑in “notify” primitive.  
STP fills that missing gap by treating **events as advisory notifications about state change**, and making **state streams the authoritative source of truth**.

STP therefore includes a simple **Notify mechanism**, where a peer can POST:

- an optional **State URL (SURL)** you should follow, and/or
- one or more **Notify URLs (NURLs)** you can call back later (often with different roles / event types).

This pattern appears everywhere:

- **bootstrap:** “here’s how to notify me back” (handshake)
- **fan-out:** “follow this SURL; notify me if you decide to follow it”
- **subscriptions:** “notify this NURL when you publish new rows”
- **relationship establishment:** manifest exchange, trust negotiation, capability discovery
- **changefeed graphs:** tables that point to other tables, forming distributed routing networks

Because STP supports **multiple NURLs**, participants can expose different callback surfaces for different event types (e.g., `match=`, `manifest_nurl=`, `grant=`) without inventing new protocols.

**Result:** large distributed systems can be built from simple HTTP primitives:  
durable state streams (**SURLs**) + lightweight notification surfaces (**NURLs**).

---

## STP vs JSON polling, webhooks, and Kafka (one block)

**JSON polling** repeatedly re-fetches large objects and tends to reinvent ad-hoc “since” logic.  
**Webhooks** fire events but often lack replay/gap recovery, so receivers must build deduplication + backfill anyway.  
**Kafka / message buses** provide excellent high-throughput event streaming inside a single organization, but require shared broker infrastructure and coordinated operations.

**STP** is a minimal protocol primitive for **auditable incremental state transfer over HTTP across independent systems**:

- Pull-based replay (`since_id`) and gap recovery
- Idempotent by design (duplicates OK)
- Cacheable, inspectable, CDN-friendly
- No shared infrastructure required
- Works on the public internet

In practice: you can use Kafka internally and expose STP externally, or export Kafka topics into STP tables.

---

## Specification (at a glance)

### GET (stream rows)

```
GET <surl>?since_id=N
```

Responses return TSV rows with:
- strictly increasing `SeqNo` per stream
- optional long-poll / streaming until timeout or idle

**Required response header:**

```
Content-Type: text/sequence; charset=utf-8; schema=<schema_id>; version=<n>
```

### Delta sync

- `?since_id=N` → rows with `SeqNo > N`
- `?since_id=-N` → last `N` rows (tail)

If absent, treat as `since_id=0`.

### Long-poll / streaming (recommended)

Servers SHOULD stream rows until timeout (or idle), then close; clients reconnect using last seen `SeqNo`.

### Notify (optional mechanism)

Participants MAY expose **Notify URLs (NURLs)** that peers can POST to in order to:
- announce a **new or updated State URL (SURL)** the recipient should GET, and/or
- advertise callback **NURLs** for event-specific notifications or handshakes.

```http
POST <nurl>
Content-Type: application/x-www-form-urlencoded

surl=<SURL>&<event_type>=<NURL>&...
```

- `surl` is optional. If present, it MUST appear exactly once and MUST be a valid STP SURL.
- Additional parameters MAY be included to advertise event-specific NURLs.
- Unknown parameters MUST be ignored.
- Notify POSTs are advisory and idempotent; recipients MUST GET `surl` as the authoritative source of state (when provided).

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
