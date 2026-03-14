from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Iterator, TypeVar

T = TypeVar("T")


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def natural_sort_key(value: str | Path) -> list[int | str]:
    text = value.name if isinstance(value, Path) else str(value)
    parts = re.split(r"(\d+)", text)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def iter_text_files(directory: Path) -> Iterator[Path]:
    for path in sorted(directory.iterdir(), key=natural_sort_key):
        if path.is_file() and path.suffix.lower() == ".txt":
            yield path


def progress(iterable: Iterable[T], enabled: bool = True) -> Iterable[T]:
    if not enabled:
        return iterable
    try:
        from tqdm import tqdm
    except ImportError:
        return iterable
    return tqdm(iterable)
