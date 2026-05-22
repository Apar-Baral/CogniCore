"""Tests for cognition directory resolution."""

from pathlib import Path

from hermes_cognition.paths import resolve_cognition_dir, resolve_project_root


def test_resolve_cognition_primary(tmp_path: Path) -> None:
    cog = tmp_path / ".cognition"
    cog.mkdir()
    (cog / "dna.json").write_text("{}", encoding="utf-8")
    assert resolve_cognition_dir(tmp_path) == cog


def test_resolve_cognition_legacy(tmp_path: Path) -> None:
    leg = tmp_path / ".hermes" / "cognition"
    leg.mkdir(parents=True)
    (leg / "dna.json").write_text("{}", encoding="utf-8")
    assert resolve_cognition_dir(tmp_path) == leg


def test_resolve_project_root(tmp_path: Path) -> None:
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    (tmp_path / ".cognition" / "dna.json").parent.mkdir(parents=True)
    (tmp_path / ".cognition" / "dna.json").write_text("{}", encoding="utf-8")
    assert resolve_project_root(sub) == tmp_path.resolve()
