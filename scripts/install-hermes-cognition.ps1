# Install hermes-cognition into the Hermes Agent venv (Windows).
# Usage: .\scripts\install-hermes-cognition.ps1
# Optional: $env:COGNITION_ENGINE_PATH = "E:\Dream - Cognition Engine\packages\cognition-engine"

$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptRoot
$HermesPlugin = Join-Path $RepoRoot "packages\hermes-cognition"

$HermesExe = (Get-Command hermes -ErrorAction SilentlyContinue).Source
if (-not $HermesExe) {
    $HermesExe = Join-Path $env:LOCALAPPDATA "hermes\hermes-agent\venv\Scripts\hermes.exe"
}
if (-not (Test-Path $HermesExe)) {
    Write-Error "hermes not found. Install Hermes Agent first."
}

$VenvRoot = Split-Path (Split-Path $HermesExe -Parent) -Parent
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Error "Hermes venv python not found at $VenvPython"
}

Write-Host "==> Hermes python: $VenvPython"

$CePath = $env:COGNITION_ENGINE_PATH
if (-not $CePath) {
    $candidates = @(
        (Join-Path $RepoRoot "..\CognitionEngine\packages\cognition-engine"),
        (Join-Path $env:USERPROFILE "CognitionEngine\packages\cognition-engine"),
        "E:\Dream - Cognition Engine\packages\cognition-engine"
    )
    foreach ($c in $candidates) {
        if (Test-Path (Join-Path $c "pyproject.toml")) {
            $CePath = $c
            break
        }
    }
}
if (-not $CePath) {
    Write-Host "==> Cloning CognitionEngine (required dependency)..."
    $cloneRoot = Join-Path $env:USERPROFILE "CognitionEngine"
    if (-not (Test-Path (Join-Path $cloneRoot ".git"))) {
        git clone https://github.com/Apar-Baral/CognitionEngine.git $cloneRoot
    }
    $CePath = Join-Path $cloneRoot "packages\cognition-engine"
}

$pipCheck = & $VenvPython -m pip --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "==> Bootstrapping pip via ensurepip"
    & $VenvPython -m ensurepip --upgrade
}
& $VenvPython -m pip install -U pip wheel setuptools

if ($CePath -and (Test-Path (Join-Path $CePath "pyproject.toml"))) {
    Write-Host "==> Installing cognition-engine editable from $CePath"
    & $VenvPython -m pip install -e $CePath
} else {
    Write-Host "==> Installing cognition-engine from PyPI (if published)"
    & $VenvPython -m pip install "cognition-engine>=0.3.54"
}

Write-Host "==> Installing hermes-cognition from $HermesPlugin"
& $VenvPython -m pip install -e $HermesPlugin

Write-Host "==> Doctor"
& $VenvPython -m hermes_cognition.cli_standalone 2>$null
if ($LASTEXITCODE -ne 0) {
    & $VenvPython -c "from hermes_cognition.cli_commands import _doctor; raise SystemExit(_doctor())"
}

$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:USERPROFILE ".hermes" }
$UserPluginDir = Join-Path $HermesHome "plugins\cognition"
New-Item -ItemType Directory -Force -Path $UserPluginDir | Out-Null
Copy-Item (Join-Path $HermesPlugin "plugin.yaml") (Join-Path $UserPluginDir "plugin.yaml") -Force
Copy-Item (Join-Path $HermesPlugin "hermes_user_plugin\__init__.py") (Join-Path $UserPluginDir "__init__.py") -Force
Write-Host "==> Registered user plugin at $UserPluginDir"

& $VenvPython -c @"
import sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print('WARN: PyYAML missing; enable cognition in config manually', file=sys.stderr)
    sys.exit(0)
cfg_path = Path.home() / '.hermes' / 'config.yaml'
cfg_path.parent.mkdir(parents=True, exist_ok=True)
cfg = {}
if cfg_path.is_file():
    cfg = yaml.safe_load(cfg_path.read_text(encoding='utf-8')) or {}
if not isinstance(cfg, dict):
    cfg = {}
plugins = cfg.setdefault('plugins', {})
if not isinstance(plugins, dict):
    plugins = {}
    cfg['plugins'] = plugins
enabled = plugins.setdefault('enabled', [])
if not isinstance(enabled, list):
    enabled = []
    plugins['enabled'] = enabled
if 'cognition' not in enabled:
    enabled.append('cognition')
cog = cfg.setdefault('cognition', {})
if not isinstance(cog, dict):
    cog = {}
    cfg['cognition'] = cog
cog['enabled'] = True
cfg_path.write_text(yaml.safe_dump(cfg, default_flow_style=False, sort_keys=False), encoding='utf-8')
print(f'==> Updated {cfg_path}')
"@

Write-Host ""
Write-Host "Done. Run: hermes plugins list ; hermes cognition doctor"
