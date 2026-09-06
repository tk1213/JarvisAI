from __future__ import annotations

from unittest.mock import MagicMock, patch

from jarvis.audio.stream import AudioStream


def test_stream_defaults_to_selected_input_device_sample_rate() -> None:
    audio = MagicMock()
    audio.input_info.default_sample_rate = 48000

    with patch(
        "jarvis.audio.stream.AudioManager",
        return_value=audio,
    ):
        stream = AudioStream()

    assert stream.sample_rate == 48000
    assert stream.frame_samples == 960