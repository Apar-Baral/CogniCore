"""Token-aware graph navigation and retrieval."""

from __future__ import annotations

import re
from collections import deque
from typing import Any


def _token_estimate_for_read(path: str, nodes_by_path: dict[str, dict[str, Any]]) -> int:
    n = nodes_by_path.get(path.replace("\\", "/"))
    if n:
        return int(n.get("estimated_tokens", 800))
    return 800


def _score_node(node: dict[str, Any], query_tokens: set[str], phase_files: set[str]) -> float:
    path = node.get("path", "")
    name = node.get("name", "")
    text = f"{path} {name} {' '.join(node.get('symbols', []))}".lower()
    score = 0.0
    for tok in query_tokens:
        if len(tok) < 3:
            continue
        if tok in path.lower():
            score += 8.0
        if tok in text:
            score += 3.0
    if path in phase_files:
        score += 12.0
    score += min(int(node.get("access_count", 0)) * 0.5, 5.0)
    if node.get("last_access"):
        score += 1.0
    return score


def navigate(
    graph: dict[str, Any],
    task: str,
    *,
    token_budget: int = 8000,
    max_files: int = 12,
    seed_paths: list[str] | None = None,
    phase_files: list[str] | None = None,
) -> dict[str, Any]:
    """
    Return an ordered file reading plan that fits token_budget.
    Uses graph BFS from highest-scored seeds + import neighbors.
    """
    nodes = graph.get("nodes", [])
    if not nodes:
        return {"files": [], "total_estimated_tokens": 0, "reason": "empty_graph"}

    nodes_by_path = {n["path"]: n for n in nodes if n.get("path")}
    nodes_by_id = {n["id"]: n for n in nodes if n.get("id")}

    adj: dict[str, list[str]] = {}
    for e in graph.get("edges", []):
        if e.get("type") in ("imports", "same_package"):
            adj.setdefault(e["from"], []).append(e["to"])
            adj.setdefault(e["to"], []).append(e["from"])

    query_tokens = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", task.lower()))
    phase_set = set(phase_files or [])

    scored: list[tuple[float, str]] = []
    for n in nodes:
        p = n.get("path", "")
        if not p:
            continue
        scored.append((_score_node(n, query_tokens, phase_set), p))
    scored.sort(key=lambda x: -x[0])

    seeds: list[str] = []
    for _, p in scored[:5]:
        seeds.append(p)
    for sp in seed_paths or []:
        norm = sp.replace("\\", "/")
        if norm not in seeds:
            seeds.insert(0, norm)

    plan: list[dict[str, Any]] = []
    used_tokens = 0
    seen: set[str] = set()
    queue: deque[str] = deque(seeds)

    while queue and len(plan) < max_files and used_tokens < token_budget:
        path = queue.popleft()
        if path in seen or path not in nodes_by_path:
            continue
        seen.add(path)
        est = _token_estimate_for_read(path, nodes_by_path)
        if used_tokens + est > token_budget and plan:
            continue
        node = nodes_by_path[path]
        plan.append(
            {
                "path": path,
                "estimated_tokens": est,
                "relevance_score": round(_score_node(node, query_tokens, phase_set), 2),
                "symbols": node.get("symbols", [])[:5],
            }
        )
        used_tokens += est
        nid = node.get("id")
        if nid:
            for neighbor_id in adj.get(nid, [])[:8]:
                neighbor = nodes_by_id.get(neighbor_id)
                if neighbor and neighbor.get("path") not in seen:
                    queue.append(neighbor["path"])

    skip_suggest = [
        p
        for p, n in nodes_by_path.items()
        if int(n.get("access_count", 0)) >= 3 and p not in seen
    ][:5]

    return {
        "task": task,
        "token_budget": token_budget,
        "files": plan,
        "total_estimated_tokens": used_tokens,
        "files_count": len(plan),
        "skip_rereads": skip_suggest,
        "navigation_hint": (
            "Read files in listed order; avoid re-reading skip_rereads unless content changed."
        ),
    }


def format_navigation_context(nav: dict[str, Any]) -> str:
    """Compact injection block for pre_llm_call."""
    lines = [
        "<graphify_navigation>",
        "GRAPHIFY — token-optimized file plan (read these first; avoid redundant reads):",
        f"Estimated load: {nav.get('total_estimated_tokens', 0)} / {nav.get('token_budget', 0)} tokens",
        "",
    ]
    for i, f in enumerate(nav.get("files", [])[:10], 1):
        syms = ", ".join(f.get("symbols", [])[:3])
        extra = f" ({syms})" if syms else ""
        lines.append(
            f"  {i}. {f['path']} ~{f.get('estimated_tokens', '?')} tok "
            f"[score {f.get('relevance_score', 0)}]{extra}"
        )
    skip = nav.get("skip_rereads") or []
    if skip:
        lines.append("")
        lines.append("Avoid re-reading (already accessed 3+ times): " + ", ".join(skip[:5]))
    lines.append("</graphify_navigation>")
    return "\n".join(lines)
