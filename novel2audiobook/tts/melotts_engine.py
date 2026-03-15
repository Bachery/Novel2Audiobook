from __future__ import annotations

from pathlib import Path

from novel2audiobook.models import TTSOptions, VoiceInfo
from novel2audiobook.tts.base import TTSEngine
from novel2audiobook.utils import ensure_directory

DEFAULT_MELOTTS_LANGUAGE = "ZH"
DEFAULT_MELOTTS_DEVICE = "auto"
DEFAULT_MELOTTS_SPEED = 1.0
SUPPORTED_MELOTTS_SPEAKERS: dict[str, tuple[str, ...]] = {
    "EN": ("EN-Default", "EN-US", "EN-BR", "EN_INDIA", "EN-AU"),
    "ES": ("ES",),
    "FR": ("FR",),
    "ZH": ("ZH",),
    "JP": ("JP",),
    "KR": ("KR",),
}
LANGUAGE_ALIASES = {
    "EN": "EN",
    "EN-US": "EN",
    "EN-UK": "EN",
    "ES": "ES",
    "FR": "FR",
    "ZH": "ZH",
    "ZH-CN": "ZH",
    "ZH_CN": "ZH",
    "CN": "ZH",
    "JA": "JP",
    "JP": "JP",
    "KO": "KR",
    "KR": "KR",
}


def normalize_language(language: str | None) -> str:
    if not language:
        return DEFAULT_MELOTTS_LANGUAGE
    normalized = language.strip().replace("_", "-").upper()
    try:
        return LANGUAGE_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported MeloTTS language: {language}. "
            f"Available: {', '.join(sorted(SUPPORTED_MELOTTS_SPEAKERS))}"
        ) from exc


def default_speaker_for_language(language: str) -> str:
    speakers = SUPPORTED_MELOTTS_SPEAKERS[language]
    return speakers[0]


class MeloTTSEngine(TTSEngine):
    def __init__(self, default_device: str = DEFAULT_MELOTTS_DEVICE) -> None:
        self.default_device = default_device
        self._model_cache: dict[tuple[str, str], object] = {}

    def default_audio_format(self) -> str:
        return "wav"

    def _load_model(self, language: str, device: str) -> object:
        cache_key = (language, device)
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]

        try:
            from melo.api import TTS as MeloTTS
        except ImportError as exc:
            raise RuntimeError(
                "缺少 MeloTTS。请参考 README 中的 MeloTTS 安装说明完成安装。"
            ) from exc

        model = MeloTTS(language=language, device=device)
        self._model_cache[cache_key] = model
        return model

    @staticmethod
    def _resolve_speaker(model: object, language: str, options: TTSOptions) -> int:
        speaker_name = options.speaker or options.voice or default_speaker_for_language(language)
        speaker_ids = getattr(getattr(getattr(model, "hps", None), "data", None), "spk2id", None)
        if not isinstance(speaker_ids, dict) or not speaker_ids:
            raise RuntimeError("MeloTTS 模型未提供 speaker 映射")

        if speaker_name in speaker_ids:
            return int(speaker_ids[speaker_name])

        try:
            speaker_id = int(speaker_name)
        except (TypeError, ValueError):
            available = ", ".join(sorted(map(str, speaker_ids)))
            raise ValueError(f"Unknown MeloTTS speaker: {speaker_name}. Available: {available}") from None

        if speaker_id not in set(speaker_ids.values()):
            available = ", ".join(sorted(map(str, speaker_ids)))
            raise ValueError(f"Unknown MeloTTS speaker: {speaker_name}. Available: {available}")
        return speaker_id

    def synthesize_text(self, text: str, output_path: Path, options: TTSOptions) -> Path:
        language = normalize_language(options.language)
        device = options.device or self.default_device
        speed = options.speed if options.speed is not None else DEFAULT_MELOTTS_SPEED
        ensure_directory(output_path.parent)

        model = self._load_model(language, device)
        speaker_id = self._resolve_speaker(model, language, options)
        model.tts_to_file(text, speaker_id, str(output_path), speed=speed)
        return output_path

    def list_voices(self) -> list[VoiceInfo]:
        voices: list[VoiceInfo] = []
        for language, speakers in SUPPORTED_MELOTTS_SPEAKERS.items():
            default_speaker = default_speaker_for_language(language)
            for speaker in speakers:
                voices.append(
                    VoiceInfo(
                        id=speaker,
                        name=f"MeloTTS {speaker}",
                        languages=(language,),
                        is_default=speaker == default_speaker,
                    )
                )
        return voices
