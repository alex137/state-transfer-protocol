# STP Specification (Draft v0.3)

## 1. Overview

STP (State Transfer Protocol) is an HTTP-based protocol for streaming ordered rows
representing changes to a table. STP is designed for control-plane coordination,
routing, and durable changefeeds.

An STP server exposes a table via HTTP GET. Clients poll or stream the table using
`since_id` and apply each row in `SeqNo` order.

## 2. Row Format

Each row is a TSV line:

```
SeqNo \t Timestamp \t Action \t PrimaryKey \t Record
```

### 2.1 Fields

- **SeqNo**: integer, monotonic per table
- **Timestamp**: RFC3339 UTC timestamp (informational; not authoritative)
- **Action**: `+` add/replace, `-` delete
- **PrimaryKey**: the key the action applies to
- **Record**: free-form schema-defined string (may contain spaces; SHOULD avoid tabs)

### 2.2 Ordering

Servers SHOULD return rows in **strictly increasing SeqNo order** for any response.
Clients MUST handle duplicate rows (same SeqNo) idempotently.

## 3. Content-Type

STP responses MUST include:

```
Content-Type: text/sequence; charset=utf-8; schema=<schema_id>; version=<n>
```

Servers MAY also include:

```
STP-Last-SeqNo: <n>
```

## 4. GET Semantics

### 4.1 Delta sync

- `since_id=N` returns rows with SeqNo > N
- `since_id=-N` returns the last N rows
- if absent, treat as `since_id=0`

### 4.2 Long-poll (streaming)

Servers SHOULD stream rows until timeout or idle, then close.  
Clients reconnect using last processed SeqNo.

## 5. Notify

Participants MAY expose notify URLs that accept:

```
POST <notify_url>
Content-Type: application/x-www-form-urlencoded

table=<STP_Table_URL>
```

`table` MUST be a valid STP table URL.

Recipients track last processed SeqNo and GET with `since_id` as needed to retrieve
new rows and recover gaps. Notify POSTs may repeat and must be treated as idempotent.

## 6. Deletion + Auditability

STP is compatible with full audit logs:

- Servers SHOULD retain historical SeqNo rows for replay
- Clients MAY request `since_id=-N` for tailing
- Implementations that compact history SHOULD document retention policy

(If desired, future versions may add optional parameters for requesting compaction
views.)
