# STP Positioning Notes

## One-liner

**STP is a web-native protocol for streaming ordered change tables over HTTP.**

## What it replaces

- ad hoc JSON pagination endpoints
- bespoke polling loops
- vendor-specific changefeeds

## Why TSV?

- grep-able
- log-friendly
- diff-able
- durable
- easy to generate from almost any backend

TSV is also trivial to parse in any language and works well with streaming.

## Why sequence numbers?

- deterministic ordering
- easy gap detection
- supports auditing + replay

## Why notify?

Notify reduces latency without making the system stateful:

- POST announces *where* to fetch
- GET remains authoritative
- repeated POSTs are safe
