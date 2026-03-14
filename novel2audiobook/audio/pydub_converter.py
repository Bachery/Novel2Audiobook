from __future__ import annotations

from pathlib import Path

from novel2audiobook.audio.base import AudioConverter
from novel2audiobook.models import AudioConvertOptions
from novel2audiobook.utils import ensure_directory


class PydubAudioConverter(AudioConverter):
    def convert_file(self, source_path: Path, target_path: Path, options: AudioConvertOptions) -> Path:
        try:
            from pydub import AudioSegment
        except ImportError as exc:
            raise RuntimeError("缺少 pydub，请先安装后再进行音频转码") from exc

        ensure_directory(target_path.parent)
        source_format = options.source_format or source_path.suffix.lstrip(".")
        audio = AudioSegment.from_file(source_path, format=source_format)
        export_kwargs: dict[str, str] = {}
        if options.bitrate:
            export_kwargs["bitrate"] = options.bitrate
        audio.export(target_path, format=options.target_format, **export_kwargs)
        return target_path
