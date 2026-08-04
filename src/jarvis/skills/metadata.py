from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SkillMetadata:
    name: str
    version: str

    description: str = ""
    author: str = "JarvisAI"

    capabilities: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)

    priority: int = 100
    enabled: bool = True

    homepage: str | None = None
    license: str | None = None