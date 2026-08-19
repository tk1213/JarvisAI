from sqlalchemy import delete, select

from jarvis.database.db import DatabaseManager
from jarvis.database.models import ChatMessage


class MemoryService:
    def __init__(self, database: DatabaseManager) -> None:
        self.database = database

    async def save_message(
        self,
        role: str,
        content: str,
    ) -> None:
        message = ChatMessage(
            role=role,
            content=content,
        )

        async with self.database.session() as session:
            session.add(message)

    async def save_turn(
        self,
        user_content: str,
        assistant_content: str,
    ) -> None:
        user_message = ChatMessage(
            role="user",
            content=user_content,
        )

        assistant_message = ChatMessage(
            role="assistant",
            content=assistant_content,
        )

        async with self.database.session() as session:
            session.add(
                user_message
            )
            session.add(
                assistant_message
            )

    async def get_recent_messages(
        self,
        limit: int = 20,
    ) -> list[ChatMessage]:
        async with self.database.session() as session:
            statement = (
                select(ChatMessage)
                .order_by(ChatMessage.id.desc())
                .limit(limit)
            )

            result = await session.execute(statement)
            messages = list(result.scalars().all())

        messages.reverse()
        return messages

    async def get_ai_history(
        self,
        limit: int = 20,
    ) -> list[dict[str, str]]:
        messages = await self.get_recent_messages(limit)

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
            if message.role in {"user", "assistant"}
        ]

    async def clear_messages(self) -> None:
        async with self.database.session() as session:
            await session.execute(delete(ChatMessage))