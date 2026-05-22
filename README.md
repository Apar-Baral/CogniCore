# CogniCore

**CogniCore** turns [Hermes Agent](https://hermes-agent.nousresearch.com/) into a development orchestrator with persistent project memory, hallucination prevention, budget control, session continuity, and **Graphify** — a project graph for token-optimized navigation.

Built by **Apar Baral** ([@Apar-Baral](https://github.com/Apar-Baral))

[![Hermes Plugin](https://img.shields.io/badge/Hermes-Agent%20Plugin-blue)](https://hermes-agent.nousresearch.com/docs/user-guide/features/plugins)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What you get

| Capability | Description |
|------------|-------------|
| **Project DNA** | Phases, sub-tasks, architecture graph, avoid registry — survives across sessions |
| **Shield** | Validates imports and code before writes; blocks hallucinated APIs |
| **Budget zones** | GREEN → YELLOW → RED → WRAP_UP → EXHAUSTED with 90% handoff |
| **Bootstrap** | Injects structured context each session (~2000 tokens, tiered) |
| **Graphify** | Remembers file/import graph; navigates by task to save tokens |
| **Planning** | Auto phase plans, dependency order, impact analysis |
| **Multi-agent** | Role-based `delegate_task` (architect, backend, security, …) |

Full feature map: [Features.txt](Features.txt) (54 capabilities). Deep integration guide: [docs/INTEGRATION.md](docs/INTEGRATION.md).

---

## Architecture

```
Hermes Agent (CLI / Gateway)
        │
        ▼
  hermes-cognition plugin  ◄── CogniCore (this repo)
        │
        ▼
  cognition-engine library ◄── https://github.com/Apar-Baral/CognitionEngine
        │
        ▼
  .cognition/  (per project)  +  ~/.cognition/  (global registry)
```

---

## Prerequisites

1. **Hermes Agent** installed ([install guide](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart))
2. **Python 3.11+** (Hermes ships its own venv)
3. **cognition-engine** — clone sibling repo or set `COGNITION_ENGINE_PATH`:

```bash
git clone https://github.com/Apar-Baral/CognitionEngine.git
```

---

## Quick install

### Windows (native)

```powershell
git clone https://github.com/Apar-Baral/CogniCore.git
cd CogniCore

# Point to your Cognition Engine checkout
$env:COGNITION_ENGINE_PATH = "C:\path\to\CognitionEngine\packages\cognition-engine"

.\scripts\install-hermes-cognition.ps1
```

### Linux / VMware guest / WSL

```bash
git clone https://github.com/Apar-Baral/CogniCore.git
cd CogniCore

export COGNITION_ENGINE_PATH="$HOME/CognitionEngine/packages/cognition-engine"
bash scripts/install-hermes-cognition.sh
```

### Enable the plugin

Copy [config/cognition.example.yaml](config/cognition.example.yaml) into your Hermes config:

| OS | Config file |
|----|-------------|
| Windows | `%LOCALAPPDATA%\hermes\config.yaml` |
| Linux / VMware | `~/.hermes/config.yaml` |

Add under `plugins.enabled`: `cognition`, and merge the `cognition:` block.

Verify:

```bash
hermes cognition doctor
HERMES_PLUGINS_DEBUG=1 hermes plugins list   # should show cognition, 14 tools
```

---

## Setup: Windows (step by step)

1. **Install Hermes** (if not already):

   ```powershell
   iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
   ```

2. **Clone repos**:

   ```powershell
   cd $HOME\Projects
   git clone https://github.com/Apar-Baral/CogniCore.git
   git clone https://github.com/Apar-Baral/CognitionEngine.git
   ```

3. **Install CogniCore into Hermes venv**:

   ```powershell
   cd CogniCore
   $env:COGNITION_ENGINE_PATH = "$HOME\Projects\CognitionEngine\packages\cognition-engine"
   .\scripts\install-hermes-cognition.ps1
   ```

4. **Configure** — edit `%LOCALAPPDATA%\hermes\config.yaml` (see [config/cognition.example.yaml](config/cognition.example.yaml)).

5. **Initialize a project**:

   ```powershell
   cd your-app-repo
   hermes cognition init
   hermes cognition plan "Build my application with auth and API"
   hermes cognition graphify index
   hermes
   ```

---

## Setup: VMware Linux guest (step by step)

Use this when Hermes runs inside a **Linux VM** (Ubuntu/Debian/Kali) on VMware Workstation/Fusion.

1. **VM basics**
   - Guest: Ubuntu 22.04+ or Kali (network NAT or bridged for API keys / git)
   - RAM: 8 GB+ recommended if using semantic index (Chroma)
   - Shared folder (optional): map host project into `/mnt/hgfs/...`

2. **Install Hermes in the guest**:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
   source ~/.bashrc
   hermes --version
   ```

3. **Clone CogniCore + Cognition Engine**:

   ```bash
   mkdir -p ~/dev && cd ~/dev
   git clone https://github.com/Apar-Baral/CogniCore.git
   git clone https://github.com/Apar-Baral/CognitionEngine.git
   ```

4. **Install plugin**:

   ```bash
   cd ~/dev/CogniCore
   export COGNITION_ENGINE_PATH="$HOME/dev/CognitionEngine/packages/cognition-engine"
   bash scripts/install-hermes-cognition.sh
   ```

5. **Configure** — `nano ~/.hermes/config.yaml` and merge [config/cognition.example.yaml](config/cognition.example.yaml).

6. **Work on a project** (host-shared or cloned in VM):

   ```bash
   cd /path/to/your/project
   hermes cognition init
   hermes cognition graphify index
   hermes cognition graphify navigate "first task for this session"
   hermes
   ```

**Tip:** If the project lives on the Windows host, clone or sync it into the VM (git, shared folder, or `scp`) so `.cognition/` and Hermes `cwd` stay on a Linux path.

---

## Daily usage

| Command | Purpose |
|---------|---------|
| `hermes cognition init` | Create `.cognition/dna.json` |
| `hermes cognition plan "<goal>"` | Generate phased roadmap |
| `hermes cognition start` | Start CE session + bootstrap file |
| `hermes cognition graphify index` | Build project graph |
| `hermes cognition graphify navigate "<task>"` | Token-optimized file plan |
| `hermes cognition status` | Phase progress |
| `hermes cognition end` | Close session, insights, RL |
| `hermes cognition doctor` | Check install health |

**Inside Hermes chat:** `/cognition status`, `/cognition plan <goal>`, `/cognition end`

**Agent tools:** `cognition_init`, `cognition_plan`, `cognition_validate`, `cognition_graphify_navigate`, `cognition_delegate`, …

---

## Graphify (token optimization)

Graphify builds an import/symbol graph and injects a **file reading plan** each turn so the model reads fewer, more relevant files.

```bash
hermes cognition graphify index
hermes cognition graphify navigate "implement OAuth login"
```

Set `cognition.graphify.block_rereads: true` in config to block `read_file` on files already read 3+ times.

---

## Repository layout

```
CogniCore/
├── README.md                 # This page
├── Features.txt              # 54-feature specification
├── config/
│   └── cognition.example.yaml
├── packages/
│   └── hermes-cognition/     # Hermes plugin (pip installable)
├── scripts/
│   ├── install-hermes-cognition.ps1
│   └── install-hermes-cognition.sh
├── docs/
│   └── INTEGRATION.md
└── examples/
    └── hermes-dogfood/
```

---

## Related projects

| Repo | Role |
|------|------|
| [CogniCore](https://github.com/Apar-Baral/CogniCore) | Hermes plugin (this repo) |
| [CognitionEngine](https://github.com/Apar-Baral/CognitionEngine) | Core library (`cognition-engine` pip package) |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | Upstream agent |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `cognition` not in `hermes plugins list` | Add `cognition` under `plugins.enabled` in `config.yaml` |
| `cognition-engine not installed` | Set `COGNITION_ENGINE_PATH` and re-run install script |
| `hermes cognition` unknown | Re-run install script; restart terminal |
| No bootstrap injected | Run `hermes cognition init` + `start`; check `bootstrap.inject_on_session_start` |
| Graphify empty | Run `hermes cognition graphify index` |

---

## Author

**Apar Baral** — [@Apar-Baral](https://github.com/Apar-Baral) · dedsecaparb@gmail.com

Contributions and issues welcome on [GitHub Issues](https://github.com/Apar-Baral/CogniCore/issues).
