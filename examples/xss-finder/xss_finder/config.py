"""Safety and scope configuration (Phase 01)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SafetyDefaults:
    rate_limit_rps: float = 0.5
    max_params: int = 20
    follow_redirects: bool = False
    timeout_sec: float = 15.0
    max_payloads: int = 30
    require_https_patterns: bool = False

    @classmethod
    def default(cls) -> SafetyDefaults:
        return cls()


@dataclass
class ScopeConfig:
    allowed_hosts: list[str] = field(default_factory=list)
    denied_hosts: list[str] = field(default_factory=list)
    allowed_path_prefixes: list[str] = field(default_factory=list)
    max_depth: int = 1
    crawl_links: bool = False

    @classmethod
    def with_defaults(cls) -> ScopeConfig:
        return cls(
            denied_hosts=list(BUILTIN_DENY_HOSTS),
        )


# Always blocked unless explicitly allowed
BUILTIN_DENY_HOSTS = (
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
    "metadata.google.internal",
)

PRIVATE_PREFIXES = (
    "10.",
    "172.16.",
    "172.17.",
    "172.18.",
    "172.19.",
    "172.20.",
    "172.21.",
    "172.22.",
    "172.23.",
    "172.24.",
    "172.25.",
    "172.26.",
    "172.27.",
    "172.28.",
    "172.29.",
    "172.30.",
    "172.31.",
    "192.168.",
    "169.254.",
    "fc00:",
    "fd",
)


@dataclass
class ScanConfig:
    safety: SafetyDefaults = field(default_factory=SafetyDefaults.default)
    scope: ScopeConfig = field(default_factory=ScopeConfig.with_defaults)
    authorized: bool = False
