from __future__ import annotations

from novel2audiobook.tts.melotts_engine import MeloTTSEngine
from novel2audiobook.tts.qwen3tts_engine import Qwen3TTSEngine
from novel2audiobook.tts.base import TTSEngine
from novel2audiobook.tts.pyttsx3_engine import Pyttsx3Engine

TTSEngineFactory = type[TTSEngine]

_TTS_ENGINES: dict[str, TTSEngineFactory] = {}


def register_tts_engine(name: str, engine: TTSEngineFactory) -> None:
    _TTS_ENGINES[name] = engine


def create_tts_engine(name: str, **kwargs: object) -> TTSEngine:
    try:
        engine = _TTS_ENGINES[name]
    except KeyError as exc:
        raise ValueError(f"Unknown TTS engine: {name}") from exc
    return engine(**kwargs)


def available_tts_engines() -> list[str]:
    return sorted(_TTS_ENGINES)


register_tts_engine("pyttsx3", Pyttsx3Engine)
register_tts_engine("melotts", MeloTTSEngine)
register_tts_engine("qwen3tts", Qwen3TTSEngine)
