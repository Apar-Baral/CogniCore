"""AST-based import shield (features 7–12 simplified)."""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any


class ValidationPipeline:
    def __init__(self, root: Path, *, index_codebase: bool = False) -> None:
        self.root = root
        self._stats: dict[str, int] = {"validated": 0, "blocked": 0}
        if index_codebase:
            self._stats["files_scanned"] = min(500, sum(1 for _ in root.rglob("*.py")))

    def validate_code_change(
        self,
        file_path: str,
        original: str,
        proposed: str,
        *,
        mode: str = "syntax",
    ) -> dict[str, Any]:
        self._stats["validated"] += 1
        issues: list[str] = []
        shield_mode = (mode or "syntax").lower()
        if shield_mode == "off":
            return {"passed": True, "verdict": "PASS"}
        try:
            tree = ast.parse(proposed)
        except SyntaxError as e:
            return {
                "passed": False,
                "verdict": "BLOCK",
                "issues": [f"SyntaxError: {e}"],
            }
        if shield_mode == "syntax":
            return {"passed": True, "verdict": "PASS"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not _import_ok(alias.name.split(".")[0]):
                        issues.append(f"Suspicious import: {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if not _import_ok(node.module.split(".")[0]):
                    issues.append(f"Suspicious import from: {node.module}")
        if issues:
            self._stats["blocked"] += 1
            return {"passed": False, "verdict": "BLOCK", "issues": issues}
        return {"passed": True, "verdict": "PASS"}


def _import_ok(top: str) -> bool:
    if top in sys.builtin_module_names:
        return True
    std = getattr(sys, "stdlib_module_names", set())
    if top in std:
        return True
    try:
        __import__(top)
        return True
    except ImportError:
        return False
