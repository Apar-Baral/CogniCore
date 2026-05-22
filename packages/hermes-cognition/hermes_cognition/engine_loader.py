"""Resolve external Cognition Engine vs CogniCore bundled engine."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def resolve_facade(root: Path, cfg: dict[str, Any]) -> Any:
    """
    Load order (``COGNITION_ENGINE_MODE``):

    * ``bundled`` — only built-in engine (no external repo)
    * ``external`` — only external CE; fail if missing
    * ``auto`` (default) — external if available, else bundled
    """
    mode = (os.environ.get("COGNITION_ENGINE_MODE") or cfg.get("engine_mode") or "auto").lower()

    if mode == "bundled":
        return _bundled(root)

    external = _try_external(root)
    if mode == "external":
        if external is None:
            raise ImportError(
                "COGNITION_ENGINE_MODE=external but cognition-engine not found. "
                "Set COGNITION_ENGINE_PATH or pip install cognition-engine."
            )
        return external

    if external is not None:
        logger.info("Using external Cognition Engine")
        return external

    logger.info("Using CogniCore bundled cognition engine (external CE optional)")
    return _bundled(root)


def _bundled(root: Path) -> Any:
    from hermes_cognition.bundled.facade import BundledFacade

    return BundledFacade(root)


def _try_external(root: Path) -> Any | None:
    _prepend_ce_paths()
    try:
        from src.facade import CognitionFacade

        return CognitionFacade(root)
    except ImportError as exc:
        logger.debug("external CE (src.facade): %s", exc)
    try:
        from cognition_engine.facade import CognitionFacade  # type: ignore

        return CognitionFacade(root)
    except ImportError as exc:
        logger.debug("external CE (cognition_engine.facade): %s", exc)
    return None


def _prepend_ce_paths() -> None:
    raw = os.environ.get("COGNITION_ENGINE_PATH", "").strip()
    if not raw:
        return
    base = Path(raw)
    candidates: list[Path] = []
    if base.name == "cognition-engine":
        candidates.append(base)
        candidates.append(base / "src")
    else:
        candidates.append(base)
        candidates.append(base / "src")
    for p in candidates:
        s = str(p.resolve())
        if p.is_dir() and s not in sys.path:
            sys.path.insert(0, s)
