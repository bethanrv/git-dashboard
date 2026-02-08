#!/usr/bin/env python3

import tkinter as tk
import sys
from ui.main_window import DarkRepoLauncher

def main():
    root = tk.Tk()
    
    # Fix blurry text on Windows
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
            
    app = DarkRepoLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()