from jarvis.core.logger import log


class SystemService:
    def startup(self) -> None:
        log.info("System Service Started")

    def shutdown(self) -> None:
        log.info("System Service Stopped")