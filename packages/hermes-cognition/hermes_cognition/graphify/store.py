"""Persist Graphify graph and access memory."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GraphifyStore:
    def __init__(self, cognition_dir: Path) -> None:
        self.cognition_dir = cognition_dir
        self.path = cognition_dir / "graphify.json"

    def load(self) -> dict[str, Any] | None:
        if not self.path.is_file():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def save(self, graph: dict[str, Any]) -> None:
        self.cognition_dir.mkdir(parents=True, exist_ok=True)
        graph["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.path.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    def sync_to_dna(self, mutator: Any, graph: dict[str, Any]) -> None:
        """Mirror simplified graph into DNA architecture_graph for CE bootstrap."""
        dna_nodes = []
        for n in graph.get("nodes", []):
            dna_nodes.append(
                {
                    "id": n.get("id", n.get("path", "")),
                    "type": "file",
                    "name": n.get("name", n.get("path", "")),
                    "files": [n.get("path", "")],
                    "estimated_tokens": n.get("estimated_tokens", 500),
                    "dependencies": [
                        e["to"]
                        for e in graph.get("edges", [])
                        if e.get("from") == n.get("id") and e.get("type") == "imports"
                    ][:15],
                }
            )
        dna_edges = [
            {"source": e["from"], "target": e["to"], "type": e.get("type", "imports")}
            for e in graph.get("edges", [])
            if e.get("from") in {n["id"] for n in dna_nodes} and e.get("to") in {n["id"] for n in dna_nodes}
        ]

        def apply(dna: dict[str, Any]) -> None:
            dna["architecture_graph"] = {"nodes": dna_nodes, "edges": dna_edges}
            meta = dna.setdefault("project", {})
            meta["graphify_indexed"] = True
            meta["graphify_nodes"] = len(dna_nodes)

        try:
            mutator._mutate("graphify_sync", apply)
        except Exception:
            pass

    def record_access(self, graph: dict[str, Any], file_path: str) -> dict[str, Any]:
        norm = file_path.replace("\\", "/")
        now = datetime.now(timezone.utc).isoformat()
        for n in graph.get("nodes", []):
            if n.get("path") == norm or norm in n.get("files", []):
                n["access_count"] = int(n.get("access_count", 0)) + 1
                n["last_access"] = now
                break
        graph.setdefault("access_log", []).append({"path": norm, "at": now})
        if len(graph["access_log"]) > 500:
            graph["access_log"] = graph["access_log"][-500:]
        return graph
