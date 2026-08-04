from __future__ import annotations

import unicodedata
from typing import ClassVar

from jarvis.memory.extractor import MemoryExtractor
from jarvis.memory.service import MemoryService


class MemoryCommandService:
    _LIST_COMMANDS: ClassVar[frozenset[str]] = frozenset(
        {
            "what do you remember about me",
            "what do you remember",
            "show my memories",
            "list my memories",
            "คุณจำอะไรเกี่ยวกับผมบ้าง",
            "คุณจำอะไรเกี่ยวกับฉันบ้าง",
            "จำอะไรเกี่ยวกับผมบ้าง",
            "จำอะไรเกี่ยวกับฉันบ้าง",
        }
    )

    _FORGET_ALL_COMMANDS: ClassVar[frozenset[str]] = frozenset(
        {
            "forget everything about me",
            "forget all my memories",
            "delete all my memories",
            "ลืมทุกอย่างเกี่ยวกับผม",
            "ลืมทุกอย่างเกี่ยวกับฉัน",
            "ลบความจำทั้งหมด",
        }
    )

    _CONFIRM_COMMANDS: ClassVar[frozenset[str]] = frozenset(
        {
            "yes",
            "confirm",
            "yes confirm",
            "ยืนยัน",
            "ใช่",
            "ใช่ ยืนยัน",
        }
    )

    _CANCEL_COMMANDS: ClassVar[frozenset[str]] = frozenset(
        {
            "no",
            "cancel",
            "never mind",
            "nevermind",
            "ไม่",
            "ไม่ต้อง",
            "ยกเลิก",
        }
    )

    _KEY_LABELS: ClassVar[dict[str, str]] = {
        "user_name": "your name",
        "daughter_name": "your daughter's name",
        "son_name": "your son's name",
        "wife_name": "your wife's name",
        "husband_name": "your husband's name",
        "favorite_drink": "your favorite drink",
        "favorite_food": "your favorite food",
    }

    _FORGET_KEY_PHRASES: ClassVar[
        dict[str, tuple[str, ...]]
    ] = {
        "user_name": (
            "forget my name",
            "forget my user name",
            "ลืมชื่อผม",
            "ลืมชื่อฉัน",
        ),
        "daughter_name": (
            "forget my daughter name",
            "forget my daughter's name",
            "ลืมชื่อลูกสาว",
        ),
        "son_name": (
            "forget my son name",
            "forget my son's name",
            "ลืมชื่อลูกชาย",
        ),
        "wife_name": (
            "forget my wife name",
            "forget my wife's name",
            "ลืมชื่อภรรยา",
        ),
        "husband_name": (
            "forget my husband name",
            "forget my husband's name",
            "ลืมชื่อสามี",
        ),
        "favorite_drink": (
            "forget my favorite drink",
            "forget what i like to drink",
            "ลืมเครื่องดื่มที่ผมชอบ",
            "ลืมเครื่องดื่มที่ฉันชอบ",
            "ลืมว่าผมชอบดื่มอะไร",
            "ลืมว่าฉันชอบดื่มอะไร",
        ),
        "favorite_food": (
            "forget my favorite food",
            "forget what i like to eat",
            "ลืมอาหารที่ผมชอบ",
            "ลืมอาหารที่ฉันชอบ",
            "ลืมว่าผมชอบกินอะไร",
            "ลืมว่าฉันชอบกินอะไร",
        ),
    }

    _REMEMBER_PREFIXES: ClassVar[tuple[str, ...]] = (
        "remember that ",
        "remember ",
        "จำไว้ว่าผม",
        "จำไว้ว่าฉัน",
        "จำไว้ว่า",
        "จำว่า",
    )

    def __init__(
        self,
        *,
        memory: MemoryService,
        extractor: MemoryExtractor,
    ) -> None:
        self._memory = memory
        self._extractor = extractor
        self._pending_delete_key: str | None = None
        self._pending_delete_all = False

    async def handle(
        self,
        text: str,
    ) -> str | None:
        normalized = self._normalize(
            text
        )

        if not normalized:
            return None

        if self.has_pending_confirmation:
            return await self._handle_confirmation(
                normalized
            )

        if normalized in self._LIST_COMMANDS:
            return await self._list_memories()

        if normalized in self._FORGET_ALL_COMMANDS:
            self._pending_delete_all = True
            return (
                "This will delete all long-term memories. "
                "Say \"confirm\" to continue or \"cancel\" to stop."
            )

        forget_key = self._resolve_forget_key(
            normalized
        )

        if forget_key is not None:
            existing = await self._memory.recall(
                forget_key
            )

            if existing is None:
                return (
                    "I do not have that information stored."
                )

            self._pending_delete_key = forget_key
            label = self._KEY_LABELS.get(
                forget_key,
                forget_key,
            )

            return (
                f"I found {label}: {existing.value}. "
                "Say \"confirm\" to forget it or \"cancel\" to keep it."
            )

        if self._is_remember_command(
            normalized
        ):
            return await self._remember(
                text
            )

        return None

    @property
    def has_pending_confirmation(
        self,
    ) -> bool:
        return (
            self._pending_delete_all
            or self._pending_delete_key is not None
        )

    async def _remember(
        self,
        text: str,
    ) -> str:
        extracted = self._extractor.extract(
            text
        )

        if not extracted:
            return (
                "I could not identify a supported fact to remember. "
                "Try something like \"My name is TK\" or "
                "\"I like drinking black coffee\"."
            )

        stored = 0

        for item in extracted:
            await self._memory.remember(
                category=item.category,
                key=item.key,
                value=item.value,
                importance=item.importance,
                source="user",
            )
            stored += 1

        if stored == 1:
            return "I remembered that."

        return (
            f"I remembered {stored} facts."
        )

    async def _list_memories(
        self,
    ) -> str:
        memories = await self._memory.list_memories(
            limit=50
        )

        if not memories:
            return (
                "I do not have any long-term memories about you yet."
            )

        descriptions: list[str] = []

        for memory in memories:
            label = self._KEY_LABELS.get(
                memory.key,
                memory.key.replace("_", " "),
            )
            descriptions.append(
                f"{label}: {memory.value}"
            )

        return (
            "I currently remember: "
            + "; ".join(descriptions)
        )

    async def _handle_confirmation(
        self,
        normalized: str,
    ) -> str:
        if normalized in self._CANCEL_COMMANDS:
            self._clear_pending()
            return (
                "Memory deletion cancelled."
            )

        if normalized not in self._CONFIRM_COMMANDS:
            return (
                "Please say \"confirm\" to delete the memory "
                "or \"cancel\" to keep it."
            )

        if self._pending_delete_all:
            deleted = await self._memory.forget_all()
            self._clear_pending()
            return (
                f"Deleted {deleted} long-term memories."
            )

        key = self._pending_delete_key

        if key is None:
            self._clear_pending()
            return (
                "There is no pending memory deletion."
            )

        deleted = await self._memory.forget(
            key
        )
        self._clear_pending()

        if deleted:
            return (
                "I forgot that information."
            )

        return (
            "I could not find that memory to delete."
        )

    def _clear_pending(
        self,
    ) -> None:
        self._pending_delete_all = False
        self._pending_delete_key = None

    @classmethod
    def _resolve_forget_key(
        cls,
        normalized: str,
    ) -> str | None:
        for key, phrases in cls._FORGET_KEY_PHRASES.items():
            if normalized in phrases:
                return key

        return None

    @classmethod
    def _is_remember_command(
        cls,
        normalized: str,
    ) -> bool:
        return any(
            normalized.startswith(prefix)
            for prefix in cls._REMEMBER_PREFIXES
        )

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        normalized = unicodedata.normalize(
            "NFC",
            text,
        ).casefold()

        normalized = normalized.strip(
            " \t\r\n.,!?，。"
        )

        return " ".join(
            normalized.split()
        )
