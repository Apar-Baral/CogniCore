# CogniCore — How to Use Every Feature

Step-by-step guide for **Hermes Agent + CogniCore** (self-contained plugin).  
Spec reference: [Features.txt](../Features.txt) (54 features).  
Plugin details: [PLUGIN.md](PLUGIN.md).

---

## Before you start

| Requirement | Check |
|-------------|--------|
| Hermes installed | `hermes --version` |
| CogniCore installed | `bash scripts/install-hermes-cognition.sh` |
| Engine | `hermes-cognition doctor` → `cognicore-bundled` |
| Plugin enabled | `hermes plugins list` → cognition **enabled** |
| CLI on PATH | `~/.hermes/hermes-agent/venv/bin/hermes-cognition` |

**Use `hermes-cognition`** when `hermes cognition` is not in `hermes --help`.

**Build code with Hermes:** run `hermes` or `hermes -t terminal,file,web` — **not** `hermes -t cognition` only (that disables file/terminal tools).

---

## 1. Install & enable

### Windows

```powershell
git clone https://github.com/Apar-Baral/CogniCore.git
cd CogniCore
.\scripts\install-hermes-cognition.ps1
```

### Linux / Kali / VMware

```bash
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
  git clone https://github.com/Apar-Baral/CogniCore.git
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
  git clone https://github.com/Apar-Baral/CognitionEngine.git

cd CogniCore
export COGNITION_ENGINE_PATH="$HOME/CognitionEngine/packages/cognition-engine"
bash scripts/install-hermes-cognition.sh
export PATH="$HOME/.hermes/hermes-agent/venv/bin:$PATH"
```

Merge [config/cognition.example.yaml](../config/cognition.example.yaml) into `~/.hermes/config.yaml` if the installer did not.

---

## 2. Per-project workflow (core)

```bash
cd your-project-repo
hermes-cognition init
hermes-cognition plan "Your project goal in one sentence"
hermes-cognition graphify index
hermes-cognition start "optional task name"
hermes          # or: hermes -t terminal,file,web
hermes-cognition end
hermes-cognition status
```

| Step | Feature cluster | What happens |
|------|-----------------|--------------|
| `init` | A (1, 28) | Creates `.cognition/`, DNA, project scan |
| `plan` | D (24–28) | Phases + sub-tasks in DNA |
| `graphify index` | Graphify | `.cognition/graphify.json` |
| `start` | A (19–21) | CE session + bootstrap file |
| `hermes` | Hooks | Bootstrap inject, shield, budget run automatically |
| `end` | F (35–41) | Session insights, DNA update |

---

## 3. CLI command reference

| Command | Purpose |
|---------|---------|
| `hermes-cognition doctor` | Verify CE + paths |
| `hermes-cognition init [--reinit]` | Initialize `.cognition/` |
| `hermes-cognition plan "<goal>"` | Master plan / phases |
| `hermes-cognition start [task]` | Start session |
| `hermes-cognition end` | End session |
| `hermes-cognition status [--detailed] [--phase=ID]` | Progress |
| `hermes-cognition graphify index` | Build project graph |
| `hermes-cognition graphify navigate "<task>"` | File reading plan |
| `hermes-cognition graphify status` | Graph stats |
| `hermes-cognition register-project` | Add to `~/.cognition/projects/` |
| `hermes-cognition suggest-plan "<goal>"` | Hints from past projects |

### Slash commands (inside Hermes chat)

| Slash | Same as |
|-------|---------|
| `/cognition status` | status |
| `/cognition init` | init |
| `/cognition plan <goal>` | plan |
| `/cognition end` | end |

---

## 4. Agent tools (14)

Ask Hermes to call these, or they are used automatically during work.

| Tool | Features | Example use |
|------|----------|-------------|
| `cognition_init` | 1, 28 | First-time project setup |
| `cognition_plan` | 24 | New roadmap from goal |
| `cognition_status` | 2, 3, 29–34 | Where am I in phases? |
| `cognition_phase_update` | 2, 3 | Mark phase IN_PROGRESS / COMPLETED |
| `cognition_validate` | 7–12 | Validate code snippet before save |
| `cognition_index` | 4, 7 | Architecture / code index |
| `cognition_record_avoid` | 6, 23 | Log mistake to avoid registry |
| `cognition_budget` | 13–18 | Current zone / usage |
| `cognition_impact` | 27 | Impact of new feature |
| `cognition_delegate` | 46–49 | Sub-agent by role |
| `cognition_recommend_model` | 50–54 | Model tier hint |
| `cognition_graphify_index` | Graphify | Rebuild graph |
| `cognition_graphify_navigate` | Graphify | Task → files |
| `cognition_graphify_status` | Graphify | Graph + access counts |

---

## 5. Hooks (automatic — no command)

| Hook | When | Features |
|------|------|----------|
| `on_session_start` | Session begins | Init, optional Graphify index |
| `on_session_end` | Session ends | 35–41 learning / persist |
| `pre_tool_call` | Before tools | 7–12 shield on writes |
| `post_tool_call` | After tools | Stats / follow-up |
| `transform_tool_result` | Tool output | Shield messages |
| `pre_llm_call` | Before LLM | 19–23 bootstrap, Graphify nav, budget context |
| `post_api_request` | After API | 13–16 token/cost tracking |
| `transform_llm_output` | LLM output | 15 wrap-up at 90% budget |

Enable in `~/.hermes/config.yaml` — see [cognition.example.yaml](../config/cognition.example.yaml).

---

## 6. Feature clusters (54) — how to trigger each

### A — Persistent project memory (#1–6, 19–23, 28)

```bash
hermes-cognition init
hermes-cognition status --detailed
cat .cognition/dna.json
```

In Hermes: `cognition_init`, `cognition_status`, `cognition_phase_update`, `cognition_record_avoid`.

### B — Shield (#7–12)

Config:

```yaml
cognition:
  shield:
    mode: syntax   # off | syntax | strict
    block_writes: false   # true only if you want hard blocks
```

In Hermes: try writing a file with `import fake_package_xyz`; or call `cognition_validate`.

### C — Budget (#13–18)

Config:

```yaml
cognition:
  budget:
    zones: false              # advisory hints; keep false for long coding sessions
    enforce_tool_blocks: false
    session_tokens: 500000
```

In Hermes: `cognition_budget`. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if Hermes stops early.

### D — Planning (#24–28)

```bash
hermes-cognition plan "Build API with auth and tests"
```

In Hermes: `cognition_plan`, `cognition_impact`.

### E — Visualization (#29–34)

```bash
hermes-cognition status --detailed
```

In Hermes: `cognition_status` with `detailed: true`.

### F — Self-learning (#35–41)

```bash
hermes-cognition start
# ... work in hermes ...
hermes-cognition end
ls .cognition/
```

### G — Cross-project transfer (#42–45)

```bash
hermes-cognition register-project
hermes-cognition suggest-plan "New Python CLI tool"
ls ~/.cognition/projects/
```

### H — Multi-agent (#46–49)

In Hermes (with **terminal,file** toolsets):

```text
Call cognition_delegate with role backend, goal "...", toolsets ["terminal","file"].
```

Roles: `architect`, `backend`, `frontend`, `security`, `test`, `docs`, `refactor`.

### I — Model routing (#50–54)

In Hermes: `cognition_recommend_model` for simple vs complex tasks.

### Graphify

```bash
hermes-cognition graphify index
hermes-cognition graphify navigate "implement feature X"
```

Config:

```yaml
cognition:
  graphify:
    enabled: true
    inject_on_llm: false    # true = navigation on every turn (heavy)
    auto_index: false       # run `hermes-cognition graphify index` manually
    navigation_token_budget: 4000
    block_rereads: false
```

---

## 7. Build a real app (e.g. security CLI)

CogniCore does **not** ship your app — Hermes builds it in **your repo**:

```bash
mkdir -p ~/projects/my-app && cd ~/projects/my-app
git init
hermes-cognition init
hermes-cognition plan "Describe your app"
hermes -t terminal,file,web
```

Prompt example:

```text
Build the app per the cognition plan. Use write_file and terminal tools.
Call cognition_phase_update as you complete phases.
```

---

## 8. Optional: semantic index

```bash
~/.hermes/hermes-agent/venv/bin/pip install "cognition-engine[semantic]"
```

Set `cognition.semantic_index: true`, then `cognition_index` in Hermes.

---

## 9. Troubleshooting

| Problem | Fix |
|---------|-----|
| `hermes-cognition` not found | Re-run install script; add venv `bin` to PATH |
| `hermes cognition` unknown | Use `hermes-cognition` CLI |
| YAML error on `hermes` | Fix `~/.hermes/config.yaml` — see [TESTING.md](TESTING.md) |
| Agent only has cognition tools | Do not use `-t cognition` only |
| `plugins enable cognition` fails | Install script registers `~/.hermes/plugins/cognition/` |
| No bootstrap | `init` + `start`; check `bootstrap.inject_on_session_start` |
| Git SSH clone error | `scripts/clone-repos-https.sh` or unset `url.git@github.com:.insteadof` |

---

## 10. More docs

| Doc | Content |
|-----|---------|
| [INTEGRATION.md](INTEGRATION.md) | Architecture & config |
| [TESTING.md](TESTING.md) | Test all features checklist |
| [Features.txt](../Features.txt) | Full 54-feature spec |

**Author:** [Apar Baral](https://github.com/Apar-Baral)
