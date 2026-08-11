# JarvisAI Project State

## Current milestone

Sprint 5 closeout.

## Production Voice Runtime

Implemented:

- Windows audio device discovery and deterministic selection
- explicit input/output device handling
- production microphone capture
- RMS / peak / silence / clipping diagnostics
- OpenAI STT integration
- VAD speech trigger and silence stop
- ConversationManager voice-turn integration
- TTS playback
- shared AudioManager for recorder/player
- application lifecycle integration
- bounded smart-home voice disambiguation follow-up

Validated hardware path:

```text
RØDE NT-USB Mini
-> VAD
-> OpenAI STT
-> ConversationManager
-> Smart Home / AI
-> TTS
-> Realtek Speakers
```

## Next milestone

Sprint 6 -- Wake Word & Continuous Voice Runtime

Primary goals:

- wake-word activation reliability
- continuous listen / speak loop
- echo / self-trigger protection
- session state transitions
- cancellation / stop commands
- long-running stability tests
