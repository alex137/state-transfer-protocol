# STP Schemas

STP is schema-agnostic: it defines how to transport ordered change rows, but not what the rows *mean*.

A **schema** describes the meaning of:

- `PrimaryKey`
- `Record`
- allowed `Action` values (typically `+` and `-`)
- optional query parameters (e.g., `view=active`)

Schemas are identified in the STP response header:

```
Content-Type: text/sequence; charset=utf-8; schema=<schema_id>; version=<n>
```

This directory contains example schemas and conventions.
