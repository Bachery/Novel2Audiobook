from __future__ import annotations

import re
from pathlib import Path

from novel2audiobook.cli import main
from novel2audiobook.models import Book, Chapter, TTSOptions
from novel2audiobook.pipeline import synthesize_book


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"([。！？!?])", text)
    sentences: list[str] = []
    for index in range(0, len(parts), 2):
        sentence = parts[index].strip()
        if not sentence:
            continue
        punctuation = parts[index + 1] if index + 1 < len(parts) else ""
        sentences.append((sentence + punctuation).strip())
    return sentences


def tts_batch(
    text: str,
    out_dir: str = "tts_out",
    voice: str | None = None,
    voice_index: int | None = 8,
    rate: int = 180,
    volume: float = 1.0,
    audio_format: str = "aiff",
) -> list[str]:
    sentences = split_sentences(text) or [text]
    book = Book(
        title=Path(out_dir).name,
        chapters=[
            Chapter(
                index=index,
                title=f"part_{index:04d}",
                content=sentence,
                source_path=Path(f"part_{index:04d}.txt"),
            )
            for index, sentence in enumerate(sentences, start=1)
        ],
    )
    files = synthesize_book(
        book,
        out_dir,
        options=TTSOptions(
            voice=voice,
            voice_index=voice_index,
            rate=rate,
            volume=volume,
            audio_format=audio_format,
        ),
        keep_source_names=True,
        show_progress=False,
    )
    return [str(path) for path in files]


if __name__ == "__main__":
    raise SystemExit(main())
