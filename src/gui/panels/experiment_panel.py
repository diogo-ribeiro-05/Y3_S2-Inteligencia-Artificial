import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
from typing import Optional
from src.experiment.runner import ExperimentRunner, AlgorithmConfig, ExperimentResult
from src.algorithms.registry import AlgorithmRegistry
from src.algorithms.base import ParameterSchema
from src.io.parser import parse_input
from src.models.photo import Photo


class ExperimentPanel(ttk.Frame):
    """Tab "Experimento" for batch comparison with multiple runs."""

    def __init__(self, parent):
        super().__init__(parent)
        self._runner: Optional[ExperimentRunner] = None
        self._experiment_result: Optional[ExperimentResult] = None
        self._experiment_thread: Optional[threading.Thread] = None
        self._is_running = False
        self._photos: list[Photo] = []
        self._dataset_name: str = ""
        self._progress_labels: dict[str, ttk.Label] = {}
        self._algo_param_widgets: dict[str, dict[str, tuple[tk.Widget, type]]] = {}
        self._setup_ui()

    def _setup_ui(self):
        # Main horizontal paned window
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Left frame - controls
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        # Right frame - progress and log
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)

        # Setup right panel FIRST (creates algo_progress_frame)
        self._setup_right_panel(right_frame)
        # Then setup left panel (uses algo_progress_frame)
        self._setup_left_panel(left_frame)

    def _setup_left_panel(self, parent):
        # Dataset section
        dataset_frame = ttk.LabelFrame(parent, text="Dataset", padding=5)
        dataset_frame.pack(fill="x", pady=(0, 10))

        self.dataset_label = ttk.Label(dataset_frame, text="No dataset loaded")
        self.dataset_label.pack(anchor="w")

        self.load_btn = ttk.Button(dataset_frame, text="Load Dataset", command=self._load_dataset)
        self.load_btn.pack(anchor="w", pady=(5, 0))

        # Runs configuration
        config_frame = ttk.LabelFrame(parent, text="Configuration", padding=5)
        config_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(config_frame, text="Runs per algorithm:").pack(anchor="w")
        self.runs_var = tk.StringVar(value="5")
        self.runs_entry = ttk.Entry(config_frame, textvariable=self.runs_var, width=10)
        self.runs_entry.pack(anchor="w", pady=(0, 5))

        # Algorithm selection with parameters
        algo_frame = ttk.LabelFrame(parent, text="Algorithms & Parameters", padding=5)
        algo_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Scrollable frame for algorithms
        canvas = tk.Canvas(algo_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(algo_frame, orient="vertical", command=canvas.yview)
        self.algo_inner_frame = ttk.Frame(canvas)

        self.algo_inner_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.algo_inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate algorithms with their parameters
        self._setup_algorithm_sections()

        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x")

        self.run_btn = ttk.Button(btn_frame, text="Run Experiment", command=self._on_run)
        self.run_btn.pack(side="left", padx=2)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self._on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=2)

    def _setup_right_panel(self, parent):
        # Overall progress
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=5)
        progress_frame.pack(fill="x", pady=(0, 10))

        self.overall_progress_var = tk.DoubleVar(value=0)
        self.overall_progress_bar = ttk.Progressbar(
            progress_frame, variable=self.overall_progress_var, maximum=100
        )
        self.overall_progress_bar.pack(fill="x", pady=(0, 5))

        self.overall_label = ttk.Label(progress_frame, text="Overall: 0 / 0 runs")
        self.overall_label.pack(anchor="w")

        # Per-algorithm progress labels frame
        self.algo_progress_frame = ttk.LabelFrame(parent, text="Algorithm Progress", padding=5)
        self.algo_progress_frame.pack(fill="x", pady=(0, 10))

        # Log area
        log_frame = ttk.LabelFrame(parent, text="Log", padding=5)
        log_frame.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def _setup_algorithm_sections(self):
        """Create algorithm sections with checkboxes and parameter widgets."""
        self.algo_vars: dict[str, tk.BooleanVar] = {}

        for algo_name in AlgorithmRegistry.get_names():
            algo_class = AlgorithmRegistry.get(algo_name)

            # Create a frame for this algorithm
            algo_section = ttk.Frame(self.algo_inner_frame)
            algo_section.pack(fill="x", pady=5, padx=5)

            # Checkbox for algorithm selection
            var = tk.BooleanVar(value=True)
            self.algo_vars[algo_name] = var
            cb = ttk.Checkbutton(algo_section, text=algo_name, variable=var)
            cb.pack(anchor="w")

            # Parameters frame (indented)
            params_frame = ttk.Frame(algo_section)
            params_frame.pack(fill="x", padx=(20, 0), pady=(2, 0))

            # Create parameter widgets for this algorithm
            self._algo_param_widgets[algo_name] = {}
            for param in algo_class.parameters:
                self._create_param_widget(params_frame, algo_name, param)

            # Also create progress label for this algorithm
            label = ttk.Label(self.algo_progress_frame, text=f"{algo_name}: -")
            label.pack(anchor="w")
            self._progress_labels[algo_name] = label

    def _create_param_widget(self, parent, algo_name: str, param: ParameterSchema):
        """Create a widget for a single parameter."""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)

        ttk.Label(frame, text=f"{param.name}:", width=15, anchor="w").pack(side="left")

        if param.type == int:
            widget = ttk.Spinbox(
                frame,
                from_=param.min_value or 0,
                to=param.max_value or 999999,
                width=10
            )
            widget.set(param.default)
        elif param.type == float:
            widget = ttk.Spinbox(
                frame,
                from_=param.min_value or 0,
                to=param.max_value or 999999,
                increment=0.01,
                width=10
            )
            widget.set(param.default)
        else:
            widget = ttk.Entry(frame, width=12)
            widget.insert(0, str(param.default))

        widget.pack(side="left", padx=(5, 0))
        self._algo_param_widgets[algo_name][param.name] = (widget, param.type)

    def _get_algo_params(self, algo_name: str) -> dict:
        """Get configured parameters for an algorithm."""
        params = {}
        if algo_name not in self._algo_param_widgets:
            return params

        for param_name, (widget, ptype) in self._algo_param_widgets[algo_name].items():
            try:
                value = widget.get()
                params[param_name] = ptype(value)
            except (ValueError, tk.TclError):
                # Fall back to default from algorithm class
                algo_class = AlgorithmRegistry.get(algo_name)
                for param in algo_class.parameters:
                    if param.name == param_name:
                        params[param_name] = param.default
                        break
        return params

    def _load_dataset(self):
        """Open file dialog and create ExperimentRunner."""
        filepath = filedialog.askopenfilename(
            title="Load Dataset",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "r") as f:
                content = f.read()
            photos = parse_input(content)
            self.set_dataset(photos, filepath.split("/")[-1])
            self._log(f"Loaded dataset: {self._dataset_name} ({len(photos)} photos)")
        except Exception as e:
            self._log(f"Error loading dataset: {e}")

    def _on_run(self):
        """Start experiment with all selected algorithms and their parameters."""
        if not self._photos:
            self._log("Error: No dataset loaded")
            return

        # Get selected algorithms with their configured parameters
        selected_configs = []
        for algo_name, var in self.algo_vars.items():
            if var.get():
                params = self._get_algo_params(algo_name)
                selected_configs.append(AlgorithmConfig(algo_name, params))

        if not selected_configs:
            self._log("Error: No algorithms selected")
            return

        # Get runs per algorithm
        try:
            runs_per_algo = int(self.runs_var.get())
            if runs_per_algo < 1:
                raise ValueError("Runs must be at least 1")
        except ValueError as e:
            self._log(f"Error: Invalid runs value - {e}")
            return

        # Create experiment runner
        self._runner = ExperimentRunner(self._photos, self._dataset_name)

        # Update UI state
        self._is_running = True
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.load_btn.config(state="disabled")

        # Reset progress displays
        self.overall_progress_var.set(0)
        for algo_name in self.algo_vars:
            if algo_name in self._progress_labels:
                self._progress_labels[algo_name].config(text=f"{algo_name}: 0 / {runs_per_algo}")

        total_runs = len(selected_configs) * runs_per_algo
        self.overall_label.config(text=f"Overall: 0 / {total_runs} runs")

        self._log(f"Starting experiment with {len(selected_configs)} algorithms, {runs_per_algo} runs each")
        for config in selected_configs:
            params_str = ", ".join(f"{k}={v}" for k, v in config.parameters.items())
            self._log(f"  - {config.algorithm_name} ({params_str})")

        # Start experiment in background thread
        self._experiment_thread = threading.Thread(
            target=self._run_experiment_thread,
            args=(selected_configs, runs_per_algo),
            daemon=True
        )
        self._experiment_thread.start()

    def _run_experiment_thread(self, configs: list[AlgorithmConfig], runs_per_algo: int):
        """Run experiment in background thread."""
        try:
            result = self._runner.run_experiment(
                configs=configs,
                runs_per_config=runs_per_algo,
                progress_callback=self._progress_callback
            )
            self.after(0, lambda: self._experiment_finished(result))
        except Exception as e:
            self.after(0, lambda: self._log(f"Experiment error: {e}"))
            self.after(0, self._reset_ui_state)

    def _progress_callback(self, algo_name: str, run_num: int, runs_total: int, completed: int, total: int):
        """Callback for progress updates from ExperimentRunner."""
        # Schedule UI update on main thread
        self.after(0, lambda: self._update_progress(algo_name, run_num, runs_total, completed, total))

    def _on_stop(self):
        """Request experiment stop."""
        if self._runner:
            self._runner.request_stop()
            self._log("Stop requested...")
            self.stop_btn.config(state="disabled")

    def _log(self, message: str):
        """Append message to log area."""
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _update_progress(self, algo_name: str, run_num: int, runs_total: int, completed: int, total: int):
        """Update UI with progress information."""
        # Update per-algorithm label
        if algo_name in self._progress_labels:
            self._progress_labels[algo_name].config(text=f"{algo_name}: {run_num} / {runs_total}")

        # Update overall progress
        progress_percent = (completed / total) * 100 if total > 0 else 0
        self.overall_progress_var.set(progress_percent)
        self.overall_label.config(text=f"Overall: {completed} / {total} runs")

        # Log progress
        self._log(f"{algo_name}: Run {run_num}/{runs_total} completed (Total: {completed}/{total})")

    def _experiment_finished(self, result: ExperimentResult):
        """Handle experiment completion."""
        self._experiment_result = result
        self._is_running = False
        self._reset_ui_state()

        # Log summary
        self._log("=" * 50)
        self._log("Experiment completed!")
        self._log(f"Dataset: {result.dataset_name}")
        self._log(f"Total runs: {len(result.runs)}")
        self._log("")

        for summary in result.get_summary():
            self._log(f"{summary['algorithm']}:")
            self._log(f"  Parameters: {summary['parameters']}")
            self._log(f"  Mean score: {summary['mean_score']:.2f} (+/- {summary['std_score']:.2f})")
            self._log(f"  Best score: {summary['best_score']}")
            self._log(f"  Worst score: {summary['worst_score']}")
            self._log(f"  Mean time: {summary['mean_time']:.3f}s")

        self._log("=" * 50)

    def _reset_ui_state(self):
        """Reset UI to non-running state."""
        self._is_running = False
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.load_btn.config(state="normal")

    def set_dataset(self, photos: list[Photo], dataset_name: str):
        """External setter for dataset."""
        self._photos = photos
        self._dataset_name = dataset_name
        self.dataset_label.config(text=f"{dataset_name} ({len(photos)} photos)")

    def get_experiment_result(self) -> Optional[ExperimentResult]:
        """Return last experiment result for ResultsPanel."""
        return self._experiment_result
