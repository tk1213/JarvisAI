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
            timeout=60.0,
            max_retries=2,
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

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        conversation = self._build_conversation(
            message=message,
            history=history,
        )

        instructions = prompt_manager.load("system")

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