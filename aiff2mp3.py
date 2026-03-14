from __future__ import annotations

from pathlib import Path

from novel2audiobook.models import AudioConvertOptions
from novel2audiobook.pipeline import convert_audio_directory

DEFAULT_AIFF_DIR = Path("Output/《 》_audiobook")
DEFAULT_MP3_DIR = Path("Output/《 》_audiobook_mp3")


def convert_directory(aiff_dir: str | Path, mp3_dir: str | Path) -> list[Path]:
    return convert_audio_directory(
        aiff_dir,
        mp3_dir,
        converter_name="pydub",
        source_ext=".aiff",
        options=AudioConvertOptions(source_format="aiff", target_format="mp3"),
    )


if __name__ == "__main__":
    files = convert_directory(DEFAULT_AIFF_DIR, DEFAULT_MP3_DIR)
    print(f"转换完成，共生成 {len(files)} 个 mp3 文件")
