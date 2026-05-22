"""``hermes cognition`` CLI subcommands."""

from __future__ import annotations

import sys

from hermes_cognition.bridge import CognitionBridge
from hermes_cognition.tools import handlers
from hermes_cognition.transfer import register_completed_project, suggest_plan_from_history


def run_cli(args: list[str]) -> int:
    cmd = (args[0] if args else "help").lower()
    bridge = CognitionBridge.get()

    try:
        if cmd in ("help", "-h", "--help"):
            _print_help()
            return 0
        if cmd == "doctor":
            return _doctor()
        if cmd == "init":
            print(handlers.cognition_init({"reinit": "--reinit" in args}))
            return 0
        if cmd == "plan":
            goal = " ".join(args[1:]) if len(args) > 1 else ""
            if not goal:
                print("Usage: hermes cognition plan <goal>")
                return 1
            print(handlers.cognition_plan({"goal": goal}))
            return 0
        if cmd == "start":
            f = bridge.facade()
            f.ctx.require_initialized()
            r = f.start_session(" ".join(args[1:]) if len(args) > 1 else "")
            print(f"Session {r['session_id']} started. Bootstrap: {r['bootstrap_path']}")
            return 0
        if cmd == "end":
            print(handlers.cognition_end_via_facade())
            return 0
        if cmd == "status":
            detailed = "--detailed" in args
            phase = None
            for a in args[1:]:
                if a.startswith("--phase="):
                    phase = a.split("=", 1)[1]
            print(handlers.cognition_status({"detailed": detailed, "phase_id": phase}))
            return 0
        if cmd == "register-project":
            scan = bridge.facade().scan() if bridge.facade().is_initialized() else {}
            entry = register_completed_project(
                bridge.project_root,
                language=scan.get("language", ""),
                framework=scan.get("framework", ""),
            )
            print(entry)
            return 0
        if cmd == "graphify":
            sub = (args[1] if len(args) > 1 else "status").lower()
            f = bridge.facade()
            f.ctx.require_initialized()
            engine = __import__(
                "hermes_cognition.graphify.engine", fromlist=["GraphifyEngine"]
            ).GraphifyEngine(bridge.project_root, bridge.cognition_dir)
            if sub == "index":
                print(
                    engine.index(
                        sync_dna=True,
                        mutator=f.ctx.mutator,
                    )
                )
                return 0
            if sub == "navigate":
                task = " ".join(args[2:]) if len(args) > 2 else ""
                if not task:
                    print("Usage: hermes cognition graphify navigate <task>")
                    return 1
                import json

                print(json.dumps(engine.navigate_for_task(task), indent=2))
                return 0
            print(engine.status())
            return 0
        if cmd == "suggest-plan":
            scan = bridge.facade().scan()
            hint = suggest_plan_from_history(
                " ".join(args[1:]) if len(args) > 1 else "",
                scan.get("language", ""),
                scan.get("framework", ""),
            )
            print(hint)
            return 0
        print(f"Unknown command: {cmd}")
        _print_help()
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _doctor() -> int:
    ok = True
    try:
        import cognition_engine  # noqa: F401
    except ImportError:
        try:
            import src.facade  # noqa: F401
        except ImportError:
            print("FAIL: cognition-engine not installed (pip install cognition-engine)")
            ok = False
        else:
            print("OK: cognition-engine (src) importable")
    else:
        print("OK: cognition-engine package")

    try:
        f = CognitionBridge.get().facade()
        print(f"OK: project root {f.root}")
        print(f"    cognition dir {f.cognition_dir}")
        print(f"    initialized {f.is_initialized()}")
    except Exception as exc:
        print(f"WARN: facade {exc}")

    return 0 if ok else 1


def main() -> None:
    """Console entry: ``hermes-cognition`` (use when ``hermes cognition`` is unavailable)."""
    raise SystemExit(run_cli(sys.argv[1:]))


def _print_help() -> None:
    print(
        """Hermes Cognition Engine commands:
  hermes cognition doctor          Check install
  hermes cognition init [--reinit] Initialize .cognition/
  hermes cognition plan <goal>     Generate master plan
  hermes cognition start [task]    Start CE session + bootstrap
  hermes cognition end             End session + insights
  hermes cognition status [--detailed] [--phase=ID]
  hermes cognition register-project  Add to global registry
  hermes cognition suggest-plan <goal>  Hints from past projects
  hermes cognition graphify index       Build project graph
  hermes cognition graphify navigate <task>  Token-optimized file plan
  hermes cognition graphify status      Graph + access stats
"""
    )
