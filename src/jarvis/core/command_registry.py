from collections.abc import Callable


class CommandRegistry:
    def __init__(self):
        self._commands: dict[str, Callable] = {}

    def register(self, name: str, callback: Callable) -> None:
        self._commands[name.lower()] = callback

    def execute(self, name: str):
        command = self._commands.get(name.lower())

        if command is None:
            raise ValueError(f"Unknown command: {name}")

        return command()

    def list_commands(self) -> list[str]:
        return sorted(self._commands.keys())


registry = CommandRegistry()