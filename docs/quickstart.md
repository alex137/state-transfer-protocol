# Implementer Quickstart

This quickstart shows how to implement STP servers and clients with the minimum required behavior.

## 1) Implement an STP Server

### Data model (minimum)
Your server needs a persistent append-only log per table:

- `SeqNo` (monotonic int)
- `timestamp` (RFC3339 UTC)
- `op` (`+` or `-`)
- `primary_key` (string)
- `record` (string)

### GET endpoint
Implement:

```
GET /table?since_id=N
```

Behavior:
- Return rows with `SeqNo > N`, in increasing `SeqNo` order
- Support `since_id=-N` to return the last N rows (tail)
- Set the response header:

```
Content-Type: application/stp+tsv; schema=<schema_id>; version=<n>
```

### Optional streaming / long-poll
Servers SHOULD:
- stream new rows as they arrive until timeout or idle
- then close the connection
Clients reconnect with last seen `SeqNo`.

---

## 2) Implement an STP Client

Minimum client behavior:
- Track `last_seen_seqno` per table
- Fetch:

```
GET <table_url>?since_id=<last_seen_seqno>
```

- Parse each row; ignore duplicates (same SeqNo)
- Apply operations to local state:
  - `+` replaces value for Primary Key
  - `-` deletes Primary Key
- Persist `last_seen_seqno` after processing rows

### Gap recovery
If you suspect missed rows (timeout, error, network):
- Re-GET using your last durable `SeqNo`
- Server will resend from there; duplicates are fine

---

## 3) Implement Notify (optional)

If you want push-like behavior without websockets:
- Expose a notify endpoint:

```
POST /notify
Content-Type: application/x-www-form-urlencoded
Body: table=<STP_Table_URL>
```

Semantics:
- Notify contains no data
- It is a hint to GET the table URL
- Notify may be repeated and must be handled idempotently

---

## Common pitfalls

- **Do not require timestamps** for ordering; `SeqNo` is authoritative
- **Always allow duplicates** and process idempotently
- **Never treat outages as deletions**: missing tables are not `-` operations
- **Prefer small rows**: large payloads belong behind URLs, not in the changefeed
