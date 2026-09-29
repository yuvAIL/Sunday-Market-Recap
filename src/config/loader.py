from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AppConfig:
    provider: str
    api_key_env: str
    api_key: str | None
    output_dir: Path
    default_start: str
    groups: dict[str, Any]


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    required = ["provider", "api_key_env", "output_dir", "default_start", "groups"]
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"Missing required config fields: {', '.join(missing)}")

    api_key_env = str(raw["api_key_env"])
    return AppConfig(
        provider=str(raw["provider"]).lower(),
        api_key_env=api_key_env,
        api_key=os.getenv(api_key_env),
        output_dir=Path(raw["output_dir"]),
        default_start=str(raw["default_start"]),
        groups=dict(raw["groups"]),
    )
