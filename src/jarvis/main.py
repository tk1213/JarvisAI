from __future__ import annotations

import asyncio

from jarvis.config import settings
from jarvis.core.application import JarvisApplication
from jarvis.core.container import container
from jarvis.core.logger import log
from jarvis.core.prompt_manager import prompt_manager
from jarvis.services.ai_service import AIService
from jarvis.services.assistant_runtime_service import (
    AssistantRuntimeService,
)
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.health_contracts import (
    HealthCheckResult,
    HealthState,
)
from jarvis.services.memory_service import MemoryService
from jarvis.version import __version__


async def _shutdown_application(
    app: JarvisApplication,
) -> None:
    """
    Complete application cleanup even when the main runtime
    is being cancelled by Ctrl+C.
    """

    shutdown_task = asyncio.create_task(
        app.shutdown(),
        name="jarvis-shutdown",
    )

    try:
        await asyncio.shield(shutdown_task)

    except asyncio.CancelledError:
        await shutdown_task


async def run() -> None:
    print("=" * 40)
    print(f"{settings.app_name} v{__version__}")
    print("=" * 40)

    log.info("Starting JarvisAI")

    app = JarvisApplication()

    try:
        await app.start()

        assistant_runtime = container.resolve(
            "assistant_runtime",
            AssistantRuntimeService,
        )

        print()
        print(f"Environment : {settings.app_environment}")
        print(f"Wake Word   : {settings.wake_word}")
        print(f"Smart Home  : {settings.smart_home_provider}")

        print()
        print("System Ready.")
        print('Say "Hey Jarvis" to start.')
        print("Press Ctrl+C to stop JarvisAI.")

        await assistant_runtime.run(
            language="th",
        )

    except KeyboardInterrupt:
        log.info("Keyboard interrupt received")

    except asyncio.CancelledError:
        log.info("JarvisAI runtime cancelled")

    except Exception:  # noqa: BLE001
        log.exception("JarvisAI encountered an error")

    finally:
        await _shutdown_application(app)


async def chat() -> None:
    print("=" * 40)
    print("JarvisAI Interactive Chat")
    print("=" * 40)
    print("Commands: exit, quit, clear, history, reload")
    print()

    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        ai = container.resolve(
            "ai",
            AIService,
        )

        memory = container.resolve(
            "memory",
            MemoryService,
        )

        conversation = container.resolve(
            "conversation",
            ConversationManager,
        )

        print(f"Smart Home Provider: {settings.smart_home_provider}")
        print()

        while True:
            user_message = await asyncio.to_thread(
                input,
                "You: ",
            )

            user_message = user_message.strip()

            if not user_message:
                continue

            command = user_message.lower()

            if command in {
                "exit",
                "quit",
            }:
                print("Chat ended.")
                break

            if command == "clear":
                ai.reset_conversation()

                await memory.clear_messages()

                print("Jarvis: Conversation cleared.")
                print()

                continue

            if command == "reload":
                prompt_manager.reload("system")

                print("Jarvis: Prompt reloaded.")
                print()

                continue

            if command == "history":
                messages = await memory.get_recent_messages(
                    limit=20,
                )

                print()
                print("Conversation History")
                print("--------------------")

                if not messages:
                    print("No conversation history.")

                for message in messages:
                    speaker = "You" if message.role == "user" else "Jarvis"

                    print(f"{speaker}: {message.content}")

                print()

                continue

            reply = await conversation.ask(user_message)

            if not reply:
                reply = "Jarvis did not return a response."

            print(f"Jarvis: {reply}")
            print()

    except EOFError:
        print()
        print("Chat ended.")

    except KeyboardInterrupt:
        print()
        print("Chat stopped.")

    except asyncio.CancelledError:
        print()
        print("Chat cancelled.")

    except Exception:  # noqa: BLE001
        log.exception("Jarvis chat error")

        print()
        print("Jarvis: An unexpected error occurred.")

    finally:
        await _shutdown_application(app)


def _doctor_status_label(
    state: HealthState,
) -> str:
    if state is HealthState.HEALTHY:
        return "PASS"

    if state is HealthState.DEGRADED:
        return "WARN"

    return "FAIL"

def _print_doctor_details(
    check_name: str,
    result: HealthCheckResult,
) -> None:
    if check_name != "audio":
        return

    input_details = result.details.get(
        "input"
    )
    output_details = result.details.get(
        "output"
    )

    if isinstance(
        input_details,
        dict,
    ):
        print(
            "       Input : "
            f"[{input_details.get('index')}] "
            f"{input_details.get('name')}"
        )
        print(
            "       API   : "
            f"{input_details.get('host_api')}"
        )
        print(
            "       Rate  : "
            f"{input_details.get('sample_rate')} Hz"
        )

    if isinstance(
        output_details,
        dict,
    ):
        print(
            "       Output: "
            f"[{output_details.get('index')}] "
            f"{output_details.get('name')}"
        )
        print(
            "       API   : "
            f"{output_details.get('host_api')}"
        )
        print(
            "       Rate  : "
            f"{output_details.get('sample_rate')} Hz"
        )

async def doctor() -> bool:
    print("=" * 40)
    print("JarvisAI System Doctor")
    print("=" * 40)

    app = JarvisApplication()

    try:
        await app.start()

        health = container.get("health")

        results = await health.operational_diagnostics()

        print()

        for check_name, result in results.items():
            status = _doctor_status_label(result.state)

            print(f"[{status}] {check_name}")

            if result.reason:
                print(f"       Reason: {result.reason}")

            _print_doctor_details(
                check_name,
                result,
            )

        healthy = all(result.passed for result in results.values() if result.critical)

        print()

        if healthy:
            print("Overall Status: HEALTHY")
        else:
            print("Overall Status: UNHEALTHY")

        return healthy

    except asyncio.CancelledError:
        log.info("Jarvis doctor cancelled")
        return False

    except Exception:  # noqa: BLE001
        log.exception("Jarvis doctor encountered an error")

        print()
        print("Overall Status: ERROR")

        return False

    finally:
        await _shutdown_application(app)


def main() -> None:
    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        print()
        print("JarvisAI stopped by user.")


if __name__ == "__main__":
    main()