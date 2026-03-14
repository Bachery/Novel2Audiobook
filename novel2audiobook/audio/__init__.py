from __future__ import annotations

from novel2audiobook.audio.base import AudioConverter
from novel2audiobook.audio.pydub_converter import PydubAudioConverter

AudioConverterFactory = type[AudioConverter]

_AUDIO_CONVERTERS: dict[str, AudioConverterFactory] = {}


def register_audio_converter(name: str, converter: AudioConverterFactory) -> None:
    _AUDIO_CONVERTERS[name] = converter


def create_audio_converter(name: str, **kwargs: object) -> AudioConverter:
    try:
        converter = _AUDIO_CONVERTERS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown audio converter: {name}") from exc
    return converter(**kwargs)


def available_audio_converters() -> list[str]:
    return sorted(_AUDIO_CONVERTERS)


register_audio_converter("pydub", PydubAudioConverter)
