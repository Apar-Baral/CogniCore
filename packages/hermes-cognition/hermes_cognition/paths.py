"""Resolve Cognition data directories (.cognition primary, .hermes/cognition fallback)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

DataDirMode = Literal["auto", "cognition", "hermes"]


def hermes_cognition_dir(project_root: Path) -> Path:
    return project_root / ".hermes" / "cognition"


def primary_cognition_dir(project_root: Path) -> Path:
    return project_root / ".cognition"


def resolve_cognition_dir(
    project_root: Path | str,
    mode: DataDirMode = "auto",
) -> Path:
    root = Path(project_root).resolve()
    primary = primary_cognition_dir(root)
    legacy = hermes_cognition_dir(root)

    if mode == "cognition":
        return primary
    if mode == "hermes":
        return legacy

    if (primary / "dna.json").is_file():
        return primary
    if (legacy / "dna.json").is_file():
        return legacy
    return primary


def resolve_project_root(start: Path | str | None = None) -> Path:
    """Walk parents for DNA; honor COGNITION_PROJECT and HERMES_COGNITION_PROJECT."""
    for key in ("COGNITION_PROJECT", "HERMES_COGNITION_PROJECT"):
        env = os.environ.get(key, "").strip()
        if env:
            candidate = Path(env).expanduser().resolve()
            if _has_dna(candidate):
                return candidate

    current = (Path(start) if start else Path.cwd()).resolve()
    for path in [current, *current.parents]:
        if _has_dna(path):
            return path
    return current


def _has_dna(path: Path) -> bool:
    return (
        (path / ".cognition" / "dna.json").is_file()
        or (path / ".hermes" / "cognition" / "dna.json").is_file()
        or (path / "cognition-dna.json").is_file()
    )
