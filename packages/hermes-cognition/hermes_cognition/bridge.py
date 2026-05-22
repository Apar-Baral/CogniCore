"""Bridge between Hermes hooks/tools and Cognition Engine."""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

from hermes_cognition.config import get_nested, load_cognition_config
from hermes_cognition.engine_loader import resolve_facade
from hermes_cognition.paths import resolve_cognition_dir, resolve_project_root

logger = logging.getLogger(__name__)

_WRITE_TOOLS = frozenset({"write_file", "patch"})


class CognitionBridge:
    """Session-scoped Cognition Engine integration."""

    _instance: CognitionBridge | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self.cfg = load_cognition_config()
        self._facade: Any = None
        self._budget_enforcer: Any = None
        self._graphify: Any = None
        self._last_navigation_task: str = ""
        self._session_inject_pending = False
        self._wrap_up_sent = False
        self._hermes_session_ids: set[str] = set()

    @classmethod
    def get(cls) -> CognitionBridge:
        with cls._lock:
            if cls._instance is None:
                cls._instance = CognitionBridge()
            return cls._instance

    def reset_session_flags(self, session_id: str) -> None:
        if session_id not in self._hermes_session_ids:
            self._hermes_session_ids.add(session_id)
            self._session_inject_pending = True
            self._wrap_up_sent = False

    @property
    def data_mode(self) -> str:
        return str(self.cfg.get("data_dir", "auto"))

    @property
    def project_root(self) -> Path:
        cwd = Path.cwd()
        try:
            from hermes_constants import get_terminal_cwd

            cwd = Path(get_terminal_cwd() or cwd)
        except Exception:
            pass
        return resolve_project_root(cwd)

    @property
    def cognition_dir(self) -> Path:
        return resolve_cognition_dir(self.project_root, self.data_mode)  # type: ignore[arg-type]

    def facade(self) -> Any:
        if self._facade is None:
            self._facade = resolve_facade(self.project_root, self.cfg)
            if self.cfg.get("migrate_legacy", True):
                try:
                    self._facade.migrate_legacy_data_dir()
                except Exception as exc:
                    logger.debug("legacy migration skipped: %s", exc)
        return self._facade

    def shield_enabled(self) -> bool:
        return bool(get_nested(self.cfg, "shield", "block_writes", default=True))

    def shield_sensitivity(self) -> str:
        return str(get_nested(self.cfg, "shield", "mode", default="medium"))

    def bootstrap_enabled(self) -> bool:
        return bool(get_nested(self.cfg, "bootstrap", "inject_on_session_start", default=True))

    def budget_enabled(self) -> bool:
        return bool(get_nested(self.cfg, "budget", "zones", default=True))

    def graphify_enabled(self) -> bool:
        return bool(get_nested(self.cfg, "graphify", "enabled", default=True))

    def graphify_block_rereads(self) -> bool:
        return bool(get_nested(self.cfg, "graphify", "block_rereads", default=False))

    def graphify_nav_token_budget(self) -> int:
        custom = get_nested(self.cfg, "graphify", "navigation_token_budget")
        if isinstance(custom, int) and custom > 0:
            return custom
        return int(get_nested(self.cfg, "bootstrap", "max_tokens", default=2000)) * 2

    def graphify_engine(self) -> Any:
        if self._graphify is None:
            from hermes_cognition.graphify.engine import GraphifyEngine

            self._graphify = GraphifyEngine(self.project_root, self.cognition_dir)
        return self._graphify

    def session_budget_limit(self) -> int:
        custom = get_nested(self.cfg, "budget", "session_tokens")
        if isinstance(custom, int) and custom > 0:
            return custom
        state = self._load_ce_session_state()
        if state and state.get("budget"):
            return int(state["budget"])
        return 200_000

    def _load_ce_session_state(self) -> dict[str, Any] | None:
        try:
            f = self.facade()
            return f.ctx.load_session_state()
        except Exception:
            return None

    def ensure_budget_enforcer(self) -> Any:
        if self._budget_enforcer is None:
            try:
                from src.proxy.budget_enforcer import BudgetEnforcer
            except ImportError:
                from hermes_cognition.bundled.budget import BudgetEnforcer

            self._budget_enforcer = BudgetEnforcer(self.session_budget_limit())
        return self._budget_enforcer

    def on_hermes_session_start(self, session_id: str) -> None:
        self.reset_session_flags(session_id)
        try:
            f = self.facade()
            if not f.is_initialized():
                return
            if not f.ctx.load_session_state():
                f.start_session(write_bootstrap_file=True)
            else:
                f.get_bootstrap_for_injection()
                try:
                    f.ctx.precompiler().warm_up()
                except Exception:
                    pass
            if self.graphify_enabled() and f.is_initialized():
                gpath = self.cognition_dir / "graphify.json"
                if not gpath.is_file() and get_nested(self.cfg, "graphify", "auto_index", default=True):
                    try:
                        self.graphify_engine().index(
                            max_files=int(get_nested(self.cfg, "graphify", "max_files", default=400)),
                            sync_dna=True,
                            mutator=f.ctx.mutator,
                        )
                    except Exception as exc:
                        logger.debug("graphify auto_index: %s", exc)
        except Exception as exc:
            logger.warning("cognition on_session_start: %s", exc)

    def on_hermes_session_end(self, session_id: str) -> None:
        try:
            f = self.facade()
            if not f.is_initialized():
                return
            if f.ctx.load_session_state():
                f.end_session(summary=f"Hermes session {session_id} ended.")
        except Exception as exc:
            logger.warning("cognition on_session_end: %s", exc)
        finally:
            self._session_inject_pending = False

    def pre_llm_context(self, *, is_first_turn: bool) -> str | None:
        if not self.bootstrap_enabled():
            return None
        try:
            f = self.facade()
            if not f.is_initialized():
                return None
            text = f.get_bootstrap_for_injection()
            if not text:
                if is_first_turn or self._session_inject_pending:
                    result = f.start_session(write_bootstrap_file=True)
                    text = result.get("bootstrap_text", "")
                else:
                    return None
            if text and (is_first_turn or self._session_inject_pending):
                self._session_inject_pending = False
                header = (
                    "<cognition_bootstrap>\n"
                    "The following is your Cognition Engine project context. "
                    "Follow CURRENT MISSION and DO NOT REPEAT sections.\n\n"
                )
                return header + text + "\n</cognition_bootstrap>"
        except Exception as exc:
            logger.warning("cognition bootstrap inject: %s", exc)
        return None

    def pre_llm_graphify_context(self, user_message: str = "") -> str | None:
        if not self.graphify_enabled():
            return None
        try:
            f = self.facade()
            if not f.is_initialized():
                return None
            task = (user_message or self._last_navigation_task or "").strip()
            if not task:
                phase = f.ctx.query.get_current_phase()
                if phase:
                    task = str(phase.get("description") or phase.get("name") or "continue work")
                else:
                    task = "continue project work"
            self._last_navigation_task = task
            phase_files: list[str] = []
            phase = f.ctx.query.get_current_phase()
            if phase:
                for st in phase.get("sub_tasks", []):
                    if isinstance(st, dict):
                        phase_files.extend(st.get("files_modified", []))
            ctx = self.graphify_engine().navigation_context(
                task,
                token_budget=self.graphify_nav_token_budget(),
                phase_files=phase_files,
            )
            return ctx or None
        except Exception as exc:
            logger.debug("graphify pre_llm: %s", exc)
        return None

    def pre_llm_budget_check(self) -> dict[str, Any] | None:
        if not self.budget_enabled():
            return None
        enforcer = self.ensure_budget_enforcer()
        try:
            f = self.facade()
            if f.is_initialized() and f.ctx.load_session_state():
                op = f.ctx.active_operational_memory()
                enforcer.tokens_used = op.tokens_used
        except Exception:
            pass
        check = enforcer.check_budget()
        parts: list[str] = []
        if not check.get("continue_session", True):
            parts.append(
                check.get("warning")
                or "TOKEN BUDGET EXHAUSTED. Do not make further API-heavy work. Produce handoff only."
            )
        inject = check.get("inject_text") or enforcer.consume_pending_injection()
        if inject:
            parts.append(inject)
        if parts:
            return {"context": "<cognition_budget>\n" + "\n\n".join(parts) + "\n</cognition_budget>"}
        return None

    def post_api_tokens(self, usage: dict[str, Any] | None) -> None:
        if not usage:
            return
        total = int(usage.get("total_tokens") or usage.get("input_tokens", 0) + usage.get("output_tokens", 0))
        if total <= 0:
            return
        try:
            self.facade().record_api_tokens(total)
            enforcer = self.ensure_budget_enforcer()
            enforcer.add_usage(total)
        except Exception as exc:
            logger.debug("post_api_request metering: %s", exc)

    def transform_llm_wrap_up(self, response_text: str) -> str | None:
        if self._wrap_up_sent or not self.budget_enabled():
            return None
        enforcer = self.ensure_budget_enforcer()
        check = enforcer.check_budget()
        try:
            from src.core.constants import BudgetZone, budget_zone_for_ratio
        except ImportError:
            from hermes_cognition.bundled.constants import BudgetZone, budget_zone_for_ratio

        ratio = enforcer.tokens_used / enforcer.budget_limit if enforcer.budget_limit else 0
        zone = budget_zone_for_ratio(ratio)
        if zone not in (BudgetZone.WRAP_UP, BudgetZone.RED) and not enforcer.wrap_up_mode:
            return None
        self._wrap_up_sent = True
        msg = enforcer.get_zone_message(BudgetZone.WRAP_UP)
        return (response_text or "") + "\n\n---\n**Cognition Engine:** " + msg

    def pre_tool_shield(
        self,
        tool_name: str,
        args: dict[str, Any],
    ) -> dict[str, str] | None:
        if tool_name not in _WRITE_TOOLS or not self.shield_enabled():
            return None
        try:
            f = self.facade()
            if not f.is_initialized():
                return None
            path, proposed, original = self._extract_write_payload(tool_name, args)
            if not path or proposed is None:
                return None
            result = f.validate_code(path, proposed, original_content=original)
            if result.get("passed"):
                return None
            verdict = result.get("verdict", "BLOCK")
            if verdict == "PASS":
                return None
            issues = result.get("issues") or result.get("errors") or []
            msg = f"Cognition Shield blocked {tool_name} on {path}: {issues[:3]}"
            self._record_avoid_from_block(path, msg)
            return {"action": "block", "message": msg}
        except Exception as exc:
            logger.debug("shield pre_tool_call: %s", exc)
        return None

    def transform_tool_shield(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: str,
    ) -> str | None:
        if tool_name not in _WRITE_TOOLS:
            return None
        try:
            f = self.facade()
            if not f.is_initialized():
                return None
            path, proposed, original = self._extract_write_payload(tool_name, args)
            if not path or proposed is None:
                return None
            validation = f.validate_code(path, proposed, original_content=original)
            corrected = validation.get("proposed_content") or validation.get("corrected_content")
            if validation.get("auto_corrected") and corrected and corrected != proposed:
                return json.dumps(
                    {
                        "cognition_shield": "auto_corrected",
                        "message": "Shield applied corrections before write.",
                        "validation": validation,
                    }
                )
        except Exception:
            pass
        return None

    def _extract_write_payload(
        self,
        tool_name: str,
        args: dict[str, Any],
    ) -> tuple[str, str | None, str]:
        root = self.project_root
        if tool_name == "write_file":
            path = str(args.get("path", ""))
            content = args.get("content")
            if content is None:
                return path, None, ""
            full = (root / path).resolve() if path else root
            original = full.read_text(encoding="utf-8", errors="replace") if full.is_file() else ""
            return path, str(content), original
        if tool_name == "patch":
            mode = args.get("mode", "replace")
            if mode == "replace" and args.get("path") and args.get("new_string") is not None:
                path = str(args["path"])
                full = (root / path).resolve()
                original = full.read_text(encoding="utf-8", errors="replace") if full.is_file() else ""
                old = str(args.get("old_string", ""))
                new = str(args.get("new_string", ""))
                if args.get("replace_all"):
                    proposed = original.replace(old, new)
                else:
                    proposed = original.replace(old, new, 1) if old in original else original
                return path, proposed, original
        return "", None, ""

    def _record_avoid_from_block(self, path: str, message: str) -> None:
        try:
            f = self.facade()
            if not f.is_initialized():
                return
            f.ctx.mutator.add_hallucination(
                {
                    "description": message[:500],
                    "file": path,
                    "source": "hermes_shield",
                }
            )
        except Exception:
            pass

    def pre_tool_graphify(self, tool_name: str, args: dict[str, Any]) -> dict[str, str] | None:
        if tool_name != "read_file" or not self.graphify_enabled() or not self.graphify_block_rereads():
            return None
        path = str((args or {}).get("path", ""))
        if not path:
            return None
        try:
            check = self.graphify_engine().check_read_efficiency(path)
            if check and check.get("warn"):
                return {"action": "block", "message": check["message"]}
        except Exception:
            pass
        return None

    def post_tool_observe(self, tool_name: str, args: dict[str, Any], result: str) -> None:
        if tool_name != "read_file":
            return
        path = str((args or {}).get("path", ""))
        try:
            if self.graphify_enabled():
                self.graphify_engine().record_read(path)
        except Exception:
            pass
        try:
            f = self.facade()
            if f.is_initialized() and f.ctx.load_session_state():
                import hashlib

                h = hashlib.sha256(result[:8000].encode()).hexdigest()[:16]
                f.ctx.active_operational_memory().log_file_operation(
                    path, "read", "", h
                )
        except Exception:
            pass

    def set_plugin_ctx(self, ctx: Any) -> None:
        self._plugin_ctx = ctx

    def get_plugin_ctx(self) -> Any:
        return getattr(self, "_plugin_ctx", None)
