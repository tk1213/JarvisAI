from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.services.ai_capability_resolver import AICapabilityResolver
from jarvis.services.capability_router import CapabilityRouter
from jarvis.smart_home.service import SmartHomeService


async def main() -> None:
    print("=" * 60)
    print(" JarvisAI - Live AI Smart Home Capability Test")
    print("=" * 60)

    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        resolver = container.resolve(
            "ai_capability_resolver",
            AICapabilityResolver,
        )

        router = container.resolve(
            "capability_router",
            CapabilityRouter,
        )

        smart_home = container.resolve(
            "smart_home",
            SmartHomeService,
        )

        test_commands = [
            "เปิดไฟห้องนั่งเล่น",
            "ปิดไฟห้องนั่งเล่น",
            "เปิดพัดลมห้องนั่งเล่น",
            "เปิดแอร์ห้องนอน",
            "ตรวจสอบสถานะแอร์ห้องนอน",
            "เปิดประตูโรงรถ",
            "มีอุปกรณ์ Smart Home อะไรบ้าง",
        ]

        for text in test_commands:
            print()
            print("-" * 60)
            print(f"User: {text}")

            request = await resolver.resolve(
                text,
            )

            if request is None:
                print("Capability: NONE")
                print("Action    : Normal AI fallback")
                continue

            print(
                f"Capability: {request.capability}"
            )
            print(
                f"Arguments : {request.arguments}"
            )

            if (
                request.capability.startswith(
                    "smart_home."
                )
                and "device_id" in request.arguments
            ):
                print()
                print(
                    "SAFETY FAILURE: AI generated device_id."
                )
                print(
                    "Expected device_query instead."
                )
                continue

            result = await router.execute_request(
                request,
            )

            print(f"Result    : {result}")

        print()
        print("=" * 60)
        print(" Final Mock Device State")
        print("=" * 60)

        devices = await smart_home.list_devices()

        for device in devices:
            print(
                f"{device.id:<12} "
                f"{device.name:<30} "
                f"power={device.power}"
            )

        print()
        print("=" * 60)
        print(" Test Complete")
        print("=" * 60)

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())