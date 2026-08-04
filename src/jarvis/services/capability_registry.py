from __future__ import annotations

from collections.abc import Iterable

from jarvis.services.capability import CapabilityDefinition


class CapabilityRegistry:
    def __init__(
        self,
        capabilities: Iterable[
            str | CapabilityDefinition
        ]
        | None = None,
    ) -> None:
        self._capabilities: dict[
            str,
            CapabilityDefinition,
        ] = {}

        if capabilities is not None:
            for capability in capabilities:
                self.register(capability)

    @classmethod
    def from_capabilities(
        cls,
        capabilities: Iterable[
            str | CapabilityDefinition
        ],
    ) -> CapabilityRegistry:
        return cls(capabilities)

    def register(
        self,
        capability: str | CapabilityDefinition,
    ) -> None:
        if isinstance(
            capability,
            CapabilityDefinition,
        ):
            definition = capability

        else:
            capability = capability.strip()

            if not capability:
                raise ValueError(
                    "Capability cannot be empty."
                )

            definition = CapabilityDefinition(
                name=capability,
            )

        self._capabilities[
            definition.name
        ] = definition

    def unregister(
        self,
        capability: str,
    ) -> None:
        self._capabilities.pop(
            capability.strip(),
            None,
        )

    def get(
        self,
        capability: str,
    ) -> CapabilityDefinition | None:
        return self._capabilities.get(
            capability.strip(),
        )

    def is_allowed(
        self,
        capability: str,
    ) -> bool:
        return (
            capability.strip()
            in self._capabilities
        )

    def list_capabilities(
        self,
    ) -> list[str]:
        return sorted(
            self._capabilities,
        )

    def list_definitions(
        self,
    ) -> list[CapabilityDefinition]:
        return [
            self._capabilities[name]
            for name in sorted(
                self._capabilities
            )
        ]

    def __contains__(
        self,
        capability: str,
    ) -> bool:
        return self.is_allowed(
            capability,
        )

    def __len__(self) -> int:
        return len(
            self._capabilities
        )