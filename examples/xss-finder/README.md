# XSS Finder (example)

Authorized reflected XSS CLI with **Phase 01 — scope & safety controls**.

## Legal

Only scan systems you own or have **written permission** to test.

## Install

```bash
cd examples/xss-finder
pip install -e .
```

## Phase 01 features

- **Denylist** — blocks localhost, private IPs, link-local by default
- **Allow-host** — optional whitelist (`--allow-host`)
- **Rate limit** — default `0.5` req/s
- **Safe defaults** — `max_params=20`, `follow_redirects=false`
- **Authorization** — requires `--i-agree`

## Usage

```bash
xss-finder scan 'https://testphp.vulnweb.com/search.php?test=query' \
  --i-agree \
  --allow-host testphp.vulnweb.com

xss-finder scan -f urls.txt --i-agree --json
```

## Modules

| File | Role |
|------|------|
| `config.py` | `SafetyDefaults`, `ScopeConfig`, `ScanConfig` |
| `scope.py` | `ScopeGuard` — URL validation, denylist |
| `scanner.py` | HTTP scan + reflection checks |
| `payloads.py` | Payload list |
| `cli.py` | Arguments and `--i-agree` |

## Build with CogniCore + Hermes

```bash
cd ~/projects/xss-finder
hermes-cognition init
hermes-cognition plan "XSS scanner phases"
hermes -t terminal,file,web
```

Write **one file per message** to avoid Hermes output truncation.
