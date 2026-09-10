from __future__ import annotations

from unittest.mock import patch

import pytest

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container


@pytest.mark.asyncio
async def test_application_forwards_headless_registration() -> None:
    app = JarvisApplication()

    with (
        patch(
            "jarvis.core.application.ServiceFactory.register_all",
            side_effect=RuntimeError(
                "controlled registration stop"
            ),
        ) as register_all,
        pytest.raises(
            RuntimeError,
            match="controlled registration stop",
        ),
    ):
        await app.start(
            start_background_tasks=False,
            include_voice=False,
        )

    register_all.assert_called_once_with(
        include_voice=False,
    )

    assert app.started is False
    assert len(container) == 0