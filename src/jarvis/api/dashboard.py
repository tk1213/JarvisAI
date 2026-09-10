from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from jarvis.core.logger import log


def default_dashboard_directory() -> Path:
    return Path(__file__).resolve().parents[3] / "dashboard" / "dist"


def mount_dashboard(
    app: FastAPI,
    *,
    directory: Path | None = None,
) -> bool:
    dashboard_directory = (
        directory if directory is not None else default_dashboard_directory()
    )

    index_file = dashboard_directory / "index.html"

    if not index_file.is_file():
        log.warning(
            "Dashboard build not found at {}. Run `npm run build --prefix dashboard`.",
            dashboard_directory,
        )
        return False

    app.mount(
        "/",
        StaticFiles(
            directory=dashboard_directory,
            html=True,
        ),
        name="dashboard",
    )

    return True
