# STP — State Transfer Protocol

> **STP (State Transfer Protocol)** is a tiny, web‑native way to replicate *changing state* across systems — fast, auditable, and implementation‑friendly.

Most integrations fall into one of two bad choices:

1. **Poll JSON endpoints** and re-download full objects (wasteful, inconsistent, hard to audit), or  
2. **Build custom event streams** (complex, brittle, and hard to standardize across orgs).

STP is the missing primitive: **a simple, ordered change log for a “table” of keyed records**, delivered over plain HTTPS, with a standard delta query (`since_id=`) and an optional notification hook.

---

## The idea in one sentence

**Expose your system’s state as an append‑only, monotonically‑ordered change stream, so others can maintain an identical copy without re-fetching everything.**

- **“Table”** just means a set of **primary keys → records**.  
- The **sequence** is how you get integrity, replay, and auditability.

---

## Why STP (vs JSON polling)

### JSON polling is deceptively expensive
- You repeatedly fetch whole objects even when only a few fields changed.
- You need ad‑hoc paging, caching, and retry logic.
- You lose a reliable audit trail (what changed *when*).
- Providers often “drop” old events; consumers can’t prove completeness.

### STP gives you a standard answer
- **Deltas are first‑class** (`since_id=`).
- **Ordering is explicit** (monotonic `SeqNo`).
- **Replay is natural** (start at `since_id=0`).
- **Streaming is easy** (long‑poll GET).
- **Auditing is built in** (append‑only, ordered rows).

---

## Core model

An STP “table” is a stream of TSV rows:

```
[SeqNo] \t [RFC3339 UTC Timestamp] \t [+/-] \t [Primary Key] \t [Record]
```

- `SeqNo` is **monotonic per table** and is the authoritative ordering.
- `+` means *add/replace* a primary key.
- `-` means *delete* a primary key.
- Clients **MUST tolerate duplicate rows** (same `SeqNo`) and apply changes idempotently.

**Content-Type**

Servers SHOULD set:

```
Content-Type: application/stp+tsv; schema=<schema_id>; version=<n>
```

This makes tables self-describing (a core advantage over ad‑hoc JSON).

---

## Delta sync

- `?since_id=N` → rows with `SeqNo > N`
- `?since_id=-N` → last `N` rows
- If absent, treat as `since_id=0`.

---

## Long-poll (recommended)

Servers SHOULD hold a GET connection open and stream new rows until:
- timeout, or
- the server becomes idle / expects no near-term updates,

then close. Clients reconnect using the last seen `SeqNo`.

---

## Notify (optional mechanism)

Participants MAY expose a **notify URL** that peers can POST to in order to:
- announce a **new table** the recipient should begin monitoring, or
- signal that a table **has new rows**.

POST format:

```
POST <notify_url>
Content-Type: application/x-www-form-urlencoded

table=<STP_Table_URL>
```

Recipients track last processed `SeqNo` and GET with `since_id` to retrieve new rows and recover gaps.

Notify POSTs may be sent repeatedly and must be treated as idempotent.

---

## Minimal example

1) Client begins sync:

```
GET https://example.com/table?since_id=0
```

2) Server returns:

```
1    2026-01-08T10:00:00Z    +    alice    {"status":"ok"}
2    2026-01-08T10:02:00Z    +    bob      {"status":"warn"}
3    2026-01-08T10:03:00Z    -    bob
```

3) Client persists `SeqNo=3` and later resumes:

```
GET https://example.com/table?since_id=3
```

---

## Reference implementation draft

This repo contains:
- A concise spec (`spec/`)
- Examples (`examples/`)
- Test vectors (`test-vectors/`)
- A lightweight reference parser (`lib/`)

---

## Status

**Draft v0.x** — the goal is to keep STP extremely small, boring, and implementable.

PRs welcome: clarity > features.
