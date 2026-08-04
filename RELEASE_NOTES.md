# JarvisAI v0.4.0-alpha.12 — Sprint 3.2 Pack F

Sprint 3.2 End-to-End Coordination and Regression Gate.

This pack intentionally adds no new production behavior.

It locks and verifies the architecture introduced across Sprint 3.2:

- CapabilityRegistry remains the authoritative permission boundary
- OpenAI tool names are adapter-safe underscore names
- Jarvis internal capability names remain dot-separated
- native tool calling exposes read-only capabilities only
- state-changing native tool execution is blocked again at execution time
- Planner requires confirmation for any plan containing a side effect
- unknown future actions fail closed
- mixed plans are held pending before any execution
- pending plans can be cancelled without side effects

The live test uses the real runtime container and real configured AI model.
The Planner side-effect test is cancelled before execution.
