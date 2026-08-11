from __future__ import annotations

import asyncio
from pathlib import Path

from openai import AsyncOpenAI

from jarvis.config import settings


async def main() -> None:
    audio_path = Path("record.wav").resolve()

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=60.0,
        max_retries=2,
    )

    print(f"Model    : {settings.stt_model}")
    print(f"Audio    : {audio_path}")
    print(f"Size     : {audio_path.stat().st_size} bytes")

    with audio_path.open("rb") as audio_file:
        result = await client.audio.transcriptions.create(
            model=settings.stt_model,
            file=audio_file,
            language="th",
            temperature=0.0,
        )

    print(f"RAW STT  : {result.text!r}")


if __name__ == "__main__":
    asyncio.run(main())