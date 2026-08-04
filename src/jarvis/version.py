from __future__ import annotations

__version__ = "0.3.0"


def get_version() -> str:
    return __version__


def get_version_display() -> str:
    return f"JarvisAI {__version__}"