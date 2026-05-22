# Install hermes-cognition into the Hermes Agent venv (Windows).
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
Write-Host "==> Hermes python: $VenvPython"

& $VenvPython -m pip install -U pip wheel setuptools
Write-Host "==> Installing hermes-cognition (CogniCore — self-contained)"
& $VenvPython -m pip install -e $HermesPlugin

$HermesBin = Split-Path $VenvPython -Parent
$Cli = Join-Path $HermesBin "hermes-cognition.exe"
if (Test-Path $Cli) { & $Cli doctor } else {
    & $VenvPython -c "from hermes_cognition.cli_commands import _doctor; raise SystemExit(_doctor())"
}

$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:USERPROFILE ".hermes" }
$UserPluginDir = Join-Path $HermesHome "plugins\cognition"
New-Item -ItemType Directory -Force -Path $UserPluginDir | Out-Null
Copy-Item (Join-Path $HermesPlugin "plugin.yaml") (Join-Path $UserPluginDir "plugin.yaml") -Force
Copy-Item (Join-Path $HermesPlugin "hermes_user_plugin\__init__.py") (Join-Path $UserPluginDir "__init__.py") -Force

$ExampleYaml = Join-Path $RepoRoot "config\cognition.example.yaml"
& $VenvPython -c @"
from pathlib import Path
cfg_path = Path.home() / '.hermes' / 'config.yaml'
example = Path(r'$ExampleYaml')
text = cfg_path.read_text(encoding='utf-8') if cfg_path.is_file() else ''
if 'cognition:' in text:
    print('config already has cognition')
else:
    lines = example.read_text(encoding='utf-8').splitlines()
    block = '\n'.join(lines[7:]) if 'plugins:' in text else example.read_text(encoding='utf-8')
    with cfg_path.open('a', encoding='utf-8') as f:
        f.write('\n\n# --- CogniCore ---\n' + block)
    print('Updated', cfg_path)
"@

Write-Host ""
Write-Host "Done. CLI folder: $HermesBin"
Write-Host "  $(Join-Path $HermesBin 'hermes-cognition.exe')"
