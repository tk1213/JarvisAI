from __future__ import annotations

from unittest.mock import MagicMock, patch

from jarvis.audio.stream import AudioStream


class FakeRawInputStream:
    exit_count = 0

    def __init__(
        self,
        *,
        samplerate,
        blocksize,
        dtype,
        channels,
        device,
    ) -> None:
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.dtype = dtype
        self.channels = channels
        self.device = device
        self.read_count = 0

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ):
        type(self).exit_count += 1

    def read(
        self,
        frames,
    ):
        self.read_count += 1
        return b"\x01\x02", False


class OverflowThenDataStream(FakeRawInputStream):
    def read(
        self,
        frames,
    ):
        self.read_count += 1

        if self.read_count == 1:
            return b"\x00\x00", True

        return b"\x03\x04", False


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

def test_closing_frames_generator_closes_input_stream() -> None:
    audio = MagicMock()
    audio.input_info.default_sample_rate = 48000
    audio.input_device = 7

    FakeRawInputStream.exit_count = 0

    with (
        patch(
            "jarvis.audio.stream.AudioManager",
            return_value=audio,
        ),
        patch(
            "jarvis.audio.stream.sd.RawInputStream",
            FakeRawInputStream,
        ),
    ):
        stream = AudioStream()
        frames = stream.frames()

        assert next(frames) == b"\x01\x02"

        frames.close()

    assert FakeRawInputStream.exit_count == 1


def test_frames_skips_overflow_and_yields_next_valid_frame() -> None:
    audio = MagicMock()
    audio.input_info.default_sample_rate = 48000
    audio.input_device = 7

    OverflowThenDataStream.exit_count = 0

    with (
        patch(
            "jarvis.audio.stream.AudioManager",
            return_value=audio,
        ),
        patch(
            "jarvis.audio.stream.sd.RawInputStream",
            OverflowThenDataStream,
        ),
    ):
        stream = AudioStream()
        frames = stream.frames()

        assert next(frames) == b"\x03\x04"

        frames.close()

    assert OverflowThenDataStream.exit_count == 1