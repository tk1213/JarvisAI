# Sprint 6 Pack D Hotfix 3.1 — Audio-Time VAD Boundaries

This hotfix changes callback VAD timing from wall-clock time to captured audio
sample counts.

## Why

Callback frames can be delivered faster than real time in unit tests and in
buffered audio backends. Using `time.monotonic()` for `max_wait_seconds` and
`max_record_seconds` makes behavior depend on delivery timing instead of audio
duration.

The production contract should be:

```text
audio samples received / sample rate = elapsed audio duration
```

## Manual patch

Open:

```text
src\jarvis\audio\recorder.py
```

Inside `record_until_silence()`, replace the wall-clock timing variables:

```python
wait_started = time.monotonic()
record_started: float | None = None
```

with:

```python
waiting_samples = 0
recording_samples = 0

max_wait_samples = max(
    1,
    round(
        max_wait_seconds
        * rate
    ),
)

max_record_samples = max(
    1,
    round(
        max_record_seconds
        * rate
    ),
)
```

Then immediately after:

```python
rms = self._rms(
    frame
)
```

add:

```python
frame_sample_count = int(
    frame.shape[0]
)
```

Inside the `if not triggered:` branch, add:

```python
waiting_samples += frame_sample_count
```

Replace:

```python
record_started = time.monotonic()
```

with:

```python
recording_samples = sum(
    int(
        item.shape[0]
    )
    for item in pre_roll
)
```

Replace the max-wait condition:

```python
if (
    time.monotonic()
    - wait_started
    >= max_wait_seconds
):
```

with:

```python
if waiting_samples >= max_wait_samples:
```

After:

```python
captured.append(
    frame.copy()
)
```

add:

```python
recording_samples += frame_sample_count
```

Finally replace:

```python
if (
    record_started is not None
    and (
        time.monotonic()
        - record_started
    )
    >= max_record_seconds
):
```

with:

```python
if recording_samples >= max_record_samples:
```

After this change remove the unused import:

```python
import time
```

## Gate

```powershell
ruff check src\jarvis\audio\recorder.py --fix
python tools/run_sprint_6_pack_d_hotfix3_gate.py
```
