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

ICONS = get_icons()