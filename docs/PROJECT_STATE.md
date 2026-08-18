JarvisAI Project State

Current Milestone

Sprint 7 closeout.

Current validated release baseline:

JarvisAI 0.7.0-alpha.1
Sprint 7: Tuya Smart Home Reliability - COMPLETE

Release checkpoint:

Version : 0.7.0-alpha.1
Git tag : v0.7.0-alpha.1
Commit  : 6825df0

Sprint 7 builds on the validated Sprint 6 voice-runtime baseline.

Engineering Status

JarvisAI is an alpha-stage, production-oriented JARVIS-style AI
assistant.

Development currently prioritizes:

stability before feature expansion

reliability

maintainability

backward compatibility whenever possible

bounded execution

explicit cancellation behavior

side-effect safety

deterministic context handling

automated regression coverage

real-world hardware validation

A feature is not considered production-ready only because its
implementation exists. Relevant static, automated, and live gates must
also pass.

Production Conversation Runtime

Implemented:

ConversationManager as the production request entry point

conversation turn lifecycle

execution boundaries

deterministic routing

actual route attribution

bounded turn execution

failure classification

recovery planning

recovery execution

safe degradation

reliability outcomes

bounded turn tracing

operational diagnostics

system health integration

Production flow:

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

Recovery Runtime

Implemented recovery path:

failure
-> ConversationFailureClassifier
-> ConversationRecoveryService
-> ConversationRecoveryExecutor

Timeout recovery:

timeout
-> retryable failure
-> safe-message fallback
-> return safe reply

Standard-AI recovery:

retryable tool/upstream failure
-> standard-AI fallback
-> one fallback call maximum

Fallback failure remains bounded:

fallback failure
-> no recursive recovery
-> no second fallback call
-> safe-message degradation
-> fallback_error_type recorded

Recovery metadata can include:

whether recovery executed

fallback kind

attempts used

fallback error type

External cancellation remains visible to callers.

Production Voice Runtime

Implemented:

Windows audio-device discovery

deterministic audio-device selection

explicit input/output device handling

production microphone capture

RMS diagnostics

peak diagnostics

silence diagnostics

clipping diagnostics

voice activity detection

speech-triggered recording

silence-based recording stop

OpenAI speech-to-text integration

text-to-speech generation

audio playback

shared AudioManager integration

wake-word activation

wake acknowledgement

post-acknowledgement command handoff

continuous wake-activated runtime

silent-command rejection

wake re-arm after silent turns

STT prompt-echo protection

ConversationManager voice-turn integration

TTS reply playback

bounded continuous runtime execution

cancellation propagation and diagnostics

application lifecycle integration

Validated Sprint 6 live path included:

real wake-word detection

acknowledgement playback

microphone command capture

real STT

conversation execution

TTS reply playback

silent-turn recovery

wake re-arm after silence

successful next-turn execution

cancellation behavior

successful 10-turn continuous runtime soak test

Sprint 6 release checkpoint:

Version : 0.6.0-alpha.1
Git tag : v0.6.0-alpha.1
Commit  : d99be25

AI Runtime

Implemented:

OpenAI Responses API integration

OpenAI client

Responses API contracts

Responses service

AIService

configurable model selection

timeout handling

bounded retry configuration

configurable output-token limits

OpenAI tool calling

structured tool arguments

conversation context integration

agent-runtime integration

Architecture decision:

Responses API is the standard AI interface.

Agent Runtime

Implemented agent infrastructure includes:

agent bootstrap

runtime orchestration

sessions

conversation bridge

planning context

replanning

memory integration

memory persistence

memory retention

execution reporting

session reporting

Conceptual runtime:

Request
-> Planning
-> Execution
-> Reflection
-> Memory
-> Response

Planning remains separated from execution.

Autonomous execution remains bounded.

Planner and Execution

Implemented infrastructure includes:

structured plans

AI-generated planning

plan parsing

plan schema validation

plan execution

reflection

bounded replanning

execution policy

execution deadlines

timeout handling

retry handling

backoff

bulkheads

circuit breakers

compensation

recovery policies

execution journaling

execution persistence

execution history

execution statistics

execution health

health trends

anomaly handling

incident reporting

resilience metrics

capability reliability reporting

Side-effect execution is controlled by execution policy.

Memory

Implemented memory capabilities include:

conversation history

durable agent memory

memory capture

capture policy

extraction

retrieval

bounded context construction

confidence handling

conflict handling

memory rules

persistence

retention

audit records

memory-aware conversation integration

Production context assembly remains bounded and deterministic:

SYSTEM
CONVERSATION MEMORY
AGENT MEMORY
HISTORY
CURRENT USER

Memory-domain safety remains explicit:

stored memory = reference data only

Stored memory is not executable instruction authority.

Tools and Capabilities

Implemented infrastructure includes:

capability definitions

capability registry

capability resolver

capability router

AI capability resolution

tool contracts

tool adapters

tool execution

safe tool wrappers

OpenAI tool runner

conversation/tool bridge

command registry

command service

Current safety boundary:

read-only capabilities may execute automatically where allowed

side-effect capabilities require the appropriate confirmation policy

Skills

Implemented skill infrastructure includes:

skill base contracts

skill metadata

skill context

skill loader

skill registry

skill resolver

skill manager

Smart-home behavior is integrated through this capability/skill
architecture rather than being coupled directly to the AI provider.

Smart Home Foundation

Implemented:

SmartHomeAdapter abstraction

SmartHomeService

generic SmartDevice model

MockAdapter

TuyaAdapter

device resolution

pending-action handling

smart-home text normalization

bounded voice disambiguation

smart-home capability integration

smart-home skill integration

Provider selection is configuration-driven:

SMART_HOME_PROVIDER=mock

or:

SMART_HOME_PROVIDER=tuya

The mock provider remains available for deterministic development and
automated testing.

Sprint 7 - Tuya Smart Home Reliability

Sprint 7 hardened and validated the real Tuya Cloud integration.

Implemented and validated:

Tuya Cloud authentication

access-token retrieval

configurable Tuya endpoint

HMAC-SHA256 request signing

canonical query handling

request body hashing

signed request headers

real device discovery

device metadata mapping

online-state mapping

device status retrieval

power-state extraction

switch datapoint discovery

device ON

device OFF

device toggle

post-command state verification

bounded verification retries

explicit connection lifecycle

clean disconnect

HTTP failure propagation

network failure propagation

Tuya API failure propagation

cancellation propagation

Production path:

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

Tuya Contract Validation

Dedicated Tuya adapter contract coverage includes:

disconnected initial state

credential validation

endpoint validation

device ID validation

token acquisition

token response validation

request signing

query canonicalization

body hashing

request headers

malformed response handling

Tuya failure responses

HTTP error propagation

device discovery

malformed-device filtering

metadata normalization

device lookup

status lookup

power-state extraction

switch datapoint discovery

unsupported-device behavior

ON/OFF delegation

toggle behavior

command payload generation

state verification

bounded verification retries

retry exhaustion

command failure behavior

connection lifecycle

disconnect lifecycle

cancellation behavior

Validated contract result:

73 passed

Focused Smart Home Regression

Validated test set:

tests/test_tuya_adapter_contract.py
tests/test_smart_home.py
tests/test_smart_home_capability_integration.py
tests/test_smart_home_skill.py
tests/test_smart_home_text_normalizer.py

Result:

104 passed

Tuya Read-Only Live Gate

Live test:

python tools/test_tuya_readonly_live.py

Validated against the real Tuya Cloud environment:

Cloud connection

authentication

real-device discovery

device metadata

online state

power state

device status

switch datapoint retrieval

clean disconnect

Observed live environment:

Devices discovered: 2

An online smart plug exposed:

category: cz
switch datapoint: switch_1

Validated result:

Tuya read-only live gate: PASS

No real Tuya credentials or secrets are recorded in project
documentation.

Tuya Controlled Power Live Gate

Live test:

python tools/test_tuya_power_control_live.py

The gate requires explicit YES confirmation before changing physical
device state.

Validated sequence:

Original state: False
Requested state: True
Verified changed state: True

Power transition: PASS

Restoring original state: True -> False
Restored state verified: False

Power restore: PASS
Tuya controlled power live gate: PASS

The gate records the original state and restores it before successful
completion instead of assuming a fixed final state.

This is an explicit safety requirement for physical-device validation.

Tuya Failure Semantics

Current Tuya behavior preserves explicit failure boundaries:

network errors propagate

HTTP errors propagate

malformed response data fails explicitly

Tuya success=false responses fail explicitly

unsupported power datapoints fail explicitly

command verification is bounded

verification exhaustion does not retry indefinitely

cancellation propagates rather than being swallowed

The power-control verification loop is bounded.

Current verification configuration in the validated implementation:

maximum attempts: 10
retry delay: 0.5 seconds

No uncontrolled retry loop is introduced.

Safety

Current architectural safety requirements include:

safety before automation

confirmation for side effects

read-only automatic capabilities where allowed

explicit confirmation for physical-device side effects

bounded autonomous replanning

bounded context assembly

memory-domain separation

durable memory retention

bounded turn history

bounded production execution time

bounded recovery attempts

single-attempt standard-AI fallback

no recursive recovery

non-retryable failures remain explicit

external cancellation propagation

backward compatibility whenever possible

Turn Tracing and Observability

Production turn records can include:

turn ID

route/source

status

duration

timestamps

failure classification

reliability outcome

recovery execution metadata

Execution and planner infrastructure also provide bounded operational
diagnostics for reliability and recovery behavior.

Configuration Baseline

Environment-based configuration is used.

Example smart-home development configuration:

SMART_HOME_PROVIDER=mock

Production Tuya configuration requires:

SMART_HOME_PROVIDER=tuya
TUYA_ACCESS_ID=
TUYA_ACCESS_KEY=
TUYA_ENDPOINT=

Real secrets belong only in the local .env.

They must not be committed to source control or documentation.

Sprint 7 Automated Validation

Validated static and automated gates:

Compile: PASS
Ruff: PASS
Tuya adapter contract: 73 passed
Smart Home regression: 104 passed
Full regression: 882 passed

Full regression command:

python -m pytest -q

Compile validation:

python -m compileall -q src tests tools

Static analysis:

ruff check src tests tools

Sprint 7 Live Validation

Validated live gates:

Tuya read-only live gate   : PASS
Tuya physical control gate : PASS
Original-state restoration : PASS
Clean disconnect           : PASS

Sprint 7 therefore includes both automated contract coverage and
real-world Cloud/device validation.

Current Quality Baseline

Validated Sprint 7 release:

JarvisAI 0.7.0-alpha.1

Release checkpoint:

Tag    : v0.7.0-alpha.1
Commit : d99be25

Sprint 7 release quality state:

Python compile validation : PASS
Ruff                      : PASS
Tuya adapter contract     : 73 passed
Smart Home regression     : 104 passed
Full regression           : 882 passed
Tuya read-only live gate  : PASS
Tuya physical control     : PASS
Original-state restore    : PASS

Current post-release hardening baseline:

Commit          : d99be25
Branch          : main
Remote          : origin/main
Working tree    : clean
Full regression : 981 passed
Ruff            : PASS

Post-release hardening completed after v0.7.0-alpha.1:

- operational health and heartbeat reliability hardening
- degraded subsystem startup reliability hardening
- retirement of legacy plugin runtime routing

Sprint 8.1 runtime reliability and safety work completed:

- improved natural-language system health routing
- added aggregate Smart Home status queries
- enforced explicit confirmation for Smart Home side effects
- preserved read-only Smart Home status and device-list queries while
  side-effect confirmation is pending
- validated confirmation, cancellation, physical execution, and
  original-state restoration against live Tuya devices

Sprint 8.1 validation baseline:

Ruff                                : PASS
Full regression                     : 946 passed
Tuya aggregate status live gate     : PASS
Tuya device status live gate        : PASS
Tuya side-effect confirmation gate  : PASS
Tuya cancellation gate              : PASS
Tuya original-state restoration     : PASS

Sprint 8.2 voice confirmation safety integration completed:

- exposed pending Smart Home confirmation through the shared pending
  Smart Home state used by the voice dialogue runtime
- ensured Smart Home cancellation clears both device clarification and
  side-effect confirmation state
- added VoiceDialogueRuntime integration coverage for confirmation,
  cancellation, and read-only status while confirmation is pending
- preserved bounded voice follow-up behavior while Smart Home
  confirmation is active

Sprint 8.2 validation baseline:

Ruff                              : PASS
Full regression                   : 951 passed
Voice confirmation integration    : PASS
Voice cancellation integration    : PASS
Voice read-only pending query     : PASS

Sprint 8.3 voice Tuya live safety validation completed:

- validated production microphone selection against the real Windows
  audio environment
- validated the Windows WASAPI representation of the RØDE NT-USB Mini
  for production microphone capture
- validated production microphone capture through OpenAI STT
- validated spoken Smart Home side-effect confirmation through the
  production voice dialogue runtime
- validated spoken Smart Home cancellation through the production voice
  dialogue runtime
- confirmed that cancellation clears the pending Smart Home action
  without executing it
- added repeatable live gates for voice Tuya confirmation and
  cancellation

Sprint 8.3 validation baseline:

Ruff                              : PASS
Full regression                   : 952 passed
Microphone -> STT live gate       : PASS
Voice Tuya confirmation live gate : PASS
Voice Tuya cancellation live gate : PASS

Sprint 8.4 audio-device diagnostics and observability hardening completed:

- exposed selected production audio-device metadata through runtime
  health diagnostics
- added doctor reporting for input and output device name, index,
  Windows host API, and sample rate
- preserved existing health-state and criticality semantics
- retained compatibility with generic placeholder audio services used
  by readiness tests
- validated the production doctor path against the active Windows
  WASAPI microphone and speaker endpoints

Sprint 8.4 validation baseline:

Ruff                              : PASS
Full regression                   : 954 passed
Audio runtime diagnostics         : PASS
Doctor audio endpoint reporting   : PASS
Production doctor live gate       : PASS

Sprint 8.5 resilience runtime diagnostics and observability hardening
completed:

- exposed the production resilience runtime snapshot through structured
  health diagnostics
- added explicit degraded resilience health reporting while preserving
  noncritical operational-health semantics
- exposed resilience summary, plan and step counters, retries, timeouts,
  circuit-breaker rejections, bulkhead rejections, and capability
  failure counts through the system doctor
- retained backward compatibility with generic placeholder resilience
  runtime services that do not expose snapshot diagnostics
- preserved existing operational readiness and criticality semantics

Sprint 8.5 validation baseline:

Ruff                                : PASS
Full regression                     : 956 passed
Resilience runtime health reporting : PASS
Degraded resilience diagnostics     : PASS
Doctor resilience reporting         : PASS

Sprint 8.6 wake cancellation boundary reliability hardening completed:

- added explicit regression coverage for active wake-wait cancellation
  and cleanup
- validated that the wake activation boundary can wait again after
  cancellation
- validated parent-task cancellation propagation
- preserved concurrent-wait rejection semantics
- confirmed that cancelling an active boundary wait does not close the
  wake-word service
- replaced direct wake cancellation diagnostic console output with the
  shared structured logging infrastructure
- preserved existing wake-word detection behavior

Sprint 8.6 validation baseline:

Ruff                            : PASS
Full regression                 : 962 passed
Wake-focused regression         : 37 passed
Wake cancellation boundary      : PASS
Wake cancellation observability : PASS

Sprint 8.7 voice capture cancellation boundary hardening completed:

- added cooperative cancellation support to AudioRecorder VAD capture
- added cooperative cancellation support to adaptive noise calibration
- moved blocking recorder operations out of the asyncio event loop
- added explicit STT recorder-worker lifecycle ownership
- shielded recorder workers from direct asyncio cancellation
- cancellation now signals the recorder and waits for worker shutdown
  before propagating CancelledError
- validated VoiceService IDLE restoration after listening cancellation
- validated assistant follow-up timeout cancellation cleanup
- preserved existing normal voice and wake behavior

Sprint 8.7 validation baseline:

Ruff                            : PASS
Full regression                 : 968 passed
VAD capture cancellation        : PASS
Calibration cancellation        : PASS
STT worker cancellation         : PASS
Voice session cleanup           : PASS
Follow-up timeout cleanup       : PASS

Implementation commit:

cf9ed9e

Sprint 8.8 continuous voice cancellation semantics hardening completed:

- preserved external cancellation semantics across
  VoiceService.run_continuous()
- continuous voice now propagates CancelledError after cleanup
- preserved continuous_running reset during cancellation
- preserved SessionState.IDLE restoration during cancellation
- added automated coverage for cancellation while waiting for speech
- added automated coverage for cancellation during idle delay
- preserved existing continuous voice behavior

Sprint 8.8 validation baseline:

Ruff                                : PASS
Full regression                     : 970 passed
Continuous voice cancellation       : PASS
Listening cancellation propagation  : PASS
Idle-delay cancellation propagation : PASS
Voice session cleanup               : PASS

Implementation commit:

3e18908

Sprint 8.9 database transaction cancellation and lifecycle reliability
hardening completed:

- database transactions now explicitly roll back on external
  cancellation
- CancelledError propagation is preserved after rollback
- cancellation during commit is also covered
- successful sessions continue to commit normally
- ordinary failures continue to roll back normally
- database shutdown lifecycle state is validated for both successful
  and failed engine disposal

Sprint 8.9 validation baseline:

Ruff                         : PASS
Full regression              : 981 passed
Transaction cancellation     : PASS
Commit cancellation rollback : PASS
Shutdown lifecycle           : PASS

Implementation commit:

d99be25

The v0.7.0-alpha.1 release checkpoint remains the validated Sprint 7
release baseline. The current main branch includes additional
post-release reliability, architecture hardening, Sprint 8.1 runtime
safety work, Sprint 8.2 voice confirmation safety integration, Sprint
8.3 voice Tuya live safety validation, Sprint 8.4 audio-device
diagnostics and observability hardening, Sprint 8.5 resilience runtime
diagnostics and observability hardening, and Sprint 8.6 wake
cancellation boundary reliability hardening that have not yet been
assigned a new release tag.



Architecture Decisions

Current documented decisions:

ADR-001

Responses API is the standard AI interface.

ADR-002

ConversationManager is the entry point for user requests.

ADR-003

Planning is separated from execution.

ADR-004

Execution Policy controls confirmation for side effects.

ADR-005

AI Agent Runtime orchestrates planning, execution, reflection, and
memory.

ADR-006

Dependency injection uses the central service container.

ADR-007

Read-only capabilities execute automatically where allowed.

Side-effect capabilities require explicit confirmation.

ADR-008

Production code must pass the required:

Ruff

Pytest

compile validation

relevant live gates

Definition of Done

A production feature is complete when:

implementation is complete

type and async behavior are appropriate

error handling is explicit

tests are added or updated

relevant focused regression passes

full regression passes

Ruff passes

compile validation passes

relevant live gate passes

documentation is aligned

Git working tree is clean at the release checkpoint

Current Boundaries

JarvisAI remains an alpha-stage project.

The current baseline validates substantial production-oriented
subsystems, but it does not imply that every planned JARVIS capability
is complete.

New work must not weaken:

Sprint 6 voice-runtime reliability

Sprint 7 Tuya reliability

cancellation semantics

side-effect confirmation

bounded recovery

bounded replanning

context boundaries

memory-domain safety

regression coverage

hardware validation requirements

Next Milestone

Sprint 8 begins from the validated Sprint 7 baseline.

Starting release:

v0.7.0-alpha.1

Sprint 8.1 runtime reliability and Smart Home confirmation safety work
has been completed and validated.

Sprint 8.2 voice Smart Home confirmation safety integration has also
been completed and validated.

Sprint 8.3 voice Tuya live safety validation has also been completed
and validated against the production microphone, STT, voice dialogue,
and physical Tuya integration path.

Sprint 8.4 audio-device diagnostics and observability hardening has
also been completed and validated.

Sprint 8.5 resilience runtime diagnostics and observability hardening
has also been completed and validated.

Sprint 8.6 wake cancellation boundary reliability hardening has also
been completed and validated.

Sprint 8.7 voice capture cancellation boundary hardening has also
been completed and validated.

Sprint 8.8 continuous voice cancellation semantics hardening has also
been completed and validated.

The next Sprint 8 scope has not yet been fixed.

Scope selection should be based on:

current implementation state

remaining production gaps

architecture consistency

reliability risk

regression risk

safety implications

real-world usability

No Sprint 8 feature should be considered complete until its
implementation, automated regression, documentation, and relevant live
validation have passed.