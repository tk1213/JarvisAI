from __future__ import annotations

import asyncio
import unicodedata

from jarvis.core.session import SessionState
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.session_manager import SessionManager
from jarvis.services.stt_service import STTService
from jarvis.services.tts_service import TTSService


class VoiceService:
    def __init__(
        self,
        stt: STTService,
        conversation: ConversationManager,
        tts: TTSService,
        session: SessionManager,
    ) -> None:
        self._stt = stt
        self._conversation = conversation
        self._tts = tts
        self._session = session

        self._continuous_running = False

    @property
    def continuous_running(self) -> bool:
        return self._continuous_running

    async def listen_for_text(
        self,
        seconds: float = 5.0,
        language: str = "th",
    ) -> str:
        """
        Listen for one real user utterance without sending it
        to ConversationManager.

        Repeated wake words are ignored automatically.
        """

        try:
            while True:
                text = await self._listen(
                    seconds=seconds,
                    language=language,
                )

                if not text:
                    return ""

                if self._is_duplicate_wake_word(
                    text
                ):
                    print()
                    print(
                        "Wake word repeated. "
                        "Waiting for command..."
                    )
                    continue

                return text

        finally:
            await self._session.set_state(
                SessionState.IDLE,
            )

    async def reply_to_text(
        self,
        text: str,
    ) -> str:
        text = text.strip()

        if not text:
            return ""

        return await self._reply(
            text
        )

    async def listen_and_reply(
        self,
        seconds: float = 5.0,
        language: str = "th",
    ) -> str:
        try:
            text = await self.listen_for_text(
                seconds=seconds,
                language=language,
            )

            if not text:
                print()
                print("[No speech detected]")
                return ""

            return await self.reply_to_text(
                text
            )

        finally:
            await self._session.set_state(
                SessionState.IDLE,
            )

    async def run_continuous(
        self,
        seconds: float = 5.0,
        language: str = "th",
        idle_delay: float = 0.25,
    ) -> None:
        if self._continuous_running:
            raise RuntimeError(
                "Continuous voice session is already running."
            )

        self._continuous_running = True

        print()
        print("=" * 60)
        print(" JarvisAI Continuous Voice Session")
        print("=" * 60)
        print()
        print("Jarvis is listening continuously.")
        print(
            'พูด "หยุดการทำงาน" '
            "เพื่อออกจากโหมดสนทนา"
        )
        print()

        try:
            while self._continuous_running:
                text = await self.listen_for_text(
                    seconds=seconds,
                    language=language,
                )

                if not text:
                    await self._session.set_state(
                        SessionState.IDLE,
                    )

                    if idle_delay > 0:
                        await asyncio.sleep(
                            idle_delay
                        )

                    continue

                print()
                print(f"You: {text}")

                if self._is_stop_command(
                    text
                ):
                    await self._stop_with_reply()
                    break

                await self._reply(
                    text,
                    print_user=False,
                )

                if idle_delay > 0:
                    await asyncio.sleep(
                        idle_delay
                    )

        except asyncio.CancelledError:
            self._continuous_running = False
            raise

        finally:
            self._continuous_running = False

            await self._session.set_state(
                SessionState.IDLE,
            )

            print()
            print(
                "Continuous voice session stopped."
            )

    def stop_continuous(self) -> None:
        self._continuous_running = False

    async def _listen(
        self,
        *,
        seconds: float,
        language: str,
    ) -> str:
        await self._session.set_state(
            SessionState.LISTENING,
        )

        text = await self._stt.listen(
            seconds=seconds,
            language=language,
        )

        return text.strip()

    async def _reply(
        self,
        text: str,
        *,
        print_user: bool = True,
    ) -> str:
        if print_user:
            print()
            print(f"You: {text}")

        await self._session.set_state(
            SessionState.THINKING,
        )

        reply = await self._conversation.ask(
            text=text,
            voice_mode=True,
        )

        reply = reply.strip()

        if not reply:
            print()
            print("[AI returned no response]")

            await self._session.set_state(
                SessionState.IDLE,
            )

            return ""

        print()
        print(f"Jarvis: {reply}")

        await self._session.set_state(
            SessionState.SPEAKING,
        )

        await self._tts.speak(
            text=reply,
        )

        await self._session.set_state(
            SessionState.IDLE,
        )

        return reply

    async def _stop_with_reply(
        self,
    ) -> None:
        self._continuous_running = False

        reply = "หยุดการฟังแล้วครับ"

        print()
        print(f"Jarvis: {reply}")

        await self._session.set_state(
            SessionState.SPEAKING,
        )

        await self._tts.speak(
            text=reply,
        )

        await self._session.set_state(
            SessionState.IDLE,
        )

    @classmethod
    def _is_duplicate_wake_word(
        cls,
        text: str,
    ) -> bool:
        normalized = cls._normalize_command_text(
            text
        )

        exact_phrases = {
            "jarvis",
            "hey jarvis",
            "hi jarvis",
            "hello jarvis",
            "จาร์วิส",
            "จาวิส",
            "เฮ้จาร์วิส",
            "เฮ้ จาร์วิส",
            "เฮ้จาวิส",
            "เฮ้ จาวิส",
        }

        if normalized in exact_phrases:
            return True

        compact = normalized.replace(
            " ",
            "",
        )

        compact_phrases = {
            "heyjarvis",
            "เฮ้จาร์วิส",
            "เฮ้จาวิส",
        }

        return compact in compact_phrases

    @classmethod
    def _is_stop_command(
        cls,
        text: str,
    ) -> bool:
        normalized = cls._normalize_command_text(
            text
        )

        exact_commands = {
            "หยุด",
            "หยุดฟัง",
            "หยุดการฟัง",
            "หยุดทำงาน",
            "หยุดการทำงาน",
            "เลิกฟัง",
            "เลิกการฟัง",
            "หยุดจาร์วิส",
            "หยุดจาวิส",
            "จาร์วิสหยุด",
            "จาวิสหยุด",
            "ยุทธการทำงาน",
            "ยุทธทำงาน",
            "stop",
            "stop listening",
            "stop jarvis",
            "jarvis stop",
            "exit voice",
            "stop voice",
            "yud",
            "yoot",
            "you chavis",
            "you jarvis",
        }

        if normalized in exact_commands:
            return True

        stop_phrases = (
            "หยุดการฟัง",
            "หยุดการทำงาน",
            "หยุดจาร์วิส",
            "หยุดจาวิส",
            "stop listening",
            "stop jarvis",
            "jarvis stop",
        )

        return any(
            phrase in normalized
            for phrase in stop_phrases
        )

    @staticmethod
    def _normalize_command_text(
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

