from __future__ import annotations

import asyncio

from jarvis.services.ai_capability_resolver import AICapabilityResolver
from jarvis.services.ai_service import AIService
from jarvis.services.capability_registry import CapabilityRegistry


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Live AI Capability Resolver Test")
    print("=" * 60)

    registry = CapabilityRegistry(
        {
            "system.health",
            "system.ping",
            "system.version",
        }
    )

    ai = AIService()

    resolver = AICapabilityResolver(
        ai=ai,
        registry=registry,
    )

    test_messages = [
        "Jarvis ใช้เวอร์ชันอะไร",
        "ตรวจสอบสุขภาพของระบบ Jarvis ให้หน่อย",
        "ทดสอบว่า Jarvis ยังทำงานอยู่ไหม",
        "อธิบาย Python async ให้หน่อย",
    ]

    for text in test_messages:
        print()
        print("-" * 60)
        print(f"User: {text}")

        request = await resolver.resolve(text)

        if request is None:
            print("Capability: NONE")
            print("Action    : Normal AI fallback")
            continue

        print(f"Capability: {request.capability}")
        print(f"Arguments : {request.arguments}")

    print()
    print("=" * 60)
    print(" Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())