import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess
import webbrowser
from ui.theme import *
from ui.settings import SettingsWindow
from ui.login_window import LoginWindow
from services.git_service import get_git_repos
import services.config  as config
from services.auth_service import AuthService

class DarkRepoLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Repo Dashboard")
        self.root.geometry("550x700")
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

        search_container = tk.Frame(top_frame, bg=BG_STRIPE)
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(
            search_container, 
            text=ICONS["SEARCH_ICON"], 
            bg=BG_STRIPE, 
            fg=FG_TEXT,  # Using FG_TEXT (light grey) instead of ACCENT
            font=(SYS_FONT, 12)
        ).pack(side=tk.LEFT, padx=(10, 0))


        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        self.search_entry = tk.Entry(
            search_container,
            textvariable=self.search_var,
            bg=BG_STRIPE,
            fg=FG_TEXT,
            insertbackground=FG_TEXT,
            borderwidth=0,
            highlightthickness=0,
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

        # --- PR SECTION ---
        self.pr_frame = tk.Frame(root, bg=BG_MAIN)
        self.pr_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        tk.Label(
            self.pr_frame, text="OPEN PULL REQUESTS", 
            bg=BG_MAIN, fg=ACCENT, font=FONT_BOLD, anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))

        # We'll use a smaller Treeview for PRs
        self.pr_tree = ttk.Treeview(
            self.pr_frame, columns=("Repo", "Title", "Status"), 
            show="headings", height=4 # Show 4 PRs before scrolling
        )
        self.pr_tree.heading("Repo", text=" REPO")
        self.pr_tree.heading("Title", text=" TITLE")
        self.pr_tree.heading("Status", text=" STAT")
        
        self.pr_tree.column("Repo", width=100, stretch=False)
        self.pr_tree.column("Title", width=300, stretch=True)
        self.pr_tree.column("Status", width=60, anchor="center", stretch=False)
        
        self.pr_tree.tag_configure("oddrow", background=BG_MAIN)
        self.pr_tree.tag_configure("evenrow", background=BG_STRIPE)
        self.pr_tree.pack(fill=tk.X)

        # Bind click to open PR in browser
        self.pr_tree.bind("<Double-1>", self.open_selected_pr)

        # --- REVIEWS SECTION ---
        self.rev_frame = tk.Frame(root, bg=BG_MAIN)
        self.rev_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        tk.Label(
            self.rev_frame, text="REVIEW REQUESTS", 
            bg=BG_MAIN, fg="#FFA500", font=FONT_BOLD, anchor="w" # Orange color for urgency
        ).pack(fill=tk.X, pady=(0, 5))

        self.rev_tree = ttk.Treeview(
            self.rev_frame, columns=("Repo", "Author", "Title"), 
            show="headings", height=3 
        )
        self.rev_tree.heading("Repo", text=" REPO")
        self.rev_tree.heading("Author", text=" AUTHOR")
        self.rev_tree.heading("Title", text=" TITLE")
        
        self.rev_tree.column("Repo", width=100, stretch=False)
        self.rev_tree.column("Author", width=100, stretch=False)
        self.rev_tree.column("Title", width=250, stretch=True)
        
        self.rev_tree.tag_configure("oddrow", background=BG_MAIN)
        self.rev_tree.tag_configure("evenrow", background=BG_STRIPE)
        self.rev_tree.pack(fill=tk.X)

        self.rev_tree.bind("<Double-1>", self.open_selected_review)

        # --- BOTTOM BAR (Status, Sign In, and Logo) ---
        bottom_frame = tk.Frame(root, bg=BG_MAIN)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=(0, 10))

        # Status Label (Left)
        self.status_var = tk.StringVar()
        tk.Label(
            bottom_frame,
            textvariable=self.status_var,
            bg=BG_MAIN,
            fg="#666666",
            font=FONT_SMALL,
        ).pack(side=tk.LEFT)

        # --- LOGO LOADING ---
        try:
            # Safer pathing: looks for 'assets' inside the same folder as this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            asset_path = os.path.join(current_dir, "assets", "git-icon-white.png")
            
            img = Image.open(asset_path)
            img = img.resize((24, 24), Image.Resampling.LANCZOS) # Slightly smaller than 32 for better fit
            self.logo_img = ImageTk.PhotoImage(img)
            
            logo_label = tk.Label(bottom_frame, image=self.logo_img, bg=BG_MAIN)
            logo_label.pack(side=tk.RIGHT, padx=(10, 0))
        except Exception as e:
            print(f"Could not load logo: {e}")

        # Sign In Link (Next to Logo)
        self.btn_signin = tk.Label(
            bottom_frame,
            text="Sign In",
            bg=BG_MAIN,
            fg=ACCENT, # Use your theme accent color (blue/light blue)
            font=FONT_SMALL,
            cursor="hand2"
        )
        self.btn_signin.pack(side=tk.RIGHT)
        
        # Simple hover effect
        self.btn_signin.bind("<Enter>", lambda e: self.btn_signin.configure(fg="white"))
        self.btn_signin.bind("<Leave>", lambda e: self.btn_signin.configure(fg=ACCENT))
        self.btn_signin.bind("<Button-1>", lambda e: self.handle_signin())

        self.setUser()

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
        self.load_prs()
        self.load_reviews()

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

    def handle_signin(self):
        webbrowser.open("https://github.com/login")

    def update_auth_ui(self):
        if self.current_user:
            self.btn_signin.config(text=f"@{self.current_user}", fg="#888888")
            # Change hover to indicate logout
            self.btn_signin.bind("<Enter>", lambda e: self.btn_signin.configure(fg="#a83232")) # Red for logout
            self.btn_signin.bind("<Leave>", lambda e: self.btn_signin.configure(fg="#888888"))
            self.btn_signin.bind("<Button-1>", lambda e: self.confirm_logout())
        else:
            self.btn_signin.config(text="Sign In", fg=ACCENT)
            self.btn_signin.bind("<Enter>", lambda e: self.btn_signin.configure(fg="white"))
            self.btn_signin.bind("<Leave>", lambda e: self.btn_signin.configure(fg=ACCENT))
            self.btn_signin.bind("<Button-1>", lambda e: self.open_login())

    def open_login(self):
        LoginWindow(self.root, on_success=self.handle_login_success)

    def handle_login_success(self, username):
        self.current_user = username
        self.update_auth_ui()
        self.status_var.set(f"Logged in as {username}")

    def confirm_logout(self):
        if tk.messagebox.askyesno("Logout", "Are you sure you want to sign out?"):
            AuthService.logout()
            self.current_user = None
            self.update_auth_ui()

    def setUser(self):
        self.current_user = AuthService.get_current_user()
        self.update_auth_ui()

    def load_prs(self):
        """Fetches and displays PRs from GitHub."""
        # Clear existing
        for item in self.pr_tree.get_children():
            self.pr_tree.delete(item)
            
        if not self.current_user:
            return

        from services.git_service import fetch_open_prs # Ensure this exists in git_service
        self.current_prs = fetch_open_prs()
        
        for i, pr in enumerate(self.current_prs):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.pr_tree.insert(
                "", tk.END, 
                values=(pr["repo"], pr["title"], pr["status"]), 
                tags=(tag,)
            )

    def open_selected_pr(self, event):
        """Opens the selected PR URL in the default browser."""
        selection = self.pr_tree.selection()
        if selection:
            # Get index of selected item to find the URL in our list
            item_id = selection[0]
            index = self.pr_tree.index(item_id)
            if index < len(self.current_prs):
                webbrowser.open(self.current_prs[index]["url"])

    def load_reviews(self):
        """Fetches and displays PRs where a review is requested from the user."""
        for item in self.rev_tree.get_children():
            self.rev_tree.delete(item)
            
        if not self.current_user:
            return

        from services.git_service import fetch_review_requests
        self.current_reviews = fetch_review_requests()
        
        for i, rev in enumerate(self.current_reviews):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.rev_tree.insert(
                "", tk.END, 
                values=(rev["repo"], f"@{rev['author']}", rev["title"]), 
                tags=(tag,)
            )

    def open_selected_review(self, event):
        selection = self.rev_tree.selection()
        if selection:
            index = self.rev_tree.index(selection[0])
            if index < len(self.current_reviews):
                webbrowser.open(self.current_reviews[index]["url"])

    def open_settings(self):
        SettingsWindow(self)

    def quit_app(self, event=None):
        self.root.quit()
        self.root.destroy()
        os._exit(0)
