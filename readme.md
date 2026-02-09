# Git Repo Dashboard
This script is a persistent project launcher designed for high-speed navigation between Git repositories. It scans a designated parent directory, identifies Git-initialized folders, and displays them in a modern, dark-themed GUI.

--- 

## 🚀 Installation & Command Setup

Clone Repo:
```
git clone https://github.com/brianrodgersvargo/git-dashboard.git
cd git-dashboard
```

**Linux / macOS**
The script will detect your shell (Bash or Zsh) and add the necessary alias.
```
chmod +x setup.sh
./setup.sh
source ~/.bashrc  # Or source ~/.zshrc for macOS/Zsh
```

**Windows**
Run the PowerShell setup script as an Administrator to allow symbolic link creation.
```
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup-windows.ps1
# Restart PowerShell to apply changes
```

---

## 🛠 What the Setup Script Does

  - Dependency Check: Verifies python3-tk is installed and installs python-dotenv.

  - Symbolic Link: Links the script to your local bin (or adds to Windows PATH) so it behaves like a system command.

  - Detached Alias: Adds a specialized function (repos) to your shell profile. This ensures the GUI runs as a background process, meaning it won't close if you close your terminal window.

---

## 📖 Usage
Simply type `repos` in any terminal window.
- Search: Start typing to filter repos instantly.
- Open: Double-click a row or press `Enter` to open the repo in your editor.
- Web Link: Select a row to reveal the 🌐/↗ icon to open the remote URL in your browser.
- Navigation: Use the Arrow Keys to navigate and Esc to quit.

**Configuration**:
Click the Settings (⚙) icon to configure:
  - Editor Command: Set your CLI command (e.g., code, zed, subl, or nvim).
  - Search Path: Choose the parent directory where your Git repositories live.

---

## 📝 To-Do List:
[ ] Test build on mac, windows
[ ] loading animationfor requests
[ ] Actions showing success on multiple checks including 1 failure
[ ] Linux search icon malformed
[ ] Add screenshots to readme
