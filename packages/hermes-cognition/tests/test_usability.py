"""Regression tests for Hermes usability (no early stop / write blocks)."""

from __future__ import annotations

from hermes_cognition.bundled.shield import ValidationPipeline
from hermes_cognition.bridge import CognitionBridge


def test_shield_syntax_allows_unknown_import(tmp_path) -> None:
    pipe = ValidationPipeline(tmp_path)
    code = "import totally_fake_module_xyz\nx = 1\n"
    r = pipe.validate_code_change("a.py", "", code, mode="syntax")
    assert r["passed"] is True


def test_shield_strict_blocks_bad_import(tmp_path) -> None:
    pipe = ValidationPipeline(tmp_path)
    code = "import totally_fake_module_xyz\nx = 1\n"
    r = pipe.validate_code_change("a.py", "", code, mode="strict")
    assert r["passed"] is False


def test_usage_tokens_prefers_input_output() -> None:
    u = {"total_tokens": 999999, "input_tokens": 100, "output_tokens": 50}
    assert CognitionBridge._usage_tokens_delta(u) == 150


def test_bridge_defaults_are_non_blocking(monkeypatch) -> None:
    monkeypatch.setattr(
        "hermes_cognition.bridge.load_cognition_config",
        lambda: {},
    )
    CognitionBridge._instance = None
    b = CognitionBridge.get()
    assert b.shield_blocks_writes() is False
    assert b.shield_mode() == "syntax"
    assert b.budget_blocks_tools() is False
    assert b.budget_zone_injections() is False
    assert b.budget_wrap_up_messages() is False
    CognitionBridge._instance = None
