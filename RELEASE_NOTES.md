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
Commit  : b1b2bc0

Sprint 7 builds on that validated voice-runtime baseline.

Current Quality Baseline

Compile validation          : PASS
Ruff                        : PASS
Tuya adapter contract       : 73 passed
Smart Home regression       : 104 passed
Full regression             : 882 passed
Tuya read-only live gate    : PASS
Tuya physical control gate  : PASS
Original-state restoration  : PASS

Next Milestone

Sprint 8 begins from the validated v0.7.0-alpha.1 baseline.

Sprint 8 scope has not yet been fixed.

No Sprint 8 feature should be considered complete until its
implementation, automated regression, documentation, and relevant
live validation have passed.