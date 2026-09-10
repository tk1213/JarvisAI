from __future__ import annotations

from unittest.mock import Mock, patch

from jarvis.core.service_factory import ServiceFactory


def test_register_all_includes_voice_by_default() -> None:
    factory = ServiceFactory(
        Mock(),
    )

    with (
        patch.object(
            factory,
            "register_core",
        ) as register_core,
        patch.object(
            factory,
            "register_smart_home",
        ) as register_smart_home,
        patch.object(
            factory,
            "register_ai",
        ) as register_ai,
        patch.object(
            factory,
            "register_voice",
        ) as register_voice,
    ):
        factory.register_all()

    register_core.assert_called_once_with()
    register_smart_home.assert_called_once_with()
    register_ai.assert_called_once_with()
    register_voice.assert_called_once_with()


def test_register_all_skips_voice_when_disabled() -> None:
    factory = ServiceFactory(
        Mock(),
    )

    with (
        patch.object(
            factory,
            "register_core",
        ) as register_core,
        patch.object(
            factory,
            "register_smart_home",
        ) as register_smart_home,
        patch.object(
            factory,
            "register_ai",
        ) as register_ai,
        patch.object(
            factory,
            "register_voice",
        ) as register_voice,
    ):
        factory.register_all(
            include_voice=False,
        )

    register_core.assert_called_once_with()
    register_smart_home.assert_called_once_with()
    register_ai.assert_called_once_with()
    register_voice.assert_not_called()