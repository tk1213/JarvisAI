from jarvis.version import (
    __version__,
    get_version,
    get_version_display,
)


def test_version_matches_current_release() -> None:
    assert __version__ == "0.7.0-alpha.1"


def test_get_version_returns_current_version() -> None:
    assert get_version() == __version__


def test_get_version_display_uses_current_version() -> None:
    assert (
        get_version_display()
        == f"JarvisAI {__version__}"
    )