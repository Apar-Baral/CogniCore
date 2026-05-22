"""Cross-project learning (features 42-45)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def global_registry_dir() -> Path:
    return Path.home() / ".cognition" / "projects"


def register_completed_project(
    project_root: Path,
    *,
    language: str = "",
    framework: str = "",
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Add project to global registry (feature 42)."""
    reg_dir = global_registry_dir()
    reg_dir.mkdir(parents=True, exist_ok=True)
    dna_path = project_root / ".cognition" / "dna.json"
    if not dna_path.is_file():
        dna_path = project_root / ".hermes" / "cognition" / "dna.json"
    entry: dict[str, Any] = {
        "path": str(project_root.resolve()),
        "language": language,
        "framework": framework,
        "metrics": metrics or {},
    }
    if dna_path.is_file():
        dna = json.loads(dna_path.read_text(encoding="utf-8"))
        entry["name"] = dna.get("project", {}).get("name", project_root.name)
        entry["phases"] = len(dna.get("master_plan", {}).get("phase_sequence", []))
        entry["patterns"] = extract_patterns(dna)
    slug = project_root.name.replace(" ", "_").lower()
    out = reg_dir / f"{slug}.json"
    out.write_text(json.dumps(entry, indent=2), encoding="utf-8")
    return entry


def extract_patterns(dna: dict[str, Any]) -> dict[str, Any]:
    """Mine phase sequences and budgets from DNA (feature 43)."""
    phases = dna.get("master_plan", {}).get("phase_sequence", [])
    return {
        "phase_count": len(phases),
        "phase_names": [p.get("name") for p in phases[:10]],
        "total_sessions": dna.get("project", {}).get("total_sessions", 0),
        "hallucinations_caught": dna.get("project", {}).get("total_hallucinations_caught", 0),
    }


def find_similar_projects(language: str, framework: str, limit: int = 5) -> list[dict[str, Any]]:
    """Similarity search over registry (feature 44)."""
    reg_dir = global_registry_dir()
    if not reg_dir.is_dir():
        return []
    scored: list[tuple[float, dict[str, Any]]] = []
    for path in reg_dir.glob("*.json"):
        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        score = 0.0
        if language and entry.get("language") == language:
            score += 0.5
        if framework and entry.get("framework") == framework:
            score += 0.3
        score += min(entry.get("phases", 0) / 30.0, 0.2)
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda x: -x[0])
    return [e for _, e in scored[:limit]]


def suggest_plan_from_history(goal: str, language: str, framework: str) -> dict[str, Any]:
    """Bootstrap plan hints from past projects (feature 45)."""
    similar = find_similar_projects(language, framework)
    if not similar:
        return {"hint": "no_similar_projects", "goal": goal}
    best = similar[0]
    patterns = best.get("patterns", {})
    return {
        "hint": "use_patterns",
        "goal": goal,
        "reference_project": best.get("name"),
        "suggested_phase_count": patterns.get("phase_count", 24),
        "suggested_phase_names": patterns.get("phase_names", []),
    }
