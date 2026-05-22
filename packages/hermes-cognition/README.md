# hermes-cognition

Hermes Agent plugin integrating [Cognition Engine](https://github.com/Apar-Baral/CognitionEngine) (54-feature dev orchestrator).

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
hermes cognition init
hermes cognition plan "Build my application"
hermes
```

See [docs/INTEGRATION.md](../../docs/INTEGRATION.md) for full details.
