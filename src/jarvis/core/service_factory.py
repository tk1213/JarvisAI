from __future__ import annotations

from jarvis.audio.manager import AudioManager
from jarvis.audio.player import AudioPlayer
from jarvis.audio.recorder import AudioRecorder
from jarvis.config import settings
from jarvis.core.container import ServiceContainer
from jarvis.core.logger import log
from jarvis.database.db import DatabaseManager
from jarvis.memory.audit_repository import MemoryAuditRepository
from jarvis.memory.audit_service import MemoryAuditService
from jarvis.memory.aware_conversation import MemoryAwareConversationManager
from jarvis.memory.capture import MemoryCaptureService
from jarvis.memory.commands import MemoryCommandService
from jarvis.memory.context import MemoryContextBuilder
from jarvis.memory.extractor import MemoryExtractor
from jarvis.memory.repository import MemoryRepository
from jarvis.memory.retriever import MemoryRetriever
from jarvis.memory.service import MemoryService as LongTermMemoryService
from jarvis.services.ai_service import AIService
from jarvis.services.assistant_runtime_service import AssistantRuntimeService
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
from jarvis.services.wake_word_service import WakeWordService
from jarvis.smart_home.adapter import SmartHomeAdapter
from jarvis.smart_home.mock_adapter import MockAdapter
from jarvis.smart_home.service import SmartHomeService
from jarvis.smart_home.tuya_adapter import TuyaAdapter
from jarvis.speech.stt import SpeechToText
from jarvis.speech.tts import TextToSpeech
from jarvis.voice.turn_runtime import VoiceTurnRuntime
from jarvis.wake.boundary import WakeActivationBoundary


class ServiceFactory:
    def __init__(
        self,
        container: ServiceContainer,
    ) -> None:
        self.container = container

    def register_core(self) -> None:
        system = SystemService()
        commands = CommandService()
        database = DatabaseManager()
        session_manager = SessionManager()
        tool_router = ToolRouter()
        heartbeat_service = HeartbeatService()
        health_service = HealthService()

        self.container.register("system", system, overwrite=False)
        self.container.register("commands", commands, overwrite=False)
        self.container.register("database", database, overwrite=False)
        self.container.register("session", session_manager, overwrite=False)
        self.container.register("tool_router", tool_router, overwrite=False)
        self.container.register("heartbeat", heartbeat_service, overwrite=False)
        self.container.register("health", health_service, overwrite=False)

    def register_smart_home(self) -> None:
        smart_home_adapter = self._create_smart_home_adapter()
        smart_home_service = SmartHomeService(
            adapter=smart_home_adapter,
        )

        self.container.register(
            "smart_home_adapter",
            smart_home_adapter,
            overwrite=False,
        )
        self.container.register(
            "smart_home",
            smart_home_service,
            overwrite=False,
        )

    def _create_smart_home_adapter(self) -> SmartHomeAdapter:
        provider = settings.smart_home_provider.strip().lower()

        if provider == "mock":
            return MockAdapter()

        if provider == "tuya":
            return TuyaAdapter()

        raise ValueError(
            "Unsupported SMART_HOME_PROVIDER: "
            f"{settings.smart_home_provider}"
        )

    def register_ai(self) -> None:
        database = self.container.resolve(
            "database",
            DatabaseManager,
        )
        tool_router = self.container.resolve(
            "tool_router",
            ToolRouter,
        )
        smart_home_service = self.container.resolve(
            "smart_home",
            SmartHomeService,
        )

        memory_service = MemoryService(database)
        ai_service = AIService()

        long_term_repository = MemoryRepository(database)
        memory_audit_repository = MemoryAuditRepository(database)
        memory_audit = MemoryAuditService(memory_audit_repository)
        long_term_memory = LongTermMemoryService(
            long_term_repository,
            audit=memory_audit,
        )
        memory_extractor = MemoryExtractor()
        memory_commands = MemoryCommandService(
            memory=long_term_memory,
            extractor=memory_extractor,
        )
        memory_capture = MemoryCaptureService(
            extractor=memory_extractor,
            memory=long_term_memory,
            audit=memory_audit,
        )
        memory_retriever = MemoryRetriever(long_term_memory)
        memory_context = MemoryContextBuilder(memory_retriever)

        conversation_manager = MemoryAwareConversationManager(
            ai=ai_service,
            memory=memory_service,
            router=tool_router,
            smart_home=smart_home_service,
            memory_capture=memory_capture,
            memory_context=memory_context,
            memory_commands=memory_commands,
        )

        self.container.register("memory", memory_service, overwrite=False)
        self.container.register("ai", ai_service, overwrite=False)
        self.container.register(
            "conversation",
            conversation_manager,
            overwrite=False,
        )
        self.container.register(
            "long_term_memory_repository",
            long_term_repository,
            overwrite=False,
        )
        self.container.register(
            "long_term_memory",
            long_term_memory,
            overwrite=False,
        )
        self.container.register(
            "memory_audit_repository",
            memory_audit_repository,
            overwrite=False,
        )
        self.container.register(
            "memory_audit",
            memory_audit,
            overwrite=False,
        )
        self.container.register(
            "memory_extractor",
            memory_extractor,
            overwrite=False,
        )
        self.container.register(
            "memory_capture",
            memory_capture,
            overwrite=False,
        )
        self.container.register(
            "memory_retriever",
            memory_retriever,
            overwrite=False,
        )
        self.container.register(
            "memory_context",
            memory_context,
            overwrite=False,
        )
        self.container.register(
            "memory_commands",
            memory_commands,
            overwrite=False,
        )

    def register_voice(self) -> None:
        conversation_manager = self.container.resolve(
            "conversation",
            ConversationManager,
        )
        session_manager = self.container.resolve(
            "session",
            SessionManager,
        )

        audio = AudioManager()

        recorder = AudioRecorder(
            audio=audio,
        )

        stt_engine = SpeechToText()
        stt_service = STTService(
            recorder=recorder,
            stt=stt_engine,
        )

        player = AudioPlayer(
            audio=audio,
        )

        tts_engine = TextToSpeech()
        tts_service = TTSService(
            player=player,
            tts=tts_engine,
        )

        voice_service = VoiceService(
            stt=stt_service,
            conversation=conversation_manager,
            tts=tts_service,
            session=session_manager,
        )

        voice_turn_runtime = VoiceTurnRuntime(
            stt=stt_service,
            conversation=conversation_manager,
            tts=tts_service,
        )

        wake_word_service = WakeWordService(
            audio=audio,
        )
        wake_activation = WakeActivationBoundary(
            wake_word_service
        )

        assistant_runtime = AssistantRuntimeService(
            wake_word=wake_word_service,
            voice=voice_service,
            conversation=conversation_manager,
            tts=tts_service,
            session=session_manager,
        )

        self.container.register("audio", audio, overwrite=False)
        self.container.register("recorder", recorder, overwrite=False)
        self.container.register("stt_engine", stt_engine, overwrite=False)
        self.container.register("stt", stt_service, overwrite=False)
        self.container.register("player", player, overwrite=False)
        self.container.register("tts_engine", tts_engine, overwrite=False)
        self.container.register("tts", tts_service, overwrite=False)
        self.container.register("voice", voice_service, overwrite=False)
        self.container.register(
            "voice_turn",
            voice_turn_runtime,
            overwrite=False,
        )
        self.container.register(
            "wake_word",
            wake_word_service,
            overwrite=False,
        )
        self.container.register(
            "wake_activation",
            wake_activation,
            overwrite=False,
        )
        self.container.register(
            "assistant_runtime",
            assistant_runtime,
            overwrite=False,
        )

    def register_all(self) -> None:
        self.register_core()
        self.register_smart_home()
        self.register_ai()

        try:
            self.register_voice()

        except Exception:  # noqa: BLE001
            log.exception(
                "Voice subsystem registration failed; "
                "continuing without voice runtime"
            )
