#!/bin/bash

# --- CONFIGURATION ---
SCRIPT_PATH="$(pwd)/git-dashboard-osx.py"
BIN_LINK="$HOME/.local/bin/repos"

FUNC_CMD="repos() { nohup $BIN_LINK >/dev/null 2>&1 & }"

echo "--- Starting Git Repo Dashboard Setup (macOS) ---"

# Deps
command -v brew >/dev/null 2>&1 || { echo "Homebrew not found. Please install it at https://brew.sh/"; exit 1; }
python3 -c "import tkinter" &> /dev/null || brew install python-tk
pip3 install python-dotenv --quiet

# Permissions & Link
chmod +x "$SCRIPT_PATH"
mkdir -p "$HOME/.local/bin"
ln -sf "$SCRIPT_PATH" "$BIN_LINK"

# Detect Shell Config File
if [[ "$SHELL" == *"zsh"* ]]; then
    CONF_FILE="$HOME/.zshrc"
else
    CONF_FILE="$HOME/.bashrc"
fi

# Add Function
grep -v "alias repos=" "$CONF_FILE" | grep -v "repos() {" | grep -v "nohup ~/.local/bin/repos" > "$CONF_FILE.tmp"
mv "$CONF_FILE.tmp" "$CONF_FILE"

echo -e "\n# Git Dashboard\n$FUNC_CMD" >> "$CONF_FILE"

echo "✔ Configuration updated in $CONF_FILE"
echo "------------------------------------------"
echo "DONE! Refresh your shell to start:"
echo "source $CONF_FILE"
echo "Then simply type 'repos' to launch."