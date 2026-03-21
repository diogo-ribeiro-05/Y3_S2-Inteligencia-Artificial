# src/gui/app.py
import tkinter as tk
from tkinter import ttk


class PhotoSlideshowApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo Slideshow Solver - Hill Climbing")
        self.root.geometry("1200x800")

        self._setup_ui()

    def _setup_ui(self):
        # Main container with grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Placeholder panels (will be replaced in later tasks)
        self.dataset_frame = ttk.LabelFrame(self.root, text="Dataset", padding=10)
        self.dataset_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.slideshow_frame = ttk.LabelFrame(self.root, text="Slideshow", padding=10)
        self.slideshow_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        self.control_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding=10)
        self.stats_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)


def create_app() -> tk.Tk:
    """Create and return the main application window."""
    root = tk.Tk()
    app = PhotoSlideshowApp(root)
    return root
