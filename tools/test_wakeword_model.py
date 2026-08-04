from __future__ import annotations

from pyopen_wakeword import Model, OpenWakeWord


def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Wake Word Model Smoke Test")
    print("=" * 60)
    print()

    print("Available built-in models:")

    for model in Model:
        print(
            f" - {model.name}: {model.value}"
        )

    print()
    print("Selected wake word:")
    print(f" - {Model.HEY_JARVIS.value}")
    print()

    print("Loading HEY_JARVIS model...")

    wake_word = OpenWakeWord.from_builtin(
        Model.HEY_JARVIS
    )

    print()
    print("Wake word model loaded: PASS")
    print(
        f"Engine type : "
        f"{type(wake_word).__name__}"
    )
    print(
        f"Model       : "
        f"{Model.HEY_JARVIS.value}"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()