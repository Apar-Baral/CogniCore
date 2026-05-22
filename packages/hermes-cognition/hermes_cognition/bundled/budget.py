"""Session budget zones (features 13–18 simplified)."""

from __future__ import annotations

from hermes_cognition.bundled.constants import BudgetZone, budget_zone_for_ratio


class BudgetEnforcer:
    def __init__(self, budget_limit: int) -> None:
        self.budget_limit = max(1000, budget_limit)
        self.tokens_used = 0
        self.wrap_up_mode = False
        self._pending_injection = ""

    def add_usage(self, tokens: int) -> None:
        self.tokens_used += max(0, tokens)

    def check_budget(self) -> dict:
        ratio = self.tokens_used / self.budget_limit
        zone = budget_zone_for_ratio(ratio)
        out: dict = {
            "continue_session": zone not in (BudgetZone.EXHAUSTED,),
            "zone": zone.value,
            "ratio": round(ratio, 4),
        }
        if zone == BudgetZone.YELLOW:
            out["inject_text"] = "Budget YELLOW (60%+): prefer smaller edits and avoid re-reading large files."
        elif zone == BudgetZone.RED:
            out["inject_text"] = "Budget RED (85%+): finish current sub-task only; no new scope."
        elif zone in (BudgetZone.WRAP_UP, BudgetZone.EXHAUSTED):
            self.wrap_up_mode = True
            out["warning"] = "Budget 90%+: produce handoff summary (done, pending, next steps)."
            out["inject_text"] = out["warning"]
        return out

    def consume_pending_injection(self) -> str:
        msg = self._pending_injection
        self._pending_injection = ""
        return msg

    def get_zone_message(self, zone: BudgetZone) -> str:
        return {
            BudgetZone.WRAP_UP: "Wrap up now: summarize accomplishments, blockers, and next session steps.",
            BudgetZone.RED: "Budget critical — minimize tool calls.",
        }.get(zone, "Budget notice.")
