from __future__ import annotations

import asyncio
import unicodedata

from jarvis.core.logger import log
from jarvis.core.session import SessionState
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.session_manager import SessionManager
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.services.wake_word_service import WakeWordService


class AssistantRuntimeService:
    def __init__(
        self,
        *,
        wake_word: WakeWordService,
        voice: VoiceService,
        conversation: ConversationManager,
        tts: TTSService,
        session: SessionManager,
        follow_up_timeout: float = 12.0,
        max_follow_up_turns: int = 3,
        max_silence_retries: int = 2,
        max_clarification_silence_retries: int = 2,
        error_retry_delay: float = 1.0,
    ) -> None:
        if follow_up_timeout <= 0:
            raise ValueError(
                "follow_up_timeout must be greater than zero."
            )

        if max_follow_up_turns < 0:
            raise ValueError(
                "max_follow_up_turns cannot be negative."
            )

        if max_silence_retries < 1:
            raise ValueError(
                "max_silence_retries must be at least 1."
            )

        if max_clarification_silence_retries < 1:
            raise ValueError(
                "max_clarification_silence_retries "
                "must be at least 1."
            )

        if error_retry_delay < 0:
            raise ValueError(
                "error_retry_delay cannot be negative."
            )

        self._wake_word = wake_word
        self._voice = voice
        self._conversation = conversation
        self._tts = tts
        self._session = session

        self._follow_up_timeout = follow_up_timeout
        self._max_follow_up_turns = max_follow_up_turns
        self._max_silence_retries = max_silence_retries
        self._max_clarification_silence_retries = (
            max_clarification_silence_retries
        )
        self._error_retry_delay = error_retry_delay

        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    @property
    def follow_up_timeout(self) -> float:
        return self._follow_up_timeout

    @property
    def max_follow_up_turns(self) -> int:
        return self._max_follow_up_turns

    @property
    def max_silence_retries(self) -> int:
        return self._max_silence_retries

    @property
    def max_clarification_silence_retries(
        self,
    ) -> int:
        return self._max_clarification_silence_retries

    async def run(
        self,
        *,
        language: str = "th",
    ) -> None:
        if self._running:
            raise RuntimeError(
                "Assistant runtime is already running."
            )

        self._running = True

        print()
        print("=" * 60)
        print(" JarvisAI Voice Assistant")
        print("=" * 60)
        print()
        print(
            'Jarvis is ready. Say "Hey Jarvis" '
            "to start."
        )

        try:
            while self._running:
                try:
                    await self._run_wake_cycle(
                        language=language,
                    )

                except asyncio.CancelledError:
                    raise

                except Exception as exc:  # noqa: BLE001
                    await self._recover_from_cycle_error(
                        exc
                    )

        except asyncio.CancelledError:
            self._running = False

        finally:
            self._running = False

            print()
            print(
                "Jarvis voice assistant stopped."
            )

    def stop(self) -> None:
        self._running = False

    async def _run_wake_cycle(
        self,
        *,
        language: str,
    ) -> None:
        print()
        print("-" * 60)
        print(
            'Waiting for wake word: "Hey Jarvis"...'
        )
        print("-" * 60)

        score = (
            await self._wake_word.wait_for_wake_word()
        )

        if not self._running:
            return

        print()
        print(
            "Wake word detected "
            f"(score={score:.4f})"
        )

        await self._acknowledge_wake()

        if not self._running:
            return

        await self._handle_conversation(
            language=language,
        )

    async def _acknowledge_wake(
        self,
    ) -> None:
        await self._speak_runtime_reply(
            "ครับ คุณ TK",
            output="wake_ack.wav",
        )

    async def _handle_conversation(
        self,
        *,
        language: str,
    ) -> None:
        print()
        print("Listening for command...")

        text = await self._voice.listen_for_text(
            language=language,
        )

        if not text:
            print()
            print(
                "No command detected. "
                "Returning to wake mode."
            )
            return

        if await self._handle_session_end_command(
            text
        ):
            return

        reply = await self._voice.reply_to_text(
            text
        )

        if not reply:
            return

        clarification_completed = (
            await self._handle_pending_clarification(
                language=language,
            )
        )

        if not clarification_completed:
            return

        if not self._running:
            return

        await self._handle_follow_up_window(
            language=language,
        )

        print()
        print(
            "Conversation complete. "
            "Returning to wake mode."
        )

    async def _handle_pending_clarification(
        self,
        *,
        language: str,
    ) -> bool:
        silence_count = 0

        while (
            self._running
            and self._conversation.has_pending_smart_home
        ):
            print()
            print(
                "Waiting for clarification..."
            )

            text = await self._voice.listen_for_text(
                language=language,
            )

            if not text:
                silence_count += 1

                if (
                    silence_count
                    >= self._max_clarification_silence_retries
                ):
                    await self._cancel_pending_smart_home(
                        speak=True,
                    )
                    return False

                print()
                print(
                    "No clarification detected. "
                    "Listening once more..."
                )
                continue

            silence_count = 0

            if self._is_cancel_command(
                text
            ):
                await self._cancel_pending_smart_home(
                    speak=True,
                )
                return False

            if await self._handle_session_end_command(
                text
            ):
                self._conversation.cancel_pending_smart_home()
                return False

            await self._voice.reply_to_text(
                text
            )

        return True

    async def _handle_follow_up_window(
        self,
        *,
        language: str,
    ) -> None:
        if self._max_follow_up_turns == 0:
            return

        silence_count = 0

        for turn in range(
            1,
            self._max_follow_up_turns + 1,
        ):
            if not self._running:
                return

            print()
            print(
                "Follow-up listening "
                f"({turn}/{self._max_follow_up_turns})..."
            )

            print(
                "Speak another command, "
                f"or stay quiet for "
                f"{self._follow_up_timeout:.0f} seconds."
            )

            try:
                text = await asyncio.wait_for(
                    self._voice.listen_for_text(
                        language=language,
                    ),
                    timeout=self._follow_up_timeout,
                )

            except TimeoutError:
                print()
                print(
                    "Follow-up window expired."
                )
                return

            if not text:
                silence_count += 1

                if (
                    silence_count
                    >= self._max_silence_retries
                ):
                    print()
                    print(
                        "No usable speech detected. "
                        "Returning to wake mode."
                    )
                    return

                print()
                print(
                    "No speech detected. "
                    "Listening once more..."
                )
                continue

            silence_count = 0

            if await self._handle_session_end_command(
                text
            ):
                return

            reply = await self._voice.reply_to_text(
                text
            )

            if not reply:
                continue

            clarification_completed = (
                await self._handle_pending_clarification(
                    language=language,
                )
            )

            if not clarification_completed:
                return

            if not self._running:
                return

    async def _cancel_pending_smart_home(
        self,
        *,
        speak: bool,
    ) -> bool:
        cancelled = (
            self._conversation.cancel_pending_smart_home()
        )

        if not cancelled:
            return False

        if speak:
            await self._speak_runtime_reply(
                "ยกเลิกคำสั่งนี้แล้วครับ คุณ TK",
                output="smart_home_cancel.wav",
            )

        return True

    async def _handle_session_end_command(
        self,
        text: str,
    ) -> bool:
        response = self._session_end_response(
            text
        )

        if response is None:
            return False

        if self._conversation.has_pending_smart_home:
            self._conversation.cancel_pending_smart_home()

        await self._speak_runtime_reply(
            response,
            output="session_end.wav",
        )

        return True

    @classmethod
    def _session_end_response(
        cls,
        text: str,
    ) -> str | None:
        normalized = cls._normalize_text(
            text
        )

        thank_you_phrases = {
            "ขอบคุณ",
            "ขอบคุณครับ",
            "ขอบใจ",
            "thank you",
            "thanks",
        }

        if normalized in thank_you_phrases:
            return "ยินดีครับ คุณ TK"

        end_phrases = {
            "พอแล้ว",
            "แค่นี้",
            "แค่นี้พอ",
            "จบการสนทนา",
            "หยุดคุย",
            "พอแค่นี้",
            "that's all",
            "thats all",
            "end conversation",
        }

        if normalized in end_phrases:
            return "ครับ คุณ TK"

        return None

    @classmethod
    def _is_cancel_command(
        cls,
        text: str,
    ) -> bool:
        normalized = cls._normalize_text(
            text
        )

        cancel_phrases = {
            "ยกเลิก",
            "ยกเลิกคำสั่ง",
            "ไม่เอา",
            "ไม่เอาแล้ว",
            "ช่างมัน",
            "ช่างเถอะ",
            "ไม่ต้องแล้ว",
            "cancel",
            "cancel command",
            "never mind",
            "nevermind",
        }

        return normalized in cancel_phrases

    async def _recover_from_cycle_error(
        self,
        error: Exception,
    ) -> None:
        log.exception(
            "Voice runtime cycle failed: {}",
            error,
        )

        if self._conversation.has_pending_smart_home:
            self._conversation.cancel_pending_smart_home()

        try:
            await self._session.set_state(
                SessionState.IDLE,
            )

        except Exception as state_error:  # noqa: BLE001
            log.error(
                "Failed to reset session state: {}",
                state_error,
            )

        print()
        print(
            "Jarvis: เกิดข้อผิดพลาดชั่วคราวครับ "
            "ระบบจะกลับไปรอคำสั่งใหม่"
        )

        if (
            self._running
            and self._error_retry_delay > 0
        ):
            await asyncio.sleep(
                self._error_retry_delay
            )

    async def _speak_runtime_reply(
        self,
        text: str,
        *,
        output: str,
    ) -> None:
        print()
        print(
            f"Jarvis: {text}"
        )

        await self._session.set_state(
            SessionState.SPEAKING,
        )

        try:
            try:
                await self._tts.speak(
                    text=text,
                    output=output,
                )

            except Exception as exc:  # noqa: BLE001
                log.exception(
                    "Runtime TTS failed: {}",
                    exc,
                )

                print()
                print(
                    "[TTS unavailable - continuing without audio]"
                )

        finally:
            await self._session.set_state(
                SessionState.IDLE,
            )

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFC",
            text,
        )

        normalized = (
            normalized.lower()
            .strip()
        )

        normalized = normalized.replace(
            "\u0e4d\u0e32",
            "\u0e33",
        )

        punctuation = (
            ".",
            ",",
            "!",
            "?",
            "。",
            "，",
            "！",
            "？",
            ":",
            ";",
        )

        for character in punctuation:
            normalized = normalized.replace(
                character,
                ""
            )

        return " ".join(
            normalized.split()
        )