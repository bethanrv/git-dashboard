import os
import tkinter as tk
from tkinter import ttk
from dotenv import set_key

# Import theme constants and config service
from ui.theme import *
import services.config as config

class DarkFolderBrowser(tk.Toplevel):
    def __init__(self, parent, initial_dir):
        super().__init__(parent)
        self.title("Select Directory")
        self.geometry("500x500")
        self.configure(bg=BG_MAIN)
        self.result = None
        
        # Ensure we handle the initial path safely
        start_path = initial_dir or "~"
        self.current_dir = os.path.abspath(os.path.expanduser(start_path))
        
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()

        # --- UI Construction ---
        self.path_label = tk.Label(
            self, text=self.current_dir, bg=BG_MAIN, fg=ACCENT,
            font=FONT_SMALL, anchor="w"
        )
        self.path_label.pack(fill=tk.X, padx=15, pady=10)

        self.tree = ttk.Treeview(self, columns=("Name"), show="headings")
        self.tree.heading("Name", text="FOLDERS", anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=15)
        self.tree.bind("<Double-1>", self.on_double_click)

        btn_frame = tk.Frame(self, bg=BG_MAIN)
        btn_frame.pack(fill=tk.X, padx=15, pady=15)

        self.btn_up = tk.Label(
            btn_frame, text="UP", bg=BG_HEADER, fg=FG_TEXT,
            width=10, pady=5, cursor="hand2"
        )
        self.btn_up.pack(side=tk.LEFT)
        self.btn_up.bind("<Button-1>", lambda e: self.go_up())

        self.btn_sel = tk.Label(
            btn_frame, text="SELECT THIS FOLDER", bg=SUCCESS,
            fg="white", font=FONT_BOLD, pady=5, cursor="hand2"
        )
        self.btn_sel.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        self.btn_sel.bind("<Button-1>", lambda e: self.select())
        
        self.load_dir()

    def load_dir(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.path_label.config(text=self.current_dir)
        try:
            entries = sorted(
                [f.name for f in os.scandir(self.current_dir) 
                 if f.is_dir() and not f.name.startswith(".")],
                key=str.lower
            )
            for entry in entries:
                self.tree.insert("", tk.END, values=(entry,))
        except Exception:
            self.go_up()

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
