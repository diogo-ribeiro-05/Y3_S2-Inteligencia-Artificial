# src/gui/app.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.gui.panels.dataset_panel import DatasetPanel
from src.gui.panels.control_panel import ControlPanel
from src.gui.panels.stats_panel import StatsPanel
from src.gui.panels.slideshow_viewer import SlideshowViewer
from src.solver.hill_climbing import HillClimbingSolver
from src.models.photo import Photo


class PhotoSlideshowApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo Slideshow Solver - Hill Climbing")
        self.root.geometry("1200x800")

        self.photos: list[Photo] = None
        self.solver: HillClimbingSolver = None
        self.best_score: int = 0

        self._setup_ui()

    def _setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.dataset_panel = DatasetPanel(self.root, self._on_dataset_loaded)
        self.dataset_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.slideshow_viewer = SlideshowViewer(self.root)
        self.slideshow_viewer.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.control_panel = ControlPanel(self.root, self._on_run, self._on_stop)
        self.control_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.stats_panel = StatsPanel(self.root)
        self.stats_panel.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

    def _on_dataset_loaded(self, photos: list[Photo]):
        self.photos = photos
        self.solver = HillClimbingSolver(photos)
        self.stats_panel.reset()
        self.slideshow_viewer.clear()
        self.best_score = 0
        self.control_panel.reset()

    def _on_run(self):
        if not self.solver:
            messagebox.showwarning("Warning", "Please load a dataset first")
            self.control_panel.set_running(False)
            return

        max_iter = self.control_panel.get_iterations()
        self.stats_panel.reset()
        self.best_score = 0
        self.control_panel.set_running(True)

        def run_solver():
            def callback(iteration: int, score: int):
                if score > self.best_score:
                    self.best_score = score
                self.root.after(0, lambda: self._update_ui(iteration, max_iter, score))

            result = self.solver.solve(max_iterations=max_iter, callback=callback)
            self.root.after(0, lambda: self._solver_finished(result))

        thread = threading.Thread(target=run_solver, daemon=True)
        thread.start()

    def _on_stop(self):
        if self.solver:
            self.solver.request_stop()

    def _update_ui(self, iteration: int, max_iter: int, score: int):
        self.control_panel.update_progress(iteration, max_iter, score, self.best_score)
        self.stats_panel.append_score(score)

    def _solver_finished(self, result):
        self.control_panel.set_running(False)
        self.slideshow_viewer.load_slideshow(result)

        final_score = result.calculate_score()
        messagebox.showinfo(
            "Complete",
            f"Optimization complete!\nFinal score: {final_score}"
        )


def create_app() -> tk.Tk:
    """Create and return the main application window."""
    root = tk.Tk()
    app = PhotoSlideshowApp(root)
    return root
