import os
import sys
import tkinter as tk
from tkinter import ttk
import subprocess
import webbrowser
from ui.theme import *
from ui.settings import SettingsWindow
from services.git_service import get_git_repos
import services.config as config

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
        self.style.configure(
            "Treeview",
            background=BG_MAIN,
            foreground=FG_TEXT,
            fieldbackground=BG_MAIN,
            borderwidth=0,
            font=FONT_MAIN,
        )
        self.style.map(
            "Treeview",
            background=[("selected", SELECTED)],
            foreground=[("selected", "white")],
        )
        self.style.configure(
            "Treeview.Heading",
            background=BG_HEADER,
            foreground=ACCENT,
            relief="flat",
            font=FONT_BOLD,
        )

        # UI Components
        top_frame = tk.Frame(root, bg=BG_MAIN)
        top_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        tk.Label(top_frame, text="SEARCH", bg=BG_MAIN, fg=ACCENT, font=FONT_BOLD).pack(
            side=tk.LEFT
        )

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        self.search_entry = tk.Entry(
            top_frame,
            textvariable=self.search_var,
            bg=BG_STRIPE,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            borderwidth=0,
            font=FONT_MAIN,
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=4)
        self.search_entry.focus_set()

        self.btn_refresh = tk.Label(
            top_frame,
            text=ICONS["RELOAD_ICON"],
            bg=BG_HEADER,
            fg=FG_TEXT,
            font=(SYS_FONT, 14),
            padx=8,
            cursor="hand2",
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=2)
        self.btn_refresh.bind("<Button-1>", lambda e: self.refresh_data())

        self.btn_settings = tk.Label(
            top_frame,
            text=ICONS["SETTINGS_ICON"],
            bg=BG_HEADER,
            fg=FG_TEXT,
            font=(SYS_FONT, 14),
            padx=8,
            cursor="hand2",
        )
        self.btn_settings.pack(side=tk.LEFT, padx=2)
        self.btn_settings.bind("<Button-1>", lambda e: self.open_settings())

        # Tree Table
        self.tree_frame = tk.Frame(root, bg=BG_MAIN)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.tree = ttk.Treeview(
            self.tree_frame, columns=("Name", "Last Commit"), show="headings"
        )
        self.tree.heading(
            "Name", text=" NAME", command=lambda: self.sort_column("Name")
        )
        self.tree.heading(
            "Last Commit",
            text=" LAST COMMIT",
            command=lambda: self.sort_column("Last Commit"),
        )
        self.tree.column("Name", width=300)
        self.tree.column("Last Commit", width=100, anchor="center")
        self.tree.tag_configure("oddrow", background=BG_MAIN)
        self.tree.tag_configure("evenrow", background=BG_STRIPE)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Selection Logic for Globe
        self.globe_btn = tk.Label(
            self.tree,
            text=ICONS["GLOBE_ICON"],
            bg=SELECTED,
            fg="#888888",
            font=(SYS_FONT, 12),
            cursor="hand2",
            padx=5,
        )
        self.globe_btn.bind("<Button-1>", self.open_browser)
        self.globe_btn.bind("<Enter>", lambda e: self.globe_btn.configure(fg="white"))
        self.globe_btn.bind("<Leave>", lambda e: self.globe_btn.configure(fg="#888888"))

        self.tree.bind("<<TreeviewSelect>>", self.handle_selection)
        self.tree.bind("<Double-1>", self.open_repo)
        self.tree.bind("<Return>", self.open_repo)

        # Status & Open Button
        self.status_var = tk.StringVar()
        tk.Label(
            root,
            textvariable=self.status_var,
            bg=BG_MAIN,
            fg="#666666",
            font=FONT_SMALL,
        ).pack(anchor="w", padx=15)

        self.btn_open = tk.Label(
            root,
            text=f"OPEN IN {config.get_editor().upper()}",
            bg=SUCCESS,
            fg="white",
            font=FONT_BOLD,
            pady=12,
            cursor="hand2",
        )
        self.btn_open.pack(fill=tk.X, padx=15, pady=15)
        self.btn_open.bind("<Button-1>", lambda e: self.open_repo())
        self.btn_open.bind(
            "<Enter>", lambda e: self.btn_open.configure(bg=SUCCESS_HOVER)
        )
        self.btn_open.bind("<Leave>", lambda e: self.btn_open.configure(bg=SUCCESS))

        self.refresh_data()

    def handle_selection(self, event):
        selection = self.tree.selection()
        if not selection:
            self.globe_btn.place_forget()
            return

        item_id = selection[0]
        index = self.tree.index(item_id)
        repo = self.filtered_repos[index]

        if repo.get("remote_url"):
            self.current_url = repo["remote_url"]
            bbox = self.tree.bbox(item_id, "#1")
            if bbox:
                x, y, w, h = bbox
                self.globe_btn.place(x=w - 35, y=y, height=h)
        else:
            self.globe_btn.place_forget()

    def open_browser(self, event):
        if hasattr(self, "current_url"):
            webbrowser.open(self.current_url)

    def refresh_data(self):
        config.reload_config()
        self.all_repos = get_git_repos(config.get_base_path())
        col = "Last Commit" if self.sort_reverse["Last Commit"] else "Name"
        self.sort_column(col, toggle=False)
        self.btn_open.config(text=f"OPEN IN {config.get_editor().upper()}")

    def update_list(self, *args):
        self.globe_btn.place_forget()
        search_term = self.search_var.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.filtered_repos = []
        count = 0
        for repo in self.all_repos:
            if search_term in repo["name"].lower():
                tag = "evenrow" if count % 2 == 0 else "oddrow"
                self.tree.insert(
                    "",
                    tk.END,
                    values=(f"  {repo['name']}", repo["time_ago"]),
                    tags=(tag,),
                )
                self.filtered_repos.append(repo)
                count += 1
        self.status_var.set(f"Found {count} repositories")

    def sort_column(self, col, toggle=True):
        reverse = self.sort_reverse[col]
        self.all_repos.sort(
            key=lambda x: x["name"].lower() if col == "Name" else x["mtime"],
            reverse=reverse,
        )
        if toggle:
            self.sort_reverse[col] = not reverse
        self.update_list()

    def open_repo(self, event=None):
        selection = self.tree.selection()
        if selection:
            index = self.tree.index(selection[0])
            path = self.filtered_repos[index]["path"]
            try:
                subprocess.Popen(
                    [config.get_editor(), path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                if sys.platform == "win32":
                    os.startfile(path)  # Opens in default File Explorer
                else:
                    cmd = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.Popen([cmd, path])

    def open_settings(self):
        SettingsWindow(self)

    def quit_app(self, event=None):
        self.root.quit()
        self.root.destroy()
        os._exit(0)
