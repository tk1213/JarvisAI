# JarvisAI v0.6.1-alpha.6.1 — Sprint 6 Pack F Hotfix 1

## Wake Handoff + Cancellation Diagnostics

This hotfix addresses the Pack F live failure where:

- the first transcript could be unrelated to the spoken phrase
- the second turn ended with `cancelled`

It shortens the post-ack handoff and adds stage diagnostics without weakening
real asyncio cancellation semantics.
