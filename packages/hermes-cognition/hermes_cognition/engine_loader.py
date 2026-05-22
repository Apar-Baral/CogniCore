"""Load CogniCore built-in cognition engine (standalone — no external CognitionEngine repo)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def resolve_facade(root: Path, cfg: dict[str, Any]) -> Any:
    from hermes_cognition.bundled.facade import BundledFacade

    logger.debug("CogniCore built-in cognition engine")
    return BundledFacade(root)
