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

    print(f"Model : {settings.stt_model}")
    print(f"Audio : {audio_path}")
    print()

    with audio_path.open("rb") as audio_file:
        result_th = await client.audio.transcriptions.create(
            model=settings.stt_model,
            file=audio_file,
            language="th",
            temperature=0.0,
        )

    print(
        "TH language =",
        repr(result_th.text),
    )

    with audio_path.open("rb") as audio_file:
        result_auto = await client.audio.transcriptions.create(
            model=settings.stt_model,
            file=audio_file,
            temperature=0.0,
        )

    print(
        "AUTO language =",
        repr(result_auto.text),
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )