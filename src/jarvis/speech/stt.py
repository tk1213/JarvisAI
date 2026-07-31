from pathlib import Path

from openai import AsyncOpenAI

from jarvis.config import settings


class SpeechToText:
    def __init__(self) -> None:
        api_key = (settings.openai_api_key or "").strip()

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for SpeechToText."
            )

        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=2,
        )
        self.model = "gpt-4o-mini-transcribe"

    async def transcribe(
        self,
        audio_file: str | Path,
        language: str | None = None,
    ) -> str:
        audio_path = Path(audio_file).resolve()

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        if audio_path.stat().st_size == 0:
            raise ValueError(
                f"Audio file is empty: {audio_path}"
            )

        selected_language = language or settings.stt_language

        with audio_path.open("rb") as file:
            transcription = (
                await self.client.audio.transcriptions.create(
                    model=self.model,
                    file=file,
                    language=selected_language,
                    prompt=(
                        "ถ้าไม่มีเสียงพูดที่ชัดเจน "
                        "ให้ส่งข้อความว่างกลับมา "
                        "ห้ามเดาหรือสร้างประโยคขึ้นเอง"
                    ),
                )
            )

        text = transcription.text.strip()

        suspicious_phrases = {
            "kosol lubos siang, loso nga lai pakete.",
            "có sao phải bóp riêng là sẽ nên lại",
        }

        if text.lower() in suspicious_phrases:
            return ""

        return text