<p align="center">
  <img src="docs/assets/og-banner.png" alt="CogniCore — Hermes development orchestrator plugin" width="100%"/>
</p>

<h1 align="center">CogniCore</h1>

<p align="center">
  <strong>Hermes Agent plugin — project memory, shield, budget, Graphify</strong><br/>
  Self-contained · No separate engine repo required
</p>

<p align="center">
  <a href="https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins"><img src="https://img.shields.io/badge/Hermes-Agent%20Plugin-3b82f6?style=for-the-badge" alt="Hermes Plugin"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-22c55e?style=for-the-badge" alt="Python 3.11+"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge" alt="MIT"/></a>
</p>

<p align="center">
  <a href="docs/VISION.md"><b>What We Build</b></a> ·
  <a href="docs/GETTING_STARTED.md"><b>Start Here (5 min)</b></a> ·
  <a href="docs/USER_GUIDE.md"><b>User Guide</b></a> ·
  <a href="docs/PLUGIN.md"><b>Plugin Details</b></a> ·
  <a href="docs/FEATURE_MAP.md"><b>54 Features</b></a>
</p>

<p align="center">
  Built by <a href="https://github.com/Apar-Baral"><b>Apar Baral</b></a>
</p>

---

## What we want to build

**CogniCore helps Hermes remember your project, plan from your goal, and code safely** — not replace the coder.

| You do | CogniCore does | Hermes does |
|--------|----------------|-------------|
| `plan "Build my API with auth"` | Writes phases to `.cognition/` | — |
| `status --detailed` | Shows your roadmap | — |
| `hermes -t terminal,file,web` | Bootstrap, shield, budget, Graphify | Writes and runs code |

Plans are **not hardcoded**: they come from **your goal string**.  
The XSS “Phase 01” text in `examples/xss-finder` is only for that sample app.

**New here?** Read **[docs/VISION.md](docs/VISION.md)** and **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)**.

---

## What is CogniCore?

**CogniCore** is a [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin (`hermes-cognition`). It turns Hermes into a **development orchestrator** with:

| Capability | What it does |
|------------|----------------|
| **Project DNA** | Phases, sub-tasks, goals — stored in `.cognition/` |
| **Shield** | Blocks suspicious imports before file writes |
| **Budget zones** | GREEN → YELLOW → RED → 90% wrap-up |
| **Bootstrap** | Injects mission context each session |
| **Graphify** | File graph + token-smart navigation |
| **Planning** | `plan` command generates phased roadmaps |
| **Multi-agent** | `cognition_delegate` with roles |

All logic ships **inside this repo** (`packages/hermes-cognition/`).  
**CognitionEngine** is a **separate project** — not bundled or required here.

---

## Feature map (54 capabilities)

**[Open the full feature table → docs/FEATURE_MAP.md](docs/FEATURE_MAP.md)**

<p align="center">
  <a href="docs/FEATURE_MAP.md">
    <img src="docs/assets/cognicore-architecture.svg" alt="CogniCore architecture" width="700"/>
  </a>
  <br/>
  <sub>Click diagram for feature table · SVG requires GitHub render — use FEATURE_MAP.md if image does not load</sub>
</p>

---

## Architecture

```mermaid
flowchart TB
  U[You] --> H[Hermes Agent]
  H --> P[hermes-cognition plugin]
  P --> D[".cognition/ per project"]
  P --> HK[Hooks: shield · budget · bootstrap]
  P --> TL[14 cognition tools]
  P --> G[Graphify module]
```

Details: **[docs/PLUGIN.md](docs/PLUGIN.md)**

---

## Quick install

### Linux / Kali

```bash
git clone https://github.com/Apar-Baral/CogniCore.git
cd CogniCore
bash scripts/install-hermes-cognition.sh
export PATH="$HOME/.hermes/hermes-agent/venv/bin:$PATH"
hermes-cognition doctor
```

### Windows

```powershell
git clone https://github.com/Apar-Baral/CogniCore.git
cd CogniCore
.\scripts\install-hermes-cognition.ps1
hermes-cognition doctor
```

Merge [config/cognition.example.yaml](config/cognition.example.yaml) into Hermes config if needed.

---

## How to use (daily workflow)

```bash
cd your-project
hermes-cognition init
hermes-cognition plan "Build my application"
hermes-cognition graphify index
hermes -t terminal,file,web
```

| Command | Purpose |
|---------|---------|
| `hermes-cognition doctor` | Health check |
| `hermes-cognition init` | Create `.cognition/` |
| `hermes-cognition plan "..."` | Phase roadmap |
| `hermes-cognition status` | Progress |
| `hermes-cognition graphify index` | Build file graph |
| `hermes` | Agent builds code (with file + terminal tools) |

**Important:** Use `hermes` or `hermes -t terminal,file,web` — **not** `hermes -t cognition` only.

Slash commands in chat: `/cognition status`, `/cognition plan …`, `/cognition end`

---

## Example project (not the core product)

**[examples/xss-finder/](examples/xss-finder/)** — sample authorized XSS CLI used to demo CogniCore on a security tool.  
Your real workflow: use CogniCore on **your own repo** with **your own** `plan "..."` goal.

```bash
cd examples/xss-finder && pip install -e .
xss-finder scan 'https://testphp.vulnweb.com/search.php?test=1' --i-agree --allow-host testphp.vulnweb.com
```

---

## Documentation

| Doc | Content |
|-----|---------|
| [PROJECT.md](PROJECT.md) | One-page summary for GitHub visitors |
| [docs/VISION.md](docs/VISION.md) | **Mission, goals, what we are / are not building** |
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | **5-minute onboarding** |
| [docs/PLUGIN.md](docs/PLUGIN.md) | Detailed plugin behavior (tools, hooks, data) |
| [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | Step-by-step usage |
| [docs/FEATURE_MAP.md](docs/FEATURE_MAP.md) | All 54 features (table) |
| [docs/TESTING.md](docs/TESTING.md) | Test checklist |
| [docs/INTEGRATION.md](docs/INTEGRATION.md) | Config reference |
| [docs/SOCIAL_PREVIEW.md](docs/SOCIAL_PREVIEW.md) | GitHub social preview image |
| [docs/HERMES_TIPS.md](docs/HERMES_TIPS.md) | Avoid Hermes truncation errors |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `hermes-cognition` not found | `export PATH="$HOME/.hermes/hermes-agent/venv/bin:$PATH"` |
| Feature diagram not opening | Use [FEATURE_MAP.md](docs/FEATURE_MAP.md) (markdown table) |
| Agent cannot write files | Do not use `-t cognition` only |
| Hermes truncated writes | One file per turn — see [HERMES_TIPS.md](docs/HERMES_TIPS.md) |
| YAML config error | Fix `~/.hermes/config.yaml` indentation |

---

## Author

**Apar Baral** — [@Apar-Baral](https://github.com/Apar-Baral)

Issues: [GitHub Issues](https://github.com/Apar-Baral/CogniCore/issues)
