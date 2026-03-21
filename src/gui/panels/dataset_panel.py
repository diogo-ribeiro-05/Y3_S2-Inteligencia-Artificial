# src/gui/panels/dataset_panel.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional
from src.io.parser import parse_input
from src.models.photo import Photo


class DatasetPanel(ttk.Frame):
    def __init__(self, parent, on_dataset_loaded: Callable[[list[Photo]], None]):
        super().__init__(parent)
        self.on_dataset_loaded = on_dataset_loaded
        self.photos: Optional[list[Photo]] = None
        self.filename: Optional[str] = None
        self._setup_ui()

    def _setup_ui(self):
        # Load button
        self.load_btn = ttk.Button(self, text="Load Dataset", command=self._load_file)
        self.load_btn.pack(anchor="w", pady=5)

        # File info
        self.file_label = ttk.Label(self, text="No file loaded")
        self.file_label.pack(anchor="w", pady=2)

        # Statistics
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(anchor="w", fill="x")

        self.total_label = ttk.Label(self.stats_frame, text="Photos: -")
        self.total_label.pack(anchor="w")

        self.horizontal_label = ttk.Label(self.stats_frame, text="Horizontal: -")
        self.horizontal_label.pack(anchor="w")

        self.vertical_label = ttk.Label(self.stats_frame, text="Vertical: -")
        self.vertical_label.pack(anchor="w")

    def _load_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            self.photos = parse_input(content)
            self.filename = filepath.split('/')[-1]

            self._update_stats()
            self.on_dataset_loaded(self.photos)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def _update_stats(self):
        self.file_label.config(text=f"File: {self.filename}")

        total = len(self.photos)
        horizontal = sum(1 for p in self.photos if p.is_horizontal)
        vertical = total - horizontal

        self.total_label.config(text=f"Photos: {total}")
        self.horizontal_label.config(text=f"Horizontal: {horizontal}")
        self.vertical_label.config(text=f"Vertical: {vertical}")
