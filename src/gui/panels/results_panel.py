import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from typing import Optional
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.experiment.runner import ExperimentResult


class ResultsPanel(ttk.Frame):
    """Tab "Resultados" with statistics display and export."""

    def __init__(self, parent):
        super().__init__(parent)
        self._experiment_result: Optional[ExperimentResult] = None
        self._summaries: list[dict] = []
        self._setup_ui()

    def _setup_ui(self):
        # Top frame for export buttons
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=5, pady=5)

        self.export_csv_btn = ttk.Button(top_frame, text="Export CSV", command=self._export_csv)
        self.export_csv_btn.pack(side="left", padx=2)

        self.export_latex_btn = ttk.Button(top_frame, text="Export LaTeX", command=self._export_latex)
        self.export_latex_btn.pack(side="left", padx=2)

        self.save_report_btn = ttk.Button(top_frame, text="Save Report", command=self._save_report)
        self.save_report_btn.pack(side="left", padx=2)

        # Main content frame with horizontal paned window
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Left frame - Statistics table
        left_frame = ttk.LabelFrame(paned, text="Statistics", padding=5)
        paned.add(left_frame, weight=1)

        self._setup_table(left_frame)

        # Right frame - Charts
        right_frame = ttk.LabelFrame(paned, text="Charts", padding=5)
        paned.add(right_frame, weight=2)

        self._setup_charts(right_frame)

    def _setup_table(self, parent):
        """Set up the statistics Treeview table."""
        columns = ("algorithm", "runs", "mean", "std", "best", "worst", "time")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

        # Define column headings
        self.tree.heading("algorithm", text="Algorithm")
        self.tree.heading("runs", text="Runs")
        self.tree.heading("mean", text="Mean")
        self.tree.heading("std", text="Std")
        self.tree.heading("best", text="Best")
        self.tree.heading("worst", text="Worst")
        self.tree.heading("time", text="Time (s)")

        # Define column widths
        self.tree.column("algorithm", width=120, anchor="w")
        self.tree.column("runs", width=50, anchor="center")
        self.tree.column("mean", width=80, anchor="center")
        self.tree.column("std", width=80, anchor="center")
        self.tree.column("best", width=80, anchor="center")
        self.tree.column("worst", width=80, anchor="center")
        self.tree.column("time", width=80, anchor="center")

        # Add scrollbars
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def _setup_charts(self, parent):
        """Set up matplotlib charts for visualization."""
        # Create figure with two subplots side by side
        self.figure = Figure(figsize=(10, 5), dpi=100)
        self.ax_bar = self.figure.add_subplot(121)
        self.ax_box = self.figure.add_subplot(122)

        self.figure.tight_layout(pad=3.0)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def set_experiment_result(self, result: ExperimentResult):
        """Load results, update table and charts."""
        self._experiment_result = result
        self._summaries = result.get_summary()
        self._update_table()
        self._update_charts()

    def _update_table(self):
        """Populate Treeview from ExperimentResult.get_summary()."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add rows for each algorithm summary
        for summary in self._summaries:
            self.tree.insert("", "end", values=(
                summary["algorithm"],
                summary["runs"],
                f"{summary['mean_score']:.2f}",
                f"{summary['std_score']:.2f}",
                summary["best_score"],
                summary["worst_score"],
                f"{summary['mean_time']:.3f}"
            ))

    def _update_charts(self):
        """Create matplotlib visualizations."""
        # Clear previous plots
        self.ax_bar.clear()
        self.ax_box.clear()

        if not self._summaries:
            self.canvas.draw()
            return

        # Extract data
        algorithms = [s["algorithm"] for s in self._summaries]
        mean_scores = [s["mean_score"] for s in self._summaries]
        std_scores = [s["std_score"] for s in self._summaries]

        # Left chart: Bar chart of mean scores with error bars
        x_pos = range(len(algorithms))
        bars = self.ax_bar.bar(x_pos, mean_scores, yerr=std_scores,
                               capsize=5, alpha=0.7, color='steelblue',
                               error_kw={'elinewidth': 2, 'capthick': 2})
        self.ax_bar.set_xlabel("Algorithm")
        self.ax_bar.set_ylabel("Mean Score")
        self.ax_bar.set_title("Mean Scores Comparison")
        self.ax_bar.set_xticks(x_pos)
        self.ax_bar.set_xticklabels(algorithms, rotation=45, ha='right')
        self.ax_bar.grid(axis='y', alpha=0.3)

        # Right chart: Box plot of score distributions per algorithm
        # Gather all scores per algorithm
        score_distributions = []
        for summary in self._summaries:
            algo_name = summary["algorithm"]
            # Get all scores for this algorithm from the experiment runs
            scores = [
                r.result.score for r in self._experiment_result.runs
                if r.config.algorithm_name == algo_name
            ]
            score_distributions.append(scores)

        self.ax_box.boxplot(score_distributions, labels=algorithms)
        self.ax_box.set_xlabel("Algorithm")
        self.ax_box.set_ylabel("Score Distribution")
        self.ax_box.set_title("Score Distributions")
        self.ax_box.set_xticklabels(algorithms, rotation=45, ha='right')
        self.ax_box.grid(axis='y', alpha=0.3)

        self.figure.tight_layout(pad=3.0)
        self.canvas.draw()

    def _export_csv(self):
        """Save statistics to CSV file."""
        if not self._summaries:
            messagebox.showwarning("No Data", "No experiment results to export.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "w") as f:
                # Write header
                f.write("Algorithm,Runs,Mean Score,Std Score,Best,Worst,Mean Time (s)\n")

                # Write data rows
                for summary in self._summaries:
                    f.write(f"{summary['algorithm']},{summary['runs']},"
                           f"{summary['mean_score']:.4f},{summary['std_score']:.4f},"
                           f"{summary['best_score']},{summary['worst_score']},"
                           f"{summary['mean_time']:.4f}\n")

            messagebox.showinfo("Export Successful", f"CSV exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{e}")

    def _export_latex(self):
        """Save statistics as LaTeX table."""
        if not self._summaries:
            messagebox.showwarning("No Data", "No experiment results to export.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export LaTeX",
            defaultextension=".tex",
            filetypes=[("LaTeX files", "*.tex"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "w") as f:
                # Begin table environment
                f.write("\\begin{table}[htbp]\n")
                f.write("\\centering\n")

                # Column specification
                num_cols = 7
                f.write(f"\\begin{{tabular}}{{{'l' + 'c' * (num_cols - 1)}}}\n")
                f.write("\\hline\n")

                # Header row
                f.write("Algorithm & Runs & Mean Score & Std Score & Best & Worst & Mean Time (s) \\\\\n")
                f.write("\\hline\n")

                # Data rows
                for summary in self._summaries:
                    algo = summary["algorithm"].replace("_", "\\_")
                    f.write(f"{algo} & {summary['runs']} & "
                           f"{summary['mean_score']:.2f} & {summary['std_score']:.2f} & "
                           f"{summary['best_score']} & {summary['worst_score']} & "
                           f"{summary['mean_time']:.3f} \\\\\n")

                f.write("\\hline\n")
                f.write("\\end{tabular}\n")
                f.write("\\caption{Algorithm Performance Comparison}\n")
                f.write("\\label{tab:results}\n")
                f.write("\\end{table}\n")

            messagebox.showinfo("Export Successful", f"LaTeX table exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export LaTeX:\n{e}")

    def _save_report(self):
        """Create results/ directory, save JSON summary + best slideshows."""
        if not self._experiment_result:
            messagebox.showwarning("No Data", "No experiment results to save.")
            return

        # Ask for base directory
        dir_path = filedialog.askdirectory(title="Select Directory for Results")
        if not dir_path:
            return

        # Create results subdirectory
        results_dir = os.path.join(dir_path, "results")
        os.makedirs(results_dir, exist_ok=True)

        try:
            # Save JSON summary
            json_path = os.path.join(results_dir, "summary.json")
            summary_data = {
                "dataset": self._experiment_result.dataset_name,
                "timestamp": self._experiment_result.timestamp,
                "total_runs": len(self._experiment_result.runs),
                "algorithms": []
            }

            for summary in self._summaries:
                algo_data = {
                    "name": summary["algorithm"],
                    "parameters": summary["parameters"],
                    "runs": summary["runs"],
                    "mean_score": summary["mean_score"],
                    "std_score": summary["std_score"],
                    "best_score": summary["best_score"],
                    "worst_score": summary["worst_score"],
                    "mean_time": summary["mean_time"]
                }
                summary_data["algorithms"].append(algo_data)

            with open(json_path, "w") as f:
                json.dump(summary_data, f, indent=2)

            # Save best slideshows for each algorithm
            slideshows_dir = os.path.join(results_dir, "best_slideshows")
            os.makedirs(slideshows_dir, exist_ok=True)

            for summary in self._summaries:
                best_result = summary["best_result"]
                algo_name = best_result.config.algorithm_name
                slideshow = best_result.result.slideshow

                # Create filename safe version of algorithm name
                safe_name = algo_name.replace(" ", "_").replace("/", "_")
                slideshow_path = os.path.join(slideshows_dir, f"{safe_name}_best.txt")

                with open(slideshow_path, "w") as f:
                    f.write(slideshow.to_output_string())

            messagebox.showinfo("Report Saved",
                f"Report saved successfully!\n\n"
                f"Directory: {results_dir}\n"
                f"- summary.json\n"
                f"- best_slideshows/ ({len(self._summaries)} files)")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save report:\n{e}")
