import asyncio
import threading
import tkinter as tk
import webbrowser

from services.auth_service import AuthService
from ui.theme import *


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("GitHub Sign In")
        self.geometry("400x240")  # Increased height slightly for status messages
        self.configure(bg=BG_MAIN)
        self.transient(parent)

        # UI Setup
        tk.Label(
            self,
            text="Enter GitHub Personal Access Token",
            bg=BG_MAIN,
            fg=ACCENT,
            font=FONT_BOLD,
        ).pack(pady=(20, 5))

        help_link = tk.Label(
            self,
            text="Where do I get a token?",
            bg=BG_MAIN,
            fg="#888888",
            font=FONT_SMALL,
            cursor="hand2",
        )
        help_link.pack()
        help_link.bind(
            "<Button-1>",
            lambda e: webbrowser.open("https://github.com/settings/tokens"),
        )

        self.token_entry = tk.Entry(
            self,
            bg=BG_STRIPE,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            borderwidth=0,
            show="*",
            font=FONT_MAIN,
        )
        self.token_entry.pack(fill=tk.X, padx=30, pady=20, ipady=8)

        self.btn_login = tk.Label(
            self,
            text="VERIFY & SAVE",
            bg=SUCCESS,
            fg="white",
            font=FONT_BOLD,
            pady=10,
            cursor="hand2",
        )
        self.btn_login.pack(fill=tk.X, padx=30)
        self.btn_login.bind("<Button-1>", lambda e: self.attempt_login())

        # Modal logic
        self.token_entry.focus_set()
        self.wait_visibility()
        self.grab_set()

    def attempt_login(self):
        token = self.token_entry.get().strip()
        if not token:
            return

        # 1. Update UI to "Loading" state
        self.btn_login.config(bg=BG_STRIPE, text="VERIFYING...", cursor="watch")
        self.btn_login.unbind("<Button-1>")  # Prevent double clicks

        # 2. Run the async validation in a background thread
        thread = threading.Thread(
            target=self.run_validation, args=(token,), daemon=True
        )
        thread.start()

    def run_validation(self, token):
        # We use asyncio.run here because this is a fresh background thread
        result = AuthService.validate_and_save(token)

        # 3. Use .after() to send result back to the main UI thread
        self.after(0, lambda: self.handle_result(result))

    def handle_result(self, result):
        if result["success"]:
            self.on_success(result["username"])
            self.destroy()
        else:
            # Re-enable the button on failure
            self.btn_login.config(
                bg="#a83232", text=f"FAILED: {result['error']}", cursor="hand2"
            )
            self.btn_login.bind("<Button-1>", lambda e: self.attempt_login())
