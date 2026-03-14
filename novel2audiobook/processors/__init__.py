from __future__ import annotations

from novel2audiobook.processors.chapter_splitter import ChapterSplitter, ChineseNovelChapterSplitter

SplitterFactory = type[ChapterSplitter]

_SPLITTERS: dict[str, SplitterFactory] = {}


def register_splitter(name: str, splitter: SplitterFactory) -> None:
    _SPLITTERS[name] = splitter


def create_splitter(name: str, **kwargs: object) -> ChapterSplitter:
    try:
        splitter = _SPLITTERS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown splitter: {name}") from exc
    return splitter(**kwargs)


def available_splitters() -> list[str]:
    return sorted(_SPLITTERS)


register_splitter("chinese_novel", ChineseNovelChapterSplitter)
