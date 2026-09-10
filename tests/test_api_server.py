from __future__ import annotations

from unittest.mock import Mock, patch

from jarvis.api.server import run_api_server
from jarvis.config import settings


def test_api_server_uses_configured_endpoint(
    monkeypatch,
) -> None:
    api_app = Mock()

    monkeypatch.setattr(
        settings,
        "api_host",
        "127.0.0.1",
    )
    monkeypatch.setattr(
        settings,
        "api_port",
        8123,
    )
    monkeypatch.setattr(
        settings,
        "log_level",
        "WARNING",
    )

    with (
        patch(
            "jarvis.api.server.create_production_api_app",
            return_value=api_app,
        ) as create_app,
        patch(
            "jarvis.api.server.uvicorn.run",
        ) as uvicorn_run,
    ):
        run_api_server()

    create_app.assert_called_once_with()
    uvicorn_run.assert_called_once_with(
        api_app,
        host="127.0.0.1",
        port=8123,
        log_level="warning",
    )