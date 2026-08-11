from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from jarvis.config import settings
from jarvis.core.logger import log
from jarvis.database.models import Base
from jarvis.database.schema_agent_memory import (
    AGENT_MEMORY_INDEXES,
    AGENT_MEMORY_SCHEMA,
)
from jarvis.database.schema_memory import (
    MEMORY_INDEXES,
    MEMORY_SCHEMA,
)


class DatabaseManager:
    def __init__(self) -> None:
        self.engine: AsyncEngine = create_async_engine(
            settings.database_url,
            echo=False,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        self.started = False

    async def startup(self) -> None:
        if self.started:
            return

        log.info("Connecting to database...")

        async with self.engine.begin() as connection:
            await connection.execute(
                text("SELECT 1")
            )

            await connection.run_sync(
                Base.metadata.create_all
            )

            await self.create_memory_tables(
                connection
            )

            await self.create_agent_memory_tables(
                connection
            )

        self.started = True

        log.info("Database connected")

    async def create_memory_tables(
        self,
        connection: AsyncConnection,
    ) -> None:
        await connection.exec_driver_sql(
            MEMORY_SCHEMA
        )

        for sql in MEMORY_INDEXES:
            await connection.exec_driver_sql(
                sql
            )

    async def create_agent_memory_tables(
        self,
        connection: AsyncConnection,
    ) -> None:
        await connection.exec_driver_sql(
            AGENT_MEMORY_SCHEMA
        )

        for sql in AGENT_MEMORY_INDEXES:
            await connection.exec_driver_sql(
                sql
            )

    async def health_check(self) -> bool:
        try:
            async with self.engine.connect() as connection:
                await connection.execute(
                    text("SELECT 1")
                )

            return True

        except Exception:  # noqa: BLE001
            log.exception(
                "Database health check failed"
            )
            return False

    @asynccontextmanager
    async def session(
        self,
    ) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()

            except Exception:
                await session.rollback()
                raise

    async def shutdown(self) -> None:
        if not self.started:
            return

        await self.engine.dispose()

        self.started = False

        log.info("Database disconnected")