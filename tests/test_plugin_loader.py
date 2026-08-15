from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from jarvis.core import plugin_loader


def test_legacy_plugin_loader_returns_empty_when_directory_missing(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "plugins"

    with patch.object(
        plugin_loader,
        "PLUGIN_DIR",
        missing,
    ):
        result = plugin_loader.load_plugins()

    assert result == []


def test_legacy_plugin_loader_lists_candidate_modules(
    tmp_path: Path,
) -> None:
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()

    (plugin_dir / "alpha.py").write_text(
        "",
        encoding="utf-8",
    )
    (plugin_dir / "_internal.py").write_text(
        "",
        encoding="utf-8",
    )
    (plugin_dir / "beta.py").write_text(
        "",
        encoding="utf-8",
    )

    with patch.object(
        plugin_loader,
        "PLUGIN_DIR",
        plugin_dir,
    ):
        result = plugin_loader.load_plugins()

    assert result == [
        "alpha",
        "beta",
    ]