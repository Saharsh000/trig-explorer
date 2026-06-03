"""
main.py — Entry point for Trig Explorer.

Run with:
    python main.py
"""

import sys
import os

# Ensure the project root is on the path so relative imports work
sys.path.insert(0, os.path.dirname(__file__))

try:
    import customtkinter as ctk
except ImportError:
    print(
        "[ERROR] CustomTkinter is not installed.\n"
        "  Run:  pip install customtkinter\n"
    )
    sys.exit(1)

from ui import TrigExplorerApp


def main() -> None:
    app = TrigExplorerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
