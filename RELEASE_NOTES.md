# JarvisAI 0.6.0-alpha.1

## Sprint 6 - Voice Runtime Reliability

JarvisAI 0.6.0-alpha.1 establishes the validated Sprint 6
production voice-runtime baseline.

## Highlights

- wake-word activation boundary
- wake acknowledgement before command capture
- post-acknowledgement command handoff
- continuous wake-activated assistant runtime
- silent-command rejection
- wake re-arm after silent turns
- STT prompt-echo protection
- VAD-based speech capture
- explicit audio input/output selection
- shared AudioManager integration
- TTS acknowledgement and reply playback
- session state transitions
- cancellation propagation and diagnostics
- bounded continuous runtime execution
- conversation and agent runtime integration

## Reliability

Sprint 6 added and validated:

- wake transition stage tracking
- full-turn stage tracking
- cancellation-stage diagnostics
- silent-turn recovery
- no cancellation leakage between turns
- bounded continuous assistant execution
- long-running voice runtime validation

## Automated Validation

Sprint 6 closeout:

```text
Compile: PASS
Ruff: PASS
Focused Sprint 6 regression: PASS
Full regression: PASS
806 tests passed
```

## Live Validation

Validated on the production Windows audio path:

- real wake-word detection
- acknowledgement playback
- microphone command capture
- real STT
- conversation execution
- TTS reply playback
- silent command rejection
- wake re-arm after silence
- successful next-turn execution
- cancellation behavior
- 10-turn continuous runtime soak test

## Release Checkpoint

```text
Version: 0.6.0-alpha.1
Git tag: v0.6.0-alpha.1
Commit: b1b2bc0
```

Python packaging may display the PEP 440 normalized form:

```text
0.6.0a1
```

## Next

Sprint 7 planning begins from this validated baseline.
Its feature scope is not yet defined by this release note.
