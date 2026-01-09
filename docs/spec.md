# STP Specification (Draft v0.4)

## 1. Overview

STP (State Transfer Protocol) is an HTTP-based protocol for streaming ordered rows
representing changes to a table. STP is designed for control-plane coordination,
routing, and durable changefeeds.

An STP server exposes a table via HTTP GET. Clients poll or stream the table using
`since_id` and apply each row in `SeqNo` order.

Terminology:
- **SURL** (State URL): an HTTP URL that serves STP rows via GET.
- **NURL** (Notify URL): an HTTP URL that accepts STP Notify POSTs.

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

## 5. Notify (NURLs)

Participants MAY expose Notify URLs (**NURLs**) that accept HTTP POSTs with
`Content-Type: application/x-www-form-urlencoded`.

Notify POSTs are advisory. They communicate:

- an optional **State URL (SURL)** that may have new state, and/or  
- one or more **NURLs** the sender wishes to advertise for callbacks.

### 5.1 Notify Body Format

The POST body is a form-encoded set of key/value pairs:

- `surl` is a **reserved parameter name**
- all other parameters represent advertised NURLs

Rules:

- `surl` MAY be present. If present, it MUST appear exactly once and MUST be a valid STP SURL.
- If `surl` is absent, the Notify POST is treated as **NURL advertisement / handshake** only.
- All other parameters MUST have values that are valid Notify URLs (NURLs).
- Unknown parameter names MUST be ignored.
- Notify POSTs MAY repeat and MUST be treated as idempotent.
- Recipients MUST GET `surl` (when provided) as the authoritative source of state.

Examples:

**State notification with callback:**
```
surl=https://example.com/state&match=https://example.com/match_nurl
```

**Handshake (callback advertisement only):**
```
manifest_nurl=https://example.com/manifest_nurl
```

## 6. Deletion + Auditability

STP is compatible with full audit logs:

- Servers SHOULD retain historical SeqNo rows for replay
- Clients MAY request `since_id=-N` for tailing
- Implementations that compact history SHOULD document retention policy

(If desired, future versions may add optional parameters for requesting compaction
views.)
