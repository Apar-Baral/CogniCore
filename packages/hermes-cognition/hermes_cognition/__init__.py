"""
Hermes Cognition plugin — integrates Cognition Engine with Hermes Agent.
"""

from __future__ import annotations

import logging
from functools import partial
from pathlib import Path
from typing import Any

from hermes_cognition import hooks
from hermes_cognition.bridge import CognitionBridge
from hermes_cognition.tools import handlers, schemas

logger = logging.getLogger(__name__)

_TOOL_SPECS: list[tuple[str, dict, Any]] = [
    ("cognition_init", schemas.COGNITION_INIT, handlers.cognition_init),
    ("cognition_plan", schemas.COGNITION_PLAN, handlers.cognition_plan),
    ("cognition_status", schemas.COGNITION_STATUS, handlers.cognition_status),
    ("cognition_phase_update", schemas.COGNITION_PHASE_UPDATE, handlers.cognition_phase_update),
    ("cognition_validate", schemas.COGNITION_VALIDATE, handlers.cognition_validate),
    ("cognition_index", schemas.COGNITION_INDEX, handlers.cognition_index),
    ("cognition_record_avoid", schemas.COGNITION_RECORD_AVOID, handlers.cognition_record_avoid),
    ("cognition_budget", schemas.COGNITION_BUDGET, handlers.cognition_budget),
    ("cognition_impact", schemas.COGNITION_IMPACT, handlers.cognition_impact),
    ("cognition_delegate", schemas.COGNITION_DELEGATE, handlers.cognition_delegate),
    ("cognition_recommend_model", schemas.COGNITION_RECOMMEND_MODEL, handlers.cognition_recommend_model),
    ("cognition_graphify_index", schemas.COGNITION_GRAPHIFY_INDEX, handlers.cognition_graphify_index),
    ("cognition_graphify_navigate", schemas.COGNITION_GRAPHIFY_NAVIGATE, handlers.cognition_graphify_navigate),
    ("cognition_graphify_status", schemas.COGNITION_GRAPHIFY_STATUS, handlers.cognition_graphify_status),
]


def register(ctx: Any) -> None:
    """Hermes plugin entry point."""
    bridge = CognitionBridge.get()
    bridge.set_plugin_ctx(ctx)

    for name, schema, handler in _TOOL_SPECS:
        if name == "cognition_delegate":
            h = partial(handler, plugin_ctx=ctx)
        else:
            h = handler
        ctx.register_tool(
            name=name,
            toolset="cognition",
            schema=schema,
            handler=h,
        )

    ctx.register_hook("on_session_start", hooks.on_session_start)
    ctx.register_hook("on_session_end", hooks.on_session_end)
    ctx.register_hook("pre_tool_call", hooks.pre_tool_call)
    ctx.register_hook("post_tool_call", hooks.post_tool_call)
    ctx.register_hook("transform_tool_result", hooks.transform_tool_result)
    ctx.register_hook("pre_llm_call", hooks.pre_llm_call)
    ctx.register_hook("post_api_request", hooks.post_api_request)
    ctx.register_hook("transform_llm_output", hooks.transform_llm_output)

    skill_path = Path(__file__).parent / "skills" / "cognition-dev-orchestrator" / "SKILL.md"
    if skill_path.is_file():
        ctx.register_skill(
            "cognition-dev-orchestrator",
            skill_path,
            description="Cognition Engine development orchestration procedures",
        )

    from hermes_cognition.cli_hermes import register_cli

    register_cli(ctx)
    ctx.register_command(
        "cognition",
        _slash_cognition,
        description="Cognition: status | init | plan | end",
    )

    logger.info("hermes-cognition registered (tools, hooks, CLI)")


def _slash_cognition(ctx: Any, argstr: str) -> str:
    parts = (argstr or "").strip().split(maxsplit=1)
    sub = parts[0].lower() if parts else "status"
    rest = parts[1] if len(parts) > 1 else ""
    if sub == "status":
        return handlers.cognition_status({"detailed": "detailed" in rest})
    if sub == "init":
        return handlers.cognition_init({})
    if sub == "plan":
        return handlers.cognition_plan({"goal": rest or "Continue project"})
    if sub == "end":
        bridge = CognitionBridge.get()
        bridge.on_hermes_session_end("")
        return '{"ok": true, "message": "Cognition session ended"}'
    return '{"error": "Usage: /cognition status|init|plan <goal>|end"}'
