from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config_mapping(config_path: str | Path) -> tuple[dict[str, Any], Path]:
    path = Path(config_path).expanduser().resolve()
    suffix = path.suffix.lower()

    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    elif suffix == ".toml":
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    elif suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("读取 YAML 配置需要先安装 PyYAML") from exc
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Unsupported config format: {suffix}")

    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a mapping at root: {path}")
    return data, path


def extract_tts_config(data: dict[str, Any]) -> dict[str, Any]:
    if "tts" in data:
        value = data["tts"]
        if not isinstance(value, dict):
            raise ValueError("Config key 'tts' must be a mapping")
        return dict(value)
    return dict(data)


def resolve_config_paths(config: dict[str, Any], config_path: Path) -> dict[str, Any]:
    resolved = dict(config)
    for key in ("ref_audio",):
        value = resolved.get(key)
        if not isinstance(value, str) or not value.strip():
            continue
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = (config_path.parent / candidate).resolve()
        resolved[key] = str(candidate)
    return resolved
