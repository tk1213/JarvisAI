from loguru import logger

logger.add(
    "logs/jarvis.log",
    rotation="5 MB",
    retention=10,
    enqueue=True,
)

log = logger