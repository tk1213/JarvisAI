from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from jarvis.api.dashboard import mount_dashboard


@pytest.mark.asyncio
async def test_mounts_built_dashboard(
    tmp_path,
) -> None:
    dashboard_directory = tmp_path / "dist"
    dashboard_directory.mkdir()

    index_file = dashboard_directory / "index.html"
    index_file.write_text(
        "<html><body>JarvisAI Dashboard</body></html>",
        encoding="utf-8",
    )

    app = FastAPI()

    mounted = mount_dashboard(
        app,
        directory=dashboard_directory,
    )

    transport = ASGITransport(
        app=app,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert mounted is True
    assert response.status_code == 200
    assert "JarvisAI Dashboard" in response.text


def test_skips_dashboard_when_build_is_missing(
    tmp_path,
) -> None:
    app = FastAPI()

    mounted = mount_dashboard(
        app,
        directory=tmp_path / "missing",
    )

    assert mounted is False
