#!/bin/bash

# --- CONFIGURATION ---
DASHBOARD_FILE="app.py"
SCRIPT_PATH="$(pwd)/$DASHBOARD_FILE"
BIN_DIR="$HOME/.local/bin"
BIN_LINK="$BIN_DIR/repos"
FUNC_CMD="repos() { nohup $BIN_LINK >/dev/null 2>&1 & }"

echo "🚀 Starting Git Repo Dashboard Unified Setup..."

# Platform Detection & Dependency Install
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS detected"
    CONF_FILE="$HOME/.zshrc" # Default for modern macOS
    [[ ! -f "$CONF_FILE" ]] && CONF_FILE="$HOME/.bash_profile"

    command -v brew >/dev/null 2>&1 || { echo "❌ Homebrew not found. Install it at https://brew.sh/"; exit 1; }
    python3 -c "import tkinter" &> /dev/null || brew install python-tk
    pip3 install python-dotenv --quiet
else
    echo "🐧 Linux detected"
    CONF_FILE="$HOME/.bashrc"

    python3 -c "import tkinter" &> /dev/null || (sudo apt update && sudo apt install -y python3-tk)
    pip install python-dotenv --quiet
fi

# Permissions & Binary Link
chmod +x "$SCRIPT_PATH"
mkdir -p "$BIN_DIR"
ln -sf "$SCRIPT_PATH" "$BIN_LINK"

# 3. Clean up old references and append new function
# Using a temporary file to safely scrub existing 'repos' definitions
if [ -f "$CONF_FILE" ]; then
    sed -i.bak '/alias repos=/d' "$CONF_FILE" 2>/dev/null || sed -i '' '/alias repos=/d' "$CONF_FILE"
    sed -i.bak '/repos() {/,/}/d' "$CONF_FILE" 2>/dev/null || sed -i '' '/repos() {/,/}/d' "$CONF_FILE"
fi

echo -e "\n# Git Dashboard\n$FUNC_CMD" >> "$CONF_FILE"

echo "✅ Configuration updated in $CONF_FILE"
echo "✅ Shortcut created at $BIN_LINK"
echo "------------------------------------------"
echo "DONE! To start using the command, reload your shell:"
echo ""
echo "   source $CONF_FILE"
echo ""
echo "Then simply type 'repos' from any directory."
echo "------------------------------------------"
