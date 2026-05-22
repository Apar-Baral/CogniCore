"""Multi-agent orchestration (features 46-49) via Hermes delegate_task."""

from __future__ import annotations

import json
from typing import Any

ROLE_PROMPTS: dict[str, str] = {
    "architect": "You are the Architect agent. Design only — no implementation. Output diagrams, interfaces, and decisions.",
    "backend": "You are the Backend Dev agent. Implement server logic, APIs, and data layers. Follow existing patterns.",
    "frontend": "You are the Frontend Dev agent. Implement UI components and client integration only.",
    "security": "You are the Security Reviewer. Audit for vulnerabilities; do not add features unless fixing security issues.",
    "test": "You are the Test Writer. Add or update tests; minimal production code changes.",
    "docs": "You are the Doc Writer. Update README, API docs, and comments — no logic changes unless documenting.",
    "refactor": "You are the Refactor agent. Improve structure without changing behavior; run tests if present.",
}


def decompose_phase_tasks(phases: list[dict[str, Any]], phase_id: str) -> list[dict[str, Any]]:
    """Break phase sub-tasks into parallelizable units (feature 47)."""
    for phase in phases:
        if phase.get("id") != phase_id:
            continue
        units = []
        for st in phase.get("sub_tasks", []):
            est = st.get("estimated_tokens", 25000)
            units.append(
                {
                    "subtask_id": st.get("id"),
                    "name": st.get("name"),
                    "estimated_tokens": est,
                    "parallel_safe": st.get("status") == "pending",
                    "contract": f"Deliver: {st.get('name')}; files: {st.get('files_modified', [])}",
                }
            )
        return units
    return []


def merge_agent_outputs(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    """Combine parallel agent results (feature 48)."""
    merged_files: dict[str, str] = {}
    conflicts: list[dict[str, Any]] = []
    for out in outputs:
        for path, content in (out.get("files") or {}).items():
            if path in merged_files and merged_files[path] != content:
                conflicts.append({"path": path, "sources": 2})
            merged_files[path] = content
    resolution = resolve_conflicts(conflicts)
    return {"files": merged_files, "conflicts": conflicts, "resolution": resolution}


def resolve_conflicts(conflicts: list[dict[str, Any]]) -> str:
    """Conflict resolution strategy (feature 49)."""
    if not conflicts:
        return "none"
    if len(conflicts) == 1:
        return "last_write_wins"
    return "manual_required"


def delegate_with_role(
    plugin_ctx: Any,
    *,
    role: str,
    goal: str,
    toolsets: list[str] | None = None,
) -> str:
    prompt = ROLE_PROMPTS.get(role, ROLE_PROMPTS["backend"])
    full_goal = f"{prompt}\n\nTask: {goal}"
    ts = toolsets or ["terminal", "file", "web"]
    result = plugin_ctx.dispatch_tool(
        "delegate_task",
        {
            "goal": full_goal,
            "toolsets": ts,
        },
    )
    return json.dumps({"role": role, "delegated": True, "result": result})
