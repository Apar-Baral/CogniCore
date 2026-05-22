"""Terminal status rendering without external CE visualization."""

from __future__ import annotations

from typing import Any

_ICONS = {
    "COMPLETED": "✅",
    "IN_PROGRESS": "🔄",
    "IN_REVIEW": "👁",
    "BLOCKED": "🔒",
    "NOT_STARTED": "⬜",
}


def compact_progress(phases: list[dict[str, Any]], *, overall: float) -> str:
    icons = "".join(_ICONS.get(p.get("status", "NOT_STARTED"), "⬜") for p in phases[:24])
    return f"[{icons}] {overall}% complete ({len(phases)} phases)"


def phase_map(phases: list[dict[str, Any]], *, project: str, current: int, overall: float) -> str:
    lines = [f"Project: {project}", f"Overall: {overall}%", "YOU ARE HERE →", ""]
    for i, p in enumerate(phases, 1):
        mark = " <<" if i == current else ""
        lines.append(
            f"  {_ICONS.get(p.get('status', 'NOT_STARTED'), '⬜')} {p.get('id', '?')}: "
            f"{p.get('name', '?')} [{p.get('status', '?')}]{mark}"
        )
    return "\n".join(lines)


def phase_detail(phase: dict[str, Any], *, project: str) -> str:
    lines = [f"{project} — {phase.get('id')}: {phase.get('name')}", phase.get("description", ""), "", "Sub-tasks:"]
    for st in phase.get("sub_tasks", []):
        lines.append(f"  - {st.get('id')}: {st.get('name')} ({st.get('progress', 0)}%)")
    return "\n".join(lines)
