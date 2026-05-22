"""Tests for Graphify navigation."""

from pathlib import Path

from hermes_cognition.graphify.builder import build_project_graph
from hermes_cognition.graphify.navigator import navigate


def test_build_and_navigate(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "main.py").write_text(
        "from pkg.util import helper\n\ndef run():\n    return helper()\n",
        encoding="utf-8",
    )
    (pkg / "util.py").write_text("def helper():\n    return 1\n", encoding="utf-8")

    graph = build_project_graph(tmp_path, max_files=50)
    assert graph["node_count"] >= 2

    nav = navigate(graph, "fix helper function in util", token_budget=5000)
    paths = [f["path"] for f in nav["files"]]
    assert any("util" in p for p in paths)
