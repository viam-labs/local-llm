#!/usr/bin/bash
cd `dirname $0`

MODULE_DIR=$(dirname $0)
VIRTUAL_ENV=$MODULE_DIR/.venv
PYTHON=$VIRTUAL_ENV/bin/python
SUDO=sudo

if ! command -v $SUDO; then
  echo "no sudo on this system, proceeding as current user"
  SUDO=""
fi

if command -v apt-get; then
  if dpkg -l python3-venv; then
    echo "python3-venv is installed, skipping setup"
  else
    if ! apt info python3-venv; then
      echo "package info not found, trying apt update"
      $SUDO apt-get -qq update
    fi
    $SUDO apt-get install -qqy python3-venv
  fi
else
  echo "Skipping tool installation because your platform is missing apt-get"
  echo "If you see failures below, install the equivalent of python3-venv for your system"
fi

source .env
if [ ! -d "$VIRTUAL_ENV" ]; then
  echo "creating virtualenv at $VIRTUAL_ENV"
  python3 -m venv $VIRTUAL_ENV
fi
if [ ! -f .installed ]; then
  echo "installing dependencies from requirements.txt"
  $VIRTUAL_ENV/bin/pip install ./dist/local_llm*.whl

  if [ $? -eq 0 ]; then
    touch .installed
  fi
fi

exec $PYTHON -m local_llm $@
