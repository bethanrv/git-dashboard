import os
import sys
import tkinter as tk
import webbrowser
from ui.theme import *
import services.config as config
from services.auth_service import AuthService


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("GitHub Sign In")
        self.geometry("400x200")
        self.configure(bg=BG_MAIN)
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text="Enter GitHub Personal Access Token", 
                 bg=BG_MAIN, fg=ACCENT, font=FONT_BOLD).pack(pady=10)
        
        # Link to help users find where to get a token
        help_link = tk.Label(self, text="Where do I get a token?", 
                             bg=BG_MAIN, fg="#888888", font=FONT_SMALL, cursor="hand2")
        help_link.pack()
        help_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/settings/tokens"))

        self.token_entry = tk.Entry(self, bg=BG_STRIPE, fg=FG_TEXT, 
                                    insertbackground=FG_TEXT, borderwidth=0, show="*")
        self.token_entry.pack(fill=tk.X, padx=30, pady=20, ipady=4)

        self.btn_login = tk.Label(self, text="VERIFY & SAVE", bg=SUCCESS, 
                                  fg="white", font=FONT_BOLD, pady=8, cursor="hand2")
        self.btn_login.pack(fill=tk.X, padx=30)
        self.btn_login.bind("<Button-1>", lambda e: self.attempt_login())

    def attempt_login(self):
        token = self.token_entry.get().strip()
        result = AuthService.validate_and_save(token)
        if result["success"]:
            self.on_success(result["username"])
            self.destroy()
        else:
            self.btn_login.config(bg="#a83232", text=result["error"])