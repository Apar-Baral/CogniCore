#!/usr/bin/env bash
# Install hermes-cognition into the Hermes Agent venv (Linux/macOS/WSL).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/packages/hermes-cognition"

find_hermes_python() {
  if command -v hermes >/dev/null 2>&1; then
    local exe
    exe="$(command -v hermes)"
    local venv
    venv="$(dirname "$(dirname "$(dirname "$exe")")")"
    if [[ -x "$venv/bin/python" ]]; then
      echo "$venv/bin/python"
      return 0
    fi
  fi
  for candidate in \
    "$HOME/.hermes/hermes-agent/venv/bin/python" \
    "${HERMES_HOME:-$HOME/.hermes}/hermes-agent/venv/bin/python"; do
    if [[ -x "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

PY="$(find_hermes_python)" || { echo "ERROR: hermes venv python not found"; exit 1; }
echo "==> Hermes python: $PY"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CE_PATH="${COGNITION_ENGINE_PATH:-}"
for candidate in \
  "$REPO_ROOT/../CognitionEngine/packages/cognition-engine" \
  "$HOME/Desktop/CognitionEngine/packages/cognition-engine" \
  "$HOME/CognitionEngine/packages/cognition-engine" \
  "/mnt/e/Dream - Cognition Engine/packages/cognition-engine"; do
  if [[ -z "$CE_PATH" && -f "$candidate/pyproject.toml" ]]; then
    CE_PATH="$candidate"
  fi
done
if [[ -z "$CE_PATH" || ! -f "$CE_PATH/pyproject.toml" ]]; then
  echo "==> Cloning CognitionEngine (required dependency)..."
  CLONE_ROOT="${HOME}/CognitionEngine"
  if [[ ! -d "$CLONE_ROOT/.git" ]]; then
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
      git clone https://github.com/Apar-Baral/CognitionEngine.git "$CLONE_ROOT"
  fi
  CE_PATH="$CLONE_ROOT/packages/cognition-engine"
fi

if ! "$PY" -m pip --version >/dev/null 2>&1; then
  echo "==> Bootstrapping pip via ensurepip"
  "$PY" -m ensurepip --upgrade
fi
"$PY" -m pip install -U pip wheel setuptools

if [[ -n "$CE_PATH" && -f "$CE_PATH/pyproject.toml" ]]; then
  echo "==> Installing cognition-engine editable from $CE_PATH"
  "$PY" -m pip install -e "$CE_PATH"
else
  echo "==> Installing cognition-engine from PyPI"
  "$PY" -m pip install "cognition-engine>=0.3.54"
fi

echo "==> Installing hermes-cognition"
"$PY" -m pip install -e "$PLUGIN_DIR"

echo "==> Doctor"
"$PY" -c "from hermes_cognition.cli_commands import _doctor; raise SystemExit(_doctor())"

HERMES_PLUGINS_DIR="${HERMES_HOME:-$HOME/.hermes}/plugins"
USER_PLUGIN_DIR="$HERMES_PLUGINS_DIR/cognition"
mkdir -p "$USER_PLUGIN_DIR"
cp "$PLUGIN_DIR/plugin.yaml" "$USER_PLUGIN_DIR/plugin.yaml"
cp "$PLUGIN_DIR/hermes_user_plugin/__init__.py" "$USER_PLUGIN_DIR/__init__.py"
echo "==> Registered user plugin at $USER_PLUGIN_DIR"

"$PY" <<'PY'
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("WARN: PyYAML missing; add cognition to ~/.hermes/config.yaml manually", file=sys.stderr)
    sys.exit(0)

cfg_path = Path.home() / ".hermes" / "config.yaml"
cfg_path.parent.mkdir(parents=True, exist_ok=True)
cfg = {}
if cfg_path.is_file():
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
if not isinstance(cfg, dict):
    cfg = {}

plugins = cfg.setdefault("plugins", {})
if not isinstance(plugins, dict):
    plugins = {}
    cfg["plugins"] = plugins
enabled = plugins.setdefault("enabled", [])
if not isinstance(enabled, list):
    enabled = []
    plugins["enabled"] = enabled
if "cognition" not in enabled:
    enabled.append("cognition")

cog = cfg.setdefault("cognition", {})
if not isinstance(cog, dict):
    cog = {}
    cfg["cognition"] = cog
cog["enabled"] = True

cfg_path.write_text(yaml.safe_dump(cfg, default_flow_style=False, sort_keys=False), encoding="utf-8")
print(f"==> Updated {cfg_path} (plugins.enabled includes cognition)")
PY

cat <<'EOF'

Done.
  hermes plugins list
  hermes plugins enable cognition   # should succeed now
  hermes cognition doctor

EOF
