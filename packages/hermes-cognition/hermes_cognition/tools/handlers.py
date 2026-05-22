"""Cognition tool handlers — return JSON strings."""

from __future__ import annotations

import json
from typing import Any

from hermes_cognition.bridge import CognitionBridge
from hermes_cognition.orchestration import delegate_with_role
from hermes_cognition.transfer import register_completed_project, suggest_plan_from_history


def _json_ok(**fields: Any) -> str:
    return json.dumps({"ok": True, **fields})


def _json_err(message: str, **fields: Any) -> str:
    return json.dumps({"ok": False, "error": message, **fields})


def _facade():
    return CognitionBridge.get().facade()


def cognition_init(args: dict, **kwargs: Any) -> str:
    try:
        f = _facade()
        result = f.init_project(args.get("project_name"), reinit=bool(args.get("reinit")))
        return _json_ok(
            project=result["dna"]["project"]["name"],
            cognition_dir=str(f.cognition_dir),
            scan=result.get("scan", {}),
        )
    except Exception as e:
        return _json_err(str(e))


def cognition_plan(args: dict, **kwargs: Any) -> str:
    try:
        goal = args.get("goal", "").strip()
        if not goal:
            return _json_err("goal is required")
        f = _facade()
        f.ctx.require_initialized()
        phases = f.generate_plan(goal, num_phases=int(args.get("phases", 24)))
        return _json_ok(phases=len(phases), goal=goal)
    except Exception as e:
        return _json_err(str(e))


def cognition_status(args: dict, **kwargs: Any) -> str:
    try:
        text = _facade().status_text(
            detailed=bool(args.get("detailed")),
            phase_id=args.get("phase_id"),
        )
        return _json_ok(status=text)
    except Exception as e:
        return _json_err(str(e))


def cognition_phase_update(args: dict, **kwargs: Any) -> str:
    try:
        f = _facade()
        f.ctx.require_initialized()
        phase_id = args["phase_id"]
        status = args["status"]
        f.ctx.mutator.update_phase_status(phase_id, status)
        if args.get("subtask_id") is not None and args.get("subtask_progress") is not None:
            f.ctx.mutator.update_subtask_progress(
                phase_id,
                args["subtask_id"],
                int(args["subtask_progress"]),
            )
        return _json_ok(phase_id=phase_id, status=status)
    except Exception as e:
        return _json_err(str(e))


def cognition_validate(args: dict, **kwargs: Any) -> str:
    try:
        result = _facade().validate_code(
            args.get("file_path", ""),
            args.get("code", ""),
        )
        return json.dumps(result)
    except Exception as e:
        return _json_err(str(e))


def cognition_index(args: dict, **kwargs: Any) -> str:
    try:
        f = _facade()
        f.ctx.require_initialized()
        pipe = f.ctx.validation_pipeline(index_codebase=True)
        return _json_ok(indexed=True, stats=getattr(pipe, "_stats", {}).__dict__)
    except Exception as e:
        return _json_err(str(e))


def cognition_record_avoid(args: dict, **kwargs: Any) -> str:
    try:
        f = _facade()
        f.ctx.require_initialized()
        cat = args.get("category", "failed_approach")
        desc = args.get("description", "")
        if cat == "hallucination":
            f.ctx.mutator.add_hallucination({"description": desc, "file": args.get("file", "")})
        elif cat == "deprecated_pattern":
            f.ctx.mutator.add_deprecated_pattern(desc)
        else:
            f.ctx.mutator.add_failed_approach({"description": desc, "file": args.get("file", "")})
        return _json_ok(recorded=True)
    except Exception as e:
        return _json_err(str(e))


def cognition_budget(args: dict, **kwargs: Any) -> str:
    try:
        status = _facade().budget_status()
        bridge = CognitionBridge.get()
        if bridge.budget_enabled():
            enforcer = bridge.ensure_budget_enforcer()
            status["enforcer"] = {
                "used": enforcer.tokens_used,
                "limit": enforcer.budget_limit,
            }
        return json.dumps(status)
    except Exception as e:
        return _json_err(str(e))


def cognition_impact(args: dict, **kwargs: Any) -> str:
    try:
        from src.navigator.complexity_forecaster import ComplexityForecaster

        f = _facade()
        f.ctx.require_initialized()
        cf = ComplexityForecaster(f.ctx.query, f.root)
        impact = cf.estimate_feature_impact(args.get("feature_description", ""))
        return json.dumps(impact)
    except Exception as e:
        return _json_err(str(e))


def cognition_delegate(args: dict, **kwargs: Any) -> str:
    try:
        ctx = kwargs.get("plugin_ctx") or CognitionBridge.get().get_plugin_ctx()
        if ctx is None:
            return _json_err("delegate requires plugin context")
        return delegate_with_role(
            ctx,
            role=args.get("role", "backend"),
            goal=args.get("goal", ""),
            toolsets=args.get("toolsets"),
        )
    except Exception as e:
        return _json_err(str(e))


def cognition_end_via_facade() -> str:
    try:
        return json.dumps(CognitionBridge.get().facade().end_session())
    except Exception as e:
        return _json_err(str(e))


def cognition_graphify_index(args: dict, **kwargs: Any) -> str:
    try:
        from hermes_cognition.graphify.engine import GraphifyEngine

        bridge = CognitionBridge.get()
        f = _facade()
        f.ctx.require_initialized()
        engine = GraphifyEngine(bridge.project_root, bridge.cognition_dir)
        result = engine.index(
            max_files=int(args.get("max_files", 400)),
            sync_dna=True,
            mutator=f.ctx.mutator,
        )
        return _json_ok(**result)
    except Exception as e:
        return _json_err(str(e))


def cognition_graphify_navigate(args: dict, **kwargs: Any) -> str:
    try:
        bridge = CognitionBridge.get()
        f = _facade()
        f.ctx.require_initialized()
        task = args.get("task", "").strip()
        if not task:
            return _json_err("task is required")
        bridge._last_navigation_task = task
        phase_files: list[str] = []
        phase = f.ctx.query.get_current_phase()
        if phase:
            for st in phase.get("sub_tasks", []):
                if isinstance(st, dict):
                    phase_files.extend(st.get("files_modified", []))
        nav = bridge.graphify_engine().navigate_for_task(
            task,
            token_budget=int(args.get("token_budget", bridge.graphify_nav_token_budget())),
            phase_files=phase_files,
        )
        return json.dumps({"ok": True, **nav})
    except Exception as e:
        return _json_err(str(e))


def cognition_graphify_status(args: dict, **kwargs: Any) -> str:
    try:
        bridge = CognitionBridge.get()
        f = _facade()
        f.ctx.require_initialized()
        return json.dumps(bridge.graphify_engine().status())
    except Exception as e:
        return _json_err(str(e))


def cognition_recommend_model(args: dict, **kwargs: Any) -> str:
    try:
        f = _facade()
        f.ctx.require_initialized()
        router = f.ctx.intelligent_router()
        complexity = args.get("complexity", "MEDIUM")
        check = CognitionBridge.get().ensure_budget_enforcer().check_budget()
        budget_zone = check.get("zone", "green")
        route = router.route_task(task_complexity=complexity, budget_zone=budget_zone)
        model_id = route.model_id
        pricing = f.ctx.model_registry().list_models()
        compare = f.ctx.model_registry()
        from src.models.pricing_tracker import PricingTracker

        tracker = PricingTracker(compare)
        costs = tracker.compare_costs(1000, 500, [model_id] if model_id else None)
        return _json_ok(recommended_model=model_id, complexity=complexity, costs=costs)
    except Exception as e:
        return _json_err(str(e))
