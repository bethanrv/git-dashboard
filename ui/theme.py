import sys

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

# --- FONT LOGIC ---
def get_system_font():
    if sys.platform == "darwin":
        return "SF Pro Display"
    if sys.platform == "win32":
        return "Segoe UI"
    return "DejaVu Sans"

SYS_FONT = get_system_font()
FONT_MAIN = (SYS_FONT, 10)
FONT_BOLD = (SYS_FONT, 10, "bold")
FONT_SMALL = (SYS_FONT, 9)

# --- ICON LOGIC ---
def get_icons():
    is_linux = sys.platform.startswith("linux")
    if is_linux:
        return {
            "GLOBE_ICON": "↗",
            "SETTINGS_ICON": "⚙",
            "RELOAD_ICON": "↻",
            "SEARCH_ICON": "⌕",
        }
    return {
        "GLOBE_ICON": "🌐︎",
        "SETTINGS_ICON": "⚙",
        "RELOAD_ICON": "↻",
        "SEARCH_ICON": "⌕",
    }

# ... (Keep your existing constants and icon logic) ...

def apply_ttk_styles(style):
    """Applies the dark theme to ttk widgets."""
    style.theme_use("clam") # 'clam' is the most customizable base theme

    # --- Treeview ---
    style.configure("Treeview", background=BG_MAIN, foreground=FG_TEXT, 
                    fieldbackground=BG_MAIN, borderwidth=0, font=FONT_MAIN)
    style.map("Treeview", background=[("selected", SELECTED)], foreground=[("selected", "white")])
    style.configure("Treeview.Heading", background=BG_HEADER, foreground=ACCENT, 
                    relief="flat", font=FONT_BOLD)
    
    # --- Treeview Styling ---
    style.configure(
        "Treeview",
        background=BG_MAIN,
        foreground=FG_TEXT,
        fieldbackground=BG_MAIN,
        borderwidth=0,
        font=FONT_MAIN,
    )
    style.map(
        "Treeview",
        background=[("selected", SELECTED)],
        foreground=[("selected", "white")],
    )
    style.configure(
        "Treeview.Heading",
        background=BG_HEADER,
        foreground=ACCENT,
        relief="flat",
        font=FONT_BOLD,
    )

    # --- Spinbox Styling (The new part) ---
    style.configure(
        "TSpinbox",
        arrowcolor=FG_TEXT,
        arrowsize=12,
        foreground=FG_TEXT,
        fieldbackground=BG_STRIPE,
        background=BG_STRIPE,   # Background of the button area
        bordercolor=BG_STRIPE,
        lightcolor=BG_STRIPE,
        darkcolor=BG_STRIPE,
        insertcolor=FG_TEXT     # Cursor color
    )
    
    style.map(
        "TSpinbox",
        fieldbackground=[("active", BG_STRIPE), ("focus", BG_STRIPE)],
    )

    style.configure(
        "Vertical.TScrollbar",
        troughcolor=BG_MAIN,       # The track background
        background=BG_HEADER,      # The scroll thumb
        bordercolor=BG_MAIN,       # Border around the thumb
        arrowcolor=FG_TEXT,        # The tiny arrows
        lightcolor=BG_HEADER,      # Highlights on the thumb
        darkcolor=BG_HEADER,       # Shadows on the thumb
        gripcount=0,
        relief="flat"
    )

    style.map("Vertical.TScrollbar",
        background=[("active", HOVER), ("pressed", SELECTED)],
        arrowcolor=[("active", ACCENT)]
    )

ICONS = get_icons()