# Sprint 4.0 Pack F — AI Agent Runtime

Prerequisite: Sprint 4.0 Packs A-E PASS.

This pack is additive. It does not replace `application.py`,
`PlannerOrchestrator`, `AIPlanGenerator`, or `PlanExecutor`.

Copy all files into the JarvisAI project root.

Run:

```powershell
python tools/run_sprint_4_0_gate.py
```

Then run:

```powershell
python tools/test_ai_agent_runtime_live.py
```

Expected ending:

```text
Sprint 4.0 AI Agent Runtime
------------------------------------------------------------
AI agent run: status=completed, success=True, requires_confirmation=False.
Plan: ...
Execution: status=completed, completed_steps=...
Reflection: decision=complete
Memory: ...
AI agent runtime gate: PASS
```

The live test uses read-only system capabilities.

Side-effect plans remain behind the existing confirmation flow.
