"""CLI for XSS Finder — Phase 01 safety controls."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from xss_finder.config import SafetyDefaults, ScanConfig, ScopeConfig
from xss_finder.scanner import result_to_json, scan_targets


def main() -> None:
    raise SystemExit(run())


def run(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Authorized reflected XSS scanner")
    sub = p.add_subparsers(dest="cmd", required=True)

    scan = sub.add_parser("scan", help="Scan URL(s)")
    scan.add_argument("url", nargs="?", help="Single target URL")
    scan.add_argument("-f", "--file", help="File with one URL per line")
    scan.add_argument("--json", action="store_true")
    scan.add_argument(
        "--i-agree",
        action="store_true",
        help="Confirm you have written authorization to test targets",
    )
    scan.add_argument("--allow-host", action="append", default=[], help="Allowed host (repeatable)")
    scan.add_argument("--deny-host", action="append", default=[], help="Extra denied host")
    scan.add_argument("--allow-path", action="append", default=[], help="Allowed path prefix")
    scan.add_argument("--rate-limit", type=float, default=0.5, help="Max requests per second")
    scan.add_argument("--max-params", type=int, default=20)
    scan.add_argument("--max-payloads", type=int, default=30)
    scan.add_argument("--timeout", type=float, default=15.0)
    scan.add_argument("--follow-redirects", action="store_true", default=False)
    scan.add_argument("-k", "--insecure", action="store_true")

    args = p.parse_args(argv)
    if args.cmd != "scan":
        return 1

    cfg = ScanConfig(
        authorized=bool(args.i_agree),
        safety=SafetyDefaults(
            rate_limit_rps=args.rate_limit,
            max_params=args.max_params,
            max_payloads=args.max_payloads,
            timeout_sec=args.timeout,
            follow_redirects=args.follow_redirects,
        ),
        scope=ScopeConfig(
            allowed_hosts=args.allow_host,
            denied_hosts=args.deny_host,
            allowed_path_prefixes=args.allow_path,
        ),
    )

    urls: list[str] = []
    if args.url:
        urls.append(args.url)
    if args.file:
        for line in Path(args.file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    if not urls:
        print("Provide a URL or -f file", file=sys.stderr)
        return 1

    try:
        results = scan_targets(urls, cfg)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(result_to_json(results))
    else:
        for r in results:
            print(f"\n=== {r.target} === requests={r.requests}")
            for e in r.errors[:5]:
                print(f"  ! {e}")
            for f in r.findings:
                print(f"  [{f.severity}] param={f.param} payload={f.payload[:60]}...")
                print(f"      {f.evidence[:120]}")
            if not r.findings:
                print("  No reflections detected.")

    return 2 if any(r.findings for r in results) else 0


if __name__ == "__main__":
    main()
