#!/bin/bash -e
cd "$(dirname "$0")"
rm -fr build

# Install or find Python 3.8.
if [[ "$(uname)" =~ ([Ll]inux) ]]; then
  if [[ "$TRAVIS_OS_NAME" == 'linux' ]]; then
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-dev
  fi
  PYTHON=/usr/bin/python3.8
elif [[ "$(uname)" =~ ([Dd]arwin) ]]; then
  if brew ls --versions python > /dev/null; then
    brew upgrade python3
  else
    brew install python3
  fi
  PYTHON=/usr/local/bin/python3
elif [[ -n "$APPVEYOR" ]]; then
  if [[ "$(./os_classifier.sh)" == 'windows-x86_32' ]]; then
    PYTHON=/c/Python36/python
  else
    PYTHON=/c/Python36-x64/python
  fi
else
  echo "Unsupported build environment: $(uname -a)"
  exit 1
fi

# Create and activate a Python 3.6 virtualenv.
echo "Creating a new virtualenv with $PYTHON"
"$PYTHON" -m venv build/venv
export PATH="$PWD/build/venv/bin:$PWD/build/venv/Scripts:$PATH"

# Upgrade pip and setuptools.
if [[ -n "$APPVEYOR" ]]; then
  # Windows
  python -m pip install --upgrade pip setuptools
else
  pip install --upgrade pip setuptools
fi

# Make sure we use Python 3.8.
PYVER="$(python --version)"
PIPVER="$(pip --version)"
echo "$(which python) --version: $PYVER"
echo "$(which pip) --version: $PIPVER"
echo "os.classifier: $(./os_classifier.sh)"
if [[ ! "$PYVER" =~ (^Python 3\.8\.) ]] || \
   [[ ! "$(which python)" =~ (^.*/build/venv/.*$) ]]; then
  echo 'Must run on Python 3.8'
  exit 1
fi
