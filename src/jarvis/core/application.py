from __future__ import annotations

from jarvis.audio.player import AudioPlayer
from jarvis.audio.recorder import AudioRecorder
from jarvis.core.container import container
from jarvis.core.logger import log
from jarvis.core.plugin_loader import load_plugins
from jarvis.core.task_manager import task_manager
from jarvis.database.db import DatabaseManager
from jarvis.services.ai_service import AIService
from jarvis.services.command_service import CommandService
from jarvis.services.conversation_manager import ConversationManager
from jarvis.services.health_service import HealthService
from jarvis.services.heartbeat_service import HeartbeatService
from jarvis.services.memory_service import MemoryService
from jarvis.services.session_manager import SessionManager
from jarvis.services.stt_service import STTService
from jarvis.services.system_service import SystemService
from jarvis.services.tool_router import ToolRouter
from jarvis.services.tts_service import TTSService
from jarvis.services.voice_service import VoiceService
from jarvis.smart_home.mock_adapter import MockAdapter
from jarvis.smart_home.service import SmartHomeService
from jarvis.speech.stt import SpeechToText
from jarvis.speech.tts import TextToSpeech


class JarvisApplication:
    def __init__(self) -> None:
        self.started = False

    async def start(
        self,
        start_background_tasks: bool = True,
    ) -> None:
        if self.started:
            return

        log.info("Initializing Jarvis Application...")

        # ---------------------------------------------------------
        # Core components
        # ---------------------------------------------------------
        system = SystemService()
        commands = CommandService()
        database = DatabaseManager()

        # ---------------------------------------------------------
        # Application services
        # ---------------------------------------------------------
        memory_service = MemoryService(database)
        ai_service = AIService()
        session_manager = SessionManager()
        tool_router = ToolRouter()

        # ---------------------------------------------------------
        # Smart Home services
        # ---------------------------------------------------------
        smart_home_adapter = MockAdapter()
        smart_home_service = SmartHomeService(
            adapter=smart_home_adapter,
        )

        conversation_manager = ConversationManager(
            ai=ai_service,
            memory=memory_service,
            router=tool_router,
            smart_home=smart_home_service,
        )

        heartbeat_service = HeartbeatService()
        health_service = HealthService()

        # ---------------------------------------------------------
        # Speech-to-text components
        # ---------------------------------------------------------
        recorder = AudioRecorder()
        stt_engine = SpeechToText()

        stt_service = STTService(
            recorder=recorder,
            stt=stt_engine,
        )

        # ---------------------------------------------------------
        # Text-to-speech components
        # ---------------------------------------------------------
        player = AudioPlayer()
        tts_engine = TextToSpeech()

        tts_service = TTSService(
            player=player,
            tts=tts_engine,
        )

        # ---------------------------------------------------------
        # Voice service
        # ---------------------------------------------------------
        voice_service = VoiceService(
            stt=stt_service,
            conversation=conversation_manager,
            tts=tts_service,
            session=session_manager,
        )

        # ---------------------------------------------------------
        # Register core services
        # ---------------------------------------------------------
        container.register("system", system)
        container.register("commands", commands)
        container.register("database", database)
        container.register("tool_router", tool_router)
        container.register("session", session_manager)

        # ---------------------------------------------------------
        # Register application services
        # ---------------------------------------------------------
        container.register("memory", memory_service)
        container.register("ai", ai_service)
        container.register("conversation", conversation_manager)
        container.register("heartbeat", heartbeat_service)
        container.register("health", health_service)

        # ---------------------------------------------------------
        # Register Smart Home services
        # ---------------------------------------------------------
        container.register(
            "smart_home_adapter",
            smart_home_adapter,
        )
        container.register(
            "smart_home",
            smart_home_service,
        )

        # ---------------------------------------------------------
        # Register speech-to-text services
        # ---------------------------------------------------------
        container.register("recorder", recorder)
        container.register("stt_engine", stt_engine)
        container.register("stt", stt_service)

        # ---------------------------------------------------------
        # Register text-to-speech services
        # ---------------------------------------------------------
        container.register("player", player)
        container.register("tts_engine", tts_engine)
        container.register("tts", tts_service)

        # ---------------------------------------------------------
        # Register voice service
        # ---------------------------------------------------------
        container.register("voice", voice_service)

        # ---------------------------------------------------------
        # Start core services
        # ---------------------------------------------------------
        system.startup()
        await database.startup()
        await smart_home_service.connect()

        # Register built-in commands
        commands.register_default_commands()

        # ---------------------------------------------------------
        # Start background services
        # ---------------------------------------------------------
        if start_background_tasks:
            task_manager.create_task(
                "heartbeat",
                heartbeat_service.run(),
            )

        # Load external plugins
        load_plugins()

        self.started = True
        log.info("Jarvis Application Ready")

    async def shutdown(self) -> None:
        if not self.started:
            return

        log.info("Shutting down Jarvis Application...")

        await task_manager.stop_all()

        smart_home_service = container.get("smart_home")
        await smart_home_service.disconnect()

        database = container.get("database")
        await database.shutdown()

        system = container.get("system")
        system.shutdown()

        self.started = False
        log.info("Jarvis Application Stopped")