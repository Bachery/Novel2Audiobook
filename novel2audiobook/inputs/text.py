from __future__ import annotations

from pathlib import Path

from novel2audiobook.inputs.base import BookInput
from novel2audiobook.models import Book, Chapter
from novel2audiobook.processors.chapter_splitter import is_chapter_heading
from novel2audiobook.utils import iter_text_files


class TextBookInput(BookInput):
    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    def load(self, source: Path) -> Book:
        source = Path(source)
        if source.is_dir():
            return self._load_directory(source)
        if source.is_file() and source.suffix.lower() == ".txt":
            return self._load_text_file(source)
        raise ValueError(f"Unsupported text source: {source}")

    def _load_directory(self, source: Path) -> Book:
        chapters: list[Chapter] = []
        for index, path in enumerate(iter_text_files(source), start=1):
            content = path.read_text(encoding=self.encoding)
            title = self._guess_title(content, fallback=path.stem)
            chapters.append(
                Chapter(
                    index=index,
                    title=title,
                    content=content,
                    source_path=path,
                )
            )
        return Book(title=source.name, chapters=chapters, metadata={"source": source})

    def _load_text_file(self, source: Path) -> Book:
        text = source.read_text(encoding=self.encoding)
        return Book(title=source.stem, raw_text=text, metadata={"source": source})

    @staticmethod
    def _guess_title(content: str, fallback: str) -> str:
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if is_chapter_heading(line):
                return line
            return fallback
        return fallback
