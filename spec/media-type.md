# Media Type: text/sequence (Draft)

STP defines a line-oriented TSV representation and uses:

```
text/sequence; charset=utf-8; schema=<schema_id>; version=<n>
```

## Parameters

- **schema**: identifies the table schema (e.g. `endpoint_manifest`)
- **version**: schema version number (integer)

## Notes

- `text/sequence` is currently an unregistered media type.
- If adoption warrants, it can be registered as an IANA media type.
