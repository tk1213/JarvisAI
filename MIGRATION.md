# Sprint 3.5 Pack H — Final Gate

Prerequisite: Sprint 3.5 Packs A-G PASS.

Copy this pack into the JarvisAI project root.

No production file is replaced.

Run:

```powershell
python tools/run_sprint_3_5_gate.py
```

Or manually:

```powershell
python -m compileall -q src tests tools
ruff check src tests tools
pytest
```

Then run:

```powershell
python tools/test_sprint_3_5_e2e_live.py
```

Expected ending:

```text
Sprint 3.5 End-to-End Persistence Gate
============================================================

[Gate 1] Persistent execution history
Execution history: ...

[Gate 2] Native tool surface
system_execution_history present: True

[Gate 3] Runtime capability read
Available: True
Summary: Execution history: ...

Sprint 3.5 end-to-end gate: PASS
```

The live gate is read-only and does not control smart-home devices.

After both gates pass, Sprint 3.5 can be checkpointed in Git.
