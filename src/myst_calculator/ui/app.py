"""Desktop user-interface application for Myst Calculator."""

import tkinter as tk
from tkinter import ttk

from myst_calculator.ui.theme import configure_theme
from myst_calculator.ui.widgets import OpposedRollTab


class MystCalculatorApp(tk.Tk):
    """Host scenario tabs for the Myst Calculator desktop application."""

    def __init__(self) -> None:
        """Create the main desktop window and available scenario tabs."""
        super().__init__()
        configure_theme(self)
        self.title("Myst Calculator")
        self.geometry("1080x800")
        self.minsize(840, 640)

        header = ttk.Frame(self)
        header.pack(fill="x", padx=24, pady=(20, 10))
        ttk.Label(
            header,
            text="Myst Calculator",
            style="AppTitle.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Explore probability distributions for Myst roll scenarios.",
            style="AppSubtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        self._opposed_tab = OpposedRollTab(notebook)
        notebook.add(self._opposed_tab, text="Opposed Roll")
        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self) -> None:
        """Cancel active work and close the desktop window."""
        self._opposed_tab.shutdown()
        self.destroy()


def launch() -> int:
    """Launch the desktop user interface and run its event loop."""
    app = MystCalculatorApp()
    app.mainloop()
    return 0
