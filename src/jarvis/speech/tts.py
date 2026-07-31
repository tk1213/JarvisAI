from pathlib import Path

from openai import AsyncOpenAI

from jarvis.config import settings


class TextToSpeech:
    def __init__(self) -> None:
        api_key = (settings.openai_api_key or "").strip()

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for TextToSpeech."
            )

        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=60.0,
            max_retries=2,
        )

        self.model = settings.tts_model
        self.voice = "alloy"

    async def generate(
        self,
        text: str,
        output: str = "output.wav",
    ) -> Path:
        text = text.strip()

        if not text:
            raise ValueError("TTS text cannot be empty.")

        output_path = Path(output).resolve()
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        async with (
            self.client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                input=text,
                response_format="wav",
            )
        ) as response:
            await response.stream_to_file(output_path)

        return output_path