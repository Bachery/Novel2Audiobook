from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Chapter:
    index: int
    title: str
    content: str
    source_path: Path | None = None


@dataclass(slots=True)
class Book:
    title: str
    chapters: list[Chapter] = field(default_factory=list)
    raw_text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_chapters(self) -> bool:
        return bool(self.chapters)


@dataclass(slots=True)
class TTSOptions:
    voice: str | None = None
    voice_index: int | None = None
    rate: int = 230
    volume: float = 1.0
    audio_format: str = "aiff"


@dataclass(slots=True)
class VoiceInfo:
    id: str
    name: str
    languages: tuple[str, ...] = ()
    candidate_index: int | None = None
    is_default: bool = False


@dataclass(slots=True)
class AudioConvertOptions:
    source_format: str | None = None
    target_format: str = "mp3"
    bitrate: str | None = None
