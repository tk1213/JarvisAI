from __future__ import annotations

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import RowMapping

from jarvis.database.db import DatabaseManager
from jarvis.memory.models import Memory
from jarvis.memory.types import (
    MemoryCategory,
    MemoryImportance,
)


class MemoryRepository:
    def __init__(
        self,
        database: DatabaseManager,
    ) -> None:
        self._database = database

    async def add(
        self,
        memory: Memory,
    ) -> int:
        sql = text(
            """
            INSERT INTO memories (
                category,
                key,
                value,
                importance,
                source,
                created_at,
                updated_at
            )
            VALUES (
                :category,
                :key,
                :value,
                :importance,
                :source,
                :created_at,
                :updated_at
            )
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "category": memory.category.value,
                    "key": memory.key.strip(),
                    "value": memory.value.strip(),
                    "importance": memory.importance.value,
                    "source": memory.source.strip(),
                    "created_at": memory.created_at.isoformat(),
                    "updated_at": memory.updated_at.isoformat(),
                },
            )

            inserted_id = result.lastrowid

        if inserted_id is None:
            raise RuntimeError(
                "Database did not return the inserted memory ID."
            )

        return int(inserted_id)

    async def get(
        self,
        memory_id: int,
    ) -> Memory | None:
        sql = text(
            """
            SELECT
                id,
                category,
                key,
                value,
                importance,
                source,
                created_at,
                updated_at
            FROM memories
            WHERE id = :memory_id
            LIMIT 1
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "memory_id": memory_id,
                },
            )

            row = result.mappings().first()

        if row is None:
            return None

        return self._row_to_memory(
            row
        )

    async def update(
        self,
        memory: Memory,
    ) -> bool:
        if memory.id is None:
            raise ValueError(
                "Memory ID is required for update."
            )

        sql = text(
            """
            UPDATE memories
            SET
                category = :category,
                key = :key,
                value = :value,
                importance = :importance,
                source = :source,
                updated_at = :updated_at
            WHERE id = :memory_id
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "memory_id": memory.id,
                    "category": memory.category.value,
                    "key": memory.key.strip(),
                    "value": memory.value.strip(),
                    "importance": memory.importance.value,
                    "source": memory.source.strip(),
                    "updated_at": memory.updated_at.isoformat(),
                },
            )

            affected_rows = result.rowcount

        return bool(
            affected_rows
            and affected_rows > 0
        )

    async def delete(
        self,
        memory_id: int,
    ) -> bool:
        sql = text(
            """
            DELETE FROM memories
            WHERE id = :memory_id
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "memory_id": memory_id,
                },
            )

            affected_rows = result.rowcount

        return bool(
            affected_rows
            and affected_rows > 0
        )

    async def find_by_key(
        self,
        key: str,
    ) -> list[Memory]:
        normalized_key = key.strip()

        if not normalized_key:
            return []

        sql = text(
            """
            SELECT
                id,
                category,
                key,
                value,
                importance,
                source,
                created_at,
                updated_at
            FROM memories
            WHERE key = :key
            ORDER BY
                importance DESC,
                updated_at DESC
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "key": normalized_key,
                },
            )

            rows = result.mappings().all()

        return [
            self._row_to_memory(row)
            for row in rows
        ]

    async def find_by_category(
        self,
        category: MemoryCategory,
    ) -> list[Memory]:
        sql = text(
            """
            SELECT
                id,
                category,
                key,
                value,
                importance,
                source,
                created_at,
                updated_at
            FROM memories
            WHERE category = :category
            ORDER BY
                importance DESC,
                updated_at DESC
            """
        )

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                {
                    "category": category.value,
                },
            )

            rows = result.mappings().all()

        return [
            self._row_to_memory(row)
            for row in rows
        ]

    async def list_all(
        self,
        *,
        limit: int | None = None,
    ) -> list[Memory]:
        if limit is not None and limit < 1:
            raise ValueError(
                "limit must be at least 1."
            )

        if limit is None:
            sql = text(
                """
                SELECT
                    id,
                    category,
                    key,
                    value,
                    importance,
                    source,
                    created_at,
                    updated_at
                FROM memories
                ORDER BY
                    importance DESC,
                    updated_at DESC
                """
            )

            parameters: dict[str, object] = {}

        else:
            sql = text(
                """
                SELECT
                    id,
                    category,
                    key,
                    value,
                    importance,
                    source,
                    created_at,
                    updated_at
                FROM memories
                ORDER BY
                    importance DESC,
                    updated_at DESC
                LIMIT :limit
                """
            )

            parameters = {
                "limit": limit,
            }

        async with self._database.session() as session:
            result = await session.execute(
                sql,
                parameters,
            )

            rows = result.mappings().all()

        return [
            self._row_to_memory(row)
            for row in rows
        ]

    @staticmethod
    def _row_to_memory(
        row: RowMapping,
    ) -> Memory:
        return Memory(
            id=int(row["id"]),
            category=MemoryCategory(
                str(row["category"])
            ),
            key=str(row["key"]),
            value=str(row["value"]),
            importance=MemoryImportance(
                int(row["importance"])
            ),
            source=str(row["source"]),
            created_at=MemoryRepository._parse_datetime(
                row["created_at"]
            ),
            updated_at=MemoryRepository._parse_datetime(
                row["updated_at"]
            ),
        )

    @staticmethod
    def _parse_datetime(
        value: object,
    ) -> datetime:
        if isinstance(
            value,
            datetime,
        ):
            return value

        return datetime.fromisoformat(
            str(value)
        )