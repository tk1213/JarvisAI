from pathlib import Path

from jarvis.core.logger import log

BASE_DIR = Path(__file__).resolve().parents[3]
PROMPTS_DIR = BASE_DIR / "prompts"


class PromptManager:
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def load(self, name: str) -> str:
        if name in self._cache:
            return self._cache[name]

        prompt_path = PROMPTS_DIR / f"{name}.txt"

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}"
            )

        prompt = prompt_path.read_text(
            encoding="utf-8",
        ).strip()

        if not prompt:
            raise ValueError(
                f"Prompt file is empty: {prompt_path}"
            )

        self._cache[name] = prompt

        log.info("Loaded prompt: {}", name)

        return prompt

    def reload(self, name: str) -> str:
        self._cache.pop(name, None)
        return self.load(name)

    def clear_cache(self) -> None:
        self._cache.clear()


prompt_manager = PromptManager()