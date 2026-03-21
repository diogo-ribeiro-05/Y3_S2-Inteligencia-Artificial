# src/gui/widgets/slide_card.py
import tkinter as tk
from tkinter import ttk
from src.models.slide import Slide


class SlideCard(ttk.Frame):
    def __init__(self, parent, slide: Slide, index: int, on_click=None):
        super().__init__(parent, relief="raised", borderwidth=2)
        self.slide = slide
        self.index = index
        self.on_click = on_click
        self._setup_ui()

    def _setup_ui(self):
        # Slide number
        ttk.Label(self, text=f"S{self.index}", font=("Arial", 10, "bold")).pack()

        # Photo IDs
        ids = " + ".join(str(pid) for pid in self.slide.photo_ids)
        ttk.Label(self, text=f"[{ids}]", font=("Arial", 8)).pack()

        # Tag count
        ttk.Label(self, text=f"{len(self.slide.tags)} tags", font=("Arial", 8)).pack()

        # Make clickable
        if self.on_click:
            self.bind("<Button-1>", lambda e: self.on_click(self.index))
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda e: self.on_click(self.index))
