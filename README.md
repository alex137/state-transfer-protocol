# State Transfer Protocol (STP)

**State Transfer Protocol (STP)** is a tiny HTTP convention for synchronizing changing **state** as an append-only change log — with **gap recovery**, **idempotency**, and **auditable ordering** via a monotonic sequence number.

STP is to state synchronization what HTTP is to hypertext: a simple, universal substrate for **linking and transferring state** across independent systems.

It is designed to replace bespoke “poll JSON until it changes” patterns and ad‑hoc webhooks with a *minimal*, *standardizable* primitive that is easy to implement, cache, and reason about — especially when participants do **not** share infrastructure.

---

## Quick example (wire format)

```http
GET /table?since_id=42
Accept: text/sequence; charset=utf-8; schema=endpoint_manifest; version=1
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

## STP vs JSON polling, webhooks, and Kafka

These patterns exist because **HTTP has no built‑in state‑notify primitive** — so systems invented their own.

### JSON polling
- often forces full-state downloads or bespoke “since” APIs
- expensive and ambiguous
- easy to lose updates during outages
- hard to audit (no canonical ordering)

### Webhooks
- “event-only” notifications without a durable authoritative log
- brittle under retries, failures, and race conditions
- requires bespoke signing, replay protection, and idempotency logic

### Kafka / message buses
- great for high-throughput streams inside one organization
- assumes shared broker infrastructure and coordinated ops
- not designed as a universal cross-org protocol

**STP provides a better common primitive:** durable state streams + lightweight advisory notifications, all over HTTP.

---

## STP includes Notify: SURLs + NURLs

STP defines two concepts:

- **SURL (State URL):** a URL that serves STP rows via HTTP GET.
- **NURL (Notify URL):** an HTTP endpoint that accepts STP Notify POSTs.

In real systems, polling alone isn’t enough. You also need a way to:

- bootstrap relationships (“follow this table”),
- signal updates (“something changed; re-GET”),
- and advertise callback endpoints for later use.

STP therefore includes a simple **Notify mechanism**: peers POST a `surl=...` and may include one or more event-specific callback NURLs.

This pattern appears everywhere:

- **bootstrap:** “follow this SURL, and here’s how to notify me back”
- **fan-out:** “here’s my table; notify me if you decide to follow it”
- **subscriptions:** “notify this endpoint when you publish new rows”
- **relationship establishment:** manifests, trust negotiation, capability discovery
- **changefeed graphs:** tables pointing to tables, forming distributed routing networks

Because Notify supports **multiple event keys**, systems can expose distinct callback surfaces (e.g. `manifest_notify=`, `grant_notify=`) without inventing new protocols.

**Result:** large distributed systems can be built from simple HTTP primitives:
durable state streams (**SURLs**) + lightweight notification surfaces (**NURLs**).

---

## Specification (at a glance)

### GET (stream rows)

```
GET <surl>?since_id=N
```

Responses return TSV rows with:
- strictly increasing `SeqNo` per response
- optional long-poll / streaming until timeout or idle

**Required response header:**

```
Content-Type: text/sequence; charset=utf-8; schema=<schema_id>; version=<n>
```

### Delta sync

- `?since_id=N` → rows with `SeqNo > N`
- `?since_id=-N` → last `N` rows (tail)

If absent, treat as `since_id=0`.

### Long‑poll / streaming (recommended)

Servers SHOULD stream rows until timeout (or idle), then close; clients reconnect using last seen `SeqNo`.

### Notify

Participants MAY expose **Notify URLs (NURLs)** that peers can POST to announce a new or updated **State URL (SURL)**.

```http
POST <nurl>
Content-Type: application/x-www-form-urlencoded

surl=<STP_State_URL>&<event_type>=<NURL>&...
```

- `surl` MUST be present exactly once and MUST be a valid STP State URL.
- Additional parameters MAY advertise event-specific callback NURLs.
  - Each key is an `event_type` token matching: `[a-z][a-z0-9_]*`
  - Each value MUST be a NURL.
- Unknown parameters MUST be ignored.
- Notify POSTs are advisory and idempotent; recipients MUST GET `surl` as the authoritative source of state.

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
