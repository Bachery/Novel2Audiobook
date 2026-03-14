from __future__ import annotations

from pathlib import Path

from novel2audiobook.models import TTSOptions, VoiceInfo
from novel2audiobook.tts.base import TTSEngine
from novel2audiobook.utils import ensure_directory

CHINESE_VOICE_KEYS = (
    "zh",
    "zh-cn",
    "zh_cn",
    "zh-hk",
    "zh_tw",
    "chinese",
    "mandarin",
    "ting-ting",
    "mei-jia",
    "sin-ji",
)
DEFAULT_CHINESE_VOICE_INDEX = 8


def _normalize_languages(languages: object) -> tuple[str, ...]:
    raw_languages = languages or ()
    normalized: list[str] = []
    for item in raw_languages:
        if isinstance(item, (bytes, bytearray)):
            normalized.append(item.decode("utf-8", "ignore"))
        else:
            normalized.append(str(item))
    return tuple(normalized)


def list_chinese_voices(engine: object) -> list[object]:
    voices = engine.getProperty("voices")
    candidates: list[object] = []
    for voice in voices:
        languages = _normalize_languages(getattr(voice, "languages", ()))
        haystack = " ".join(
            [*languages, getattr(voice, "name", "") or "", getattr(voice, "id", "") or ""]
        ).lower()
        if any(key in haystack for key in CHINESE_VOICE_KEYS):
            candidates.append(voice)
    return candidates


def pick_chinese_voice(engine: object, preferred_index: int = DEFAULT_CHINESE_VOICE_INDEX) -> object:
    candidates = list_chinese_voices(engine)
    if not candidates:
        raise RuntimeError("未找到中文语音，请先在系统中安装可用中文语音")
    if preferred_index < 0 or preferred_index >= len(candidates):
        raise IndexError(
            f"中文语音索引 {preferred_index} 超出范围，可用数量为 {len(candidates)}"
        )
    return candidates[preferred_index]


class Pyttsx3Engine(TTSEngine):
    def __init__(self, auto_pick_chinese_voice: bool = True) -> None:
        self.auto_pick_chinese_voice = auto_pick_chinese_voice

    def synthesize_text(self, text: str, output_path: Path, options: TTSOptions) -> Path:
        try:
            import pyttsx3
        except ImportError as exc:
            raise RuntimeError("缺少 pyttsx3，请先安装后再使用 pyttsx3 引擎") from exc

        ensure_directory(output_path.parent)
        engine = pyttsx3.init()
        try:
            if options.voice:
                engine.setProperty("voice", options.voice)
            elif self.auto_pick_chinese_voice:
                voice_index = (
                    options.voice_index
                    if options.voice_index is not None
                    else DEFAULT_CHINESE_VOICE_INDEX
                )
                voice = pick_chinese_voice(engine, preferred_index=voice_index)
                engine.setProperty("voice", getattr(voice, "id"))
            engine.setProperty("rate", options.rate)
            engine.setProperty("volume", options.volume)
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
        finally:
            engine.stop()
        return output_path

    def list_voices(self) -> list[VoiceInfo]:
        try:
            import pyttsx3
        except ImportError as exc:
            raise RuntimeError("缺少 pyttsx3，请先安装后再列出语音") from exc

        engine = pyttsx3.init()
        try:
            chinese_candidates = {
                getattr(voice, "id", ""): index
                for index, voice in enumerate(list_chinese_voices(engine))
            }
            voices = []
            for voice in engine.getProperty("voices"):
                voice_id = getattr(voice, "id", "")
                candidate_index = chinese_candidates.get(voice_id)
                voices.append(
                    VoiceInfo(
                        id=voice_id,
                        name=getattr(voice, "name", ""),
                        languages=_normalize_languages(getattr(voice, "languages", ())),
                        candidate_index=candidate_index,
                        is_default=candidate_index == DEFAULT_CHINESE_VOICE_INDEX,
                    )
                )
            return voices
        finally:
            engine.stop()
