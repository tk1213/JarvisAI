# JarvisAI

JarvisAI is a production-oriented JARVIS-style AI assistant built with Python.

Current development baseline:

```text
JarvisAI 0.6.0-alpha.1
Sprint 6: Voice Runtime Reliability - COMPLETE
```

## Current Capabilities

JarvisAI currently includes:

- wake-word activation
- continuous wake-activated voice runtime
- microphone capture and audio diagnostics
- voice activity detection (VAD)
- OpenAI speech-to-text integration
- text-to-speech generation and playback
- interactive text chat
- production conversation routing
- deterministic system fast paths
- OpenAI tool calling
- structured capability arguments
- conversation memory
- durable agent memory
- bounded context assembly
- AI agent runtime
- bounded replanning
- confirmation boundaries for side effects
- recovery and safe degradation
- turn tracing and operational diagnostics
- smart-home skill foundation
- system health checks

## CLI

Start the production voice assistant:

```powershell
jarvis run
```

Start interactive text chat:

```powershell
jarvis chat
```

Run system health checks:

```powershell
jarvis doctor
```

Show the application version:

```powershell
jarvis version
```

## Development

JarvisAI requires Python 3.12 or newer.

Install the project in editable mode:

```powershell
python -m pip install -e .
```

Run the complete automated test suite:

```powershell
python -m pytest -q
```

Run Ruff:

```powershell
ruff check src tests tools
```

Run compile validation:

```powershell
python -m compileall -q src tests tools
```

## Quality Policy

Production milestones must pass:

1. Python compile validation
2. Ruff
3. focused regression tests
4. full pytest regression
5. relevant live integration tests

Development prioritizes stability, reliability, maintainability,
bounded execution, explicit cancellation behavior, safety, and
real-world hardware validation before feature expansion.

## Sprint 6 Baseline

Sprint 6 completed the production wake-word and continuous voice
runtime reliability milestone.

The Sprint 6 closeout baseline passed:

```text
Compile: PASS
Ruff: PASS
Focused Sprint 6 regression: PASS
Full regression: PASS
806 tests passed
```

Live validation also covered silent-turn recovery, wake re-arming,
cancellation behavior, and a successful 10-turn continuous runtime
soak test.

Git release checkpoint:

```text
Tag: v0.6.0-alpha.1
Commit: b1b2bc0
```

## Architecture

See:

```text
docs/ARCHITECTURE.md
docs/PROJECT_STATE.md
```

`ARCHITECTURE.md` describes the production conversation, recovery,
context, tracing, and safety architecture.

`PROJECT_STATE.md` tracks the current implementation milestone and
validated system baseline.

## Next Milestone

Sprint 7 planning begins from the verified Sprint 6 baseline.

Sprint 7 scope will be selected from the current architecture and
feature inventory rather than from outdated milestone assumptions.
