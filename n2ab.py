from __future__ import annotations

from pathlib import Path

from novel2audiobook.models import Book, TTSOptions
from novel2audiobook.pipeline import load_book, synthesize_book
from novel2audiobook.tts.pyttsx3_engine import DEFAULT_CHINESE_VOICE_INDEX, pick_chinese_voice

DEFAULT_TEXT_DIR = Path("Novels/《 》")
DEFAULT_OUTPUT_DIR = Path("Output/《 》_audiobook")
DEFAULT_START = 1180
DEFAULT_STOP = 1200
DEFAULT_VOICE_INDEX = DEFAULT_CHINESE_VOICE_INDEX
DEFAULT_RATE = 230
DEFAULT_VOLUME = 1.0


def text_to_speech(
    file_name: str,
    text_dir: str | Path,
    out_dir: str | Path,
    voice: str | None,
    rate: int,
    volume: float,
    *,
    voice_index: int | None = DEFAULT_VOICE_INDEX,
) -> Path:
    book = load_book(Path(text_dir), input_format="txt", encoding="utf-8")
    chapter = next(
        (chapter for chapter in book.chapters if chapter.source_path and chapter.source_path.name == file_name),
        None,
    )
    if chapter is None:
        raise FileNotFoundError(f"未找到章节文件: {file_name}")
    subset = Book(title=book.title, chapters=[chapter], metadata=book.metadata)
    files = synthesize_book(
        subset,
        out_dir,
        engine_name="pyttsx3",
        options=TTSOptions(
            voice=voice,
            voice_index=voice_index,
            rate=rate,
            volume=volume,
            audio_format="aiff",
        ),
        keep_source_names=True,
        show_progress=False,
    )
    return files[0]


def batch_text_to_speech(
    text_dir: str | Path,
    out_dir: str | Path,
    *,
    start: int = DEFAULT_START,
    stop: int = DEFAULT_STOP,
    voice: str | None = None,
    voice_index: int | None = DEFAULT_VOICE_INDEX,
    rate: int = DEFAULT_RATE,
    volume: float = DEFAULT_VOLUME,
) -> list[Path]:
    book = load_book(Path(text_dir), input_format="txt", encoding="utf-8")
    subset = Book(
        title=book.title,
        chapters=book.chapters[start:stop],
        metadata=book.metadata,
    )
    if not subset.chapters:
        return []
    return synthesize_book(
        subset,
        out_dir,
        engine_name="pyttsx3",
        options=TTSOptions(
            voice=voice,
            voice_index=voice_index,
            rate=rate,
            volume=volume,
            audio_format="aiff",
        ),
        keep_source_names=True,
        show_progress=True,
    )


if __name__ == "__main__":
    files = batch_text_to_speech(DEFAULT_TEXT_DIR, DEFAULT_OUTPUT_DIR)
    print(f"生成了 {len(files)} 个音频文件到 {DEFAULT_OUTPUT_DIR}")
