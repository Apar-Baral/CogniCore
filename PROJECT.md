# CogniCore — project summary for contributors & users

## Mission

Make **Hermes Agent** a reliable **long-running development partner** by adding structured project memory, automatic phased planning from user goals, code guardrails, token budget discipline, and Graphify navigation.

## What users should do

1. Install the plugin into Hermes  
2. `cd` into **their application repository**  
3. `hermes-cognition init`  
4. `hermes-cognition plan "<their goal>"` — **plans are goal-driven, not hardcoded**  
5. `hermes -t terminal,file,web` to implement  
6. `hermes-cognition status --detailed` to see progress anytime  

## What this repository contains

- **Product:** `packages/hermes-cognition` (Hermes plugin)  
- **Engine:** `hermes_cognition/bundled/` (self-contained; no external repo required)  
- **Spec:** `Features.txt` (54 features)  
- **Examples:** `examples/xss-finder` (security CLI sample), `examples/hermes-dogfood`  
- **Docs:** `docs/VISION.md`, `docs/GETTING_STARTED.md`, `docs/USER_GUIDE.md`, …  

## What this repository does NOT require

- Cloning [CognitionEngine](https://github.com/Apar-Baral/CognitionEngine) — separate project, optional future alignment only  
- Building only the XSS example — that is demonstration code  
- Using `hermes -t cognition` alone — must include `terminal` and `file` toolsets to write code  

## Quick links

| Audience | Start here |
|----------|------------|
| New user | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| Vision / goals | [docs/VISION.md](docs/VISION.md) |
| Feature list | [docs/FEATURE_MAP.md](docs/FEATURE_MAP.md) |
| Install | [README.md](README.md) |

## Author

Apar Baral — [@Apar-Baral](https://github.com/Apar-Baral)
