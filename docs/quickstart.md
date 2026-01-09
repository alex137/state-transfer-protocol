# STP Implementer Quickstart

## 1) Serve a SURL (State URL)

Expose an HTTP GET endpoint that returns TSV rows:

```
[SeqNo] \t [RFC3339 UTC Timestamp] \t [+/-] \t [Primary Key] \t [Record]
```

Include:

```
Content-Type: text/sequence; charset=utf-8; schema=<schema_id>; version=<n>
```

Support:

- `?since_id=N` (delta sync)
- optional long-poll (stream until idle / timeout)

## 2) Follow a SURL

Clients store the last processed `SeqNo` and reconnect with:

```
GET <surl>?since_id=<last_seqno>
```

Clients MUST tolerate duplicate rows (same `SeqNo`) and process idempotently.

## 3) Use NURLs (Notify URLs)

Implement a POST endpoint that accepts:

```
POST <nurl>
Content-Type: application/x-www-form-urlencoded
```

Notify bodies may contain:

### A) State notification (recommended)

```
surl=<SURL>&match=<NURL>&...
```

Meaning: “GET this SURL; also, here is how to notify me back.”

### B) Handshake / callback-only advertisement

```
manifest_nurl=<NURL>
```

Meaning: “Here is a callback NURL you can use; I’m not pointing to state yet.”

Notify is advisory: state is authoritative at SURLs.
