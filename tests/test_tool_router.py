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

def test_route_music_request_falls_back_to_ai() -> None:
    router = ToolRouter()

    result = router.route(
        "play music"
    )

    assert result == ToolType.AI


def test_route_music_keyword_falls_back_to_ai_case_insensitively() -> None:
    router = ToolRouter()

    result = router.route(
        "MUSIC"
    )

    assert result == ToolType.AI


def test_route_trims_whitespace() -> None:
    router = ToolRouter()

    result = router.route("   restart   ")

    assert result == ToolType.SYSTEM

def test_route_explicit_system_commands() -> None:
    router = ToolRouter()

    assert router.route("system version") == ToolType.SYSTEM
    assert router.route("jarvis version") == ToolType.SYSTEM
    assert router.route("system health") == ToolType.SYSTEM
    assert router.route("jarvis health") == ToolType.SYSTEM
    assert router.route("system ping") == ToolType.SYSTEM
    assert router.route("jarvis ping") == ToolType.SYSTEM


def test_route_thai_system_commands() -> None:
    router = ToolRouter()

    assert router.route("เวอร์ชันระบบ") == ToolType.SYSTEM
    assert router.route("เวอร์ชัน jarvis") == ToolType.SYSTEM
    assert router.route("ตรวจสอบระบบ jarvis") == ToolType.SYSTEM
    assert router.route("ทดสอบระบบ") == ToolType.SYSTEM


def test_do_not_route_unrelated_version_to_system() -> None:
    router = ToolRouter()

    assert router.route("What version of Python should I use?") == ToolType.AI
    assert router.route("Windows version differences") == ToolType.AI


def test_do_not_route_unrelated_health_to_system() -> None:
    router = ToolRouter()

    assert router.route("What are the health benefits of exercise?") == ToolType.AI


def test_do_not_route_unrelated_ping_to_system() -> None:
    router = ToolRouter()

    assert router.route("Explain the rules of ping pong") == ToolType.AI    