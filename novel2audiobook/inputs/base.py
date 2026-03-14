from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from novel2audiobook.models import Book


class BookInput(ABC):
    @abstractmethod
    def load(self, source: Path) -> Book:
        raise NotImplementedError
