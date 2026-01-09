# STP Specification (Draft v0.4)

## 1. Overview

STP (State Transfer Protocol) is an HTTP-based protocol for streaming ordered rows representing changes to a table.

An STP server exposes a table via HTTP GET. Clients poll or stream the table using `since_id` and apply each row in `SeqNo` order.

STP is designed for control-plane coordination, routing, durable changefeeds, and cross-organization state synchronization.

### Terminology

- **SURL (State URL):** an STP table URL that serves rows via HTTP GET.
- **NURL (Notify URL):** an HTTP endpoint that accepts STP Notify POSTs.

---

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

### 2.2 Ordering + idempotency

- Servers SHOULD return rows in **strictly increasing SeqNo order** for any response.
- Clients MUST handle duplicate rows (same SeqNo) idempotently.

---

## 3. Content-Type

STP responses MUST include:

```
Content-Type: text/sequence; charset=utf-8; schema=<schema_id>; version=<n>
```

Servers MAY also include:

```
STP-Last-SeqNo: <n>
```

---

## 4. GET Semantics

### 4.1 Delta sync

- `since_id=N` returns rows with `SeqNo > N`
- `since_id=-N` returns the last `N` rows
- if absent, treat as `since_id=0`

### 4.2 Long-poll (streaming)

Servers SHOULD stream rows until timeout or idle, then close.  
Clients reconnect using last processed SeqNo.

---

## 5. Notify

STP includes a simple mechanism for announcing new or updated state streams.

Participants MAY expose **Notify URLs (NURLs)** that peers can POST to in order to announce a new or updated **State URL (SURL)**.

### 5.1 Request

```
POST <nurl>
Content-Type: application/x-www-form-urlencoded

surl=<STP_State_URL>&<event_type>=<NURL>&...
```

- `surl` MUST be present exactly once and MUST be a valid STP State URL.
- Additional parameters MAY be included to advertise event-specific callback NURLs.
  - Each key is an `event_type` token matching: `[a-z][a-z0-9_]*`
  - Each value MUST be a NURL.
- Unknown parameters MUST be ignored.
- Notify POSTs are advisory and idempotent; recipients MUST GET `surl` as the authoritative source of state.

### 5.2 Examples

**Minimal notify:**

```
surl=https://example.com/table
```

**Notify + callback surfaces:**

```
surl=https://example.com/table&manifest_notify=https://example.com/notify&grant_notify=https://example.com/grant_notify
```

---

## 6. Deletion + Auditability

STP is compatible with full audit logs:

- Servers SHOULD retain historical SeqNo rows for replay.
- Clients MAY request `since_id=-N` for tailing.
- Implementations that compact history SHOULD document retention policy.

Optional parameters like `view=active` (omitting keys whose latest row is `-`) are allowed by schema conventions but are not required by STP core.
