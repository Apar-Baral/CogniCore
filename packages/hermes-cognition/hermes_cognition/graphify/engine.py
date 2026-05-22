"""Graphify engine — index, navigate, remember."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hermes_cognition.graphify.builder import build_project_graph
from hermes_cognition.graphify.navigator import format_navigation_context, navigate
from hermes_cognition.graphify.store import GraphifyStore


class GraphifyEngine:
    def __init__(self, project_root: Path, cognition_dir: Path) -> None:
        self.root = project_root.resolve()
        self.store = GraphifyStore(cognition_dir)
        self._graph: dict[str, Any] | None = None

    @property
    def graph(self) -> dict[str, Any]:
        if self._graph is None:
            self._graph = self.store.load() or {"nodes": [], "edges": []}
        return self._graph

    def index(
        self,
        *,
        max_files: int = 400,
        sync_dna: bool = True,
        mutator: Any = None,
    ) -> dict[str, Any]:
        g = build_project_graph(self.root, max_files=max_files)
        self._graph = g
        self.store.save(g)
        if sync_dna and mutator is not None:
            self.store.sync_to_dna(mutator, g)
        return {
            "indexed": True,
            "nodes": g.get("node_count", 0),
            "edges": g.get("edge_count", 0),
            "path": str(self.store.path),
        }

    def navigate_for_task(
        self,
        task: str,
        *,
        token_budget: int = 8000,
        seed_paths: list[str] | None = None,
        phase_files: list[str] | None = None,
    ) -> dict[str, Any]:
        return navigate(
            self.graph,
            task,
            token_budget=token_budget,
            seed_paths=seed_paths,
            phase_files=phase_files,
        )

    def navigation_context(
        self,
        task: str,
        *,
        token_budget: int = 8000,
        phase_files: list[str] | None = None,
    ) -> str:
        nav = self.navigate_for_task(task, token_budget=token_budget, phase_files=phase_files)
        if not nav.get("files"):
            return ""
        return format_navigation_context(nav)

    def record_read(self, file_path: str) -> None:
        g = self.graph
        self._graph = self.store.record_access(g, file_path)
        self.store.save(self._graph)

    def status(self) -> dict[str, Any]:
        g = self.graph
        hot = sorted(
            [n for n in g.get("nodes", []) if n.get("access_count", 0) > 0],
            key=lambda x: -int(x.get("access_count", 0)),
        )[:8]
        return {
            "graph_path": str(self.store.path),
            "nodes": g.get("node_count", len(g.get("nodes", []))),
            "edges": g.get("edge_count", len(g.get("edges", []))),
            "updated_at": g.get("updated_at"),
            "most_accessed": [
                {"path": n.get("path"), "count": n.get("access_count")} for n in hot
            ],
        }

    def check_read_efficiency(self, file_path: str) -> dict[str, Any] | None:
        """Warn when reading a file that was read many times (token waste)."""
        norm = file_path.replace("\\", "/")
        for n in self.graph.get("nodes", []):
            if n.get("path") == norm:
                count = int(n.get("access_count", 0))
                if count >= 3:
                    return {
                        "warn": True,
                        "path": norm,
                        "access_count": count,
                        "message": (
                            f"Graphify: '{norm}' was read {count} times this project. "
                            "Prefer navigation plan files or summarize from prior context."
                        ),
                    }
        return None
