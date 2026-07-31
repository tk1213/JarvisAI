from pathlib import Path

from jarvis.core.logger import log

PLUGIN_DIR = Path("src/jarvis/plugins")


def load_plugins():

    if not PLUGIN_DIR.exists():
        log.warning("Plugin directory not found.")
        return

    for file in PLUGIN_DIR.glob("*.py"):

        if file.name.startswith("_"):
            continue

        log.info(f"Loaded plugin : {file.stem}")