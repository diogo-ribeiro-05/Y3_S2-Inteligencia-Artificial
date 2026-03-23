# src/gui/widgets/algorithm_config.py
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from src.algorithms.base import ParameterSchema
from src.algorithms.registry import AlgorithmRegistry


class AlgorithmConfigWidget(ttk.Frame):
    """Widget for configuring an algorithm with dynamic parameters."""

    def __init__(self, parent, on_algorithm_change: Optional[Callable] = None):
        super().__init__(parent)
        self.on_algorithm_change = on_algorithm_change
        self._param_widgets: dict[str, tuple[tk.Widget, type]] = {}
        self._setup_ui()

    def _setup_ui(self):
        ttk.Label(self, text="Algorithm:").pack(anchor="w")
        self.algo_combo = ttk.Combobox(
            self,
            values=AlgorithmRegistry.get_names(),
            state="readonly"
        )
        self.algo_combo.pack(fill="x", pady=(0, 10))
        self.algo_combo.bind("<<ComboboxSelected>>", self._on_algo_selected)

        self.params_frame = ttk.LabelFrame(self, text="Parameters")
        self.params_frame.pack(fill="x", pady=10)

        if AlgorithmRegistry.get_names():
            self.algo_combo.current(0)
            self._on_algo_selected(None)

    def _on_algo_selected(self, event):
        algo_name = self.algo_combo.get()
        if not algo_name:
            return
        algo_class = AlgorithmRegistry.get(algo_name)
        self._build_param_fields(algo_class.parameters)

        if self.on_algorithm_change:
            self.on_algorithm_change(algo_name)

    def _build_param_fields(self, parameters: list[ParameterSchema]):
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self._param_widgets.clear()

        for param in parameters:
            frame = ttk.Frame(self.params_frame)
            frame.pack(fill="x", padx=5, pady=5)

            ttk.Label(frame, text=param.name).pack(anchor="w")

            if param.type == int:
                widget = ttk.Spinbox(
                    frame,
                    from_=param.min_value or 0,
                    to=param.max_value or 999999,
                    value=param.default
                )
            elif param.type == float:
                widget = ttk.Spinbox(
                    frame,
                    from_=param.min_value or 0,
                    to=param.max_value or 999999,
                    increment=0.01,
                    value=param.default
                )
            else:
                widget = ttk.Entry(frame)
                widget.insert(0, str(param.default))

            widget.pack(fill="x")
            self._param_widgets[param.name] = (widget, param.type)

    def get_config(self) -> dict:
        """Return current configuration (algorithm + parameters)."""
        params = {}
        for name, (widget, ptype) in self._param_widgets.items():
            value = widget.get()
            params[name] = ptype(value)

        return {
            "algorithm_name": self.algo_combo.get(),
            "parameters": params
        }
