"""HTTP scanner with rate limits and reflection detection."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

from xss_finder.config import ScanConfig
from xss_finder.payloads import CANARY, generate_payloads
from xss_finder.scope import ScopeGuard


@dataclass
class Finding:
    url: str
    param: str
    payload: str
    evidence: str
    severity: str


@dataclass
class ScanResult:
    target: str
    findings: list[Finding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    requests: int = 0


class _RateLimiter:
    def __init__(self, rps: float) -> None:
        self._min_interval = 1.0 / max(0.1, rps)
        self._last = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        delta = now - self._last
        if delta < self._min_interval:
            time.sleep(self._min_interval - delta)
        self._last = time.monotonic()


def scan_targets(urls: list[str], config: ScanConfig) -> list[ScanResult]:
    guard = ScopeGuard(config)
    auth = guard.check_authorization()
    if not auth.ok:
        raise PermissionError(auth.reason)
    ok_urls, errs = guard.filter_urls(urls)
    results: list[ScanResult] = []
    for url in ok_urls:
        r = ScanResult(target=url)
        r.errors.extend(errs)
        try:
            _scan_one(url, config, guard, r)
        except Exception as exc:
            r.errors.append(str(exc))
        results.append(r)
    return results


def _scan_one(url: str, config: ScanConfig, guard: ScopeGuard, result: ScanResult) -> None:
    limiter = _RateLimiter(config.safety.rate_limit_rps)
    opener = _build_opener(config)
    _, html = _fetch(opener, url, config, limiter)
    result.requests += 1
    points = _discover_params(url, html, config)
    points = points[: config.safety.max_params]
    payloads = generate_payloads(max_count=config.safety.max_payloads)
    for point in points:
        for payload in payloads:
            check = guard.validate_url(point["url"])
            if not check.ok:
                result.errors.append(check.reason)
                continue
            limiter.wait()
            try:
                inj_url = _inject_param(point["url"], point["param"], payload)
            except ValueError as exc:
                result.errors.append(str(exc))
                continue
            try:
                _, body = _fetch(opener, inj_url, config, limiter)
                result.requests += 1
                if CANARY in body or payload[:40] in body:
                    result.findings.append(
                        Finding(
                            url=point["url"],
                            param=point["param"],
                            payload=payload,
                            evidence=_snippet(body, CANARY if CANARY in body else payload[:20]),
                            severity="high" if "<script" in body.lower() else "medium",
                        )
                    )
                    break
            except Exception as exc:
                result.errors.append(f"{point['param']}: {exc}")


def _build_opener(config: ScanConfig) -> urllib.request.OpenerDirector:
    if config.safety.follow_redirects:
        return urllib.request.build_opener()
    ctx = ssl.create_default_context()
    return urllib.request.build_opener(urllib.request.HTTPHandler(), urllib.request.HTTPSHandler(context=ctx))


def _inject_param(url: str, param: str, value: str) -> str:
    parts = urlparse(url)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    q[param] = value
    return urlunparse(parts._replace(query=urlencode(q, doseq=True)))


def _fetch(
    opener: urllib.request.OpenerDirector,
    url: str,
    config: ScanConfig,
    limiter: _RateLimiter,
) -> tuple[int, str]:
    limiter.wait()
    handlers: list[Any] = []
    if not config.safety.follow_redirects:

        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl=None):
                return None

        handlers.append(_NoRedirect)
    handlers.append(urllib.request.HTTPSHandler())
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers={"User-Agent": "XSS-Finder/0.1 (authorized-test)"})
    with opener.open(req, timeout=config.safety.timeout_sec) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.status, resp.read().decode(charset, errors="replace")


def _discover_params(url: str, html: str, config: ScanConfig) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    parts = urlparse(url)
    for k, _ in parse_qsl(parts.query, keep_blank_values=True):
        key = (url, k)
        if key not in seen:
            seen.add(key)
            out.append({"url": url, "param": k, "method": "GET"})
    if not out:
        for name in ("q", "search", "id", "test"):
            out.append({"url": url, "param": name, "method": "GET"})
    return out


def _snippet(text: str, needle: str, radius: int = 60) -> str:
    i = text.find(needle)
    if i < 0:
        return ""
    return text[max(0, i - radius) : i + len(needle) + radius].replace("\n", " ")


def result_to_json(results: list[ScanResult]) -> str:
    payload = []
    for r in results:
        payload.append(
            {
                "target": r.target,
                "requests": r.requests,
                "findings": [f.__dict__ for f in r.findings],
                "errors": r.errors,
            }
        )
    return json.dumps(payload, indent=2)
