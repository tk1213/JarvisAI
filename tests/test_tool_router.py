from jarvis.services.tool_router import ToolRouter, ToolType


def test_route_ai_message() -> None:
    router = ToolRouter()

    result = router.route("What is artificial intelligence?")

    assert result == ToolType.AI


def test_route_smart_home_command() -> None:
    router = ToolRouter()

    result = router.route("เปิดไฟห้องนั่งเล่น")

    assert result == ToolType.SMART_HOME


def test_route_system_command() -> None:
    router = ToolRouter()

    result = router.route("shutdown")

    assert result == ToolType.SYSTEM


def test_route_plugin_command() -> None:
    router = ToolRouter()

    result = router.route("เปิดเพลง")

    assert result == ToolType.PLUGIN


def test_route_is_case_insensitive() -> None:
    router = ToolRouter()

    result = router.route("MUSIC")

    assert result == ToolType.PLUGIN


def test_route_trims_whitespace() -> None:
    router = ToolRouter()

    result = router.route("   restart   ")

    assert result == ToolType.SYSTEM