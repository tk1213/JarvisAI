from __future__ import annotations

import asyncio

from jarvis.core.session import SessionState
from jarvis.services.session_manager import SessionManager


async def main() -> None:
    session = SessionManager()

    print(session.state)

    await session.set_state(SessionState.STARTING)
    print(session.state)

    await session.set_state(SessionState.IDLE)
    print(session.state)

    await session.set_state(SessionState.LISTENING)
    print(session.state)

    await session.set_state(SessionState.THINKING)
    print(session.state)

    await session.set_state(SessionState.SPEAKING)
    print(session.state)


if __name__ == "__main__":
    asyncio.run(main())