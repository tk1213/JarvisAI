# Sprint 3.7 Pack G — Final Gate

Prerequisite: Sprint 3.7 Packs A-F PASS.

Copy this pack into the JarvisAI project root.

No production file is replaced.

Run:

```powershell
python tools/run_sprint_3_7_gate.py
```

Or manually:

```powershell
python -m compileall -q src tests tools
ruff check src tests tools
pytest
```

Then run:

```powershell
python tools/test_sprint_3_7_e2e_live.py
```

Expected ending:

```text
Sprint 3.7 End-to-End Execution Analytics Gate
============================================================

[Gate 1] system.execution_statistics
Available: True

[Gate 2] system.capability_reliability
Available: True

[Gate 3] system.execution_health
Available: True

[Gate 4] system.execution_health_trend
Available: True

[Gate 5] Native read-only tool surface
Analytics tools present: True
Forbidden side-effect tools exposed: []

Sprint 3.7 end-to-end gate: PASS
```

Zero-valued analytics are valid when execution history is empty.

The final gate is read-only.
