from __future__ import annotations

import re
import unicodedata
from typing import ClassVar


class SmartHomeTextNormalizer:
    """
    Normalize deterministic Smart Home speech/text variations.

    Examples
    --------
    เปิดปลัก
        -> เปิดปลั๊ก

    plak
        -> ปลั๊ก

    สมาร์ทปลักสอง
        -> สมาร์ทปลั๊ก 2

    Smart Plug Two
        -> smart plug 2
    """

    _PHRASE_REPLACEMENTS: ClassVar[dict[str, str]] = {
        # -----------------------------------------------------
        # Smart Plug - Thai variants
        # -----------------------------------------------------
        "สมาร์ท พลั๊ก": "สมาร์ทปลั๊ก",
        "สมาร์ท พลัก": "สมาร์ทปลั๊ก",
        "สมาร์ท ปลั๊ก": "สมาร์ทปลั๊ก",
        "สมาร์ท ปลัก": "สมาร์ทปลั๊ก",
        "สมาร์ทพลั๊ก": "สมาร์ทปลั๊ก",
        "สมาร์ทพลัก": "สมาร์ทปลั๊ก",
        "สมาร์ทปลัก": "สมาร์ทปลั๊ก",

        # -----------------------------------------------------
        # Plug - Thai variants
        # -----------------------------------------------------
        "พลั๊ก": "ปลั๊ก",
        "พลัก": "ปลั๊ก",
        "ปลัก": "ปลั๊ก",

        # -----------------------------------------------------
        # English formatting
        # -----------------------------------------------------
        "smartplug": "smart plug",
    }

    _WORD_REPLACEMENTS: ClassVar[dict[str, str]] = {
        # -----------------------------------------------------
        # STT phonetic variants
        # -----------------------------------------------------
        "plak": "ปลั๊ก",
        "pluk": "ปลั๊ก",
        "plag": "ปลั๊ก",

        # -----------------------------------------------------
        # Thai numbers
        # -----------------------------------------------------
        "ศูนย์": "0",
        "หนึ่ง": "1",
        "เอ็ด": "1",
        "สอง": "2",
        "สาม": "3",
        "สี่": "4",
        "ห้า": "5",
        "หก": "6",
        "เจ็ด": "7",
        "แปด": "8",
        "เก้า": "9",
        "สิบ": "10",

        # -----------------------------------------------------
        # English numbers
        # -----------------------------------------------------
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }

    _THAI_NUMBER_SUFFIXES: ClassVar[tuple[str, ...]] = (
        "ศูนย์",
        "หนึ่ง",
        "เอ็ด",
        "สอง",
        "สาม",
        "สี่",
        "ห้า",
        "หก",
        "เจ็ด",
        "แปด",
        "เก้า",
        "สิบ",
    )

    @classmethod
    def normalize(
        cls,
        text: str,
    ) -> str:
        text = unicodedata.normalize(
            "NFC",
            text,
        )

        text = text.lower().strip()

        text = cls._replace_phrases(
            text
        )

        text = cls._separate_number_suffixes(
            text
        )

        text = cls._replace_words(
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @classmethod
    def _replace_phrases(
        cls,
        text: str,
    ) -> str:
        for source, target in (
            cls._PHRASE_REPLACEMENTS.items()
        ):
            text = text.replace(
                source,
                target,
            )

        return text

    @classmethod
    def _separate_number_suffixes(
        cls,
        text: str,
    ) -> str:
        """
        Separate Thai number words when STT joins them
        directly to the preceding device name.

        Example:
            สมาร์ทปลั๊กสอง
            -> สมาร์ทปลั๊ก สอง
        """

        for number_word in cls._THAI_NUMBER_SUFFIXES:
            text = re.sub(
                rf"(?<=\S){re.escape(number_word)}",
                rf" {number_word}",
                text,
            )

        return text

    @classmethod
    def _replace_words(
        cls,
        text: str,
    ) -> str:
        words = text.split()

        normalized_words = [
            cls._WORD_REPLACEMENTS.get(
                word,
                word,
            )
            for word in words
        ]

        return " ".join(
            normalized_words
        )