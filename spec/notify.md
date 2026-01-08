# Notify Endpoint (Draft)

Notify endpoints are a mechanism to reduce polling latency.

## POST

```
POST <notify_url>
Content-Type: application/x-www-form-urlencoded

table=<STP_Table_URL>
```

- Notify does not carry data; it announces that updates are available.
- Recipients fetch updates from the `table` URL using `since_id`.
- POSTs are idempotent and may be repeated.
