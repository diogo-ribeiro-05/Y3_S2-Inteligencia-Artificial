# src/gui/panels/slideshow_viewer.py
import tkinter as tk
from tkinter import ttk
from typing import Optional
from src.models.slideshow import Slideshow
from src.gui.widgets.slide_card import SlideCard
from src.solver.scorer import calculate_transition_score


class SlideshowViewer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.slideshow: Optional[Slideshow] = None
        self.selected_index: Optional[int] = None
        self.cards = []
        self._setup_ui()

    def _setup_ui(self):
        # Scrollable frame for slides
        canvas = tk.Canvas(self, height=150)
        scrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")

        # Details panel
        self.details_frame = ttk.LabelFrame(self, text="Slide Details", padding=10)
        self.details_frame.pack(fill="x", pady=5)

        self.tags_label = ttk.Label(self.details_frame, text="Tags: -")
        self.tags_label.pack(anchor="w")

        self.transition_label = ttk.Label(self.details_frame, text="Transition: -")
        self.transition_label.pack(anchor="w")

    def load_slideshow(self, slideshow: Slideshow):
        """Load and display a slideshow."""
        self.slideshow = slideshow
        self.selected_index = None

        # Clear existing cards
        for card in self.cards:
            card.destroy()
        self.cards = []

        # Create new cards
        for i, slide in enumerate(slideshow.slides):
            card = SlideCard(self.scroll_frame, slide, i, self._on_slide_clicked)
            card.pack(side="left", padx=5, pady=5)
            self.cards.append(card)

    def _on_slide_clicked(self, index: int):
        """Handle slide selection."""
        self.selected_index = index
        slide = self.slideshow.slides[index]

        # Update details
        tags_str = ", ".join(sorted(slide.tags))
        self.tags_label.config(text=f"Tags: [{tags_str}]")

        # Show transition score to next slide
        if index < len(self.slideshow.slides) - 1:
            next_slide = self.slideshow.slides[index + 1]
            score = calculate_transition_score(slide, next_slide)
            self.transition_label.config(text=f"Transition S{index}->S{index+1}: score = {score}")
        else:
            self.transition_label.config(text="Transition: (last slide)")

    def clear(self):
        """Clear the viewer."""
        for card in self.cards:
            card.destroy()
        self.cards = []
        self.slideshow = None
        self.tags_label.config(text="Tags: -")
        self.transition_label.config(text="Transition: -")
