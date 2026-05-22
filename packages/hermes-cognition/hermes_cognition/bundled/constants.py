from enum import Enum


class BudgetZone(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    WRAP_UP = "wrap_up"
    EXHAUSTED = "exhausted"


def budget_zone_for_ratio(ratio: float) -> BudgetZone:
    if ratio >= 1.0:
        return BudgetZone.EXHAUSTED
    if ratio >= 0.9:
        return BudgetZone.WRAP_UP
    if ratio >= 0.85:
        return BudgetZone.RED
    if ratio >= 0.6:
        return BudgetZone.YELLOW
    return BudgetZone.GREEN
