from typing import Any


class ServiceContainer:
    def __init__(self):
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        self._services[name] = service

    def get(self, name: str) -> Any:
        if name not in self._services:
            raise KeyError(f"Service '{name}' is not registered.")
        return self._services[name]

    def has(self, name: str) -> bool:
        return name in self._services

    def list_services(self) -> list[str]:
        return sorted(self._services.keys())


container = ServiceContainer()