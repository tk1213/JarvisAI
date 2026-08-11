from collections.abc import AsyncIterator

from openai import (
    APIConnectionError,
    APIStatusError,
    AsyncOpenAI,
    AuthenticationError,
    RateLimitError,
)

from jarvis.ai.base import BaseAI
from jarvis.config import settings
from jarvis.core.logger import log
from jarvis.core.prompt_manager import prompt_manager


class OpenAIClient(BaseAI):
    def __init__(self) -> None:
        api_key = (settings.openai_api_key or "").strip()

        invalid_values = {
            "",
            "ใส่_API_KEY_ตรงนี้",
            "your_api_key_here",
            "replace_me",
        }

        if api_key.lower() in invalid_values:
            raise ValueError(
                "OPENAI_API_KEY is missing or contains a placeholder."
            )

        if not api_key.isascii():
            raise ValueError(
                "OPENAI_API_KEY contains invalid characters."
            )

        self.model = settings.openai_model

        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )

    def _build_conversation(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> list[dict[str, str]]:
        message = message.strip()

        if not message:
            raise ValueError("Message cannot be empty.")

        conversation: list[dict[str, str]] = []

        if history:
            conversation.extend(history)

        conversation.append(
            {
                "role": "user",
                "content": message,
            }
        )

        return conversation

    @staticmethod
    def _build_instructions(
        *,
        voice_mode: bool,
    ) -> str:
        instructions = prompt_manager.load(
            "system"
        )

        if not voice_mode:
            return instructions

        voice_instructions = (
            "\n\n"
            "Voice response mode:\n"
            "- This response will be spoken aloud.\n"
            "- Default to ONE very short sentence.\n"
            "- Give the answer immediately.\n"
            "- For recommendations, give only ONE best recommendation.\n"
            "- Do not explain why unless the user asks why.\n"
            "- Do not add benefits, reasons, examples, or alternatives "
            "unless requested.\n"
            "- Do not repeat or paraphrase the user's message.\n"
            "- Avoid filler and conversational padding.\n"
            "- Do not use Markdown, headings, bullet lists, tables, or emojis.\n"
            "- Use additional sentences only when necessary for correctness "
            "or safety.\n"
            "- If the user explicitly asks for details, steps, options, "
            "or an explanation, provide the necessary detail.\n"
            "- Never omit important safety information for brevity."
        )
        

        return instructions + voice_instructions

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
        *,
        voice_mode: bool = False,
    ) -> str:
        conversation = self._build_conversation(
            message=message,
            history=history,
        )

        instructions = self._build_instructions(
            voice_mode=voice_mode,
        )

        try:
            log.info(
                "Sending request to OpenAI model: {}",
                self.model,
            )

            response = await self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=conversation,
            )

            answer = response.output_text.strip()

            if not answer:
                return "OpenAI returned an empty response."

            return answer

        except AuthenticationError as error:
            log.error(
                "OpenAI authentication failed: {}",
                error,
            )
            return (
                "OpenAI authentication failed. "
                "Please check OPENAI_API_KEY."
            )

        except RateLimitError as error:
            log.error(
                "OpenAI rate limit exceeded: {}",
                error,
            )
            return (
                "OpenAI rate limit exceeded. "
                "Please wait and try again."
            )

        except APIConnectionError as error:
            log.error(
                "Cannot connect to OpenAI: {}",
                error,
            )
            return (
                "Cannot connect to OpenAI. "
                "Please check your internet connection."
            )

        except APIStatusError as error:
            log.error(
                "OpenAI API error {}: {}",
                error.status_code,
                error,
            )
            return (
                f"OpenAI API returned error "
                f"{error.status_code}."
            )

        except Exception:  # noqa: BLE001
            log.exception("Unexpected OpenAI error")
            return "An unexpected AI error occurred."

    async def stream_chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncIterator[str]:
        conversation = self._build_conversation(
            message=message,
            history=history,
        )

        instructions = prompt_manager.load("system")

        try:
            log.info(
                "Streaming request to OpenAI model: {}",
                self.model,
            )

            stream = await self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=conversation,
                stream=True,
            )

            async for event in stream:
                if event.type == "response.output_text.delta":
                    delta = event.delta

                    if delta:
                        yield delta

        except AuthenticationError as error:
            log.error(
                "OpenAI authentication failed: {}",
                error,
            )
            yield (
                "OpenAI authentication failed. "
                "Please check OPENAI_API_KEY."
            )

        except RateLimitError as error:
            log.error(
                "OpenAI rate limit exceeded: {}",
                error,
            )
            yield (
                "OpenAI rate limit exceeded. "
                "Please wait and try again."
            )

        except APIConnectionError as error:
            log.error(
                "Cannot connect to OpenAI: {}",
                error,
            )
            yield (
                "Cannot connect to OpenAI. "
                "Please check your internet connection."
            )

        except APIStatusError as error:
            log.error(
                "OpenAI API error {}: {}",
                error.status_code,
                error,
            )
            yield (
                f"OpenAI API returned error "
                f"{error.status_code}."
            )

        except Exception:  # noqa: BLE001
            log.exception(
                "Unexpected OpenAI streaming error"
            )
            yield "An unexpected AI error occurred."