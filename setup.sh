#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")" || exit

# Create a virtual environment to run our code
SUDO="sudo"

export MODEL_DIR="$HOME/.data/models"
export PATH=$PATH:$HOME/.local/bin

if [ ! "$(command -v uv)" ]; then
  if [ ! "$(command -v curl)" ]; then
    echo "curl is required to install UV. please install curl on this system to continue."
    exit 1
  fi
  echo "Installing uv command"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

$SUDO apt install -qqy cmake make >/dev/null 2>&1
