from jarvis.memory.extractor import MemoryExtractor
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


def test_extract_user_name_thai() -> None:
    extractor = MemoryExtractor()

    result = extractor.extract(
        "ผมชื่อ TK"
    )

    assert len(result) == 1
    assert result[0].category is MemoryCategory.PERSONAL
    assert result[0].key == "user_name"
    assert result[0].value == "TK"
    assert result[0].importance is MemoryImportance.HIGH


def test_extract_daughter_name() -> None:
    extractor = MemoryExtractor()

    result = extractor.extract(
        "ลูกสาวชื่อ Diana"
    )

    assert len(result) == 1
    assert result[0].category is MemoryCategory.FAMILY
    assert result[0].key == "daughter_name"
    assert result[0].value == "Diana"


def test_extract_favorite_drink() -> None:
    extractor = MemoryExtractor()

    result = extractor.extract(
        "ฉันชอบดื่มกาแฟดำ"
    )

    assert len(result) == 1
    assert result[0].category is MemoryCategory.PREFERENCE
    assert result[0].key == "favorite_drink"
    assert result[0].value == "กาแฟดำ"


def test_extract_multiple_memories() -> None:
    extractor = MemoryExtractor()

    result = extractor.extract(
        "ผมชื่อ TK และลูกสาวชื่อ Diana"
    )

    assert [(item.key, item.value) for item in result] == [
        ("user_name", "TK"),
        ("daughter_name", "Diana"),
    ]


def test_unrelated_text_returns_empty_list() -> None:
    extractor = MemoryExtractor()

    result = extractor.extract(
        "วันนี้อากาศเป็นอย่างไร"
    )

    assert result == []


def test_name_question_is_not_saved_as_memory() -> None:
    extractor = MemoryExtractor()

    result = extractor.extract(
        "ผมชื่ออะไร"
    )

    assert result == []
