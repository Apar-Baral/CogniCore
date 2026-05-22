"""Minimal ProjectContext for bundled engine."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from hermes_cognition.bundled.dna_store import DnaStore, empty_dna


class Mutator:
    def __init__(self, store: DnaStore) -> None:
        self._store = store

    def _dna(self) -> dict[str, Any]:
        return self._store.load()

    def _save(self, dna: dict[str, Any]) -> None:
        self._store.save(dna)

    def update_phase_status(self, phase_id: str, status: str) -> None:
        dna = self._dna()
        for ph in dna.get("master_plan", {}).get("phase_sequence", []):
            if ph.get("id") == phase_id:
                ph["status"] = status
                break
        self._save(dna)

    def update_subtask_progress(self, phase_id: str, subtask_id: str, progress: int) -> None:
        dna = self._dna()
        for ph in dna.get("master_plan", {}).get("phase_sequence", []):
            if ph.get("id") != phase_id:
                continue
            for st in ph.get("sub_tasks", []):
                if st.get("id") == subtask_id:
                    st["progress"] = max(0, min(100, progress))
            break
        self._save(dna)

    def add_hallucination(self, entry: dict[str, Any]) -> None:
        dna = self._dna()
        reg = dna.setdefault("avoid_registry", {})
        reg.setdefault("hallucinations", []).append({**entry, "ts": time.time()})
        self._save(dna)

    def add_failed_approach(self, entry: dict[str, Any]) -> None:
        dna = self._dna()
        reg = dna.setdefault("avoid_registry", {})
        reg.setdefault("failed_approaches", []).append({**entry, "ts": time.time()})
        self._save(dna)

    def add_deprecated_pattern(self, desc: str) -> None:
        dna = self._dna()
        reg = dna.setdefault("avoid_registry", {})
        reg.setdefault("deprecated_patterns", []).append({"description": desc, "ts": time.time()})
        self._save(dna)


class Query:
    def __init__(self, store: DnaStore) -> None:
        self._store = store

    def refresh(self) -> dict[str, Any]:
        return self._store.load()

    def get_current_phase(self) -> dict[str, Any] | None:
        dna = self._store.load()
        seq = dna.get("master_plan", {}).get("phase_sequence", [])
        idx = int(dna.get("master_plan", {}).get("current_phase", 1)) - 1
        if 0 <= idx < len(seq):
            return seq[idx]
        return seq[0] if seq else None

    def get_phase_by_id(self, phase_id: str) -> dict[str, Any] | None:
        for ph in self._store.load().get("master_plan", {}).get("phase_sequence", []):
            if ph.get("id") == phase_id:
                return ph
        return None

    def calculate_project_completion(self) -> float:
        seq = self._store.load().get("master_plan", {}).get("phase_sequence", [])
        if not seq:
            return 0.0
        done = sum(1 for p in seq if p.get("status") == "COMPLETED")
        return round(100.0 * done / len(seq), 1)


class OperationalMemory:
    def __init__(self) -> None:
        self.tokens_used = 0
        self._notes = ""

    def log_api_call(self, *_a: Any, **_k: Any) -> None:
        pass

    def set_completion_notes(self, notes: str) -> None:
        self._notes = notes

    def get_session_summary(self) -> dict[str, Any]:
        return {
            "tokens": {"total": self.tokens_used},
            "efficiency_score": 70,
            "notes": self._notes,
        }

    def log_file_operation(self, *_a: Any, **_k: Any) -> None:
        pass

    def flush_to_dna(self, mutator: Mutator, query: Query, phase_id: str) -> None:
        dna = mutator._dna()
        dna.setdefault("sessions", []).append(
            {"phase_id": phase_id, "tokens": self.tokens_used, "ended_at": time.time()}
        )
        mutator._save(dna)


class ProjectContext:
    def __init__(self, root: Path, cognition_dir: Path) -> None:
        self.root = root
        self.cognition_dir = cognition_dir
        self.loader = DnaStore(cognition_dir)
        self.mutator = Mutator(self.loader)
        self.query = Query(self.loader)
        self._session_path = cognition_dir / "session_state.json"
        self._op: OperationalMemory | None = None

    def is_initialized(self) -> bool:
        return self.loader.is_initialized()

    def require_initialized(self) -> None:
        if not self.is_initialized():
            raise RuntimeError("Project not initialized — run hermes-cognition init")

    def init_project(self, name: str | None = None, *, reinit: bool = False) -> dict[str, Any]:
        if self.is_initialized() and not reinit:
            return {"dna": self.loader.load(), "scan": self.scan()}
        pname = name or self.root.name
        dna = empty_dna(pname)
        self.loader.save(dna)
        return {"dna": dna, "scan": self.scan()}

    def scan(self) -> dict[str, Any]:
        lang = "python"
        fw = ""
        if (self.root / "pyproject.toml").is_file() or list(self.root.glob("*.py")):
            lang = "python"
        elif (self.root / "package.json").is_file():
            lang = "javascript"
            fw = "node"
        return {"language": lang, "framework": fw, "root": str(self.root)}

    def set_project_goal(self, goal: str) -> None:
        dna = self.loader.load()
        dna.setdefault("master_plan", {})["goal"] = goal
        self.loader.save(dna)

    def get_project_goal(self) -> str:
        return self.loader.load().get("master_plan", {}).get("goal", "")

    def save_plan(self, phases: list[dict[str, Any]], *, goal: str = "") -> None:
        dna = self.loader.load()
        mp = dna.setdefault("master_plan", {})
        mp["phase_sequence"] = phases
        mp["goal"] = goal or mp.get("goal", "")
        mp["current_phase"] = 1
        self.loader.save(dna)

    def project_name(self) -> str:
        return self.loader.load().get("project", {}).get("name", self.root.name)

    def load_session_state(self) -> dict[str, Any] | None:
        if not self._session_path.is_file():
            return None
        return json.loads(self._session_path.read_text(encoding="utf-8"))

    def save_session_state(self, state: dict[str, Any]) -> None:
        self.cognition_dir.mkdir(parents=True, exist_ok=True)
        self._session_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def clear_session_state(self) -> None:
        if self._session_path.is_file():
            self._session_path.unlink()

    def active_operational_memory(self) -> OperationalMemory:
        if self._op is None:
            self._op = OperationalMemory()
            st = self.load_session_state()
            if st:
                self._op.tokens_used = int(st.get("tokens_used", 0))
        return self._op

    def validation_pipeline(self, *, index_codebase: bool = False) -> Any:
        from hermes_cognition.bundled.shield import ValidationPipeline

        return ValidationPipeline(self.root, index_codebase=index_codebase)

    def bootstrap_generator(self) -> Any:
        from hermes_cognition.bundled.bootstrap import BootstrapGenerator

        return BootstrapGenerator(self)

    def precompiler(self) -> Any:
        return _NoOp()

    def knowledge_synthesizer(self) -> Any:
        return _NoOp()

    def rl_allocator(self) -> Any:
        return _NoOp()

    def intelligent_router(self) -> Any:
        from hermes_cognition.bundled.router import IntelligentRouter

        return IntelligentRouter()

    def model_registry(self) -> Any:
        from hermes_cognition.bundled.router import ModelRegistry

        return ModelRegistry()

    def session_store(self) -> Any:
        return _NoOp()

    def config(self) -> Any:
        return _Config()


class _Config:
    def get_token_budget(self, _kind: str) -> int:
        return 200_000


class _NoOp:
    def warm_up(self) -> None:
        pass

    def synthesize(self, *_a: Any, **_k: Any) -> None:
        pass

    def record_session_result(self, *_a: Any, **_k: Any) -> None:
        pass

    def close_session(self, *_a: Any, **_k: Any) -> None:
        pass

    def get_recommended_allocation(self, *_a: Any) -> dict[str, int]:
        return {"build": 70, "test": 20, "docs": 10}
