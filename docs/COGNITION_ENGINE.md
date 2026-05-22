# Cognition Engine integration

CogniCore works **with or without** the separate [CognitionEngine](https://github.com/Apar-Baral/CognitionEngine) repository.

## Two engines, one plugin

| Mode | Source | When to use |
|------|--------|-------------|
| **Bundled** (default fallback) | `hermes_cognition/bundled/` inside CogniCore | Kali/VMware, quick start, CE repo not ready |
| **External** | CognitionEngine git + `COGNITION_ENGINE_PATH` | Full 54-feature depth as CE matures |

Set in config or environment:

```yaml
cognition:
  engine_mode: auto   # auto | bundled | external
```

```bash
export COGNITION_ENGINE_MODE=auto    # default
export COGNITION_ENGINE_MODE=bundled # force built-in only
export COGNITION_ENGINE_PATH="$HOME/CognitionEngine/packages/cognition-engine"
```

## What ships inside CogniCore (bundled)

Always available after `pip install hermes-cognition`:

| Area | Features covered |
|------|------------------|
| DNA & phases | 1–3, 28 (init, plan, status, phase updates) |
| Avoid registry | 6, 23 |
| Bootstrap | 19–21 (text bootstrap, bootstrap.md) |
| Shield | 7–12 (AST import checks) |
| Budget | 13–18 (zones, wrap-up messaging) |
| Planning | 24 (heuristic phase generator) |
| Impact | 27 (heuristic when CE missing) |
| Models | 50–54 (tier routing stub) |
| Graphify | Full implementation in plugin (not in CE) |

## What needs external CognitionEngine

Install optional extra:

```bash
pip install "hermes-cognition[full]"
# or editable:
pip install -e "$COGNITION_ENGINE_PATH"
```

| Area | External-only today |
|------|---------------------|
| Rich terminal viz | 29–34 (Rich progress maps) |
| Semantic truth DB | 7 Chroma index |
| Deep validation stages | 9–10 stage 2–3 |
| RL optimizer | 38–41 full Q-learning |
| Transfer / similarity | 42–45 embeddings |
| Advanced planner | 25–26 Dijkstra / deviation integrator |

As CognitionEngine matures, features move from bundled stubs → external implementation automatically when `engine_mode: auto` and CE is on `PYTHONPATH`.

## Roadmap: monorepo merge

1. **Now** — bundled engine in CogniCore; external CE optional  
2. **Next** — vendor `packages/cognition-engine` into CogniCore monorepo  
3. **Later** — single pip package `cognicore[full]` with no separate clone  

## Verify which engine is active

```bash
hermes-cognition doctor
```

Look for:

```text
OK: active engine: cognicore-bundled
# or
OK: active engine: external
```
