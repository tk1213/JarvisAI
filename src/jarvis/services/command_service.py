from jarvis.core.command_registry import registry
from jarvis.version import __version__


class CommandService:

    def register_default_commands(self):

        registry.register("help", self.help)
        registry.register("status", self.status)
        registry.register("version", self.version)

    def help(self):

        print("\nAvailable Commands")

        for cmd in registry.list_commands():
            print(f" - {cmd}")

    def status(self):

        print("JarvisAI is running.")

    def version(self):

        print(f"JarvisAI Version {__version__}")