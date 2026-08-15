from __future__ import annotations

from pathlib import Path

from jarvis.core.logger import log

PLUGIN_DIR = Path("src/jarvis/plugins")


def load_plugins() -> list[str]:
    """
    Discover legacy plugin module candidates.

    This compatibility loader no longer imports or starts plugins.
    Runtime extensions should use SkillLoader and SkillManager.
    """

    if not PLUGIN_DIR.exists():
        return []

    candidates = sorted(
        file.stem
        for file in PLUGIN_DIR.glob("*.py")
        if not file.name.startswith("_")
    )

    if candidates:
        log.warning(
            "Legacy plugin discovery found {} candidate(s). "
            "Use the Skill runtime for executable extensions.",
            len(candidates),
        )

    return candidates