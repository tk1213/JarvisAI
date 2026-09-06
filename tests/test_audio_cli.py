from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from jarvis.cli import create_parser, main
from jarvis.main import audio_devices


@pytest.mark.asyncio
async def test_audio_devices_lists_available_and_selected_devices(
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_device = Mock()
    input_device.index = 18
    input_device.name = "Desktop Microphone"
    input_device.host_api = "Windows WASAPI"
    input_device.default_sample_rate = 48000

    output_device = Mock()
    output_device.index = 16
    output_device.name = "Speakers Realtek"
    output_device.host_api = "Windows WASAPI"
    output_device.default_sample_rate = 48000

    backup_output = Mock()
    backup_output.index = 7
    backup_output.name = "Backup Speaker"
    backup_output.host_api = "MME"
    backup_output.default_sample_rate = 44100

   
    audio = Mock()
    audio.input_info = input_device
    audio.output_info = output_device
    audio.input_devices.return_value = (
        input_device,
    )
    audio.output_devices.return_value = (
        output_device,
        backup_output,
    )

    app = AsyncMock()

    with (
        patch(
            "jarvis.main.JarvisApplication",
            return_value=app,
        ),
        patch(
            "jarvis.main.container.resolve",
            return_value=audio,
        ),
    ):
        await audio_devices()

    output = capsys.readouterr().out

    assert "Audio Devices" in output

    assert "Input Devices" in output
    assert "[18] Desktop Microphone" in output
    assert "Windows WASAPI" in output
    assert "48000 Hz" in output

    assert "Output Devices" in output
    assert "[16] Speakers Realtek" in output
    assert "[7] Backup Speaker" in output
    assert "44100 Hz" in output

    assert "Selected" in output
    assert "Input : [18] Desktop Microphone" in output
    assert "Output: [16] Speakers Realtek" in output

    app.start.assert_awaited_once_with(
        start_background_tasks=False,
    )
    app.shutdown.assert_awaited_once()


def test_cli_parser_supports_audio_command() -> None:
    parser = create_parser()

    args = parser.parse_args(
        ["audio"],
    )

    assert args.command == "audio"
    

def test_cli_dispatches_audio_command() -> None:
    audio_command = Mock(
        return_value="audio-coroutine",
    )

    with (
        patch(
            "jarvis.cli.asyncio.run",
        ) as run_async,
        patch(
            "jarvis.cli.audio_devices",
            new=audio_command,
        ),
        patch(
            "jarvis.cli.argparse.ArgumentParser.parse_args",
            return_value=Mock(
                command="audio",
            ),
        ),
    ):
        main()

    audio_command.assert_called_once_with()
    run_async.assert_called_once_with(
        "audio-coroutine",
    )