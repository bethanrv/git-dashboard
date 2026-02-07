#!/bin/bash

# --- CONFIGURATION ---
SCRIPT_PATH="$(pwd)/git-dashboard.py"
BIN_LINK="$HOME/.local/bin/repos"

FUNC_CMD="repos() { nohup ~/.local/bin/repos >/dev/null 2>&1 & }"

echo "--- Starting Git Repo Dashboard Setup ---"

# 1. Deps
python3 -c "import tkinter" &> /dev/null || sudo apt update && sudo apt install -y python3-tk
pip install python-dotenv

# 2. Permissions & Link
chmod +x "$SCRIPT_PATH"
mkdir -p "$HOME/.local/bin"
ln -sf "$SCRIPT_PATH" "$BIN_LINK"

# 3. Add Function (Removing any old alias first to avoid conflicts)
# We use sed to clean up the bashrc so we don't have duplicate/conflicting commands
sed -i '/alias repos=/d' "$HOME/.bashrc"
sed -i '/repos() {/,/}/d' "$HOME/.bashrc"

echo -e "\n# Git Dashboard\n$FUNC_CMD" >> "$HOME/.bashrc"

echo "✔ Configuration updated in ~/.bashrc"
echo "------------------------------------------"
echo "DONE! To start using the command immediately, refresh shell (or run in new terminal):"
echo ""
echo "source ~/.bashrc"
echo ""
echo ""
echo "Then simply type 'repos' to launch your dashboard."
echo "------------------------------------------"
