#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")" || exit

# Create a virtual environment to run our code
export MODEL_DIR="$HOME/.data/models"
export PATH="$PATH:$HOME/.local/bin"

echo "Starting module..."
uv run main "$@"
