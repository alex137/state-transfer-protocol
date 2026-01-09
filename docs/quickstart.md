# STP Implementer Quickstart

This guide shows the minimal pieces required to serve and follow STP streams.

## 1) Serve a State URL (SURL)

Expose a table as an append-only TSV change log.

```http
GET /my_table?since_id=0
Accept: text/sequence; charset=utf-8; schema=my_schema; version=1
```

Response:

```text
Content-Type: text/sequence; charset=utf-8; schema=my_schema; version=1

1\t2026-01-01T00:00:00Z\t+\tkey1\tvalue1
2\t2026-01-01T00:00:01Z\t+\tkey2\tvalue2
```

Clients track the last processed `SeqNo` and reconnect with `since_id=<last_seqno>`.

## 2) Follow a SURL (client)

1. Initialize `last_seqno = 0`
2. `GET <surl>?since_id=last_seqno`
3. Apply each row in order (idempotently)
4. Update `last_seqno` as you process rows
5. Repeat (or hold open as a long-poll stream)

Clients MUST tolerate duplicate rows and process them idempotently.

## 3) Notify (optional but recommended)

Peers may expose **Notify URLs (NURLs)**.  
Notify is **advisory**: recipients MUST GET the SURL as the authoritative source of state.

```http
POST <nurl>
Content-Type: application/x-www-form-urlencoded

surl=https://example.com/my_table&manifest_notify=https://example.com/notify
```

- `surl` tells the recipient what to follow.
- Additional keys advertise callback NURLs for specific event types.

## 4) Common patterns

- **Bootstrap:** `surl=<table>&notify=<callback>`
- **Fan-out:** advertise a SURL and request callback if the peer follows it
- **Subscription:** publish a SURL and notify a subscriber NURL when new rows exist
- **Changefeed graphs:** tables point to other tables; notify helps propagate updates quickly
