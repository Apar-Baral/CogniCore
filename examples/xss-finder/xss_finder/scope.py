"""Target rules, denylist, and URL validation (Phase 01)."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from xss_finder.config import (
    BUILTIN_DENY_HOSTS,
    PRIVATE_PREFIXES,
    ScanConfig,
)

_URL_RE = re.compile(r"^https?://", re.I)


@dataclass
class ScopeDecision:
    ok: bool
    reason: str = ""


class ScopeGuard:
    def __init__(self, config: ScanConfig) -> None:
        self.config = config
        self._denied = {h.lower() for h in BUILTIN_DENY_HOSTS}
        self._denied.update(h.lower() for h in config.scope.denied_hosts)
        self._allowed = {h.lower() for h in config.scope.allowed_hosts}

    def check_authorization(self) -> ScopeDecision:
        if not self.config.authorized:
            return ScopeDecision(
                False,
                "Refused: pass --i-agree you have written authorization to test the target.",
            )
        return ScopeDecision(True)

    def validate_url(self, url: str) -> ScopeDecision:
        if not _URL_RE.match(url):
            return ScopeDecision(False, "URL must start with http:// or https://")
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if not host:
            return ScopeDecision(False, "Missing hostname")
        if host in self._denied:
            return ScopeDecision(False, f"Host denied by policy: {host}")
        for prefix in PRIVATE_PREFIXES:
            if host.startswith(prefix):
                return ScopeDecision(False, f"Private/reserved host blocked: {host}")
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return ScopeDecision(False, f"IP blocked: {host}")
        except ValueError:
            pass
        if self._allowed and host not in self._allowed:
            return ScopeDecision(False, f"Host not in --allow-host list: {host}")
        if self.config.scope.allowed_path_prefixes:
            path = parsed.path or "/"
            if not any(path.startswith(p) for p in self.config.scope.allowed_path_prefixes):
                return ScopeDecision(False, f"Path not allowed: {path}")
        if self.config.safety.require_https_patterns and not url.lower().startswith("https://"):
            return ScopeDecision(False, "HTTPS required by policy")
        return ScopeDecision(True)

    def filter_urls(self, urls: list[str]) -> tuple[list[str], list[str]]:
        ok_list: list[str] = []
        errors: list[str] = []
        for u in urls:
            d = self.validate_url(u)
            if d.ok:
                ok_list.append(u)
            else:
                errors.append(f"{u}: {d.reason}")
        return ok_list, errors
