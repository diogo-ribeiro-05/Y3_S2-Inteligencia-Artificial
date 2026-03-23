# src/gui/panels/explore_panel.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import Callable, Optional
from src.models.photo import Photo
from src.models.slideshow import Slideshow
from src.algorithms.registry import AlgorithmRegistry
from src.algorithms.base import AlgorithmResult
from src.io.parser import parse_input
from src.gui.widgets.algorithm_config import AlgorithmConfigWidget
from src.gui.panels.stats_panel import StatsPanel
from src.gui.panels.slideshow_viewer import SlideshowViewer


class ExplorePanel(ttk.Frame):
    """Tab "Explorar" for single algorithm runs with real-time visualization."""

    def __init__(self, parent, on_dataset_loaded: Optional[Callable] = None):
        super().__init__(parent)
        self.on_dataset_loaded = on_dataset_loaded
        self.photos: list[Photo] = []
        self.dataset_name: str = ""
        self.current_solver = None
        self.solver_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.max_iterations = 0
        self._setup_ui()

    def _setup_ui(self):
        # Main container with two columns
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Left panel - Controls
        left_frame = ttk.Frame(self, padding=10)
        left_frame.grid(row=0, column=0, sticky="ns")

        # Dataset section
        dataset_frame = ttk.LabelFrame(left_frame, text="Dataset", padding=5)
        dataset_frame.pack(fill="x", pady=(0, 10))

        self.dataset_label = ttk.Label(dataset_frame, text="No dataset loaded")
        self.dataset_label.pack(anchor="w")

        self.load_btn = ttk.Button(
            dataset_frame,
            text="Load Dataset",
            command=self._load_dataset
        )
        self.load_btn.pack(fill="x", pady=(5, 0))

        # Algorithm configuration
        self.algo_config = AlgorithmConfigWidget(left_frame)
        self.algo_config.pack(fill="x", pady=(0, 10))

        # Run controls
        controls_frame = ttk.Frame(left_frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        self.run_btn = ttk.Button(
            controls_frame,
            text="Run",
            command=self._on_run,
            state="disabled"
        )
        self.run_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.stop_btn = ttk.Button(
            controls_frame,
            text="Stop",
            command=self._on_stop,
            state="disabled"
        )
        self.stop_btn.pack(side="left", fill="x", expand=True)

        # Progress section
        progress_frame = ttk.LabelFrame(left_frame, text="Progress", padding=5)
        progress_frame.pack(fill="x", pady=(0, 10))

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode="determinate",
            length=200
        )
        self.progress_bar.pack(fill="x")

        self.iteration_label = ttk.Label(progress_frame, text="Iteration: 0 / 0")
        self.iteration_label.pack(anchor="w")

        # Score section
        score_frame = ttk.LabelFrame(left_frame, text="Score", padding=5)
        score_frame.pack(fill="x")

        self.current_score_label = ttk.Label(
            score_frame,
            text="Current: -",
            font=("Arial", 10)
        )
        self.current_score_label.pack(anchor="w")

        self.best_score_label = ttk.Label(
            score_frame,
            text="Best: -",
            font=("Arial", 12, "bold")
        )
        self.best_score_label.pack(anchor="w")

        self.time_label = ttk.Label(score_frame, text="Time: -")
        self.time_label.pack(anchor="w")

        # Right panel - Visualization
        right_frame = ttk.Frame(self, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # Stats panel (real-time chart)
        stats_container = ttk.LabelFrame(right_frame, text="Score Evolution", padding=5)
        stats_container.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        stats_container.columnconfigure(0, weight=1)
        stats_container.rowconfigure(0, weight=1)

        self.stats_panel = StatsPanel(stats_container)
        self.stats_panel.grid(row=0, column=0, sticky="nsew")

        # Slideshow viewer (result visualization)
        slideshow_container = ttk.LabelFrame(right_frame, text="Slideshow Result", padding=5)
        slideshow_container.grid(row=1, column=0, sticky="nsew")
        slideshow_container.columnconfigure(0, weight=1)
        slideshow_container.rowconfigure(0, weight=1)

        self.slideshow_viewer = SlideshowViewer(slideshow_container)
        self.slideshow_viewer.grid(row=0, column=0, sticky="nsew")

    def _load_dataset(self):
        """Open file dialog to load a dataset."""
        filepath = filedialog.askopenfilename(
            title="Select Dataset File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            self.photos = parse_input(content)

            # Extract dataset name from filename
            import os
            self.dataset_name = os.path.basename(filepath)
            self.dataset_label.config(text=f"{self.dataset_name} ({len(self.photos)} photos)")

            # Enable run button
            self.run_btn.config(state="normal")

            # Clear previous results
            self.stats_panel.reset()
            self.slideshow_viewer.clear()
            self._reset_score_labels()

            # Notify callback
            if self.on_dataset_loaded:
                self.on_dataset_loaded(self.photos, self.dataset_name)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset:\n{str(e)}")

    def _on_run(self):
        """Start algorithm execution in background thread."""
        if not self.photos:
            messagebox.showwarning("Warning", "Please load a dataset first")
            return

        if self.is_running:
            return

        # Get algorithm configuration
        config = self.algo_config.get_config()
        algo_name = config["algorithm_name"]
        params = config["parameters"]

        if not algo_name:
            messagebox.showwarning("Warning", "Please select an algorithm")
            return

        # Get algorithm class and create instance
        algo_class = AlgorithmRegistry.get(algo_name)
        if not algo_class:
            messagebox.showerror("Error", f"Algorithm '{algo_name}' not found")
            return

        self.current_solver = algo_class()

        # Reset UI
        self.stats_panel.reset()
        self.slideshow_viewer.clear()
        self._reset_score_labels()

        # Get max iterations for progress bar
        self.max_iterations = params.get("max_iterations", 10000)
        self.progress_bar["maximum"] = self.max_iterations
        self.progress_bar["value"] = 0

        # Update button states
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.load_btn.config(state="disabled")

        self.is_running = True

        # Start algorithm in background thread
        self.solver_thread = threading.Thread(
            target=self._run_solver,
            args=(self.photos, params),
            daemon=True
        )
        self.solver_thread.start()

    def _run_solver(self, photos: list[Photo], params: dict):
        """Run the solver in background thread."""
        try:
            result = self.current_solver.solve(
                photos,
                callback=self._solver_callback,
                **params
            )
            # Schedule completion on main thread
            self.after(0, lambda: self._solver_finished(result))
        except Exception as e:
            # Schedule error handling on main thread
            self.after(0, lambda: self._solver_error(e))

    def _solver_callback(self, iteration: int, score: int):
        """Callback from solver for progress updates."""
        # Schedule UI update on main thread
        self.after(0, lambda: self._update_ui(iteration, self.max_iterations, score))

    def _on_stop(self):
        """Request algorithm to stop."""
        if self.current_solver:
            self.current_solver.request_stop()
        self.stop_btn.config(state="disabled")

    def _update_ui(self, iteration: int, max_iter: int, score: int):
        """Update progress and stats display."""
        # Update progress bar
        progress = min(iteration, max_iter)
        self.progress_bar["value"] = progress

        # Update iteration label
        self.iteration_label.config(text=f"Iteration: {iteration} / {max_iter}")

        # Update score labels
        self.current_score_label.config(text=f"Current: {score}")

        # Update stats panel
        self.stats_panel.append_score(score)

    def _solver_finished(self, result: AlgorithmResult):
        """Handle algorithm completion."""
        self.is_running = False

        # Update button states
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.load_btn.config(state="normal")

        # Update final scores
        self.best_score_label.config(text=f"Best: {result.score}")
        self.time_label.config(text=f"Time: {result.execution_time:.2f}s")

        # Update stats panel with full history
        self.stats_panel.update_plot(result.history)

        # Show slideshow result
        self.slideshow_viewer.load_slideshow(result.slideshow)

        # Show completion message
        messagebox.showinfo(
            "Complete",
            f"Algorithm finished!\n\n"
            f"Final Score: {result.score}\n"
            f"Execution Time: {result.execution_time:.2f}s\n"
            f"Iterations: {len(result.history)}"
        )

    def _solver_error(self, error: Exception):
        """Handle algorithm error."""
        self.is_running = False

        # Update button states
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.load_btn.config(state="normal")

        messagebox.showerror("Error", f"Algorithm failed:\n{str(error)}")

    def _reset_score_labels(self):
        """Reset score labels to default state."""
        self.current_score_label.config(text="Current: -")
        self.best_score_label.config(text="Best: -")
        self.time_label.config(text="Time: -")
        self.iteration_label.config(text="Iteration: 0 / 0")
        self.progress_bar["value"] = 0

    def set_dataset(self, photos: list[Photo], dataset_name: str):
        """External setter for dataset."""
        self.photos = photos
        self.dataset_name = dataset_name
        self.dataset_label.config(text=f"{dataset_name} ({len(photos)} photos)")

        if photos:
            self.run_btn.config(state="normal")
            self.stats_panel.reset()
            self.slideshow_viewer.clear()
            self._reset_score_labels()
