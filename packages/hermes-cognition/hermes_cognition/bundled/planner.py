"""Phase plan generator (feature 24 simplified)."""

from __future__ import annotations

from typing import Any


def generate_goal_plan(goal: str, *, num_phases: int = 12, language: str = "python") -> list[dict[str, Any]]:
    n = max(3, min(num_phases, 30))
    templates = [
        ("Scope and safety controls", "Define authorized scope, rate limits, and legal constraints"),
        ("Project scaffold", f"Create {language} package layout and entrypoints"),
        ("Core domain logic", "Implement main algorithms and data structures"),
        ("CLI / API surface", "User-facing commands or HTTP handlers"),
        ("Input validation", "Validate and sanitize all external inputs"),
        ("Error handling and logging", "Structured errors and observability"),
        ("Tests", "Unit and integration tests for critical paths"),
        ("Documentation", "README, usage examples, and architecture notes"),
        ("Security review", "Audit dependencies and dangerous patterns"),
        ("Performance pass", "Profile and optimize hot paths"),
        ("Integration testing", "End-to-end scenarios on safe targets"),
        ("Release prep", "Versioning, packaging, and handoff summary"),
    ]
    phases: list[dict[str, Any]] = []
    for i in range(n):
        t = templates[i % len(templates)]
        pid = f"PHASE_{i + 1:02d}"
        phases.append(
            {
                "id": pid,
                "name": t[0],
                "description": f"{t[1]} — supports goal: {goal[:120]}",
                "status": "NOT_STARTED",
                "sub_tasks": [
                    {
                        "id": f"{pid}_T1",
                        "name": t[0],
                        "progress": 0,
                        "status": "pending",
                    }
                ],
            }
        )
    if phases:
        phases[0]["status"] = "IN_PROGRESS"
    return phases
