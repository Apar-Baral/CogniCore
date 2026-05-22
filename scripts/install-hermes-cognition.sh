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

if ! "$PY" -m pip --version >/dev/null 2>&1; then
  echo "==> Bootstrapping pip via ensurepip"
  "$PY" -m ensurepip --upgrade
fi
"$PY" -m pip install -U pip wheel setuptools

echo "==> Installing hermes-cognition (CogniCore — self-contained plugin)"
"$PY" -m pip install -e "$PLUGIN_DIR"

HERMES_BIN="$(dirname "$PY")"
CLI_COGNITION="$HERMES_BIN/hermes-cognition"
if [[ -x "$CLI_COGNITION" ]]; then
  echo "==> CLI: $CLI_COGNITION"
  "$CLI_COGNITION" doctor
else
  "$PY" -c "from hermes_cognition.cli_commands import _doctor; raise SystemExit(_doctor())"
fi

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
    print("WARN: merge config/cognition.example.yaml manually", file=sys.stderr)
    sys.exit(0)

lines = snippet.splitlines()
cog_block = "\n".join(lines[7:]) if len(lines) > 7 else snippet
plugins_block = "\n".join(lines[:7])
backup = cfg_path.with_suffix(".yaml.bak")
if cfg_path.is_file() and not backup.is_file():
    backup.write_text(text, encoding="utf-8")
to_append = plugins_block if "plugins:" not in text else cog_block
with cfg_path.open("a", encoding="utf-8") as f:
    f.write("\n\n# --- CogniCore ---\n")
    f.write(to_append)
print(f"==> Updated {cfg_path}")
PY

cat <<EOF

Done. Add to PATH:
  export PATH="$HERMES_BIN:\$PATH"

Commands:
  hermes-cognition doctor
  hermes plugins list
  hermes -t terminal,file,web

EOF
