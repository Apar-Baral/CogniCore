#!/usr/bin/env bash
# Clone CogniCore + CognitionEngine over HTTPS even when git rewrites to SSH.
set -euo pipefail

DEST="${1:-$HOME/Desktop}"
mkdir -p "$DEST"
cd "$DEST"

clone_one() {
  local url="$1"
  local name="$2"
  if [[ -d "$name/.git" ]]; then
    echo "==> $name already exists at $DEST/$name — skipping"
    return 0
  fi
  rm -rf "$name"
  echo "==> Cloning $name ..."
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
    git clone "$url" "$name"
}

clone_one "https://github.com/Apar-Baral/CogniCore.git" "CogniCore"
clone_one "https://github.com/Apar-Baral/CognitionEngine.git" "CognitionEngine"

echo "==> Done. Next:"
echo "    cd $DEST/CogniCore"
echo "    export COGNITION_ENGINE_PATH=\"$DEST/CognitionEngine/packages/cognition-engine\""
echo "    bash scripts/install-hermes-cognition.sh"
