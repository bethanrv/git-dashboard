#!/usr/bin/env python3
import os
import subprocess
import sys
import tkinter as tk
import re
import webbrowser
from datetime import datetime
from tkinter import messagebox, ttk

from dotenv import load_dotenv, set_key

# --- LOAD CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")
load_dotenv(ENV_PATH)

EDITOR_COMMAND = os.getenv("EDITOR_COMMAND", "code")
BASE_PATH = os.getenv("BASE_PATH", os.path.expanduser("~/Documents"))

# --- DARK THEME COLORS ---
BG_MAIN = "#1e1e1e"
BG_STRIPE = "#252526"
BG_HEADER = "#333333"
FG_TEXT = "#d4d4d4"
ACCENT = "#4fc1ff"
SELECTED = "#094771"
SUCCESS = "#2ea043"
SUCCESS_HOVER = "#3fb950"
HOVER = "#444444"

# --- CROSS-PLATFORM SYSTEM FONT ---
def get_system_font():
    if sys.platform == "darwin": return "SF Pro Display"
    if sys.platform == "win32": return "Segoe UI"
    return "Ubuntu" # Standard Linux fallback

SYS_FONT = get_system_font()
FONT_MAIN = (SYS_FONT, 10)
FONT_BOLD = (SYS_FONT, 10, "bold")
FONT_SMALL = (SYS_FONT, 9)

# --- GIT HELPERS ---
def get_time_ago(timestamp):
    if timestamp == 0: return "Never"
    diff = datetime.now() - datetime.fromtimestamp(timestamp)
    s = diff.total_seconds()
    if s < 60: return f"{int(s)}s ago"
    if s < 3600: return f"{int(s // 60)}m ago"
    if s < 86400: return f"{int(s // 3600)}h ago"
    return f"{int(s // 86400)}d ago"

def extract_git_url(repo_path):
    config_path = os.path.join(repo_path, ".git", "config")
    if not os.path.exists(config_path): return None
    try:
        with open(config_path, "r") as f:
            content = f.read()
            match = re.search(r'\[remote "origin"\][^\[]*url = ([^\s\n]+)', content)
            if match:
                url = match.group(1)
                if url.startswith("git@"):
                    url = url.replace(":", "/").replace("git@", "https://").replace(".git", "")
                return url
    except: return None
    return None

def get_git_repos(path):
    repos = []
    try:
        expanded_path = os.path.expanduser(path)
        if not os.path.exists(expanded_path): return []
        with os.scandir(expanded_path) as entries:
            for entry in entries:
                git_dir = os.path.join(entry.path, ".git")
                if entry.is_dir() and os.path.exists(git_dir):
                    msg_file = os.path.join(git_dir, "COMMIT_EDITMSG")
                    mtime = os.path.getmtime(msg_file) if os.path.exists(msg_file) else os.path.getmtime(git_dir)
                    repos.append({
                        "name": entry.name,
                        "path": entry.path,
                        "mtime": mtime,
                        "time_ago": get_time_ago(mtime),
                        "remote_url": extract_git_url(entry.path)
                    })
        return repos
    except Exception as e:
        print(f"Error: {e}"); return []

# --- CUSTOM FOLDER BROWSER ---
class DarkFolderBrowser(tk.Toplevel):
    def __init__(self, parent, initial_dir):
        super().__init__(parent)
        self.title("Select Directory")
        self.geometry("500x500")
        self.configure(bg=BG_MAIN)
        self.result = None
        self.current_dir = os.path.abspath(os.path.expanduser(initial_dir or "~"))
        self.transient(parent)
        self.grab_set()

        self.path_label = tk.Label(self, text=self.current_dir, bg=BG_MAIN, fg=ACCENT, font=FONT_SMALL, anchor="w")
        self.path_label.pack(fill=tk.X, padx=15, pady=10)

        self.tree = ttk.Treeview(self, columns=("Name"), show="headings")
        self.tree.heading("Name", text="FOLDERS", anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=15)
        self.tree.bind("<Double-1>", self.on_double_click)

        btn_frame = tk.Frame(self, bg=BG_MAIN)
        btn_frame.pack(fill=tk.X, padx=15, pady=15)

        self.btn_up = tk.Label(btn_frame, text="UP", bg=BG_HEADER, fg=FG_TEXT, width=10, pady=5, cursor="hand2")
        self.btn_up.pack(side=tk.LEFT)
        self.btn_up.bind("<Button-1>", lambda e: self.go_up())

        self.btn_sel = tk.Label(btn_frame, text="SELECT THIS FOLDER", bg=SUCCESS, fg="white", font=FONT_BOLD, pady=5, cursor="hand2")
        self.btn_sel.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        self.btn_sel.bind("<Button-1>", lambda e: self.select())
        self.load_dir()

    def load_dir(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.path_label.config(text=self.current_dir)
        try:
            entries = sorted([f.name for f in os.scandir(self.current_dir) if f.is_dir() and not f.name.startswith(".")], key=str.lower)
            for entry in entries: self.tree.insert("", tk.END, values=(entry,))
        except: self.go_up()

    def go_up(self):
        self.current_dir = os.path.dirname(self.current_dir)
        self.load_dir()

    def on_double_click(self, event):
        sel = self.tree.selection()
        if sel:
            folder_name = self.tree.item(sel[0])["values"][0]
            self.current_dir = os.path.join(self.current_dir, folder_name)
            self.load_dir()

    def select(self):
        self.result = self.current_dir
        self.destroy()

# --- SETTINGS ---
class SettingsWindow(tk.Toplevel):
    def __init__(self, launcher_instance):
        super().__init__(launcher_instance.root)
        self.launcher = launcher_instance
        self.title("Settings")
        self.geometry("500x320")
        self.configure(bg=BG_MAIN)
        self.transient(launcher_instance.root)
        self.grab_set()

        tk.Label(self, text="Application Settings", bg=BG_MAIN, fg=ACCENT, font=FONT_BOLD).pack(pady=15)
        tk.Label(self, text="Editor Command (e.g., code, zed):", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
        self.ed_entry = tk.Entry(self, bg=BG_STRIPE, fg=FG_TEXT, insertbackground=FG_TEXT, borderwidth=0)
        self.ed_entry.insert(0, EDITOR_COMMAND)
        self.ed_entry.pack(fill=tk.X, padx=20, pady=5, ipady=4)

        tk.Label(self, text="Search Path:", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        path_frame = tk.Frame(self, bg=BG_MAIN)
        path_frame.pack(fill=tk.X, padx=20, pady=5)
        self.path_entry = tk.Entry(path_frame, bg=BG_STRIPE, fg=FG_TEXT, insertbackground=FG_TEXT, borderwidth=0)
        self.path_entry.insert(0, BASE_PATH)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        self.btn_browse = tk.Label(path_frame, text="Browse...", bg=BG_HEADER, fg=FG_TEXT, padx=10, pady=4, cursor="hand2")
        self.btn_browse.pack(side=tk.LEFT, padx=(5, 0))
        self.btn_browse.bind("<Button-1>", lambda e: self.browse_folder())

        self.btn_save = tk.Label(self, text="SAVE & REFRESH", bg=SUCCESS, fg="white", font=FONT_BOLD, pady=8, cursor="hand2")
        self.btn_save.pack(pady=25, padx=20, fill=tk.X)
        self.btn_save.bind("<Button-1>", lambda e: self.save())

    def browse_folder(self):
        browser = DarkFolderBrowser(self, self.path_entry.get())
        self.wait_window(browser)
        if browser.result:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, browser.result)

    def save(self):
        new_editor, new_path = self.ed_entry.get().strip(), self.path_entry.get().strip()
        set_key(ENV_PATH, "EDITOR_COMMAND", new_editor)
        set_key(ENV_PATH, "BASE_PATH", new_path)
        global EDITOR_COMMAND, BASE_PATH
        EDITOR_COMMAND, BASE_PATH = new_editor, new_path
        self.launcher.refresh_data()
        self.destroy()

# --- MAIN DASHBOARD ---
class DarkRepoLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Repo Dashboard")
        self.root.geometry("550x650")
        self.root.configure(bg=BG_MAIN)

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.bind("<Escape>", self.quit_app)

        self.sort_reverse = {"Name": False, "Last Commit": True}
        self.all_repos = []
        self.filtered_repos = []

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background=BG_MAIN, foreground=FG_TEXT, fieldbackground=BG_MAIN, borderwidth=0, font=FONT_MAIN)
        self.style.map("Treeview", background=[("selected", SELECTED)], foreground=[("selected", "white")])
        self.style.configure("Treeview.Heading", background=BG_HEADER, foreground=ACCENT, relief="flat", font=FONT_BOLD)

        # UI Components
        top_frame = tk.Frame(root, bg=BG_MAIN)
        top_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        tk.Label(top_frame, text="SEARCH", bg=BG_MAIN, fg=ACCENT, font=FONT_BOLD).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        self.search_entry = tk.Entry(top_frame, textvariable=self.search_var, bg=BG_STRIPE, fg=FG_TEXT, insertbackground=FG_TEXT, borderwidth=0, font=FONT_MAIN)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=4)
        self.search_entry.focus_set()

        self.btn_refresh = tk.Label(top_frame, text="↻", bg=BG_HEADER, fg=FG_TEXT, font=(SYS_FONT, 14), padx=8, cursor="hand2")
        self.btn_refresh.pack(side=tk.LEFT, padx=2)
        self.btn_refresh.bind("<Button-1>", lambda e: self.refresh_data())

        self.btn_settings = tk.Label(top_frame, text="⚙", bg=BG_HEADER, fg=FG_TEXT, font=(SYS_FONT, 14), padx=8, cursor="hand2")
        self.btn_settings.pack(side=tk.LEFT, padx=2)
        self.btn_settings.bind("<Button-1>", lambda e: self.open_settings())

        # Tree Table
        self.tree_frame = tk.Frame(root, bg=BG_MAIN)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.tree = ttk.Treeview(self.tree_frame, columns=("Name", "Last Commit"), show="headings")
        self.tree.heading("Name", text=" NAME", command=lambda: self.sort_column("Name"))
        self.tree.heading("Last Commit", text=" LAST COMMIT", command=lambda: self.sort_column("Last Commit"))
        self.tree.column("Name", width=300); self.tree.column("Last Commit", width=100, anchor="center")
        self.tree.tag_configure("oddrow", background=BG_MAIN); self.tree.tag_configure("evenrow", background=BG_STRIPE)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Selection Logic for Globe
        self.globe_btn = tk.Label(self.tree, text="🌐︎", bg=SELECTED, fg="#888888", font=(SYS_FONT, 12), cursor="hand2", padx=5)
        self.globe_btn.bind("<Button-1>", self.open_browser)
        self.globe_btn.bind("<Enter>", lambda e: self.globe_btn.configure(fg="white"))
        self.globe_btn.bind("<Leave>", lambda e: self.globe_btn.configure(fg="#888888"))
        
        self.tree.bind("<<TreeviewSelect>>", self.handle_selection)
        self.tree.bind("<Double-1>", self.open_repo); self.tree.bind("<Return>", self.open_repo)

        # Status & Open Button
        self.status_var = tk.StringVar()
        tk.Label(root, textvariable=self.status_var, bg=BG_MAIN, fg="#666666", font=FONT_SMALL).pack(anchor="w", padx=15)

        self.btn_open = tk.Label(root, text=f"OPEN IN {EDITOR_COMMAND.upper()}", bg=SUCCESS, fg="white", font=FONT_BOLD, pady=12, cursor="hand2")
        self.btn_open.pack(fill=tk.X, padx=15, pady=15)
        self.btn_open.bind("<Button-1>", lambda e: self.open_repo())
        self.btn_open.bind("<Enter>", lambda e: self.btn_open.configure(bg=SUCCESS_HOVER))
        self.btn_open.bind("<Leave>", lambda e: self.btn_open.configure(bg=SUCCESS))

        self.refresh_data()

    def handle_selection(self, event):
        selection = self.tree.selection()
        if not selection:
            self.globe_btn.place_forget(); return
        
        item_id = selection[0]
        index = self.tree.index(item_id)
        repo = self.filtered_repos[index]
        
        if repo.get("remote_url"):
            self.current_url = repo["remote_url"]
            bbox = self.tree.bbox(item_id, "#1")
            if bbox:
                x, y, w, h = bbox
                self.globe_btn.place(x=w-35, y=y, height=h)
        else:
            self.globe_btn.place_forget()

    def open_browser(self, event):
        if hasattr(self, 'current_url'): webbrowser.open(self.current_url)

    def refresh_data(self):
        self.all_repos = get_git_repos(BASE_PATH)
        col = "Last Commit" if self.sort_reverse["Last Commit"] else "Name"
        self.sort_column(col, toggle=False)
        self.btn_open.config(text=f"OPEN IN {EDITOR_COMMAND.upper()}")

    def update_list(self, *args):
        self.globe_btn.place_forget()
        search_term = self.search_var.get().lower()
        for item in self.tree.get_children(): self.tree.delete(item)
        self.filtered_repos = []
        count = 0
        for repo in self.all_repos:
            if search_term in repo["name"].lower():
                tag = "evenrow" if count % 2 == 0 else "oddrow"
                self.tree.insert("", tk.END, values=(f"  {repo['name']}", repo["time_ago"]), tags=(tag,))
                self.filtered_repos.append(repo)
                count += 1
        self.status_var.set(f"Found {count} repositories")

    def sort_column(self, col, toggle=True):
        reverse = self.sort_reverse[col]
        self.all_repos.sort(key=lambda x: x["name"].lower() if col == "Name" else x["mtime"], reverse=reverse)
        if toggle: self.sort_reverse[col] = not reverse
        self.update_list()

    def open_repo(self, event=None):
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            path = self.filtered_repos[index]["path"]
            try:
                subprocess.Popen([EDITOR_COMMAND, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                cmd = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([cmd, path])

    def open_settings(self): SettingsWindow(self)
    def quit_app(self, event=None):
        self.root.quit(); self.root.destroy(); os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = DarkRepoLauncher(root)
    root.mainloop()