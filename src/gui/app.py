# src/gui/app.py
import tkinter as tk
from tkinter import ttk

# Import algorithms module to trigger registration
import src.algorithms  # noqa: F401

from src.gui.panels.explore_panel import ExplorePanel
from src.gui.panels.experiment_panel import ExperimentPanel
from src.gui.panels.results_panel import ResultsPanel
from src.models.photo import Photo


class PhotoSlideshowApp:
    """Main application with 3-tab Notebook interface."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo Slideshow Solver")
        self.root.geometry("1400x900")

        self._setup_ui()

    def _setup_ui(self):
        """Set up the main UI with Notebook tabs."""
        # Create Notebook as main container
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 1: Explore
        self.explore_panel = ExplorePanel(
            self.notebook,
            on_dataset_loaded=self._on_dataset_loaded
        )
        self.notebook.add(self.explore_panel, text="Explore")

        # Tab 2: Experiment
        self.experiment_panel = ExperimentPanel(self.notebook)
        self.notebook.add(self.experiment_panel, text="Experiment")

        # Tab 3: Results
        self.results_panel = ResultsPanel(self.notebook)
        self.notebook.add(self.results_panel, text="Results")

        # Bind experiment completion callback
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_dataset_loaded(self, photos: list[Photo], dataset_name: str):
        """Callback when dataset is loaded in ExplorePanel.

        Also sets the dataset in ExperimentPanel for consistency.
        """
        self.experiment_panel.set_dataset(photos, dataset_name)

    def _on_tab_changed(self, event):
        """Handle tab change events.

        When switching to Results tab, check if experiment has finished
        and pass result to ResultsPanel.
        """
        current_tab = self.notebook.index(self.notebook.select())

        # Tab index 2 is Results
        if current_tab == 2:
            experiment_result = self.experiment_panel.get_experiment_result()
            if experiment_result:
                self.results_panel.set_experiment_result(experiment_result)


def create_app() -> tk.Tk:
    """Create and return the main application window."""
    root = tk.Tk()
    app = PhotoSlideshowApp(root)
    return root
