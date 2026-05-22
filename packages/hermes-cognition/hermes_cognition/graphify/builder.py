"""Build a dependency graph of project files for Graphify."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

_SKIP_DIRS = {
    ".git",
    ".cognition",
    ".hermes",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".pytest_cache",
    "dist",
    "build",
    ".ruff_cache",
}

_CODE_EXTS = {".py", ".pyi", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"}


def _norm(path: str) -> str:
    return path.replace("\\", "/")


def _iter_source_files(root: Path, max_files: int = 400) -> list[Path]:
    found: list[Path] = []
    for path in root.rglob("*"):
        if len(found) >= max_files:
            break
        if not path.is_file():
            continue
        if path.suffix.lower() not in _CODE_EXTS:
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        found.append(path)
    return found


def _parse_python_imports(path: Path, root: Path) -> tuple[list[str], list[str]]:
    """Return (local_relative_imports, external_modules)."""
    local: list[str] = []
    external: list[str] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return local, external
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                external.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module
                if node.level and node.level > 0:
                    base = path.parent
                    for _ in range(node.level - 1):
                        base = base.parent
                    candidate = base / (mod.replace(".", "/") + ".py")
                    if candidate.is_file():
                        local.append(_norm(str(candidate.relative_to(root))))
                    else:
                        pkg_init = base / mod.replace(".", "/") / "__init__.py"
                        if pkg_init.is_file():
                            local.append(_norm(str(pkg_init.relative_to(root))))
                else:
                    external.append(mod.split(".")[0])
    return local, external


def _parse_js_imports(text: str) -> list[str]:
    pattern = re.compile(
        r"""(?:import\s+.*?from\s+['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\s*\))""",
        re.MULTILINE,
    )
    out: list[str] = []
    for m in pattern.finditer(text):
        out.append(m.group(1) or m.group(2) or "")
    return [x for x in out if x and not x.startswith(".")]


def _estimate_file_tokens(path: Path) -> int:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").count("\n") + 1
    except Exception:
        return 500
    return max(200, min(lines * 15, 12000))


def build_project_graph(root: Path, *, max_files: int = 400) -> dict[str, Any]:
    """Build nodes/edges graph with import relationships and token estimates."""
    root = root.resolve()
    files = _iter_source_files(root, max_files=max_files)
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    for fpath in files:
        rel = _norm(str(fpath.relative_to(root)))
        nid = f"file:{rel}"
        symbols: list[str] = []
        imports_local: list[str] = []
        imports_ext: list[str] = []

        if fpath.suffix == ".py":
            imports_local, imports_ext = _parse_python_imports(fpath, root)
            try:
                tree = ast.parse(fpath.read_text(encoding="utf-8", errors="replace"))
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        symbols.append(f"def {node.name}")
                    elif isinstance(node, ast.ClassDef):
                        symbols.append(f"class {node.name}")
            except Exception:
                pass
        elif fpath.suffix in {".js", ".ts", ".tsx", ".jsx"}:
            try:
                imports_ext = _parse_js_imports(fpath.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                pass

        nodes[nid] = {
            "id": nid,
            "type": "file",
            "name": rel,
            "path": rel,
            "files": [rel],
            "symbols": symbols[:30],
            "estimated_tokens": _estimate_file_tokens(fpath),
            "language": fpath.suffix.lstrip("."),
            "imports_local": imports_local,
            "imports_external": imports_ext[:20],
            "access_count": 0,
            "last_access": None,
        }

    file_by_rel = {n["path"]: nid for nid, n in nodes.items()}

    for nid, node in nodes.items():
        for imp in node.get("imports_local", []):
            target = file_by_rel.get(imp)
            if target:
                edges.append({"from": nid, "to": target, "type": "imports"})
        parent = str(Path(node["path"]).parent)
        if parent and parent != ".":
            parent_rel = _norm(parent)
            for other_nid, other in nodes.items():
                if other["path"] == parent_rel or other["path"].startswith(parent_rel + "/"):
                    if other_nid != nid:
                        edges.append({"from": nid, "to": other_nid, "type": "same_package"})

    return {
        "version": 1,
        "root": str(root),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": list(nodes.values()),
        "edges": edges,
    }
