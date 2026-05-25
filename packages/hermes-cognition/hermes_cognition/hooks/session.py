"""Hook handlers wired from register()."""

from __future__ import annotations

from typing import Any

from hermes_cognition.bridge import CognitionBridge
from hermes_cognition.config import plugin_enabled


def _bridge() -> CognitionBridge:
    return CognitionBridge.get()


def on_session_start(session_id: str = "", **kwargs: Any) -> None:
    if not plugin_enabled():
        return
    _bridge().on_hermes_session_start(str(session_id or kwargs.get("session_id", "")))


def on_session_end(session_id: str = "", **kwargs: Any) -> None:
    if not plugin_enabled():
        return
    _bridge().on_hermes_session_end(str(session_id or kwargs.get("session_id", "")))


def pre_tool_call(tool_name: str = "", args: dict | None = None, **kwargs: Any) -> dict[str, str] | None:
    if not plugin_enabled():
        return None
    name = tool_name or kwargs.get("tool_name", "")
    arguments = args if isinstance(args, dict) else kwargs.get("args") or {}
    bridge = _bridge()
    block = bridge.pre_tool_graphify(name, arguments)
    if block:
        return block
    block = bridge.pre_tool_shield(name, arguments)
    if block:
        return block
    if _bridge().budget_blocks_tools():
        enforcer = _bridge().ensure_budget_enforcer()
        check = enforcer.check_budget()
        if not check.get("continue_session", True) and name in {"write_file", "patch", "terminal"}:
            return {
                "action": "block",
                "message": "Cognition budget exhausted — file and shell tools disabled.",
            }
    return None


def post_tool_call(tool_name: str = "", args: dict | None = None, result: str = "", **kwargs: Any) -> None:
    if not plugin_enabled():
        return
    _bridge().post_tool_observe(
        tool_name or kwargs.get("tool_name", ""),
        args if isinstance(args, dict) else kwargs.get("args") or {},
        result or kwargs.get("result", ""),
    )


def transform_tool_result(
    tool_name: str = "",
    args: dict | None = None,
    result: str = "",
    **kwargs: Any,
) -> str | None:
    if not plugin_enabled():
        return None
    return _bridge().transform_tool_shield(
        tool_name or kwargs.get("tool_name", ""),
        args if isinstance(args, dict) else kwargs.get("args") or {},
        result or kwargs.get("result", ""),
    )


def pre_llm_call(
    session_id: str = "",
    user_message: str = "",
    is_first_turn: bool = False,
    **kwargs: Any,
) -> dict[str, str] | None:
    if not plugin_enabled():
        return None
    bridge = _bridge()
    parts: list[str] = []
    msg = user_message or kwargs.get("user_message", "")
    ctx = bridge.pre_llm_context(is_first_turn=bool(is_first_turn or kwargs.get("is_first_turn")))
    if ctx:
        parts.append(ctx)
    gfx = bridge.pre_llm_graphify_context(
        str(msg),
        is_first_turn=bool(is_first_turn or kwargs.get("is_first_turn")),
    )
    if gfx:
        parts.append(gfx)
    budget = bridge.pre_llm_budget_check()
    if budget and budget.get("context"):
        parts.append(budget["context"])
    if parts:
        return {"context": "\n\n".join(parts)}
    return None


def post_api_request(response: Any = None, usage: dict | None = None, **kwargs: Any) -> None:
    if not plugin_enabled():
        return
    u = usage
    if u is None and isinstance(response, dict):
        u = response.get("usage")
    if u is None:
        u = kwargs.get("usage")
    _bridge().post_api_tokens(u if isinstance(u, dict) else None)


def transform_llm_output(response_text: str = "", **kwargs: Any) -> str | None:
    if not plugin_enabled():
        return None
    text = response_text or kwargs.get("response_text", "")
    return _bridge().transform_llm_wrap_up(str(text))
