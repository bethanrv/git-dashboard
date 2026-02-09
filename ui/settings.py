import os
import sys
import tkinter as tk
from tkinter import ttk
import subprocess
import webbrowser
from ui.theme import *
from ui.folder_browser import DarkFolderBrowser
from services.git_service import get_git_repos
import services.config as config
from dotenv import set_key


class SettingsWindow(tk.Toplevel):
    def __init__(self, launcher_instance):
        super().__init__(launcher_instance.root)
        self.launcher = launcher_instance
        self.title("Settings")
        self.geometry("500x320")
        self.configure(bg=BG_MAIN)
        self.transient(launcher_instance.root)
        self.wait_visibility()
        self.grab_set()

        tk.Label(
            self, text="Application Settings", bg=BG_MAIN, fg=ACCENT, font=FONT_BOLD
        ).pack(pady=15)

        # Editor Command
        tk.Label(self, text="Editor Command (e.g., code, zed):", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20)
        self.ed_entry = tk.Entry(self, bg=BG_STRIPE, fg=FG_TEXT, insertbackground=FG_TEXT, borderwidth=0)
        self.ed_entry.insert(0, config.get_editor())
        self.ed_entry.pack(fill=tk.X, padx=20, pady=5, ipady=4)

        # Search Path
        tk.Label(self, text="Search Path:", bg=BG_MAIN, fg=FG_TEXT).pack(anchor="w", padx=20, pady=(10, 0))
        path_frame = tk.Frame(self, bg=BG_MAIN)
        path_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.path_entry = tk.Entry(path_frame, bg=BG_STRIPE, fg=FG_TEXT, insertbackground=FG_TEXT, borderwidth=0)
        self.path_entry.insert(0, config.get_base_path())
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        self.btn_browse = tk.Label(path_frame, text="Browse...", bg=BG_HEADER, fg=FG_TEXT, padx=10, pady=4, cursor="hand2")
        self.btn_browse.pack(side=tk.LEFT, padx=(5, 0))
        self.btn_browse.bind("<Button-1>", lambda e: self.browse_folder())

        # Save Button
        self.btn_save = tk.Label(self, text="SAVE & REFRESH", bg=SUCCESS, fg="white", font=FONT_BOLD, pady=8, cursor="hand2")
        self.btn_save.pack(pady=25, padx=20, fill=tk.X)
        self.btn_save.bind("<Button-1>", lambda e: self.save())

        self.ed_entry.focus_set()

    def browse_folder(self):
        browser = DarkFolderBrowser(self, self.path_entry.get())
        self.wait_window(browser)
        if browser.result:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, browser.result)

    def save(self):
        new_editor = self.ed_entry.get().strip()
        new_path = self.path_entry.get().strip()

        # Write directly to the .env file using the path from our config service
        set_key(config.ENV_PATH, "EDITOR_COMMAND", new_editor)
        set_key(config.ENV_PATH, "BASE_PATH", new_path)
        
        # Trigger the main window to reload its data and labels
        self.launcher.refresh_data()
        self.destroy()