import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class StatsPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.scores = []
        self._setup_ui()

    def _setup_ui(self):
        # Matplotlib figure
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Iteration")
        self.ax.set_ylabel("Score")
        self.ax.set_title("Score Evolution")
        self.line, = self.ax.plot([], [], 'b-')

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Best score label
        self.best_label = ttk.Label(self, text="Best Score: -", font=("Arial", 12, "bold"))
        self.best_label.pack(pady=5)

    def update_plot(self, history: list[int]):
        """Update the plot with new score history."""
        self.scores = history
        x = list(range(len(history)))
        self.line.set_data(x, history)

        if history:
            self.ax.relim()
            self.ax.autoscale_view()

            best = max(history)
            self.best_label.config(text=f"Best Score: {best}")

        self.canvas.draw()

    def append_score(self, score: int):
        """Append a single score and update plot."""
        self.scores.append(score)
        self.update_plot(self.scores)

    def reset(self):
        """Clear the plot."""
        self.scores = []
        self.line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.best_label.config(text="Best Score: -")
