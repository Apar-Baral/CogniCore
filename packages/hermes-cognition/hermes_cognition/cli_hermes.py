"""Hermes CLI subcommand registration for ``hermes cognition``."""

from __future__ import annotations

import argparse
from typing import Any

from hermes_cognition.cli_commands import run_cli


def _register_cognition_cli(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "cognition_args",
        nargs=argparse.REMAINDER,
        help="cognition subcommand (init, plan, start, end, status, doctor, ...)",
    )


def _cognition_command(args: argparse.Namespace) -> int:
    extra = getattr(args, "cognition_args", None) or []
    return run_cli(list(extra))


def register_cli(ctx: Any) -> None:
    ctx.register_cli_command(
        name="cognition",
        help="Cognition Engine — project DNA, planning, shield, budget",
        setup_fn=_register_cognition_cli,
        handler_fn=_cognition_command,
        description="Integrate Cognition Engine with Hermes for phased development",
    )
