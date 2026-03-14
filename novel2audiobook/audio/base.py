from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from novel2audiobook.models import AudioConvertOptions


class AudioConverter(ABC):
    @abstractmethod
    def convert_file(self, source_path: Path, target_path: Path, options: AudioConvertOptions) -> Path:
        raise NotImplementedError
