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
        await asyncio.shield(
            shutdown_task
        )

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
        print(
            "Environment : "
            f"{settings.app_environment}"
        )
        print(
            "Wake Word   : "
            f"{settings.wake_word}"
        )
        print(
            "Smart Home  : "
            f"{settings.smart_home_provider}"
        )

        print()
        print("System Ready.")
        print('Say "Hey Jarvis" to start.')
        print("Press Ctrl+C to stop JarvisAI.")

        await assistant_runtime.run(
            language="th",
        )

    except KeyboardInterrupt:
        log.info(
            "Keyboard interrupt received"
        )

    except asyncio.CancelledError:
        log.info(
            "JarvisAI runtime cancelled"
        )

    except Exception:  # noqa: BLE001
        log.exception(
            "JarvisAI encountered an error"
        )

    finally:
        await _shutdown_application(
            app
        )


async def chat() -> None:
    print("=" * 40)
    print("JarvisAI Interactive Chat")
    print("=" * 40)
    print(
        "Commands: exit, quit, clear, history, reload"
    )
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

        print(
            "Smart Home Provider: "
            f"{settings.smart_home_provider}"
        )
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

                print(
                    "Jarvis: Conversation cleared."
                )
                print()

                continue

            if command == "reload":
                prompt_manager.reload(
                    "system"
                )

                print(
                    "Jarvis: Prompt reloaded."
                )
                print()

                continue

            if command == "history":
                messages = (
                    await memory.get_recent_messages(
                        limit=20,
                    )
                )

                print()
                print("Conversation History")
                print("--------------------")

                if not messages:
                    print(
                        "No conversation history."
                    )

                for message in messages:
                    speaker = (
                        "You"
                        if message.role == "user"
                        else "Jarvis"
                    )

                    print(
                        f"{speaker}: "
                        f"{message.content}"
                    )

                print()

                continue

            reply = await conversation.ask(
                user_message
            )

            if not reply:
                reply = (
                    "Jarvis did not return a response."
                )

            print(
                f"Jarvis: {reply}"
            )
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
        log.exception(
            "Jarvis chat error"
        )

        print()
        print(
            "Jarvis: An unexpected error occurred."
        )

    finally:
        await _shutdown_application(
            app
        )


async def doctor() -> bool:
    print("=" * 40)
    print("JarvisAI System Doctor")
    print("=" * 40)

    app = JarvisApplication()

    try:
        await app.start()

        health = container.get(
            "health"
        )

        results = await health.check()

        print()

        for check_name, passed in results.items():
            status = (
                "PASS"
                if passed
                else "FAIL"
            )

            print(
                f"[{status}] {check_name}"
            )

        healthy = all(
            results.values()
        )

        print()

        if healthy:
            print(
                "Overall Status: HEALTHY"
            )
        else:
            print(
                "Overall Status: UNHEALTHY"
            )

        return healthy

    except asyncio.CancelledError:
        log.info(
            "Jarvis doctor cancelled"
        )
        return False

    except Exception:  # noqa: BLE001
        log.exception(
            "Jarvis doctor encountered an error"
        )

        print()
        print(
            "Overall Status: ERROR"
        )

        return False

    finally:
        await _shutdown_application(
            app
        )


def main() -> None:
    try:
        asyncio.run(
            run()
        )

    except KeyboardInterrupt:
        print()
        print(
            "JarvisAI stopped by user."
        )


if __name__ == "__main__":
    main()