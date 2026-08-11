from __future__ import annotations

__version__ = "0.6.0-alpha.1"


def get_version() -> str:
    return __version__


def get_version_display() -> str:
    return f"JarvisAI {__version__}"