from __future__ import annotations

import pytest

from jarvis.smart_home.text_normalizer import (
    SmartHomeTextNormalizer,
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "เปิดปลั๊ก",
            "เปิดปลั๊ก",
        ),
        (
            "เปิดปลัก",
            "เปิดปลั๊ก",
        ),
        (
            "เปิดพลัก",
            "เปิดปลั๊ก",
        ),
        (
            "เปิดสมาร์ทปลัก",
            "เปิดสมาร์ทปลั๊ก",
        ),
        (
            "เปิด SmartPlug",
            "เปิด smart plug",
        ),
        (
            "plak",
            "ปลั๊ก",
        ),
        (
            "เปิด plak",
            "เปิด ปลั๊ก",
        ),
        (
            "Smart Plug Two",
            "smart plug 2",
        ),
        (
            "สมาร์ทปลั๊ก สอง",
            "สมาร์ทปลั๊ก 2",
        ),
        (
            "  เปิด   ปลัก  ",
            "เปิด ปลั๊ก",
        ),
    ],
)
def test_normalize(
    source: str,
    expected: str,
) -> None:
    result = SmartHomeTextNormalizer.normalize(
        source
    )

    assert result == expected