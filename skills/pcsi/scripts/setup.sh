#!/usr/bin/env bash
# PCSI Setup — Idempotent
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$SKILL_DIR/data/venv"

echo "=== PCSI Setup ==="
echo "Skill directory: $SKILL_DIR"

# Create runtime directories
mkdir -p "$SKILL_DIR/data/cache" "$SKILL_DIR/data/output"

# Create venv if missing
if [ ! -f "$VENV_DIR/bin/python3" ]; then
    echo "Creating Python venv..."
    if python3 -m venv "$VENV_DIR" 2>/dev/null; then
        echo "✓ venv created with ensurepip"
    else
        echo "ensurepip not available, bootstrapping..."
        python3 -m venv --without-pip "$VENV_DIR"
        "$VENV_DIR/bin/python3" -c "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', '/tmp/get-pip.py')"
        "$VENV_DIR/bin/python3" /tmp/get-pip.py --quiet
    fi
fi

# Ensure pip exists
if [ ! -f "$VENV_DIR/bin/pip" ]; then
    "$VENV_DIR/bin/python3" -c "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', '/tmp/get-pip.py')"
    "$VENV_DIR/bin/python3" /tmp/get-pip.py --quiet
fi

# Install/upgrade deps
echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
if [ -f "$SKILL_DIR/requirements.txt" ]; then
    "$VENV_DIR/bin/pip" install --quiet -r "$SKILL_DIR/requirements.txt"
else
    "$VENV_DIR/bin/pip" install --quiet yfinance fredapi matplotlib pandas numpy scipy pyyaml
fi

# Check FRED API key
if [ -n "${FRED_API_KEY:-}" ]; then
    echo "✓ FRED_API_KEY is set in environment"
elif [ -f "$SKILL_DIR/data/fred_key.txt" ]; then
    echo "✓ FRED API key found in data/fred_key.txt"
else
    echo "⚠ No FRED API key found."
    echo "  Set FRED_API_KEY env var or create data/fred_key.txt"
fi

echo "=== Setup complete ==="
