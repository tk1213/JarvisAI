from __future__ import annotations

from jarvis.audio.manager import AudioManager


def main() -> None:
    manager = AudioManager()

    print("Sprint 5 Pack B — Production AudioManager Integration")
    print("-" * 60)

    print("Available input devices:")
    for device in manager.input_devices():
        print(
            f"  [{device.index}] {device.name} "
            f"({device.host_api})"
        )

    print("Available output devices:")
    for device in manager.output_devices():
        print(
            f"  [{device.index}] {device.name} "
            f"({device.host_api})"
        )

    print()
    print(
        "Selected input:",
        manager.input_device,
        manager.input_info.name,
    )
    print(
        "Selected output:",
        manager.output_device,
        manager.output_info.name,
    )

    assert manager.input_info.max_input_channels > 0
    assert manager.output_info.max_output_channels > 0

    print("Device enumeration: PASS")
    print("Input selection: PASS")
    print("Output selection: PASS")
    print("Sprint 5 Pack B live gate: PASS")


if __name__ == "__main__":
    main()
