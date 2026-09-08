from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from jarvis.cli import create_parser, main
from jarvis.main import audio_devices


@pytest.mark.asyncio
async def test_audio_devices_lists_available_and_selected_devices(
    capsys,
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

    audio = Mock()
    audio.input_info = input_device
    audio.output_info = output_device
    audio.input_devices.return_value = (
        input_device,
    )
    audio.output_devices.return_value = (
        output_device,
    )

    app = Mock()
    app.start = AsyncMock()

    with (
        patch(
            "jarvis.main.JarvisApplication",
            return_value=app,
        ),
        patch(
            "jarvis.main.AudioManager",
            return_value=audio,
        ) as audio_manager,
        patch(
            "jarvis.main._shutdown_application",
            new_callable=AsyncMock,
        ) as shutdown,
    ):
        await audio_devices()

    output = capsys.readouterr().out

    assert "Input Devices" in output
    assert "[18] Desktop Microphone" in output
    assert "Windows WASAPI | 48000 Hz" in output

    assert "Output Devices" in output
    assert "[16] Speakers Realtek" in output

    assert "Selected" in output
    assert "Input : [18] Desktop Microphone" in output
    assert "Output: [16] Speakers Realtek" in output

    app.start.assert_awaited_once_with(
        start_background_tasks=False,
    )

    audio_manager.assert_called_once_with()
    shutdown.assert_awaited_once_with(app)


def test_cli_parser_supports_audio_command() -> None:
    parser = create_parser()

    args = parser.parse_args(
        ["audio"]
    )

    assert args.command == "audio"


def test_cli_dispatches_audio_command() -> None:
    audio_command = Mock(
        return_value="audio-coroutine",
    )

    with (
        patch(
            "sys.argv",
            [
                "jarvis",
                "audio",
            ],
        ),
        patch(
            "jarvis.cli.audio_devices",
            new=audio_command,
        ),
        patch(
            "jarvis.cli.asyncio.run"
        ) as run_async,
    ):
        main()

    audio_command.assert_called_once_with()
    run_async.assert_called_once_with(
        "audio-coroutine"
    )


def test_cli_parser_supports_audio_input_selection() -> None:
    parser = create_parser()

    args = parser.parse_args(
        [
            "audio",
            "input",
            "12",
        ]
    )

    assert args.command == "audio"
    assert args.audio_command == "input"
    assert args.device_index == 12


def test_cli_parser_supports_audio_output_selection() -> None:
    parser = create_parser()

    args = parser.parse_args(
        [
            "audio",
            "output",
            "9",
        ]
    )

    assert args.command == "audio"
    assert args.audio_command == "output"
    assert args.device_index == 9


def test_cli_parser_supports_audio_reset() -> None:
    parser = create_parser()

    args = parser.parse_args(
        [
            "audio",
            "reset",
        ]
    )

    assert args.command == "audio"
    assert args.audio_command == "reset"


def test_cli_dispatches_audio_input_selection() -> None:
    with (
        patch(
            "sys.argv",
            [
                "jarvis",
                "audio",
                "input",
                "12",
            ],
        ),
        patch(
            "jarvis.cli.set_audio_input_device"
        ) as command,
    ):
        main()

    command.assert_called_once_with(12)


def test_cli_dispatches_audio_output_selection() -> None:
    with (
        patch(
            "sys.argv",
            [
                "jarvis",
                "audio",
                "output",
                "9",
            ],
        ),
        patch(
            "jarvis.cli.set_audio_output_device"
        ) as command,
    ):
        main()

    command.assert_called_once_with(9)


def test_cli_dispatches_audio_reset() -> None:
    with (
        patch(
            "sys.argv",
            [
                "jarvis",
                "audio",
                "reset",
            ],
        ),
        patch(
            "jarvis.cli.reset_audio_devices"
        ) as command,
    ):
        main()

    command.assert_called_once_with()

@pytest.mark.asyncio
async def test_audio_devices_does_not_require_registered_audio_service(
    capsys,
) -> None:
    input_device = Mock()
    input_device.index = 8
    input_device.name = "Desktop Microphone"
    input_device.host_api = "Windows DirectSound"
    input_device.default_sample_rate = 44100

    output_device = Mock()
    output_device.index = 16
    output_device.name = "Speakers Realtek"
    output_device.host_api = "Windows WASAPI"
    output_device.default_sample_rate = 48000

    audio = Mock()
    audio.input_info = input_device
    audio.output_info = output_device
    audio.input_devices.return_value = (
        input_device,
    )
    audio.output_devices.return_value = (
        output_device,
    )

    app = Mock()
    app.start = AsyncMock()

    with (
        patch(
            "jarvis.main.JarvisApplication",
            return_value=app,
        ),
        patch(
            "jarvis.main.AudioManager",
            return_value=audio,
        ) as audio_manager,
        patch(
            "jarvis.main.container.resolve",
            side_effect=KeyError(
                "Service 'audio' is not registered."
            ),
        ),
        patch(
            "jarvis.main._shutdown_application",
            new_callable=AsyncMock,
        ) as shutdown,
    ):
        await audio_devices()

    output = capsys.readouterr().out

    assert "[8] Desktop Microphone" in output
    assert "[16] Speakers Realtek" in output

    audio_manager.assert_called_once_with()
    shutdown.assert_awaited_once_with(app)