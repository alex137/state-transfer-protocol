# Minimal Server Sketch

STP can be served from:

- a static file
- a DB query emitting TSV
- an append-only log

## Requirements

- emit rows in increasing SeqNo order
- support `since_id` semantics
- include Content-Type with schema + version
- (recommended) support long-poll streaming
- (optional) expose notify URL to reduce latency
