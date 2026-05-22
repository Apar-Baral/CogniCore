"""Bootstrap context compiler (features 19–23 simplified)."""

from __future__ import annotations

import time
from typing import Any

from hermes_cognition.bundled.context import ProjectContext


class BootstrapGenerator:
    def __init__(self, ctx: ProjectContext) -> None:
        self.ctx = ctx
        self.budget_predictor = _BudgetPredictor()

    def generate_and_save(self, task: str, *, write_file: bool = True) -> dict[str, Any]:
        text = self._build_text(task)
        path = self.ctx.cognition_dir / "bootstrap.md"
        if write_file:
            self.ctx.cognition_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        phase = self.ctx.query.get_current_phase()
        return {
            "context_text": text,
            "session_id": int(time.time()) % 100000,
            "recommended_budget": 200_000,
            "phase_id": phase.get("id") if phase else "PHASE_01",
        }

    def preview_bootstrap(self) -> dict[str, str]:
        return {"context_text": self._build_text("")}

    def _build_text(self, task: str) -> str:
        dna = self.ctx.query.refresh()
        mp = dna.get("master_plan", {})
        phase = self.ctx.query.get_current_phase() or {}
        avoid = dna.get("avoid_registry", {})
        hal = avoid.get("hallucinations", [])[-3:]
        lines = [
            "╔══════════════════════════════════════╗",
            "║     COGNITION BOOTSTRAP (bundled)    ║",
            "╚══════════════════════════════════════╝",
            "",
            "CURRENT MISSION",
            f"  Goal: {mp.get('goal', '(unset)')}",
            f"  Phase: {phase.get('id', '?')} — {phase.get('name', '?')} ({phase.get('status', '?')})",
            f"  Task: {task or '(continue)'}",
            "",
            "PROGRESS",
            f"  Completion: {self.ctx.query.calculate_project_completion()}%",
            "",
            "DO NOT REPEAT",
        ]
        if hal:
            for h in hal:
                lines.append(f"  - {h.get('description', h)[:200]}")
        else:
            lines.append("  (none recorded)")
        lines.append("")
        lines.append("BUDGET: respect session token limits; wrap up at 90%.")
        return "\n".join(lines)


class _BudgetPredictor:
    def calibrate(self, *_a: Any, **_k: Any) -> None:
        pass
