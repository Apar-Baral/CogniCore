# What the CogniCore plugin does (detailed)

**CogniCore** = the `hermes-cognition` Hermes plugin in `packages/hermes-cognition/`.  
It is **self-contained** (built-in cognition logic). It does **not** require the separate CognitionEngine repository.

---

## Role in the stack

```text
You → Hermes Agent → hermes-cognition plugin → .cognition/ in your repo
```

Hermes runs the LLM and tools (`write_file`, terminal, web). The plugin adds **project memory**, **safety**, **budget discipline**, and **navigation** around that loop.

---

## 14 agent tools

| Tool | What it does |
|------|----------------|
| `cognition_init` | Creates `.cognition/dna.json`, scans project language/framework |
| `cognition_plan` | Builds phased roadmap from a goal string |
| `cognition_status` | Returns phase progress (compact or detailed map) |
| `cognition_phase_update` | Sets phase/sub-task status (state machine) |
| `cognition_validate` | Validates code snippet (imports/syntax) before merge |
| `cognition_index` | Indexes codebase for shield/architecture |
| `cognition_record_avoid` | Logs hallucination or failed approach to avoid registry |
| `cognition_budget` | Reports token zone (green/yellow/red) and usage |
| `cognition_impact` | Estimates disruption of adding a feature |
| `cognition_delegate` | Spawns Hermes sub-agent with role (backend, security, …) |
| `cognition_recommend_model` | Suggests economy/standard/premium tier |
| `cognition_graphify_index` | Builds `graphify.json` import/file graph |
| `cognition_graphify_navigate` | Task → ranked file reading plan (saves tokens) |
| `cognition_graphify_status` | Graph stats and file access counts |

---

## 8 hooks (automatic)

| Hook | When | Effect |
|------|------|--------|
| `on_session_start` | Session begins | Start CE session, optional auto Graphify index |
| `on_session_end` | Session ends | Flush DNA, session summary |
| `pre_tool_call` | Before each tool | **Shield** blocks bad writes; Graphify can block re-reads |
| `post_tool_call` | After tool | Track file reads for Graphify |
| `transform_tool_result` | Tool output | Shield auto-correct metadata |
| `pre_llm_call` | Before LLM | Inject **bootstrap** + **budget** + **graphify navigation** |
| `post_api_request` | After API call | Count tokens toward budget |
| `transform_llm_output` | Model output | Append wrap-up message at 90% budget |

You do not call hooks manually; they run when `cognition` is in `plugins.enabled`.

---

## Graphify

Separate module under `hermes_cognition/graphify/`:

- Parses Python (and project files) into a graph
- On each turn, injects which files to read for the current task
- Reduces token waste from blind repository walks

Commands: `hermes-cognition graphify index|navigate|status`

---

## Data on disk

| Path | Content |
|------|---------|
| `<project>/.cognition/dna.json` | Master plan, phases, avoid registry |
| `<project>/.cognition/bootstrap.md` | Last bootstrap text |
| `<project>/.cognition/graphify.json` | File/import graph |
| `<project>/.cognition/session_state.json` | Active session budget |
| `~/.cognition/projects/` | Optional global project registry |

---

## CLI (`hermes-cognition`)

Installed into Hermes venv: `~/.hermes/hermes-agent/venv/bin/hermes-cognition`

Same operations as tools, for terminals and scripts. Use if `hermes cognition` subcommand is unavailable.

---

## What Hermes must have for building code

```bash
hermes -t terminal,file,web   # correct
hermes -t cognition           # wrong — planning tools only, no write_file
```

---

## Related repos

| Repo | Relationship |
|------|----------------|
| [CogniCore](https://github.com/Apar-Baral/CogniCore) | This plugin (use this) |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Host agent |
| CognitionEngine | **Separate project** — not required for CogniCore |

See [USER_GUIDE.md](USER_GUIDE.md) for step-by-step usage.
