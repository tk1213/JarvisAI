from __future__ import annotations

import unicodedata
from pathlib import Path

from openai import AsyncOpenAI

from jarvis.config import settings


class SpeechToText:
    def __init__(self) -> None:
        api_key = (
            settings.openai_api_key or ""
        ).strip()

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required "
                "for SpeechToText."
            )

        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=2,
        )

        self.model = settings.stt_model

    async def transcribe(
        self,
        audio_file: str | Path,
        language: str | None = None,
    ) -> str:
        audio_path = Path(
            audio_file
        ).resolve()

        if not audio_path.exists():
            raise FileNotFoundError(
                "Audio file not found: "
                f"{audio_path}"
            )

        if audio_path.stat().st_size == 0:
            raise ValueError(
                "Audio file is empty: "
                f"{audio_path}"
            )

        selected_language = (
            language
            or settings.stt_language
        )

        with audio_path.open(
            "rb"
        ) as file:
            transcription = (
                await self.client.audio.transcriptions.create(
                    model=self.model,
                    file=file,
                    language=selected_language,
                    prompt=self._build_prompt(
                        selected_language
                    ),
                    temperature=0.0,
                )
            )

        text = transcription.text.strip()

        if self._is_suspicious_transcript(
            text=text,
            language=selected_language,
        ):
            return ""

        return text

    @classmethod
    def _is_suspicious_transcript(
        cls,
        *,
        text: str,
        language: str | None,
    ) -> bool:
        normalized = cls._normalize(
            text
        )

        if not normalized:
            return True

        exact_phrases = {
            "no speech detected",
            "no speech",
            "ไม่มีเสียง",
            "ไม่มีเสียงพูด",
            "ไม่มีเสียงพูดที่ชัดเจน",
            (
                "ถ้าไม่มีเสียงพูดที่ชัดเจน "
                "ให้ส่งข้อความว่างกลับมา "
                "ห้ามเดาหรือสร้างประโยคขึ้นเอง"
            ),
        }

        normalized_exact_phrases = {
            cls._normalize(
                phrase
            )
            for phrase in exact_phrases
        }

        if normalized in normalized_exact_phrases:
            return True

        suspicious_fragments = (
            "ให้ส่งข้อความว่างกลับมา",
            "ห้ามเดา",
            "ห้ามสร้างประโยค",
            "ไม่มีเสียงพูดที่ชัดเจน",
            "return an empty string",
            "do not guess",
            "no clear speech",
        )

        prompt_text = cls._build_prompt(
            language
        )

        normalized_prompt = cls._normalize(
            prompt_text
        )

        if normalized_prompt:
            if normalized == normalized_prompt:
                return True

            prompt_prefixes = (
                "บทสนทนาภาษาไทยกับผู้ช่วย jarvisai",
                "บทสนทนาภาษาไทยกับผู้ช่วย",
            )

            if any(
                normalized.startswith(
                    cls._normalize(prefix)
                )
                for prefix in prompt_prefixes
            ):
                return True

        if any(
            fragment in normalized
            for fragment in suspicious_fragments
        ):
            return True

        return (
            language is not None
            and language.lower().strip() == "th"
            and cls._looks_like_wrong_script(
                normalized
            )
        )

    @classmethod
    def _looks_like_wrong_script(
        cls,
        text: str,
    ) -> bool:
        thai_count = 0
        latin_count = 0
        other_letter_count = 0

        for character in text:
            if not character.isalpha():
                continue

            codepoint = ord(
                character
            )

            if 0x0E00 <= codepoint <= 0x0E7F:
                thai_count += 1
                continue

            if cls._is_latin_character(
                character
            ):
                latin_count += 1
                continue

            other_letter_count += 1

        total_letters = (
            thai_count
            + latin_count
            + other_letter_count
        )

        if total_letters == 0:
            return False

        allowed_letters = (
            thai_count
            + latin_count
        )

        allowed_ratio = (
            allowed_letters
            / total_letters
        )

        if (
            allowed_letters == 0
            and other_letter_count > 0
        ):
            return True

        return (
            other_letter_count >= 2
            and allowed_ratio < 0.60
        )

    @staticmethod
    def _is_latin_character(
        character: str,
    ) -> bool:
        name = unicodedata.name(
            character,
            "",
        )

        return "LATIN" in name

    @staticmethod
    def _build_prompt(
        language: str | None,
    ) -> str:
        if (
            language is not None
            and language.lower().strip() == "th"
        ):
            return (
                "บทสนทนาภาษาไทยกับผู้ช่วย JarvisAI "
                "ให้ถอดเสียงภาษาไทยตามคำพูดจริงอย่างแม่นยำ "
                "โดยเฉพาะคำต้นประโยคและคำสั้นที่ออกเสียงใกล้กัน "
                "อย่าเดาหรือเปลี่ยนคำเมื่อเสียงชัดเจน "
                "ผู้พูดอาจใช้คำภาษาอังกฤษปนภาษาไทย เช่น "
                "Jarvis, AI, smart home, system, health, "
                "version และ ping"
            )

        return ""

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFC",
            text,
        )

        return " ".join(
            normalized.lower().strip().split()
        )