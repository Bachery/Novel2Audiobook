from __future__ import annotations

from pathlib import Path

from novel2audiobook.audio import create_audio_converter
from novel2audiobook.inputs import create_input_provider, detect_input_provider
from novel2audiobook.models import AudioConvertOptions, Book, Chapter, TTSOptions
from novel2audiobook.processors import create_splitter
from novel2audiobook.processors.chapter_splitter import export_chapters
from novel2audiobook.processors.cleanup import normalize_text
from novel2audiobook.tts import create_tts_engine
from novel2audiobook.utils import ensure_directory, natural_sort_key, progress


def load_book(source: str | Path, input_format: str = "auto", encoding: str = "utf-8") -> Book:
    source_path = Path(source)
    provider_name = detect_input_provider(source_path) if input_format == "auto" else input_format
    provider = create_input_provider(provider_name, encoding=encoding)
    return provider.load(source_path)


def prepare_book(
    source: str | Path,
    input_format: str = "auto",
    encoding: str = "utf-8",
    normalize: bool = True,
    splitter_name: str = "chinese_novel",
    include_volumes: bool = False,
) -> Book:
    book = load_book(source, input_format=input_format, encoding=encoding)
    if book.chapters:
        if normalize:
            for chapter in book.chapters:
                chapter.content = normalize_text(chapter.content)
        return book

    text = book.raw_text or ""
    if normalize:
        text = normalize_text(text)
    splitter = create_splitter(splitter_name, include_volumes=include_volumes)
    book.raw_text = text
    book.chapters = splitter.split(text, book.title)
    return book


def write_chapters(book: Book, output_dir: str | Path, encoding: str = "utf-8", start_index: int = 1) -> list[Path]:
    return export_chapters(book.chapters, output_dir, encoding=encoding, start_index=start_index)


def synthesize_book(
    book: Book,
    output_dir: str | Path,
    engine_name: str = "pyttsx3",
    options: TTSOptions | None = None,
    keep_source_names: bool = True,
    show_progress: bool = True,
) -> list[Path]:
    output_path = ensure_directory(Path(output_dir))
    engine = create_tts_engine(engine_name)
    synth_options = options or TTSOptions()

    chapters = book.chapters or [
        Chapter(index=1, title=book.title, content=book.raw_text or "", source_path=None)
    ]
    written_files: list[Path] = []

    for chapter in progress(chapters, enabled=show_progress):
        stem = (
            chapter.source_path.stem
            if keep_source_names and chapter.source_path is not None
            else str(chapter.index)
        )
        target_path = output_path / f"{stem}.{synth_options.audio_format}"
        engine.synthesize_text(chapter.content, target_path, synth_options)
        written_files.append(target_path)
    return written_files


def convert_audio_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    converter_name: str = "pydub",
    source_ext: str = ".aiff",
    options: AudioConvertOptions | None = None,
    show_progress: bool = True,
) -> list[Path]:
    input_path = Path(input_dir)
    output_path = ensure_directory(Path(output_dir))
    converter = create_audio_converter(converter_name)
    convert_options = options or AudioConvertOptions(target_format="mp3")
    source_ext = source_ext if source_ext.startswith(".") else f".{source_ext}"

    written_files: list[Path] = []
    audio_files = sorted(
        [path for path in input_path.iterdir() if path.is_file() and path.suffix.lower() == source_ext.lower()],
        key=natural_sort_key,
    )
    for source_file in progress(audio_files, enabled=show_progress):
        target_file = output_path / f"{source_file.stem}.{convert_options.target_format}"
        converter.convert_file(source_file, target_file, convert_options)
        written_files.append(target_file)
    return written_files


def run_pipeline(
    source: str | Path,
    chapters_dir: str | Path | None = None,
    audio_dir: str | Path | None = None,
    converted_dir: str | Path | None = None,
    input_format: str = "auto",
    encoding: str = "utf-8",
    splitter_name: str = "chinese_novel",
    include_volumes: bool = False,
    normalize: bool = True,
    tts_engine: str = "pyttsx3",
    tts_options: TTSOptions | None = None,
    audio_converter: str = "pydub",
    convert_options: AudioConvertOptions | None = None,
) -> dict[str, list[Path]]:
    book = prepare_book(
        source=source,
        input_format=input_format,
        encoding=encoding,
        normalize=normalize,
        splitter_name=splitter_name,
        include_volumes=include_volumes,
    )
    results: dict[str, list[Path]] = {}

    if chapters_dir is not None:
        results["chapters"] = write_chapters(book, chapters_dir, encoding=encoding)
    if audio_dir is not None:
        results["audio"] = synthesize_book(book, audio_dir, engine_name=tts_engine, options=tts_options)
    if converted_dir is not None:
        actual_audio_dir = Path(audio_dir) if audio_dir is not None else None
        if actual_audio_dir is None:
            raise ValueError("converted_dir requires audio_dir")
        results["converted"] = convert_audio_directory(
            actual_audio_dir,
            converted_dir,
            converter_name=audio_converter,
            source_ext=f".{(tts_options or TTSOptions()).audio_format}",
            options=convert_options,
        )
    return results
