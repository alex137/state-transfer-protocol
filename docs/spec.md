# STP Core Specification (Draft)

## 1. Overview

STP defines a simple convention for exposing and consuming **incremental state changes** over HTTP.

It consists of:
- a TSV row format with a monotonic `SeqNo`
- delta sync via `since_id`
- optional streaming / long-poll
- an optional notify POST to prompt refresh

## 2. Row format

TSV rows:

```
[SeqNo] \t [RFC3339 UTC Timestamp] \t [+/-] \t [Primary Key] \t [Record]
```

- `SeqNo` MUST be monotonic per stream.
- Servers MUST return rows in increasing `SeqNo` order within a response.
- Clients MUST tolerate duplicate rows (same `SeqNo`) and process idempotently.

## 3. HTTP GET

```
GET <table_url>?since_id=N
```

### Query parameter: since_id
- `since_id=N` → return rows where `SeqNo > N`
- `since_id=-N` → return last `N` rows
- if absent, treat as `since_id=0`

### Response headers
Servers MUST set:

```
Content-Type: application/stp+tsv; schema=<schema_id>; version=<n>
```

## 4. Long-poll / streaming
Servers SHOULD stream rows until timeout or idle, then close.
Clients reconnect using last seen `SeqNo`.

## 5. Notify

Participants MAY expose notify URLs that peers can POST to when:
- a new table should be monitored, or
- an existing table has new rows

```
POST <notify_url>
Content-Type: application/x-www-form-urlencoded

table=<STP_Table_URL>
```

- `table` MUST be a valid STP table URL
- notify is idempotent and may be repeated
- notify carries no data; recipients GET the table URL
