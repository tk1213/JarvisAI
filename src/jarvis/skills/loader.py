from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType

from loguru import logger

from jarvis.skills.base import Skill
from jarvis.skills.context import SkillContext
from jarvis.skills.manager import SkillManager


class SkillLoader:
    def __init__(
        self,
        manager: SkillManager,
        context: SkillContext,
    ) -> None:
        self._manager = manager
        self._context = context

    def load_package(
        self,
        package_name: str,
    ) -> None:
        package = importlib.import_module(package_name)

        if not hasattr(package, "__path__"):
            raise ValueError(
                f"{package_name} is not a package."
            )

        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            full_name = f"{package_name}.{module_name}"

            logger.info("Loading module: {}", full_name)

            module = importlib.import_module(full_name)

            self._load_module(module)

    def _load_module(
        self,
        module: ModuleType,
    ) -> None:
        for _, cls in inspect.getmembers(
            module,
            inspect.isclass,
        ):
            if cls is Skill:
                continue

            if not issubclass(cls, Skill):
                continue

            try:
                skill = cls(self._context)

                self._manager.register(skill)

                logger.info(
                    "Loaded skill: {}",
                    skill.metadata.name,
                )

            except (
                ImportError,
                AttributeError,
                TypeError,
                ValueError,
            ):
                logger.exception(
                    "Failed loading {}",
                    cls.__name__,
                )