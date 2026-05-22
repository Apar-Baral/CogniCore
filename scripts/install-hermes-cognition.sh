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
    venv="$(dirname "$(dirname "$(dirname "$exe")")")")"
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

cat <<'EOF'

Done. Add to ~/.hermes/config.yaml:

plugins:
  enabled:
    - cognition
cognition:
  enabled: true

EOF
