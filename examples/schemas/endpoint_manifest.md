# Example Schema: endpoint_manifest (v1)

**schema_id:** `endpoint_manifest`  
**version:** `1`

## Row layout

PrimaryKey is `endpoint_type`.

Record is a URL.

```
[SeqNo] \t [TS] \t + \t [endpoint_type] \t [URL]
```

## Endpoint types

- `fhir_subscribe`
- `fhir_read`
- `direct_message`
- `manifest_notify`

Unknown endpoint types MUST be ignored by clients.
