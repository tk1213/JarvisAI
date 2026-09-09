from jarvis.speech.thai_text_normalizer import (
    ThaiSpeechTextNormalizer,
)


def normalizer() -> ThaiSpeechTextNormalizer:
    return ThaiSpeechTextNormalizer()


def test_normalizes_gold_price() -> None:
    assert normalizer().normalize(
        "ราคาขายออก 68,450 บาท"
    ) == (
        "ราคาขายออก "
        "หกหมื่นแปดพันสี่ร้อยห้าสิบบาท"
    )


def test_normalizes_dot_separated_time_with_suffix() -> None:
    assert normalizer().normalize(
        "เวลา 23.30 น."
    ) == (
        "เวลา ยี่สิบสามนาฬิกา "
        "สามสิบนาที"
    )


def test_normalizes_colon_separated_time() -> None:
    assert normalizer().normalize(
        "เวลา 19:39 น."
    ) == (
        "เวลา สิบเก้านาฬิกา "
        "สามสิบเก้านาที"
    )


def test_does_not_treat_decimal_as_time() -> None:
    assert normalizer().normalize(
        "ราคาหุ้น 23.30 จุด"
    ) == "ราคาหุ้น 23.30 จุด"


def test_normalizes_baht_and_satang() -> None:
    assert normalizer().normalize(
        "ราคา 1,250.50 บาท"
    ) == (
        "ราคา หนึ่งพันสองร้อยห้าสิบบาท"
        "ห้าสิบสตางค์"
    )


def test_removes_parenthesized_markdown_source_link() -> None:
    assert normalizer().normalize(
        "อ้างอิงสมาคมค้าทองคำ "
        "([เว็บไซต์](https://example.com/gold))"
    ) == "อ้างอิงสมาคมค้าทองคำ"


def test_preserves_plain_text() -> None:
    assert normalizer().normalize(
        "เปิดไฟห้องนั่งเล่นแล้วครับ"
    ) == "เปิดไฟห้องนั่งเล่นแล้วครับ"