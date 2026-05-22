"""Standalone doctor entry for pip script."""

from hermes_cognition.cli_commands import _doctor


def doctor_main() -> None:
    raise SystemExit(_doctor())
