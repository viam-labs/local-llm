#!/usr/bin/env bash
# Creates .venv and installs the module with a llama.cpp build suited to this machine. setup.sh
# runs it once per module version (it may compile llama.cpp); run.sh reruns it on every start,
# which is quick once everything is installed.

set -euo pipefail
cd "$(dirname "$0")" || exit
export PATH="$PATH:$HOME/.local/bin"

WHEELS="https://abetlen.github.io/llama-cpp-python/whl"
NVCC=""
if command -v nvcc >/dev/null; then
  NVCC="$(command -v nvcc)"
elif [[ -x /usr/local/cuda/bin/nvcc ]]; then
  NVCC=/usr/local/cuda/bin/nvcc
fi

PREBUILT=""
if [[ -n $NVCC ]]; then
  # NVIDIA GPU with the CUDA toolkit, including Jetson: build llama.cpp with CUDA. There are
  # no prebuilt CUDA wheels for arm64, and the x86 ones need a matching CUDA runtime.
  echo "Found $NVCC: using llama.cpp built with CUDA (the first install compiles it, which can take a while)"
  export CUDACXX="$NVCC"
  export CMAKE_ARGS="-DGGML_CUDA=on"
  # Compile for this GPU only. Jetson Orin is compute 8.7, Xavier 7.2. Elsewhere llama.cpp
  # picks its own list, which is slower to build.
  if grep -qs tegra234 /proc/device-tree/compatible; then
    CMAKE_ARGS="$CMAKE_ARGS -DCMAKE_CUDA_ARCHITECTURES=87"
  elif grep -qs tegra194 /proc/device-tree/compatible; then
    CMAKE_ARGS="$CMAKE_ARGS -DCMAKE_CUDA_ARCHITECTURES=72"
  fi
elif [[ $(uname) == "Darwin" ]]; then
  # Build from source, which enables Metal and takes under a minute on Apple silicon. uv fails
  # to unpack the prebuilt Metal wheel ("unexpected BufError"), as of 0.3.36.
  echo "Using llama.cpp built with Metal"
else
  PREBUILT="$WHEELS/cpu"
fi

uv venv --allow-existing -q .venv

# Use a prebuilt llama-cpp-python wheel where one exists for this platform. If not, or with
# CUDA, install from PyPI, which has only the source, so llama.cpp is compiled here.
if [[ -n $PREBUILT ]] &&
  uv pip install -q --extra-index-url "$PREBUILT" --only-binary llama-cpp-python ./dist/local_llm*.whl; then
  exit 0
fi
[[ -n $PREBUILT ]] && echo "No prebuilt llama-cpp-python wheel for this platform: compiling llama.cpp"
uv pip install -q ./dist/local_llm*.whl
