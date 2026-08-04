# Sprint 3.8 Pack F — Final Gate

Prerequisite: Sprint 3.8 Packs A-E PASS.

Copy this pack into the JarvisAI project root.

No production file is replaced.

Run:

```powershell
python tools/run_sprint_3_8_gate.py
```

Or manually:

```powershell
python -m compileall -q src tests tools
ruff check src tests tools
pytest
```

Then run:

```powershell
python tools/test_sprint_3_8_e2e_live.py
```

Expected ending:

```text
Sprint 3.8 End-to-End Execution Anomaly Gate
============================================================

[Gate 1] Anomaly capability
Available: True

[Gate 2] Triage
Summary: Execution anomaly triage: ...

[Gate 3] Advice
Summary: Execution anomaly advice: ...

[Gate 4] Native read-only tool surface
system_execution_anomalies: True
Forbidden side-effect tools exposed: []

Sprint 3.8 end-to-end gate: PASS
```

When execution history is empty, the informational
`no_execution_history` anomaly is valid.

The final gate is advisory/read-only.
