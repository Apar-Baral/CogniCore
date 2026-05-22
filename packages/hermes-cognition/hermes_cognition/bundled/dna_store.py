"""Project DNA persistence (.cognition/dna.json)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def empty_dna(project_name: str) -> dict[str, Any]:
    return {
        "project": {"name": project_name, "created_at": time.time()},
        "master_plan": {
            "goal": "",
            "current_phase": 1,
            "phase_sequence": [],
        },
        "avoid_registry": {"hallucinations": [], "failed_approaches": [], "deprecated_patterns": []},
        "architecture_graph": {"nodes": [], "edges": []},
    }


class DnaStore:
    def __init__(self, cognition_dir: Path) -> None:
        self.cognition_dir = cognition_dir
        self.path = cognition_dir / "dna.json"

    def load(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, dna: dict[str, Any]) -> None:
        self.cognition_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(dna, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def is_initialized(self) -> bool:
        return self.path.is_file()
