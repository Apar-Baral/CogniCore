# Hermes + CogniCore Integration

This project ships **hermes-cognition**, a self-contained Hermes Agent plugin (54 features from [Features.txt](../Features.txt)).

## Architecture

- **Hermes** provides the agent loop, tools, gateway, and `delegate_task`.
- **hermes-cognition** provides DNA, shield, budget, bootstrap, planning, Graphify, and hooks via the built-in engine under `hermes_cognition/bundled/`.
- **CognitionEngine** is a separate repository and is **not** required.

Project data lives at:

1. **Primary:** `.cognition/` (DNA, sessions, bootstrap)
2. **Fallback:** `.hermes/cognition/` (legacy; auto-migrated on init)

Global cross-project registry: `~/.cognition/projects/`

## Install (any machine)

### Windows

```powershell
git clone https://github.com/Apar-Baral/CogniCore.git
cd CogniCore
.\scripts\install-hermes-cognition.ps1
```

### Linux / WSL

```bash
git clone https://github.com/Apar-Baral/CogniCore.git
cd CogniCore
bash scripts/install-hermes-cognition.sh
```

### Enable plugin

Edit Hermes config (`%LOCALAPPDATA%\hermes\config.yaml` or `~/.hermes/config.yaml`):

```yaml
plugins:
  enabled:
    - cognition

cognition:
  enabled: true
  data_dir: auto          # .cognition primary, .hermes/cognition fallback
  migrate_legacy: true
  shield:
    mode: medium          # low | medium | high
    block_writes: true
  budget:
    zones: true
    session_tokens: 200000
  bootstrap:
    inject_on_session_start: true
    max_tokens: 2000
  semantic_index: false   # true requires pip install cognition-engine[semantic]
  graphify:
    enabled: true
    auto_index: true              # build graph on session start if missing
    navigation_token_budget: 8000 # max tokens in file reading plan
    max_files: 400
    block_rereads: false          # set true to block read_file on 3+ prior reads
```

Restart Hermes. Verify:

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
hermes cognition doctor
```

## Per-project workflow

```bash
cd your-repo
hermes cognition init
hermes cognition plan "Build a REST API with auth"
hermes cognition start
hermes          # bootstrap injected on first turn via pre_llm_call
# ... work ...
hermes cognition end
```

Slash commands inside Hermes chat: `/cognition status`, `/cognition plan <goal>`, `/cognition end`.

## Features mapped to Hermes surfaces

| Cluster | Features | Mechanism |
|---------|----------|-----------|
| A Project brain | 1-6, 19-23, 28 | DNA tools, `on_session_*`, `pre_llm_call` bootstrap |
| B Shield | 7-12, 23 | `pre_tool_call`, `transform_tool_result` |
| C Budget | 13-18, 15, 22 | `pre_llm_call`, `post_api_request`, `transform_llm_output` |
| D Planning | 24-28 | `cognition_plan`, `cognition_impact` |
| E Visualization | 29-34 | `hermes cognition status` |
| F Learning | 35-41 | `on_session_end` → synthesizer + RL |
| G Transfer | 42-45 | `hermes cognition register-project`, `suggest-plan` |
| H Multi-agent | 46-49 | `cognition_delegate` → `delegate_task` |
| I Models | 50-54 | `cognition_recommend_model` |
| Graphify | 4, 17, 19 (extended) | `cognition_graphify_*`, `pre_llm_call` | Graph memory + token-aware navigation |

## Graphify — project graph memory and navigation

Graphify extends architecture graph (#4) with:

- **Remember:** AST-based import graph in `.cognition/graphify.json`, synced to DNA `architecture_graph`
- **Navigate:** Task-scored file plan capped by `navigation_token_budget` (BFS over imports)
- **Retrieve:** Per-file access counts; injects `<graphify_navigation>` each turn; optional `block_rereads`

```bash
hermes cognition graphify index
hermes cognition graphify navigate "implement feature X"
hermes cognition graphify status
```

Agent tools: `cognition_graphify_index`, `cognition_graphify_navigate`, `cognition_graphify_status`.

## Optional semantic index

```bash
hermes-agent-venv/bin/pip install "cognition-engine[semantic]"
```

Then set `cognition.semantic_index: true` and run `cognition_index`.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Plugin not listed | Add `cognition` under `plugins.enabled` |
| `cognition-engine not installed` | Set `COGNITION_ENGINE_PATH` and re-run install script |
| No bootstrap inject | Run `hermes cognition init` + `start`; ensure `bootstrap.inject_on_session_start` |
| Shield blocks valid code | Lower `shield.mode` to `low` or run `cognition_index` |

## Dogfood example

See [examples/hermes-dogfood](../examples/hermes-dogfood/).
