from jarvis.core.container import container
from jarvis.core.task_manager import task_manager


class HealthService:
    async def check(self) -> dict[str, bool]:
        results: dict[str, bool] = {}

        results["service_container"] = (
            container.has("system")
            and container.has("commands")
            and container.has("database")
            and container.has("heartbeat")
        )

        database = container.get("database")
        results["database"] = await database.health_check()

        results["heartbeat_task"] = (
            "heartbeat" in task_manager.list_tasks()
        )

        system = container.get("system")
        results["system_service"] = system is not None

        return results

    async def is_healthy(self) -> bool:
        results = await self.check()
        return all(results.values())