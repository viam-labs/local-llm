#!/usr/bin/env bash
# First-run setup: installs uv and build tools, then the module's Python environment. Compiling
# llama.cpp, if needed, happens here, where there's time for it, not at module start.

set -euo pipefail
cd "$(dirname "$0")" || exit
export PATH="$PATH:$HOME/.local/bin"

if ! command -v uv >/dev/null; then
  if ! command -v curl >/dev/null; then
    echo "curl is required to install UV. please install curl on this system to continue."
    exit 1
  fi
  echo "Installing uv command"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Only needed when llama.cpp is compiled from source.
if command -v apt-get >/dev/null; then
  sudo apt-get install -qqy cmake make g++ >/dev/null 2>&1 ||
    echo "Could not install cmake, make and g++; compiling llama.cpp, if needed, may fail"
fi

./install.sh
