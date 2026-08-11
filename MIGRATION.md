# Sprint 6 Pack F Hotfix 1 — Wake Handoff + Cancellation Diagnostics

Extract over:

```text
D:\Projects\JarvisAI
```

## Changes

- acknowledgement fixed to valid UTF-8 Thai: `ครับ คุณ TK`
- default post-ack settle reduced from 0.8 s to 0.25 s
- wake-command transition stage diagnostics
- full-turn stage diagnostics
- cancellation stage attached to bounded continuous runtime result
- cancellation semantics preserved: no automatic retry of CancelledError

## Quality gate

```powershell
python tools/run_sprint_6_pack_f_hotfix1_gate.py
```

## Live gate

```powershell
python tools/test_continuous_assistant_hotfix1_live.py
```

Turn 1:

```text
Hey Jarvis
วันนี้วันอะไร
```

Turn 2:

```text
Hey Jarvis
ทดสอบระบบ
```

If cancellation occurs, the gate now reports a concrete stage such as:

```text
transition:wake_wait
transition:command_listen
conversation:completed
tts_reply:completed
```

Do not move to Pack G until two bounded real turns complete reliably.
