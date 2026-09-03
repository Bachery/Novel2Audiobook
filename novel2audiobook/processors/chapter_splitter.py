from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path

from novel2audiobook.models import Book, Chapter
from novel2audiobook.utils import ensure_directory

CHAPTER_RE = re.compile(r"^第[零一二三四五六七八九十百千万两0-9]+章(?:$|\s|[^章])")
VOLUME_RE = re.compile(r"^第.+?卷")
EXTRA_RE = re.compile(r"^番外(?:[零一二三四五六七八九十百千0-9].*|[\s:：\(\)（）【】].*|$)")
AFTERWORD_RE = re.compile(r"^完本感言(?:[\s:：\(\)（）【】].*|$)")


def is_chapter_heading(line: str) -> bool:
    return bool(CHAPTER_RE.match(line)) or bool(EXTRA_RE.match(line)) or bool(AFTERWORD_RE.match(line))


class ChapterSplitter(ABC):
    @abstractmethod
    def split(self, text: str, title: str) -> list[Chapter]:
        raise NotImplementedError


class ChineseNovelChapterSplitter(ChapterSplitter):
    def __init__(self, include_volumes: bool = False) -> None:
        self.include_volumes = include_volumes

    def split(self, text: str, title: str) -> list[Chapter]:
        chapters: list[Chapter] = []
        current_lines: list[str] = []
        pending_volume_lines: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                if current_lines:
                    current_lines.append("")
                continue

            if self.include_volumes and VOLUME_RE.match(line):
                if current_lines:
                    chapters.append(self._build_chapter(len(chapters) + 1, current_lines, title))
                    current_lines = []
                pending_volume_lines = [line]
                continue

            if is_chapter_heading(line):
                if current_lines:
                    chapters.append(self._build_chapter(len(chapters) + 1, current_lines, title))
                current_lines = [*pending_volume_lines, line]
                pending_volume_lines = []
                continue

            if not current_lines and pending_volume_lines:
                current_lines = pending_volume_lines.copy()
                pending_volume_lines = []
            current_lines.append(line)

        if current_lines:
            chapters.append(self._build_chapter(len(chapters) + 1, current_lines, title))
        elif pending_volume_lines:
            chapters.append(self._build_chapter(len(chapters) + 1, pending_volume_lines, title))
        return chapters

    @staticmethod
    def _build_chapter(index: int, lines: list[str], title: str) -> Chapter:
        chapter_title = title
        for line in lines:
            if is_chapter_heading(line):
                chapter_title = line
                break
            if VOLUME_RE.match(line):
                chapter_title = line
        content = "\n".join(lines).rstrip() + "\n"
        return Chapter(index=index, title=chapter_title, content=content)


def export_chapters(
    chapters: list[Chapter],
    output_dir: str | Path,
    encoding: str = "utf-8",
    start_index: int = 1,
) -> list[Path]:
    output_path = ensure_directory(Path(output_dir))
    written_files: list[Path] = []
    for offset, chapter in enumerate(chapters):
        path = output_path / f"{start_index + offset}.txt"
        path.write_text(chapter.content, encoding=encoding)
        written_files.append(path)
    return written_files


def split_book_to_directory(
    book: Book,
    output_dir: str | Path,
    splitter: ChapterSplitter,
    encoding: str = "utf-8",
    start_index: int = 1,
) -> list[Path]:
    if book.chapters:
        chapters = book.chapters
    else:
        chapters = splitter.split(book.raw_text or "", book.title)
    return export_chapters(chapters, output_dir, encoding=encoding, start_index=start_index)
