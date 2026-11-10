"""Configuration loading for folder2kb (``folder2kb.yaml``)."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILENAME = "folder2kb.yaml"


class ConfigError(ValueError):
    """Raised when the configuration file is invalid."""


@dataclass
class Config:
    """Runtime configuration.

    Attributes:
        kb_dir: Directory (relative to the config file) holding the knowledge base.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Characters shared between neighbouring chunks.
        top_k: Default number of results returned by ``ask``.
        root: Directory the config was loaded from (not persisted).
    """

    kb_dir: str = ".kb"
    chunk_size: int = 500
    chunk_overlap: int = 80
    top_k: int = 5
    root: Path = Path(".")

    @property
    def kb_path(self) -> Path:
        """Absolute path to the knowledge base directory."""
        p = Path(self.kb_dir).expanduser()
        return p if p.is_absolute() else (self.root / p).resolve()

    def to_dict(self) -> dict[str, Any]:
        """Return the persistable fields as a dict."""
        d = asdict(self)
        d.pop("root", None)
        return d

    def validate(self) -> None:
        """Raise :class:`ConfigError` if values are inconsistent."""
        if self.chunk_size <= 0:
            raise ConfigError("chunk_size must be > 0")
        if self.chunk_overlap < 0:
            raise ConfigError("chunk_overlap must be >= 0")
        if self.chunk_overlap >= self.chunk_size:
            raise ConfigError("chunk_overlap must be smaller than chunk_size")
        if self.top_k <= 0:
            raise ConfigError("top_k must be > 0")


def find_config(start: Path | None = None) -> Path | None:
    """Search ``start`` and its parents for ``folder2kb.yaml``."""
    cur = (start or Path.cwd()).resolve()
    for d in (cur, *cur.parents):
        candidate = d / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    return None


def load_config(start: Path | None = None) -> Config:
    """Load config from the nearest ``folder2kb.yaml``; fall back to defaults in ``start``."""
    path = find_config(start)
    if path is None:
        cfg = Config(root=(start or Path.cwd()).resolve())
        cfg.validate()
        return cfg
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a mapping")
    known = {"kb_dir", "chunk_size", "chunk_overlap", "top_k"}
    kwargs: dict[str, Any] = {}
    for key, value in data.items():
        if key not in known:
            continue
        kwargs[key] = str(value) if key == "kb_dir" else int(value)
    cfg = Config(root=path.parent, **kwargs)
    cfg.validate()
    return cfg


def write_config(directory: Path, cfg: Config | None = None) -> Path:
    """Write ``folder2kb.yaml`` into ``directory`` and return its path."""
    cfg = cfg or Config()
    path = directory / CONFIG_FILENAME
    header = "# folder2kb configuration. See folder2kb.yaml.example for details.\n"
    path.write_text(header + yaml.safe_dump(cfg.to_dict(), sort_keys=False), encoding="utf-8")
    return path
