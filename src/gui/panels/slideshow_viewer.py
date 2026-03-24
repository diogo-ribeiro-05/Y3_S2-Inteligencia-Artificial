# src/gui/panels/slideshow_viewer.py
import tkinter as tk
from tkinter import ttk
from typing import Optional
from src.models.slideshow import Slideshow
from src.gui.widgets.slide_card import SlideCard
from src.solver.scorer import calculate_transition_score

# Maximum slides to show at once (prevents X11 resource exhaustion)
PAGE_SIZE = 100


class SlideshowViewer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.slideshow: Optional[Slideshow] = None
        self.selected_index: Optional[int] = None
        self.cards = []
        self.current_page = 0
        self.total_pages = 1
        self._setup_ui()

    def _setup_ui(self):
        # Pagination controls at top
        nav_frame = ttk.Frame(self)
        nav_frame.pack(side="top", fill="x", pady=5)

        self.btn_first = ttk.Button(nav_frame, text="|<", width=3, command=self._go_first)
        self.btn_first.pack(side="left", padx=2)

        self.btn_prev = ttk.Button(nav_frame, text="<", width=3, command=self._go_prev)
        self.btn_prev.pack(side="left", padx=2)

        self.page_label = ttk.Label(nav_frame, text="Page 0 / 0")
        self.page_label.pack(side="left", padx=10)

        self.btn_next = ttk.Button(nav_frame, text=">", width=3, command=self._go_next)
        self.btn_next.pack(side="left", padx=2)

        self.btn_last = ttk.Button(nav_frame, text=">|", width=3, command=self._go_last)
        self.btn_last.pack(side="left", padx=2)

        self.slide_count_label = ttk.Label(nav_frame, text="(0 slides)")
        self.slide_count_label.pack(side="right", padx=10)

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

        self.transition_label = ttk.Label(self.details_frame, text="Transition: -", font=("Arial", 10, "bold"))
        self.transition_label.pack(anchor="w")

        ttk.Separator(self.details_frame, orient="horizontal").pack(fill="x", pady=5)

        self.common_label = ttk.Label(self.details_frame, text="S∩S: -", foreground="green")
        self.common_label.pack(anchor="w")

        self.s1_only_label = ttk.Label(self.details_frame, text="S-S: -", foreground="blue")
        self.s1_only_label.pack(anchor="w")

        self.s2_only_label = ttk.Label(self.details_frame, text="S-S: -", foreground="purple")
        self.s2_only_label.pack(anchor="w")

    def _go_first(self):
        if self.current_page > 0:
            self.current_page = 0
            self._render_current_page()

    def _go_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_current_page()

    def _go_next(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._render_current_page()

    def _go_last(self):
        if self.current_page < self.total_pages - 1:
            self.current_page = self.total_pages - 1
            self._render_current_page()

    def _update_nav_buttons(self):
        """Update navigation button states."""
        self.btn_first.config(state="normal" if self.current_page > 0 else "disabled")
        self.btn_prev.config(state="normal" if self.current_page > 0 else "disabled")
        self.btn_next.config(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
        self.btn_last.config(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
        self.page_label.config(text=f"Page {self.current_page + 1} / {self.total_pages}")

    def load_slideshow(self, slideshow: Slideshow):
        """Load and display a slideshow."""
        self.slideshow = slideshow
        self.selected_index = None
        self.current_page = 0

        # Calculate total pages
        total_slides = len(slideshow.slides) if slideshow else 0
        self.total_pages = max(1, (total_slides + PAGE_SIZE - 1) // PAGE_SIZE)

        # Update slide count label
        self.slide_count_label.config(text=f"({total_slides} slides)")

        self._render_current_page()

    def _render_current_page(self):
        """Render only the slides for the current page."""
        # Clear existing cards
        for card in self.cards:
            card.destroy()
        self.cards = []

        if not self.slideshow:
            return

        # Calculate slide range for current page
        start_idx = self.current_page * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, len(self.slideshow.slides))

        # Create cards only for current page
        for i in range(start_idx, end_idx):
            slide = self.slideshow.slides[i]
            card = SlideCard(self.scroll_frame, slide, i, self._on_slide_clicked)
            card.pack(side="left", padx=5, pady=5)
            self.cards.append(card)

        self._update_nav_buttons()

    def _on_slide_clicked(self, index: int):
        """Handle slide selection."""
        self.selected_index = index
        slide = self.slideshow.slides[index]

        # Update details
        tags_str = ", ".join(sorted(slide.tags))
        self.tags_label.config(text=f"Tags: [{tags_str}]")

        # Show transition score to next slide with interest factor breakdown
        if index < len(self.slideshow.slides) - 1:
            next_slide = self.slideshow.slides[index + 1]
            score = calculate_transition_score(slide, next_slide)

            # Calculate interest factor components
            common = slide.tags & next_slide.tags
            only_s1 = slide.tags - next_slide.tags
            only_s2 = next_slide.tags - slide.tags

            # Format the breakdown
            common_str = ", ".join(sorted(common)) if common else "∅"
            s1_str = ", ".join(sorted(only_s1)) if only_s1 else "∅"
            s2_str = ", ".join(sorted(only_s2)) if only_s2 else "∅"

            self.transition_label.config(
                text=f"S{index}→S{index+1}: min({len(common)}, {len(only_s1)}, {len(only_s2)}) = {score}"
            )
            self.common_label.config(text=f"S{index}∩S{index+1} ({len(common)}): {common_str}")
            self.s1_only_label.config(text=f"S{index}-S{index+1} ({len(only_s1)}): {s1_str}")
            self.s2_only_label.config(text=f"S{index+1}-S{index} ({len(only_s2)}): {s2_str}")
        else:
            self.transition_label.config(text="Transition: (last slide)")
            self.common_label.config(text="S∩S: -")
            self.s1_only_label.config(text="S-S: -")
            self.s2_only_label.config(text="S-S: -")

    def clear(self):
        """Clear the viewer."""
        for card in self.cards:
            card.destroy()
        self.cards = []
        self.slideshow = None
        self.current_page = 0
        self.total_pages = 1
        self.page_label.config(text="Page 0 / 0")
        self.slide_count_label.config(text="(0 slides)")
        self.tags_label.config(text="Tags: -")
        self.transition_label.config(text="Transition: -")
        self.common_label.config(text="S∩S: -")
        self.s1_only_label.config(text="S-S: -")
        self.s2_only_label.config(text="S-S: -")
