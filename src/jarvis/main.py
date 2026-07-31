import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.command_registry import registry
from jarvis.core.config import config
from jarvis.core.container import container
from jarvis.core.logger import log
from jarvis.core.prompt_manager import prompt_manager
from jarvis.core.settings import settings
from jarvis.core.task_manager import task_manager


async def run() -> None:
    print("=" * 40)
    print(f"{config.get('app', 'name')} v{config.get('app', 'version')}")
    print("=" * 40)

    log.info("Starting JarvisAI")

    app = JarvisApplication()

    try:
        await app.start()

        # ทดสอบ OpenAI
        ai = container.get("ai")

        print()
        print("AI Test")
        print("-------")

        answer = await ai.ask(
            "สวัสดี แนะนำตัวเองสั้น ๆ เป็นภาษาไทย"
        )

        print(f"Jarvis: {answer}")

        print()
        print(f"Environment : {settings.APP_ENV}")
        print(f"Wake Word   : {settings.WAKE_WORD}")

        print()
        print("Registered Services")

        for service_name in container.list_services():
            print(f" - {service_name}")

        print()
        print("Running Tasks")

        for task_name in task_manager.list_tasks():
            print(f" - {task_name}")

        print()
        print("Testing Commands")
        print("----------------")

        registry.execute("status")
        registry.execute("version")
        registry.execute("help")

        print()
        print("System Ready.")
        print("Press Ctrl+C to stop JarvisAI.")

        await asyncio.Event().wait()

    except KeyboardInterrupt:
        log.info("Keyboard interrupt received")

    except Exception:  # noqa: BLE001
        log.exception("JarvisAI encountered an error")

    finally:
        await app.shutdown()


async def chat() -> None:
    print("=" * 40)
    print("JarvisAI Interactive Chat")
    print("=" * 40)
    print("Commands: exit, quit, clear, history, reload")
    print()

    app = JarvisApplication()

    try:
        await app.start(start_background_tasks=False)

        ai = container.get("ai")
        memory = container.get("memory")

        while True:
            user_message = await asyncio.to_thread(
                input,
                "You: ",
            )

            user_message = user_message.strip()

            if not user_message:
                continue

            command = user_message.lower()

            if command in {"exit", "quit"}:
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
                    speaker = (
                        "You"
                        if message.role == "user"
                        else "Jarvis"
                    )

                    print(f"{speaker}: {message.content}")

                print()
                continue

            history = await memory.get_ai_history(limit=20)

            await memory.save_message(
                role="user",
                content=user_message,
            )

            print("Jarvis: ", end="", flush=True)

            answer_parts = []

            async for chunk in ai.stream(
                text=user_message,
                history=history,
            ):
                answer_parts.append(chunk)

                print(
                    chunk,
                    end="",
                    flush=True,
                )

            print()
            print()

            answer = "".join(answer_parts).strip()

            if not answer:
                answer = "OpenAI returned an empty response."

            await memory.save_message(
                role="assistant",
                content=answer,
            )

    except EOFError:
        print()
        print("Chat ended.")

    except KeyboardInterrupt:
        print()
        print("Chat stopped.")

    except Exception:  # noqa: BLE001
        log.exception("Jarvis chat error")

        print()
        print(
            "Jarvis: An unexpected error occurred."
        )

    finally:
        await app.shutdown()
        

async def doctor() -> bool:
    print("=" * 40)
    print("JarvisAI System Doctor")
    print("=" * 40)

    app = JarvisApplication()

    try:
        await app.start()

        health = container.get("health")
        results = await health.check()

        print()

        for check_name, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {check_name}")

        healthy = all(results.values())

        print()

        if healthy:
            print("Overall Status: HEALTHY")
        else:
            print("Overall Status: UNHEALTHY")

        return healthy

    except Exception:  # noqa: BLE001
        log.exception("Jarvis doctor encountered an error")
        print()
        print("Overall Status: ERROR")
        return False

    finally:
        await app.shutdown()


def main() -> None:
    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        print()
        print("JarvisAI stopped by user.")


if __name__ == "__main__":
    main()