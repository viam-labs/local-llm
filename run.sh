#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")" || exit
export PATH="$PATH:$HOME/.local/bin"

# A no-op when setup.sh has already installed everything.
./install.sh

echo "Starting module..."
# exec, so viam-server's stop signal reaches the module rather than this shell.
exec uv run python -m local_llm "$@"
