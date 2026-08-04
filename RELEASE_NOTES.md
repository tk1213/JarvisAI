# JarvisAI v0.3.8 — Sprint 2.5 Pack H

Adds persistent observability and audit history for Long-Term Memory.

## Audited actions
- created
- updated
- unchanged
- deleted
- rejected

## Stored audit metadata
- memory key
- memory value
- source
- reason
- UTC timestamp

## Storage
Audit events are persisted in SQLite table `memory_audit`.
The table and indexes are created lazily and idempotently on first use.

## Compatibility
MemoryService and MemoryCaptureService remain backward compatible because
the audit dependency is optional.
