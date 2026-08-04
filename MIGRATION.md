# Sprint 3.2 Pack F — Final Gate

Prerequisite: Sprint 3.2 Packs A-E PASS.

Copy the pack into the JarvisAI project root.

There is no patch script and no production source replacement in this pack.

Run the static gate:

```powershell
python tools/run_sprint_3_2_gate.py
```

Or run manually:

```powershell
python -m compileall -q src tests tools
ruff check src tests tools
pytest
```

Then run the real runtime coordination gate:

```powershell
python tools/test_sprint_3_2_e2e_live.py
```

Expected final output:

```text
Forbidden native side effects: []
...
Requires confirmation: True
Pending plan cancelled: True

Sprint 3.2 coordination gate: PASS
```

The live Planner test deliberately cancels the side-effect plan.
It does not turn off the device.

Finally run:

```powershell
jarvis chat
```

Regression checks:

```text
Hello Jarvis
What is my name?
Check whether JarvisAI is running
Turn off Smart Plug 1 and check its status
```

The last request must require confirmation before execution.

If all gates pass, Sprint 3.2 is ready for a Git checkpoint before
Sprint 3.3 Multi-step Execution.
