JarvisAI 0.7.0-alpha.1

Sprint 7 - Tuya Smart Home Reliability

JarvisAI 0.7.0-alpha.1 establishes the validated Sprint 7
Tuya smart-home production baseline on top of the Sprint 6
voice-runtime reliability baseline.

Release Summary

Sprint 7 focused on hardening the existing Tuya smart-home path
rather than adding new providers or unrelated features.

Validated production path:

JarvisAI
-> SmartHomeService
-> TuyaAdapter
-> Tuya Cloud
-> Physical Smart Device
-> State Verification

Highlights

production Tuya Cloud configuration

provider selection through SMART_HOME_PROVIDER

Tuya credential handling

configurable Tuya endpoint

Tuya Cloud authentication

access-token acquisition

HMAC-SHA256 request signing

canonical query handling

JSON body hashing

signed request headers

real device discovery

device metadata mapping

device status retrieval

online-state mapping

power-state mapping

switch datapoint resolution

ON/OFF/toggle execution

post-command status verification

bounded verification retries

connection and disconnect lifecycle

cancellation propagation

network, HTTP, and Tuya API failure propagation

Tuya Contract Validation

Dedicated Tuya adapter contract coverage reached:

73 passed

Coverage includes authentication, signing, discovery, status,
device mapping, power commands, verification, failure propagation,
connection lifecycle, and cancellation semantics.

Smart Home Regression

Focused smart-home regression:

104 passed

Validated test set:

tests/test_tuya_adapter_contract.py
tests/test_smart_home.py
tests/test_smart_home_capability_integration.py
tests/test_smart_home_skill.py
tests/test_smart_home_text_normalizer.py

Full Regression

Sprint 7 full regression:

882 passed

Static gates:

Compile: PASS
Ruff: PASS
Smart Home regression: PASS
Full regression: PASS

Tuya Read-Only Live Validation

Live gate:

python tools/test_tuya_readonly_live.py

Validated:

Tuya Cloud connection

authentication

real device discovery

online-state retrieval

device-status retrieval

switch datapoint retrieval

clean disconnect

Result:

Tuya read-only live gate: PASS

Controlled Physical Power Validation

Live gate:

python tools/test_tuya_power_control_live.py

The gate requires explicit confirmation before changing physical state.

Validated flow:

Initial state: OFF
Requested state: ON
Changed state verified: ON
Original state restored: OFF
Restore verified: PASS

Final result:

Power transition: PASS
Power restore: PASS
Tuya controlled power live gate: PASS

Safety

The physical-device live gate records the original state before
testing and restores that original state before successful completion.

Side-effect operations continue to require explicit confirmation.

Failure and Cancellation Semantics

Current Tuya behavior includes:

network errors propagate

HTTP errors propagate

malformed JSON errors propagate

Tuya success=false responses fail explicitly

unsupported power datapoints fail explicitly

post-command verification is bounded

cancellation is propagated rather than swallowed

Configuration

Example provider configuration:

SMART_HOME_PROVIDER=mock

Production Tuya configuration:

SMART_HOME_PROVIDER=tuya
TUYA_ACCESS_ID=
TUYA_ACCESS_KEY=
TUYA_ENDPOINT=

Real credentials belong only in the local .env.

Release Checkpoint

Version : 0.7.0-alpha.1
Git tag : v0.7.0-alpha.1
Commit  : 6825df0

Python packaging may display:

0.7.0a1

Previous Validated Baseline

Sprint 6 established the wake-word and continuous voice-runtime
reliability baseline:

Version : 0.6.0-alpha.1
Git tag : v0.6.0-alpha.1
Commit  : 3e18908

Sprint 7 builds on that validated voice-runtime baseline.

Current Quality Baseline

Compile validation          : PASS
Ruff                        : PASS
Tuya adapter contract       : 73 passed
Smart Home regression       : 104 passed
Full regression             : 970 passed
Tuya read-only live gate    : PASS
Tuya physical control gate  : PASS
Original-state restoration  : PASS
Audio runtime diagnostics           : PASS
Audio input endpoint reporting      : PASS
Audio output endpoint reporting     : PASS

Post-Release Development

Additional reliability, architecture, and runtime safety work has been
completed on main after the v0.7.0-alpha.1 release checkpoint.

Current post-release development baseline:


Commit          : 3709072
Branch          : main
Full regression : 995 passed
Ruff            : PASS

Completed post-release hardening:

- operational health and heartbeat reliability hardening
- degraded subsystem startup reliability hardening
- retirement of legacy plugin runtime routing

Sprint 8.1 runtime reliability and Smart Home confirmation safety:

- improved natural-language system health routing
- added aggregate Smart Home status queries
- enforced explicit confirmation for Smart Home side effects
- preserved read-only Smart Home status and device-list queries while
  side-effect confirmation is pending
- prevented repeated side-effect commands from bypassing a pending
  confirmation
- validated confirmation and cancellation against live Tuya devices

Sprint 8.1 live validation:

Tuya aggregate status live gate     : PASS
Tuya device status live gate        : PASS
Tuya side-effect confirmation gate  : PASS
Tuya cancellation gate              : PASS
Tuya original-state restoration     : PASS

These changes do not replace the validated v0.7.0-alpha.1 Sprint 7
release checkpoint. No new release tag has been assigned to the current
post-release development baseline.

Sprint 8.2 voice Smart Home confirmation safety integration:

- exposed pending Smart Home confirmation through the shared pending
  Smart Home state used by the voice dialogue runtime
- ensured Smart Home cancellation clears both device clarification and
  side-effect confirmation state
- added VoiceDialogueRuntime integration coverage for confirmation,
  cancellation, and read-only status while confirmation is pending
- preserved bounded voice follow-up behavior while Smart Home
  confirmation is active

Sprint 8.2 validation:

Ruff                              : PASS
Full regression                   : 954 passed
Audio runtime diagnostics         : PASS
Doctor audio endpoint reporting   : PASS
Production doctor live gate       : PASS

Sprint 8.3 voice Tuya live safety validation:

- validated production microphone selection against the real Windows
  audio environment
- validated the Windows WASAPI representation of the RรDE NT-USB Mini
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

Sprint 8.3 validation:

Ruff                              : PASS
Full regression                   : 952 passed
Microphone -> STT live gate       : PASS
Voice Tuya confirmation live gate : PASS
Voice Tuya cancellation live gate : PASS

Sprint 8.4 audio-device diagnostics and observability hardening:

- exposed selected production audio-device metadata through runtime
  health diagnostics
- added doctor reporting for input and output device name, index,
  Windows host API, and sample rate
- preserved existing health-state and criticality semantics
- retained compatibility with runtime readiness tests that use generic
  placeholder audio services
- validated the production doctor path against the active Windows
  WASAPI microphone and speaker endpoints

Sprint 8.4 validation:

Ruff                              : PASS
Full regression                   : 954 passed
Audio runtime diagnostics         : PASS
Doctor audio endpoint reporting   : PASS
Production doctor live gate       : PASS

Sprint 8.5 resilience runtime diagnostics and observability hardening:

- exposed the production resilience runtime snapshot through structured
  health diagnostics
- added explicit degraded resilience health reporting while preserving
  noncritical operational-health semantics
- added doctor reporting for resilience summary, plan and step metrics,
  retries, timeouts, circuit-breaker rejections, bulkhead rejections,
  and capability failure counts
- retained backward compatibility with generic placeholder resilience
  runtime services that do not expose snapshot diagnostics
- preserved existing operational readiness behavior while improving
  resilience observability

Sprint 8.5 validation:

Ruff                                : PASS
Full regression                     : 956 passed
Resilience runtime health reporting : PASS
Degraded resilience diagnostics     : PASS
Doctor resilience reporting         : PASS


Sprint 8.6 wake cancellation boundary reliability hardening:

- added explicit regression coverage for active wake-wait cancellation
  and cleanup
- validated repeated wake waits after cancellation
- validated parent-task cancellation propagation
- preserved concurrent-wait rejection semantics
- confirmed that cancelling an active boundary wait does not close the
  wake-word service
- replaced direct wake cancellation diagnostic console output with the
  shared structured logging infrastructure
- preserved existing wake-word detection behavior

Sprint 8.6 validation:

Ruff                            : PASS
Full regression                 : 962 passed
Wake-focused regression         : 37 passed
Wake cancellation boundary      : PASS
Wake cancellation observability : PASS

Sprint 8.7 voice capture cancellation boundary hardening:

- added cooperative cancellation to VAD-driven microphone capture
- added cooperative cancellation to adaptive noise calibration
- moved blocking STT recorder operations off the asyncio event loop
- shielded recorder workers from direct asyncio task cancellation
- ensured STT cancellation signals the recorder and waits for worker
  termination before propagating CancelledError
- validated VoiceService session cleanup after listening cancellation
- validated assistant follow-up timeout behavior across the voice
  cancellation boundary
- preserved normal STT, voice-dialogue, and wake transition behavior

Sprint 8.7 validation:

Ruff                            : PASS
Full regression                 : 968 passed
VAD capture cancellation        : PASS
Calibration cancellation        : PASS
STT worker cancellation         : PASS
Voice session cleanup           : PASS
Follow-up timeout cleanup       : PASS

Sprint 8.8 continuous voice cancellation semantics hardening:

- preserved external asyncio cancellation across the continuous voice
  runtime boundary
- changed VoiceService.run_continuous() to propagate CancelledError
  after cleanup instead of converting cancellation into normal
  completion
- preserved continuous_running cleanup during cancellation
- preserved SessionState.IDLE restoration during cancellation
- added automated coverage for cancellation while waiting for speech
- added automated coverage for cancellation during idle delay
- preserved existing continuous voice behavior

Sprint 8.8 validation:

Ruff                                : PASS
Full regression                     : 970 passed
Continuous voice cancellation       : PASS
Listening cancellation propagation  : PASS
Idle-delay cancellation propagation : PASS
Voice session cleanup               : PASS

Sprint 8.9 database transaction cancellation and lifecycle reliability
hardening:

- fixed missing explicit rollback when database transactions are
  cancelled externally
- preserved CancelledError propagation after rollback
- added coverage for cancellation during transaction execution
- added coverage for cancellation during commit
- validated successful commit and ordinary rollback semantics
- validated database shutdown state after successful and failed engine
  disposal

Sprint 8.9 validation:

Ruff                         : PASS
Full regression              : 981 passed
Transaction cancellation     : PASS
Commit cancellation rollback : PASS
Shutdown lifecycle           : PASS

Sprint 8.10 TTS playback async and cancellation boundary hardening:

- moved blocking AudioPlayer playback off the asyncio event loop
- added explicit playback worker ownership in TTSService
- added cancellation cleanup that stops active playback
- waits for playback worker termination before propagating cancellation
- preserves CancelledError semantics
- avoids stopping playback when cancellation occurs during TTS
  generation before playback begins
- preserved existing voice and wake runtime behavior

Sprint 8.10 validation:

Ruff                         : PASS
Full regression              : 986 passed
Async playback boundary      : PASS
Playback cancellation        : PASS
Playback worker cleanup      : PASS
Generation cancellation      : PASS

Sprint 8.11 conversation memory atomic turn persistence hardening:

- added MemoryService.save_turn() for atomic conversation-turn
  persistence
- stores user and assistant messages within one database session
- changed ConversationManager from two independent save_message()
  operations to one save_turn() operation
- removed the partial-turn persistence boundary between user and
  assistant message commits
- migrated conversation test fixtures to the atomic save_turn contract
- preserved existing conversation and voice runtime behavior

Sprint 8.11 validation:

Ruff                         : PASS
Full regression              : 988 passed
Atomic turn persistence      : PASS
Single-session turn storage  : PASS
Conversation compatibility   : PASS

Sprint 8.12 AI agent memory retention failure and cancellation semantics
hardening:

- separated primary durable persistence from post-write retention
  maintenance semantics
- ordinary retention failures no longer make successful durable writes
  appear to have failed
- added last_retention_error diagnostics
- retained last_retention_result for successful retention enforcement
- preserved CancelledError propagation during retention cancellation
- preserved ordinary primary persistence failure propagation
- strengthened lifecycle characterization around partial-success state

Sprint 8.12 validation:

Ruff                         : PASS
Full regression              : 991 passed
Primary persistence          : PASS
Retention failure isolation  : PASS
Retention diagnostics        : PASS
Cancellation propagation     : PASS

Sprint 8.13 planner execution persistence concurrent startup and
cancellation hardening:

- serialized ExecutionPersistenceService repository startup
- prevented duplicate repository initialization under concurrent callers
- preserved sequential startup idempotency
- preserved retryability after startup failure
- preserved retryability after startup cancellation
- isolated cancellation of waiting startup callers from active startup
- preserved lazy initialization for execution persistence read/write paths

Sprint 8.13 validation:

Ruff                         : PASS
Full regression              : 995 passed
Concurrent startup           : PASS
Failure retryability         : PASS
Cancellation retryability    : PASS
Waiting caller isolation     : PASS

Sprint 8.14 planner execution persistence failure isolation and
cancellation semantics hardening:

- separated completed plan execution outcome from post-execution
  persistence failure
- ordinary persistence failures no longer replace completed execution
  results with persistence exceptions
- added last_persistence_error diagnostics
- preserved successful and failed PlanExecutionResult semantics
- preserved CancelledError propagation during persistence cancellation
- prevented persistence maintenance failure from misrepresenting the
  actual execution outcome

Sprint 8.14 validation:

Ruff                         : PASS
Full regression              : 998 passed
Execution outcome isolation  : PASS
Persistence diagnostics      : PASS
Failed execution preservation: PASS
Cancellation propagation     : PASS

Next Milestone

Sprint 8 began from the validated v0.7.0-alpha.1 baseline.

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

Sprint 8.10 TTS playback async and cancellation boundary hardening has
also been completed and validated.

Sprint 8.11 conversation memory atomic turn persistence hardening has
also been completed and validated.

Sprint 8.14 planner execution persistence failure isolation and
cancellation semantics hardening has also been completed and validated.

The next Sprint 8 scope has not yet been fixed.

No further Sprint 8 feature should be considered complete until its
implementation, automated regression, documentation, and relevant live
validation have passed.
