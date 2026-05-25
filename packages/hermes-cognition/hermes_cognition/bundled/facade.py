"""Bundled CognitionFacade — same public surface as external CE for Hermes plugin."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from hermes_cognition.bundled.constants import budget_zone_for_ratio
from hermes_cognition.bundled.context import ProjectContext
from hermes_cognition.bundled.dna_store import empty_dna
from hermes_cognition.bundled.planner import generate_goal_plan
from hermes_cognition.bundled.status_render import compact_progress, phase_detail, phase_map
from hermes_cognition.paths import resolve_cognition_dir, resolve_project_root


class BundledFacade:
    engine_source = "cognicore-bundled"

    def __init__(self, root: Path | str | None = None) -> None:
        start = Path(root) if root else Path.cwd()
        self.root = resolve_project_root(start)
        cog = resolve_cognition_dir(self.root)
        self.ctx = ProjectContext(self.root, cog)

    @property
    def cognition_dir(self) -> Path:
        return self.ctx.cognition_dir

    def is_initialized(self) -> bool:
        return self.ctx.is_initialized()

    def init_project(self, name: str | None = None, *, reinit: bool = False) -> dict[str, Any]:
        return self.ctx.init_project(name, reinit=reinit)

    def scan(self) -> dict[str, Any]:
        return self.ctx.scan()

    def set_goal(self, goal: str) -> None:
        self.ctx.require_initialized()
        self.ctx.set_project_goal(goal)

    def get_goal(self) -> str:
        return self.ctx.get_project_goal()

    def generate_plan(self, goal: str, *, num_phases: int = 24) -> list[dict[str, Any]]:
        self.ctx.require_initialized()
        scan = self.ctx.scan()
        phases = generate_goal_plan(goal, num_phases=num_phases, language=scan.get("language", "python"))
        self.ctx.save_plan(phases, goal=goal)
        return phases

    def start_session(
        self,
        task: str = "",
        *,
        budget: int | None = None,
        write_bootstrap_file: bool = True,
    ) -> dict[str, Any]:
        self.ctx.require_initialized()
        bootstrap = self.ctx.bootstrap_generator().generate_and_save(task, write_file=write_bootstrap_file)
        budget_tokens = budget or bootstrap.get("recommended_budget") or 200_000
        sid = int(bootstrap.get("session_id") or 1)
        self.ctx.save_session_state({"session_id": sid, "budget": budget_tokens, "session_type": "BUILD"})
        return {
            "session_id": sid,
            "budget": budget_tokens,
            "bootstrap_text": bootstrap.get("context_text", ""),
            "bootstrap_path": str(self.ctx.cognition_dir / "bootstrap.md"),
            "phase_id": bootstrap.get("phase_id"),
            "engine": self.engine_source,
        }

    def end_session(self, summary: str = "", *, tokens: int = 0) -> dict[str, Any]:
        self.ctx.require_initialized()
        state = self.ctx.load_session_state()
        if not state:
            return {"ended": False, "reason": "no_active_session"}
        op = self.ctx.active_operational_memory()
        if tokens:
            op.tokens_used += tokens
        if summary:
            op.set_completion_notes(summary)
        sess = op.get_session_summary()
        phase = self.ctx.query.get_current_phase()
        phase_id = phase.get("id", "PHASE_01") if phase else "PHASE_01"
        op.flush_to_dna(self.ctx.mutator, self.ctx.query, phase_id)
        self.ctx.clear_session_state()
        return {"ended": True, "summary": sess, "engine": self.engine_source}

    def validate_code(
        self,
        file_path: str,
        proposed_content: str,
        *,
        original_content: str = "",
        mode: str = "syntax",
    ) -> dict[str, Any]:
        self.ctx.require_initialized()
        return self.ctx.validation_pipeline(index_codebase=False).validate_code_change(
            file_path, original_content, proposed_content, mode=mode
        )

    def status_text(self, *, detailed: bool = False, phase_id: str | None = None) -> str:
        self.ctx.require_initialized()
        dna = self.ctx.query.refresh()
        phases = dna.get("master_plan", {}).get("phase_sequence", [])
        overall = self.ctx.query.calculate_project_completion()
        if phase_id:
            phase = self.ctx.query.get_phase_by_id(phase_id)
            return phase_detail(phase or {}, project=self.ctx.project_name()) if phase else "Phase not found"
        if detailed:
            return phase_map(
                phases,
                project=self.ctx.project_name(),
                current=int(dna.get("master_plan", {}).get("current_phase", 1)),
                overall=overall,
            )
        return compact_progress(phases, overall=overall)

    def budget_status(self) -> dict[str, Any]:
        state = self.ctx.load_session_state()
        if not state:
            return {"active": False, "engine": self.engine_source}
        op = self.ctx.active_operational_memory()
        used = op.tokens_used
        limit = int(state.get("budget", 200_000))
        ratio = used / limit if limit else 0.0
        zone = budget_zone_for_ratio(ratio)
        return {
            "active": True,
            "used": used,
            "limit": limit,
            "ratio": ratio,
            "zone": zone.value,
            "engine": self.engine_source,
        }

    def record_api_tokens(self, tokens: int) -> None:
        state = self.ctx.load_session_state()
        if state:
            self.ctx.active_operational_memory().tokens_used += tokens
            state["tokens_used"] = self.ctx.active_operational_memory().tokens_used
            self.ctx.save_session_state(state)

    def get_bootstrap_for_injection(self) -> str:
        path = self.ctx.cognition_dir / "bootstrap.md"
        if path.is_file():
            return path.read_text(encoding="utf-8")
        if self.ctx.is_initialized():
            return self.ctx.bootstrap_generator().preview_bootstrap().get("context_text", "")
        return ""

    def migrate_legacy_data_dir(self) -> Path:
        legacy = self.root / ".hermes" / "cognition"
        target = self.root / ".cognition"
        if target.joinpath("dna.json").is_file():
            return target
        if not legacy.joinpath("dna.json").is_file():
            return target
        target.mkdir(parents=True, exist_ok=True)
        for item in legacy.iterdir():
            dest = target / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
        if self.ctx.is_initialized():
            dna = self.ctx.loader.load()
            dna.setdefault("project", {})["migrated_from"] = str(legacy)
            self.ctx.loader.save(dna)
        return target
