import tkinter as tk

from ui.theme import *


class CloneWindow(tk.Toplevel):
    def __init__(self, parent, on_clone):
        super().__init__(parent)
        self.title("Clone Repository")
        self.geometry("450x200")
        self.configure(bg=BG_MAIN)
        self.on_clone = on_clone
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()

        tk.Label(
            self, text="Repository URL:", bg=BG_MAIN, fg=ACCENT, font=FONT_BOLD
        ).pack(pady=(20, 5), padx=20, anchor="w")

        self.url_entry = tk.Entry(
            self,
            bg=BG_STRIPE,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            borderwidth=0,
            font=FONT_MAIN,
        )
        self.url_entry.pack(fill=tk.X, padx=20, pady=5, ipady=8)
        self.url_entry.focus_set()

        # Simple "Clone" button using a Label for the custom look
        self.btn_clone = tk.Label(
            self,
            text="CLONE REPO",
            bg=SUCCESS,
            fg="white",
            font=FONT_BOLD,
            pady=10,
            cursor="hand2",
        )
        self.btn_clone.pack(fill=tk.X, padx=20, pady=20)
        self.btn_clone.bind("<Button-1>", lambda e: self.start_clone())

        # Bind Enter key
        self.bind("<Return>", lambda e: self.start_clone())

    def start_clone(self):
        url = self.url_entry.get().strip()
        if url:
            self.on_clone(url)
            self.destroy()
