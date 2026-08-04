# Sprint 3.6 Pack F — Final Gate

Prerequisite: Sprint 3.6 Packs A-E and Pack E Hotfix 1 PASS.

Copy this pack into the JarvisAI project root.

No production file is replaced.

Run:

```powershell
python tools/run_sprint_3_6_gate.py
```

Or manually:

```powershell
python -m compileall -q src tests tools
ruff check src tests tools
pytest
```

Then run:

```powershell
python tools/test_sprint_3_6_e2e_live.py
```

Expected ending with persisted history:

```text
Sprint 3.6 End-to-End Observability Gate
============================================================

[Gate 1] Execution query
Records visible: ...

[Gate 2] Execution detail
Available: ...

[Gate 3] Execution diagnostics
Available: ...

Sprint 3.6 end-to-end gate: PASS
```

If no persisted history exists:

```text
Sprint 3.6 end-to-end gate: PASS (no-data path)
```

The final gate is read-only.
