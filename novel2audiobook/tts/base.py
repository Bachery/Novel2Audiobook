from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from novel2audiobook.models import TTSOptions, VoiceInfo


class TTSEngine(ABC):
    @abstractmethod
    def synthesize_text(self, text: str, output_path: Path, options: TTSOptions) -> Path:
        raise NotImplementedError

    def list_voices(self) -> list[VoiceInfo]:
        return []

    def default_audio_format(self) -> str:
        return "wav"
