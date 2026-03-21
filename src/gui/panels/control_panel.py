import tkinter as tk
from tkinter import ttk
from typing import Callable


class ControlPanel(ttk.Frame):
    def __init__(self, parent, on_run: Callable, on_stop: Callable):
        super().__init__(parent)
        self.on_run = on_run
        self.on_stop = on_stop
        self._is_running = False
        self._setup_ui()

    def _setup_ui(self):
        # Iterations input
        iter_frame = ttk.Frame(self)
        iter_frame.pack(anchor="w", fill="x", pady=5)

        ttk.Label(iter_frame, text="Max Iterations:").pack(side="left")
        self.iterations_var = tk.StringVar(value="10000")
        self.iterations_entry = ttk.Entry(iter_frame, textvariable=self.iterations_var, width=10)
        self.iterations_entry.pack(side="left", padx=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(anchor="w", fill="x", pady=10)

        self.run_btn = ttk.Button(btn_frame, text="Run", command=self._run_clicked)
        self.run_btn.pack(side="left", padx=2)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self._stop_clicked, state="disabled")
        self.stop_btn.pack(side="left", padx=2)

        # Progress bar
        ttk.Label(self, text="Progress:").pack(anchor="w", pady=(10, 0))
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=5)

        # Scores
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        self.current_label = ttk.Label(self, text="Current: -")
        self.current_label.pack(anchor="w")

        self.best_label = ttk.Label(self, text="Best: -")
        self.best_label.pack(anchor="w")

    def _run_clicked(self):
        self._is_running = True
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.on_run()

    def _stop_clicked(self):
        self._is_running = False
        self.on_stop()

    def get_iterations(self) -> int:
        try:
            return int(self.iterations_var.get())
        except ValueError:
            return 10000

    def update_progress(self, iteration: int, max_iterations: int, current_score: int, best_score: int):
        progress = (iteration / max_iterations) * 100
        self.progress_var.set(progress)
        self.current_label.config(text=f"Current: {current_score}")
        self.best_label.config(text=f"Best: {best_score}")

    def reset(self):
        self._is_running = False
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress_var.set(0)
        self.current_label.config(text="Current: -")
        self.best_label.config(text="Best: -")

    def set_running(self, running: bool):
        self._is_running = running
        if running:
            self.run_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        else:
            self.run_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
