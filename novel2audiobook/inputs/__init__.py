from __future__ import annotations

from pathlib import Path

from novel2audiobook.inputs.base import BookInput
from novel2audiobook.inputs.text import TextBookInput

InputProviderFactory = type[BookInput]

_INPUT_PROVIDERS: dict[str, InputProviderFactory] = {}


def register_input_provider(name: str, provider: InputProviderFactory) -> None:
    _INPUT_PROVIDERS[name] = provider


def create_input_provider(name: str, **kwargs: object) -> BookInput:
    try:
        provider = _INPUT_PROVIDERS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown input provider: {name}") from exc
    return provider(**kwargs)


def detect_input_provider(source: Path) -> str:
    source = Path(source)
    if source.is_dir():
        return "txt"
    suffix = source.suffix.lower().lstrip(".")
    if suffix in _INPUT_PROVIDERS:
        return suffix
    raise ValueError(f"Could not detect input provider for {source}")


def available_input_providers() -> list[str]:
    return sorted(_INPUT_PROVIDERS)


register_input_provider("txt", TextBookInput)
