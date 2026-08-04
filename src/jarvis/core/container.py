from typing import Any, TypeVar, cast

T = TypeVar("T")


class ServiceContainer:
    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(
        self,
        name: str,
        service: Any,
        *,
        overwrite: bool = True,
    ) -> None:
        if not overwrite and name in self._services:
            raise ValueError(
                f"Service '{name}' is already registered."
            )

        self._services[name] = service

    def unregister(self, name: str) -> None:
        self._services.pop(name, None)

    def get(self, name: str) -> Any:
        if name not in self._services:
            raise KeyError(
                f"Service '{name}' is not registered."
            )

        return self._services[name]

    def resolve(self, name: str, expected_type: type[T]) -> T:
        service = self.get(name)

        if not isinstance(service, expected_type):
            raise TypeError(
                f"Service '{name}' is not of type "
                f"{expected_type.__name__}."
            )

        return cast(T, service)

    def has(self, name: str) -> bool:
        return name in self._services

    def clear(self) -> None:
        self._services.clear()

    def list_services(self) -> list[str]:
        return sorted(self._services.keys())

    def __contains__(self, name: str) -> bool:
        return self.has(name)

    def __len__(self) -> int:
        return len(self._services)


container = ServiceContainer()