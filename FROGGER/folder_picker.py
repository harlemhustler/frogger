"""Open the native directory chooser in the local desktop session."""
import json
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog


def choose_directory(kind, current):
    initial = Path(current) if current else Path.home()
    window = tk.Tk()
    try:
        window.withdraw()
        window.attributes("-topmost", True)
        selected = filedialog.askdirectory(
            parent=window,
            title=f"Choose {kind} folder",
            initialdir=str(initial if initial.is_dir() else Path.home()),
            mustexist=True,
        )
        return selected or None
    finally:
        window.destroy()


if __name__ == "__main__":
    print(json.dumps(choose_directory(*sys.argv[1:])))
