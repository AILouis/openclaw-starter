#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
#  Idempotent setup for eqt-report skill.
#  Clone repo, create venv, install deps, write API key.
#  All paths relative to the skill directory.
# ──────────────────────────────────────────────────────────────────
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$SKILL_DIR/data"
REPO_DIR="$DATA_DIR/eqt-report-generator"
VENV_DIR="$DATA_DIR/venv"
REPO_URL="https://github.com/AILouis/eqt-report-generator.git"
API_KEY="${OPENROUTER_API_KEY:-}"

mkdir -p "$DATA_DIR"

# ── Clone repo (skip if already exists) ──────────────────────────
if [ -d "$REPO_DIR/.git" ]; then
    echo "Repo already cloned at $REPO_DIR — pulling latest..."
    git -C "$REPO_DIR" pull --ff-only 2>/dev/null || true
else
    echo "Cloning $REPO_URL..."
    git clone "$REPO_URL" "$REPO_DIR"
fi

# ── Create venv (skip if already exists) ─────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python venv at $VENV_DIR..."
    python3 -m venv "$VENV_DIR" 2>/dev/null || python3 -m venv --without-pip "$VENV_DIR"
    # Bootstrap pip if venv was created without it
    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        echo "Bootstrapping pip into venv..."
        curl -sSL https://bootstrap.pypa.io/get-pip.py | "$VENV_DIR/bin/python3"
    fi
else
    echo "Venv already exists at $VENV_DIR"
fi

# ── Install / upgrade deps ───────────────────────────────────────
echo "Installing dependencies..."
"$VENV_DIR/bin/python3" -m pip install --quiet --upgrade pip
"$VENV_DIR/bin/python3" -m pip install --quiet -r "$REPO_DIR/requirements.txt"

# ── Write API key (only if not already set) ──────────────────────
KEY_FILE="$REPO_DIR/key.txt"
if [ ! -f "$KEY_FILE" ] || [ ! -s "$KEY_FILE" ]; then
    if [ -n "$API_KEY" ]; then
        echo "$API_KEY" > "$KEY_FILE"
        chmod 600 "$KEY_FILE"
        echo "API key written to $KEY_FILE"
    else
        echo "⚠️  No OPENROUTER_API_KEY set. Write your key to $KEY_FILE manually:"
        echo "    echo 'sk-or-...' > $KEY_FILE"
    fi
else
    echo "API key already exists at $KEY_FILE — not overwriting"
fi

# ── Create reports dir ───────────────────────────────────────────
mkdir -p "$DATA_DIR/reports"

echo ""
echo '{"ok": true, "message": "eqt-report skill setup complete", "repo": "'"$REPO_DIR"'", "venv": "'"$VENV_DIR"'"}'
