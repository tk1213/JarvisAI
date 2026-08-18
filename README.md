# JarvisAI

JarvisAI is a production-oriented JARVIS-style AI assistant built with
Python.

The project is developed incrementally with a strong focus on stability,
reliability, maintainability, bounded execution, safety, and real-world
validation before feature expansion.


Current development baseline:

```text
JarvisAI 0.7.0-alpha.1
Sprint 7: Tuya Smart Home Reliability - COMPLETE
Sprint 8.1: Runtime Reliability and Smart Home Confirmation Safety - COMPLETE
Sprint 8.2: Voice Smart Home Confirmation Safety Integration - COMPLETE
Sprint 8.3: Voice Tuya Live Safety Validation - COMPLETE
Sprint 8.4: Audio Device Diagnostics and Observability Hardening - COMPLETE
Sprint 8.5: Resilience Runtime Diagnostics and Observability - COMPLETE
Sprint 8.6: Wake Cancellation Boundary Reliability Hardening - COMPLETE
Sprint 8.7: Voice Capture Cancellation Boundary Hardening - COMPLETE
```

Current release checkpoint:

```text
Version : 0.7.0-alpha.1
Git tag : v0.7.0-alpha.1
Commit  : 6825df0
```

Current post-release development baseline:

```text
Commit          : 4d9ba0f
Branch          : main
Remote          : origin/main
Full regression : 968 passed
Ruff            : PASS
```

The `v0.7.0-alpha.1` tag remains the validated Sprint 7 release
checkpoint. Current `main` Sprint 8.6 wake cancellation boundary reliability hardening
contains additional post-release reliability,
architecture, Sprint 8.1 runtime safety, Sprint 8.2 voice confirmation
integration, Sprint 8.3 voice Tuya live safety validation, Sprint 8.4
audio-device diagnostics and observability hardening, and Sprint 8.5
resilience runtime diagnostics and observability hardening that have not
yet been assigned a new release tag.


Python packaging may display the PEP 440 normalized version:

```text
0.7.0a1
```

---

## Project Goals

JarvisAI is designed as a modular AI assistant capable of combining:

- natural-language conversation
- voice interaction
- wake-word activation
- AI reasoning
- tool and capability execution
- agent planning and replanning
- persistent memory
- recovery and safe degradation
- smart-home control
- operational diagnostics
- real-world hardware integration

The goal is not simply to demonstrate individual AI features.

The system is developed toward a reliable assistant architecture where
conversation, planning, tools, memory, voice, and physical-device control
can operate together while maintaining explicit safety and reliability
boundaries.

---

## Engineering Principles

JarvisAI follows these core engineering principles:

- production-first development
- stability before new features
- backward compatibility whenever possible
- test-first mindset
- Python 3.12+
- async-first architecture
- type hints throughout production code
- small focused modules
- dependency injection through a central container
- explicit error handling
- bounded autonomous execution
- explicit cancellation propagation
- confirmation before side effects
- deterministic and bounded context assembly
- regression testing before milestone completion
- live validation for hardware and external integrations
- tagged Git checkpoints for validated milestones

A feature is not considered complete merely because the implementation
exists.

Production milestones must pass the appropriate static, automated, and
live validation gates.

---

# Current Capabilities

## Voice Runtime

JarvisAI includes a production voice path with:

- Windows audio-device discovery
- deterministic input/output device selection
- explicit microphone selection
- explicit playback-device selection
- production microphone capture
- RMS diagnostics
- peak-level diagnostics
- silence detection
- clipping diagnostics
- voice activity detection (VAD)
- speech-triggered recording
- silence-based recording stop
- OpenAI speech-to-text integration
- text-to-speech generation
- audio playback
- shared AudioManager integration
- wake-word activation
- wake acknowledgement
- post-acknowledgement command handoff
- continuous wake-activated runtime
- silent-command rejection
- wake re-arming after silent turns
- STT prompt-echo protection
- bounded continuous execution
- cancellation propagation and diagnostics
- conversation integration
- application lifecycle integration

The validated voice path is conceptually:

```text
Microphone
    |
    v
Wake Detection
    |
    v
Wake Acknowledgement
    |
    v
Command Capture
    |
    v
VAD / Audio Diagnostics
    |
    v
Speech-to-Text
    |
    v
ConversationManager
    |
    v
AI / Tools / Agent Runtime
    |
    v
Text-to-Speech
    |
    v
Audio Playback
```

---

## Conversation Runtime

`ConversationManager` is the production entry point for user requests.

The production conversation flow is:

```text
User
-> ConversationManager.ask()
-> ConversationTurnLifecycle
-> ConversationExecutionBoundary
-> conversation routing
-> actual route attribution
-> recovery planning when needed
-> recovery execution when allowed
-> response
-> bounded turn trace history
```

The conversation subsystem includes:

- production request routing
- deterministic system fast paths
- bounded execution
- turn lifecycle management
- execution boundaries
- failure classification
- recovery planning
- recovery execution
- reliability reporting
- operational metrics
- production context assembly
- bounded turn tracing
- health reporting

---

## AI Runtime

JarvisAI uses the OpenAI Responses API as the standard AI interface.

The AI layer includes:

- OpenAI client integration
- Responses API contracts
- Responses service
- AIService
- configurable model selection
- request timeout handling
- bounded retry configuration
- configurable output-token limits
- tool calling
- structured tool arguments
- conversation context integration
- agent-runtime integration

---

## Agent Runtime

JarvisAI contains an agent runtime responsible for coordinating
higher-level execution.

The agent architecture includes:

- agent bootstrap
- runtime orchestration
- sessions
- conversation bridge
- planning context
- replanning
- memory integration
- memory persistence
- memory retention
- execution reports
- session reports

The AI agent runtime is designed to orchestrate:

```text
Request
-> Planning
-> Execution
-> Reflection
-> Memory
-> Response
```

Planning and execution remain separate architectural concerns.

---

## Planner and Execution Engine

The planner subsystem provides infrastructure for controlled autonomous
execution.

Capabilities include:

- AI-generated plans
- structured plan contracts
- plan parsing
- plan schema validation
- plan execution
- plan reflection
- bounded replanning
- execution policies
- execution deadlines
- timeout handling
- retry handling
- backoff
- bulkheads
- circuit breakers
- compensation
- recovery policies
- execution journaling
- execution persistence
- execution history
- execution statistics
- execution health
- health trends
- execution anomalies
- anomaly triage
- anomaly advice
- incident generation
- incident grouping
- incident correlation
- incident timelines
- incident dashboards
- resilience metrics
- capability reliability reporting

Autonomous execution is intentionally bounded.

---

## Memory

JarvisAI contains separate conversation and durable agent-memory
capabilities.

The memory architecture includes:

- conversation history
- durable agent memory
- memory capture
- capture policy
- memory extraction
- retrieval
- context construction
- confidence handling
- conflict handling
- memory rules
- audit records
- audit repository
- audit service
- persistence
- retention
- memory-aware conversation integration

Production context assembly remains bounded and deterministic:

```text
SYSTEM
CONVERSATION MEMORY
AGENT MEMORY
HISTORY
CURRENT USER
```

Memory-domain safety is explicit:

```text
stored memory = reference data only
```

Stored memory is not treated as executable instruction authority.

---

## Tools and Capabilities

JarvisAI includes a structured capability and tool execution layer.

The architecture includes:

- capability definitions
- capability registry
- capability resolver
- capability router
- AI capability resolution
- tool contracts
- tool adapters
- tool execution
- safe tool wrappers
- OpenAI tool runner
- conversation/tool bridge
- command registry
- command service

Read-only capabilities may execute automatically where allowed.

Capabilities that cause side effects require the appropriate execution
policy and confirmation boundary.

---

## Skills

JarvisAI includes a modular skill architecture with:

- skill base contracts
- skill metadata
- skill context
- skill loader
- skill registry
- skill resolver
- skill manager

This provides a foundation for extending JarvisAI without coupling every
new capability directly to the conversation runtime.

---

# Smart Home

## Smart Home Architecture

JarvisAI contains a provider-independent smart-home layer.

The current implementation includes:

- SmartHomeAdapter abstraction
- SmartHomeService
- generic SmartDevice model
- mock adapter
- Tuya adapter
- device resolution
- pending-action handling
- smart-home text normalization
- bounded voice disambiguation
- smart-home capability integration
- smart-home skill integration

The provider is selected through configuration:

```text
SMART_HOME_PROVIDER=mock
```

or:

```text
SMART_HOME_PROVIDER=tuya
```

The mock provider remains useful for development and automated testing.

---

## Tuya Cloud Integration

Sprint 7 established the validated production Tuya Cloud path.

The Tuya integration includes:

- Cloud API authentication
- access-token retrieval
- HMAC-SHA256 request signing
- configurable Tuya endpoint
- real device discovery
- device-status retrieval
- device metadata mapping
- power-state extraction
- switch datapoint discovery
- device ON
- device OFF
- device toggle
- post-command state verification
- bounded verification retries
- connection lifecycle management
- clean disconnect behavior
- cancellation propagation
- HTTP error propagation
- Tuya API failure handling

The production path is:

```text
User / Capability
       |
       v
SmartHomeService
       |
       v
SmartHomeAdapter
       |
       v
TuyaAdapter
       |
       v
Tuya Cloud API
       |
       v
Physical Smart Device
       |
       v
Status Verification
```

---

## Validated Tuya Hardware

Sprint 7 live validation successfully connected to the real Tuya Cloud
environment and discovered two smart plugs.

The read-only live gate validated:

- Tuya Cloud connection
- authentication
- real-device discovery
- device metadata
- online-state retrieval
- device-status retrieval
- switch datapoint retrieval
- clean disconnect

A controlled physical power test was also completed successfully.

The test:

1. read the original device state
2. requested confirmation before changing physical state
3. changed the smart plug from OFF to ON
4. verified the new physical state through Tuya
5. restored the original OFF state
6. verified restoration
7. disconnected cleanly

Validated result:

```text
Connection: PASS
Power transition: PASS
Power restore: PASS
Tuya controlled power live gate: PASS
```

The live test restores the original state instead of assuming a fixed
final power state.

---

# Recovery and Reliability

## Recovery Flow

Primary failures are processed through:

```text
failure
-> ConversationFailureClassifier
-> ConversationRecoveryService
-> ConversationRecoveryExecutor
```

### Timeout Recovery

```text
timeout
-> retryable failure
-> safe-message fallback
-> return safe reply
```

### Standard-AI Recovery

```text
retryable tool/upstream failure
-> standard-AI fallback
-> one fallback call maximum
```

If the fallback also fails:

```text
fallback failure
-> no recursive recovery
-> no second fallback call
-> safe-message degradation
-> fallback_error_type recorded
```

This prevents uncontrolled recursive recovery.

---

## Recovery Observability

Recovered turns can expose:

- whether recovery executed
- fallback kind
- attempts used
- fallback error type

Recovery metadata is retained in bounded turn history.

---

## Turn Tracing

Production turn records can include:

- turn ID
- route/source
- status
- duration
- timestamps
- failure classification
- reliability outcome
- recovery execution metadata

This provides an operational record of how a conversation request was
processed.

---

# Safety Model

Safety boundaries are architectural requirements rather than optional
application behavior.

Current principles include:

- safety before automation
- confirmation for side effects
- automatic native tools remain read-only where required
- read-only capabilities may execute automatically
- side-effect capabilities require explicit confirmation
- bounded autonomous replanning
- bounded context assembly
- memory-domain separation
- durable memory retention
- bounded turn history
- bounded production execution time
- bounded recovery attempts
- single-attempt standard-AI fallback
- no recursive recovery
- non-retryable failures remain explicit
- external cancellation propagation
- backward compatibility whenever possible

Physical smart-home control is treated as a side-effect operation.

---

# Architecture Decisions

JarvisAI currently follows these documented architecture decisions.

## ADR-001 — OpenAI Interface

The Responses API is the standard AI interface.

## ADR-002 — Conversation Entry Point

`ConversationManager` is the entry point for user requests.

## ADR-003 — Planning Boundary

Planning is separated from execution.

## ADR-004 — Side-Effect Policy

Execution Policy controls confirmation for side effects.

## ADR-005 — Agent Runtime

The AI Agent Runtime orchestrates planning, execution, reflection, and
memory.

## ADR-006 — Dependency Injection

Dependency injection uses the central service container.

## ADR-007 — Capability Safety

Read-only capabilities execute automatically where allowed.

Side-effect capabilities require explicit confirmation.

## ADR-008 — Production Quality

Production code must pass the required:

- Ruff checks
- Pytest regression
- compile validation
- relevant live gates

---

# CLI

## Start JarvisAI

Start the production assistant:

```powershell
jarvis run
```

## Interactive Text Chat

```powershell
jarvis chat
```

## System Health

```powershell
jarvis doctor
```

## Version

```powershell
jarvis version
```

Current expected result:

```text
JarvisAI 0.7.0-alpha.1
```

---

# Installation

JarvisAI requires Python 3.12 or newer.

Create and activate a virtual environment before installing project
dependencies.

Install the project in editable mode:

```powershell
python -m pip install -e .
```

The development workflow assumes commands are executed from the project
root.

Example:

```text
D:\Projects\JarvisAI
```

---

# Configuration

JarvisAI uses environment-based configuration.

Start from:

```text
.env.example.txt
```

and create a local:

```text
.env
```

Secrets must remain in the local `.env` and must not be committed to the
repository.

Important configuration areas include:

```text
APP_NAME
APP_ENVIRONMENT
DEBUG
LOG_LEVEL

DATABASE_URL

OPENAI_API_KEY
OPENAI_MODEL

SMART_HOME_PROVIDER

TUYA_ACCESS_ID
TUYA_ACCESS_KEY
TUYA_ENDPOINT

STT_MODEL
STT_LANGUAGE

TTS_MODEL
TTS_LANGUAGE

AUDIO_SAMPLE_RATE
AUDIO_CHANNELS
```

For Tuya production use:

```text
SMART_HOME_PROVIDER=tuya
```

Tuya credentials must be supplied through the local environment.

Do not place real access IDs, access keys, tokens, or device credentials
in committed documentation or source files.

---

# Development

## Compile Validation

```powershell
python -m compileall -q src tests tools
```

## Ruff

```powershell
ruff check src tests tools
```

## Full Regression

```powershell
python -m pytest -q
```

## Smart Home Regression

The Sprint 7 focused smart-home regression can be run with:

```powershell
python -m pytest `
    tests\test_tuya_adapter_contract.py `
    tests\test_smart_home.py `
    tests\test_smart_home_capability_integration.py `
    tests\test_smart_home_skill.py `
    tests\test_smart_home_text_normalizer.py `
    -q
```

Sprint 7 validated result:

```text
104 passed
```

---

# Live Integration Gates

## Tuya Read-Only Gate

```powershell
python tools\test_tuya_readonly_live.py
```

This gate performs real Tuya Cloud operations without intentionally
changing device power state.

Sprint 7 result:

```text
Tuya read-only live gate: PASS
```

## Tuya Controlled Power Gate

```powershell
python tools\test_tuya_power_control_live.py
```

This is a physical side-effect test.

The gate requires explicit confirmation before changing the device
state and restores the original state before successful completion.

Sprint 7 result:

```text
Tuya controlled power live gate: PASS
```

---

# Quality Policy

Every production milestone must pass the appropriate quality gates:

1. compile validation
2. Ruff
3. focused regression tests
4. full pytest regression
5. relevant live integration tests
6. documentation alignment
7. clean Git state
8. release checkpoint when appropriate

The development workflow is:

```text
Implement
-> Unit / Contract Tests
-> Focused Regression
-> Live Test
-> Ruff
-> Compile
-> Full Regression
-> Documentation
-> Git Checkpoint
```

The `main` branch should remain releasable.

Commits should be small and focused.

Validated sprint milestones use Git tags.

---

# Contributor Guidelines

Before opening a pull request:

- Ruff must pass
- tests must pass
- relevant live gates must pass
- debug code must be removed
- documentation must be updated

Review should verify:

- backward compatibility
- type hints
- async safety
- logging
- error handling
- test coverage

Supported commit prefixes include:

```text
feat:
fix:
refactor:
test:
docs:
chore:
```

Definition of Done:

```text
Feature implemented
Documentation updated
Required gates pass
Git working tree clean
```

---

# Repository Structure

The current high-level source layout includes:

```text
src/jarvis/
|
+-- agent/
+-- ai/
+-- audio/
+-- config/
+-- conversation/
+-- core/
+-- database/
+-- memory/
+-- planner/
+-- services/
+-- skills/
+-- smart_home/
+-- speech/
+-- tools/
+-- voice/
+-- wake/
```

Major responsibilities:

| Package | Responsibility |
| --- | --- |
| `agent` | Agent runtime, sessions, replanning, reporting and agent memory |
| `ai` | OpenAI client, Responses API contracts and services |
| `audio` | Recording, playback, devices, diagnostics and VAD |
| `config` | Application configuration |
| `conversation` | Production turn lifecycle, recovery, reliability and diagnostics |
| `core` | Application lifecycle, DI container, events, commands and infrastructure |
| `database` | Database management and schemas |
| `memory` | Capture, extraction, retrieval, persistence, audit and memory policy |
| `planner` | Planning, execution, resilience, recovery and execution observability |
| `services` | Application-level service layer |
| `skills` | Skill loading, registration and resolution |
| `smart_home` | Smart-home abstraction, Tuya integration and device resolution |
| `speech` | STT and TTS implementations |
| `tools` | Tool contracts, adapters and execution |
| `voice` | Voice dialogue and turn runtime |
| `wake` | Wake activation, handoff and continuous runtime |

---

# Validated Release Baselines

## Sprint 6 — Voice Runtime Reliability

Release:

```text
Version : 0.6.0-alpha.1
Tag     : v0.6.0-alpha.1
Commit  : b1b2bc0
```

Sprint 6 established the production wake-word and continuous voice
runtime reliability baseline.

Automated closeout:

```text
Compile: PASS
Ruff: PASS
Focused Sprint 6 regression: PASS
Full regression: PASS
806 tests passed
```

Live validation covered:

- real wake-word detection
- acknowledgement playback
- microphone command capture
- real STT
- conversation execution
- TTS reply playback
- silent-command rejection
- wake re-arm after silence
- successful next-turn execution
- cancellation behavior
- 10-turn continuous runtime soak test

Sprint 7 builds on this baseline rather than replacing its voice-runtime
guarantees.

---

## Sprint 7 — Tuya Smart Home Reliability

Release:

```text
Version : 0.7.0-alpha.1
Tag     : v0.7.0-alpha.1
Commit  : 6825df0
```

Sprint 7 established the production Tuya smart-home reliability
baseline.

Automated closeout:

```text
Compile: PASS
Ruff: PASS
Smart Home regression: PASS - 104 tests
Full regression: PASS - 882 tests
```

Real Tuya Cloud read-only validation:

```text
Connection: PASS
Device discovery: PASS
Device status: PASS
Tuya read-only live gate: PASS
```

Controlled physical-device validation:

```text
Power transition: PASS
Post-command verification: PASS
Original-state restoration: PASS
Tuya controlled power live gate: PASS
```

This checkpoint confirms that the smart-home integration was tested not
only through mocks and unit tests but also through the real Tuya Cloud
path and a physical smart device.

---

# Current Quality Baseline

At the Sprint 7 release checkpoint:

```text
Python compile validation : PASS
Ruff                      : PASS
Smart Home regression     : 104 passed
Full regression           : 882 passed
Tuya read-only live gate  : PASS
Tuya physical control     : PASS
Original-state restore    : PASS
```

Current post-release Sprint 8 baseline:

```text
Commit                              : cf9ed9e
Full regression                     : 968 passed
Ruff                                : PASS
Tuya aggregate status live gate     : PASS
Tuya device status live gate        : PASS
Tuya side-effect confirmation gate  : PASS
Tuya cancellation gate              : PASS
Tuya original-state restoration     : PASS
Voice confirmation integration      : PASS
Voice cancellation integration      : PASS
Voice read-only pending query       : PASS
Microphone -> STT live gate         : PASS
Voice Tuya confirmation live gate   : PASS
Voice Tuya cancellation live gate   : PASS
Resilience runtime health reporting : PASS
Degraded resilience diagnostics     : PASS
Doctor resilience reporting         : PASS
Wake cancellation boundary          : PASS
Wake-focused regression             : 37 passed
Wake cancellation observability     : PASS
```

Sprint 8.3 additionally validates the production voice path against the
real Windows audio environment and physical Tuya integration. The
validated microphone path uses the Windows WASAPI representation of the
RØDE NT-USB Mini rather than the unreliable WDM-KS representation.

The Sprint 8.3 live validation confirms that:

- microphone capture reaches STT successfully
- spoken Smart Home side effects enter the confirmation boundary
- spoken confirmation executes the pending Smart Home action
- spoken cancellation clears the pending action without executing it
- the voice dialogue runtime returns to a non-pending state after either
  confirmation or cancellation

Current release:

```text
JarvisAI 0.7.0-alpha.1
```

---

# Documentation

Additional project documentation is available in:

```text
docs/
|
+-- ARCHITECTURE.md
+-- PROJECT_STATE.md
+-- CONTRIBUTOR_GUIDE.md
+-- JarvisAI_Architecture_Decision_Record_ADR.md
+-- JarvisAI_Developer_Handbook_v1.0.md
```

The repository also contains document-format versions of selected
engineering documentation.

`ARCHITECTURE.md` describes the production conversation, recovery,
context, tracing, and safety architecture.

`PROJECT_STATE.md` tracks the current validated implementation state.

`CONTRIBUTOR_GUIDE.md` defines contributor workflow and Definition of
Done.

The ADR records the architectural decisions that production code should
continue to respect.

The Developer Handbook defines the broader engineering standards and
sprint workflow.

---

# Current Boundaries

JarvisAI is still an alpha-stage system.

The current release demonstrates validated production-oriented
subsystems, but the project should not claim that every planned
JARVIS capability is complete.

In particular:

- new capabilities must continue to respect execution policy
- side-effect operations must retain confirmation boundaries
- autonomous planning must remain bounded
- recovery must remain bounded and non-recursive
- cancellation semantics must not be weakened
- external integrations require their own live validation
- hardware-dependent behavior must be tested on the relevant hardware
- new features must not regress the validated Sprint 6 voice baseline
- new features must not regress the validated Sprint 7 Tuya baseline

---

# Next Milestone

## Sprint 8 - Continued Scope Selection

Sprint 8 began from the verified Sprint 7 production baseline.

Sprint 8.1 runtime reliability and Smart Home confirmation safety work
has been completed and validated.

Sprint 8.2 voice Smart Home confirmation safety integration has been
completed and validated.

Sprint 8.3 voice Tuya live safety validation has been completed and
validated against the production microphone, STT, voice dialogue, and
physical Tuya control path.

Sprint 8.4 audio-device diagnostics and observability hardening has
also been completed and validated.

Sprint 8.5 resilience runtime diagnostics and observability hardening
has also been completed and validated.

Sprint 8.6 wake cancellation boundary reliability hardening has also
been completed and validated.

Sprint 8.7 voice capture cancellation boundary hardening has also
been completed and validated.

The next Sprint 8 scope has not yet been fixed.

Scope selection should be based on:

- the current implementation
- production architecture
- remaining production gaps
- existing feature inventory
- reliability risk
- regression risk
- safety implications
- real-world usability

Sprint 8.4 hardens runtime audio observability by exposing the selected
production audio endpoints through the health and doctor diagnostics.

The system doctor now reports the selected input and output device
index, device name, Windows host API, and sample rate. This makes the
actual runtime audio routing directly observable and reduces ambiguity
when diagnosing Windows audio-device selection issues.

Sprint 8.4 validation confirms that:

- runtime readiness exposes the selected audio-device details
- the doctor command reports the selected input and output endpoints
- the validated production microphone remains on Windows WASAPI
- the validated production speaker output remains on Windows WASAPI
- operational health semantics remain unchanged
- the complete automated regression suite remains green

Sprint 8.5 hardens runtime resilience observability by making the
production resilience snapshot part of structured health diagnostics.

The system doctor can now distinguish a healthy resilience runtime from
a degraded runtime and report the current resilience summary, plan and
step counters, retries, timeouts, circuit-breaker rejections, bulkhead
rejections, and capability failure counts.

A degraded resilience snapshot is reported as a noncritical warning so
historical resilience events do not automatically make the overall
JarvisAI runtime unhealthy.

Sprint 8.5 validation confirms that:

- resilience diagnostics use the runtime snapshot when available
- degraded resilience is surfaced as a structured DEGRADED health state
- degraded resilience remains noncritical to overall operational health
- generic placeholder runtime services remain backward compatible
- the doctor command exposes resilience summary and metrics
- the complete automated regression suite remains green at 956 tests

No Sprint 8 feature should be considered complete until its
implementation, automated regression, documentation, and relevant live
validation have passed.

Sprint 8.6 hardens the wake activation cancellation boundary without
changing wake-word detection behavior.

The wake activation boundary now has explicit regression coverage for
active-wait cancellation and cleanup, repeated waits after cancellation,
parent-task cancellation propagation, concurrent-wait rejection, and
wake-service ownership preservation.

Wake cancellation diagnostics have also been moved from direct console
printing to the shared structured logging infrastructure so expected
cancellation control flow does not produce raw diagnostic output.

Sprint 8.6 validation confirms that:

- active wake waits are cancelled and cleaned up correctly
- the boundary can wait again after cancellation
- parent-task cancellation continues to propagate
- concurrent wake waits remain rejected
- cancelling a boundary wait does not close the wake-word service
- wake cancellation diagnostics use structured logging
- wake-focused regression remains green at 37 tests
- the complete automated regression suite remains green at 962 tests

Sprint 8.7 hardens the production voice capture cancellation boundary
without changing normal STT or voice-dialogue behavior.

AudioRecorder now supports cooperative cancellation during both
adaptive noise calibration and VAD-driven speech capture. Cancellation
is checked while microphone capture is active so the audio stream can
exit cleanly instead of leaving blocking recorder work behind.

STTService now executes blocking recorder operations outside the
asyncio event loop. Recorder workers are shielded from direct asyncio
task cancellation, receive a cooperative cancellation signal, and are
awaited to termination before CancelledError is propagated.

The cancellation contract is also validated through VoiceService and
the assistant follow-up timeout boundary so session state returns to
IDLE and voice cleanup completes before control returns to the runtime.

Sprint 8.7 validation confirms that:

- VAD speech capture supports cooperative cancellation
- adaptive noise calibration supports cooperative cancellation
- blocking recorder operations no longer run on the asyncio event loop
- STT cancellation waits for recorder worker termination
- microphone capture cleanup completes before cancellation propagates
- VoiceService restores IDLE state after listening cancellation
- assistant follow-up timeout waits for voice cancellation cleanup
- the complete automated regression suite remains green at 968 tests

---

# Release History

| Release | Sprint | Milestone | Status |
| --- | --- | --- | --- |
| `v0.6.0-alpha.1` | Sprint 6 | Voice Runtime Reliability | Validated |
| `v0.7.0-alpha.1` | Sprint 7 | Tuya Smart Home Reliability | Validated |

Current baseline:

```text
v0.7.0-alpha.1
```