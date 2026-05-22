# hermes-cognition

Hermes Agent plugin — **CogniCore** (54-feature dev orchestrator, self-contained).

- **What we build:** [../../docs/VISION.md](../../docs/VISION.md)  
- **Quick start:** [../../docs/GETTING_STARTED.md](../../docs/GETTING_STARTED.md)

## Install

Windows (PowerShell):

```powershell
.\scripts\install-hermes-cognition.ps1
```

Linux / macOS / WSL:

```bash
bash scripts/install-hermes-cognition.sh
```

Enable in `~/.hermes/config.yaml` (or `%LOCALAPPDATA%\hermes\config.yaml`):

```yaml
plugins:
  enabled:
    - cognition
cognition:
  enabled: true
  data_dir: auto
```

## Project setup

```bash
cd your-project
hermes-cognition init
hermes-cognition plan "Build my application"    # goal-driven plan, not hardcoded
hermes-cognition status --detailed              # see phases
hermes -t terminal,file,web
```

See [docs/GETTING_STARTED.md](../../docs/GETTING_STARTED.md) and [docs/VISION.md](../../docs/VISION.md).
