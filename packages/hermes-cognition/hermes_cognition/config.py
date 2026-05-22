"""Load Hermes cognition plugin settings from config.yaml."""

from __future__ import annotations

from typing import Any


def load_cognition_config() -> dict[str, Any]:
    try:
        from hermes_cli.config import load_config

        cfg = load_config() or {}
    except Exception:
        cfg = {}
    return cfg.get("cognition") or {}


def plugin_enabled() -> bool:
    cog = load_cognition_config()
    if cog.get("enabled") is False:
        return False
    try:
        from hermes_cli.config import load_config

        cfg = load_config() or {}
        plugins = cfg.get("plugins") or {}
        enabled = plugins.get("enabled")
        if isinstance(enabled, list) and "cognition" not in enabled:
            return False
    except Exception:
        pass
    return True


def get_nested(cfg: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = cfg
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default
