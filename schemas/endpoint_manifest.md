# Schema: endpoint_manifest (v1)

Used to exchange relationship endpoints between peers.

Row format:

```
[SeqNo] \t [TS] \t + \t [endpoint_type] \t [URL]
```

- PrimaryKey: `endpoint_type`
- Record: `URL`
- `endpoint_type` values are application-defined (e.g., `fhir_read`, `direct_message`, `notify`)
- Unknown `endpoint_type` values MUST NOT break clients.
