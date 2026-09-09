from __future__ import annotations

import re
from re import Match


class ThaiSpeechTextNormalizer:
    _DIGIT_WORDS = (
        "ศูนย์",
        "หนึ่ง",
        "สอง",
        "สาม",
        "สี่",
        "ห้า",
        "หก",
        "เจ็ด",
        "แปด",
        "เก้า",
    )

    _POSITION_WORDS = (
        "",
        "สิบ",
        "ร้อย",
        "พัน",
        "หมื่น",
        "แสน",
    )

    _PARENTHESIZED_MARKDOWN_LINK = re.compile(
        r"\s*\(\[[^\]]+\]\(https?://[^)]+\)\)"
    )
    _MARKDOWN_LINK = re.compile(
        r"\[([^\]]+)\]\(https?://[^)]+\)"
    )
    _RAW_URL = re.compile(
        r"https?://\S+"
    )

    _TIME_WITH_SUFFIX = re.compile(
        r"(?<!\d)"
        r"([01]?\d|2[0-3])"
        r"[:.]"
        r"([0-5]\d)"
        r"(?::([0-5]\d))?"
        r"\s*(?:น\.|นาฬิกา)"
    )
    _COLON_TIME = re.compile(
        r"(?<!\d)"
        r"([01]?\d|2[0-3])"
        r":"
        r"([0-5]\d)"
        r"(?::([0-5]\d))?"
        r"(?:\s*UTC)?"
        r"(?!\d)"
    )

    _MONEY = re.compile(
        r"(?<![\d.,])"
        r"(\d{1,3}(?:,\d{3})+|\d+)"
        r"(?:\.(\d{1,2}))?"
        r"\s*บาท"
    )

    _TEMPERATURE = re.compile(
        r"(?<![\d.])"
        r"(-?\d+(?:\.\d+)?)"
        r"\s*°\s*"
        r"([CcFf])"
    )

    _DOLLAR_AMOUNT = re.compile(
        r"(?<![\d.,])"
        r"(\d{1,3}(?:,\d{3})+|\d+)"
        r"(?:\.(\d+))?"
        r"\s*"
        r"(ดอลลาร์สหรัฐ|ดอลลาร์)"
    )

    def normalize(
        self,
        text: str,
    ) -> str:
        normalized = text.strip()

        normalized = self._PARENTHESIZED_MARKDOWN_LINK.sub(
            "",
            normalized,
        )
        normalized = self._MARKDOWN_LINK.sub(
            r"\1",
            normalized,
        )
        normalized = self._RAW_URL.sub(
            "",
            normalized,
        )

        normalized = self._TIME_WITH_SUFFIX.sub(
            self._replace_time,
            normalized,
        )
        normalized = self._COLON_TIME.sub(
            self._replace_time,
            normalized,
        )
        normalized = self._TEMPERATURE.sub(
            self._replace_temperature,
            normalized,
        )
        normalized = self._DOLLAR_AMOUNT.sub(
            self._replace_dollar_amount,
            normalized,
        )
        normalized = self._MONEY.sub(
            self._replace_money,
            normalized,
        )

        return " ".join(
            normalized.split()
        )

    @classmethod
    def number_to_thai_words(
        cls,
        value: int,
    ) -> str:
        if value < 0:
            return (
                "ลบ"
                + cls.number_to_thai_words(
                    abs(value)
                )
            )

        if value == 0:
            return cls._DIGIT_WORDS[0]

        if value >= 1_000_000:
            millions, remainder = divmod(
                value,
                1_000_000,
            )

            words = (
                cls.number_to_thai_words(
                    millions
                )
                + "ล้าน"
            )

            if remainder:
                words += cls.number_to_thai_words(
                    remainder
                )

            return words

        return cls._number_below_million(
            value
        )

    @classmethod
    def _number_below_million(
        cls,
        value: int,
    ) -> str:
        digits = str(value)
        length = len(digits)
        words: list[str] = []

        for index, character in enumerate(
            digits
        ):
            digit = int(character)

            if digit == 0:
                continue

            position = length - index - 1

            if position == 0:
                if digit == 1 and value > 10:
                    words.append("เอ็ด")
                else:
                    words.append(
                        cls._DIGIT_WORDS[digit]
                    )

            elif position == 1:
                if digit == 1:
                    pass
                elif digit == 2:
                    words.append("ยี่")
                else:
                    words.append(
                        cls._DIGIT_WORDS[digit]
                    )

                words.append(
                    cls._POSITION_WORDS[position]
                )

            else:
                words.append(
                    cls._DIGIT_WORDS[digit]
                )
                words.append(
                    cls._POSITION_WORDS[position]
                )

        return "".join(words)

    @classmethod
    def _replace_time(
        cls,
        match: Match[str],
    ) -> str:
        hour = int(match.group(1))
        minute = int(match.group(2))

        spoken = (
            cls.number_to_thai_words(hour)
            + "นาฬิกา"
        )

        if minute:
            spoken += (
                " "
                + cls.number_to_thai_words(
                    minute
                )
                + "นาที"
            )

        return spoken

    @classmethod
    def _replace_temperature(
        cls,
        match: Match[str],
    ) -> str:
        value = cls._number_text_to_words(
            match.group(1)
        )
        scale = match.group(2).lower()

        unit = (
            "องศาเซลเซียส"
            if scale == "c"
            else "องศาฟาเรนไฮต์"
        )

        return value + unit

    @classmethod
    def _replace_dollar_amount(
        cls,
        match: Match[str],
    ) -> str:
        integer_text = match.group(1).replace(
            ",",
            "",
        )
        decimal_text = match.group(2)
        currency = match.group(3)

        spoken = cls.number_to_thai_words(
            int(integer_text)
        )

        if decimal_text:
            spoken += (
                "จุด"
                + "".join(
                    cls._DIGIT_WORDS[int(digit)]
                    for digit in decimal_text
                )
            )

        return spoken + currency

    @classmethod
    def _number_text_to_words(
        cls,
        value: str,
    ) -> str:
        negative = value.startswith("-")
        unsigned = value.removeprefix("-")

        integer_text, separator, decimal_text = (
            unsigned.partition(".")
        )

        spoken = cls.number_to_thai_words(
            int(integer_text)
        )

        if separator:
            spoken += (
                "จุด"
                + "".join(
                    cls._DIGIT_WORDS[int(digit)]
                    for digit in decimal_text
                )
            )

        if negative:
            return "ลบ" + spoken

        return spoken

    @classmethod
    def _replace_money(
        cls,
        match: Match[str],
    ) -> str:
        baht = int(
            match.group(1).replace(
                ",",
                "",
            )
        )
        satang_text = match.group(2)

        spoken = (
            cls.number_to_thai_words(baht)
            + "บาท"
        )

        if satang_text is not None:
            satang = int(
                satang_text.ljust(
                    2,
                    "0",
                )
            )

            if satang:
                spoken += (
                    cls.number_to_thai_words(
                        satang
                    )
                    + "สตางค์"
                )

        return spoken