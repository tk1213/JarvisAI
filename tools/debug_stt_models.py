from __future__ import annotations

import asyncio
from pathlib import Path

from openai import AsyncOpenAI

from jarvis.config import settings

MODELS = (
    "gpt-4o-transcribe",
    "gpt-4o-mini-transcribe",
    "whisper-1",
)


async def main() -> None:
    audio_path = Path("fixed_test.wav").resolve()

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=60.0,
        max_retries=2,
    )

    print(f"Audio: {audio_path}")
    print()

    for model in MODELS:
        with audio_path.open("rb") as audio_file:
            result = await client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                language="th",
                temperature=0.0,
            )

        print(
            f"{model:24} = {result.text!r}"
        )


if __name__ == "__main__":
    asyncio.run(
        main()
    )