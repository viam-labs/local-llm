#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")" || exit

# Create a virtual environment to run our code
export MODEL_DIR="$HOME/.data/models"
export PATH="$PATH:$HOME/.local/bin"
SUDO="sudo"
VENV_NAME=".venv"

OS=$(uname)
if [[ $OS == "Linux" ]]; then
  echo "Running on Linux"

  if command -v clinfo; then
    echo "Setting OpenCL BLAS cmake args"
    export CMAKE_ARGS="-DLLAMA_CLBLAST=ON"
  elif command -v nvidia-smi; then
    echo "Setting Cuda BLAS cmake args"
    export CMAKE_ARGS="-DLLAMA_CUBLAST=ON"
  else
    echo "Setting OpenBLAS cmake args"
    $SUDO apt-get install -qqy clang libopenblas-dev
    export CC="clang"
    export CXX="clang"
    export CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
  fi
fi

if [[ $OS == "Darwin" ]]; then
  echo "Running on MacOS"
  echo "Setting Metal cmake args"
  export CMAKE_ARGS="-DLLAMA_METAL=on"
fi

mkdir -p "$MODEL_DIR"

uv venv $VENV_NAME

echo "Virtualenv found/created. Installing/upgrading Python packages..."
uv pip install ./dist/local_llm*.whl -q

echo "Starting module..."
uv run python -m local_llm "$@"
