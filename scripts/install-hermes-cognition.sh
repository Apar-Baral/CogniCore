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

export COGNITION_REPO_ROOT="$REPO_ROOT"
"$PY" <<'PY'
import os
import sys
from pathlib import Path

cfg_path = Path.home() / ".hermes" / "config.yaml"
example = Path(os.environ["COGNITION_REPO_ROOT"]) / "config" / "cognition.example.yaml"
cfg_path.parent.mkdir(parents=True, exist_ok=True)
text = cfg_path.read_text(encoding="utf-8") if cfg_path.is_file() else ""

if "cognition:" in text:
    print(f"==> {cfg_path} already has cognition block")
    sys.exit(0)

snippet = example.read_text(encoding="utf-8") if example.is_file() else ""
if not snippet.strip():
    print("WARN: merge config/cognition.example.yaml into ~/.hermes/config.yaml manually", file=sys.stderr)
    sys.exit(0)

lines = snippet.splitlines()
cog_block = "\n".join(lines[7:]) if len(lines) > 7 else snippet
plugins_block = "\n".join(lines[:7])

backup = cfg_path.with_suffix(".yaml.bak")
if cfg_path.is_file() and not backup.is_file():
    backup.write_text(text, encoding="utf-8")

to_append = plugins_block if "plugins:" not in text else cog_block
with cfg_path.open("a", encoding="utf-8") as f:
    f.write("\n\n# --- CogniCore (install-hermes-cognition.sh) ---\n")
    f.write(to_append)
    if "plugins:" in text and "- cognition" not in text:
        f.write("\n# Add '- cognition' under your existing plugins.enabled list\n")
print(f"==> Appended CogniCore config to {cfg_path}")
if "plugins:" in text and "- cognition" not in text:
    print("    ACTION: add '- cognition' under plugins.enabled in config.yaml")
print("    Backup:", backup if backup.is_file() else "(none)")
PY

cat <<'EOF'

Done.
  hermes plugins list
  hermes plugins enable cognition   # should succeed now
  hermes cognition doctor

EOF
