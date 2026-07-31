from __future__ import annotations

import pytest


@pytest.fixture
def sample_text():
    return "Hello Jarvis"


@pytest.fixture
def sample_command():
    return "Turn on the living room light"