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
        self._param_schemas: dict[str, ParameterSchema] = {}
        self._error_callback: Optional[Callable[[str, str, Exception], None]] = None
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
        self._param_schemas.clear()

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
            elif param.type == bool:
                var = tk.BooleanVar(value=param.default)
                widget = ttk.Checkbutton(frame, variable=var)
                widget.pack(fill="x")
                # Store the variable instead of widget for bool
                self._param_widgets[param.name] = (var, param.type)
                self._param_schemas[param.name] = param
                continue  # Skip the generic pack/store below
            elif param.type == str and param.options:
                widget = ttk.Combobox(
                    frame,
                    values=param.options,
                    state="readonly"
                )
                widget.set(param.default)
            else:
                widget = ttk.Entry(frame)
                widget.insert(0, str(param.default))

            widget.pack(fill="x")
            self._param_widgets[param.name] = (widget, param.type)
            self._param_schemas[param.name] = param

    def set_error_callback(self, callback: Callable[[str, str, Exception], None]):
        """Set callback for handling parameter conversion errors.

        Args:
            callback: Function called as callback(param_name, invalid_value, exception)
        """
        self._error_callback = callback

    def get_config(self) -> dict:
        """Return current configuration (algorithm + parameters).

        If a parameter value cannot be converted to its target type,
        returns the default value from the parameter schema.
        """
        params = {}
        for name, (widget, ptype) in self._param_widgets.items():
            value = widget.get()
            try:
                params[name] = ptype(value)
            except (ValueError, TypeError) as e:
                # Get default value from schema
                default = self._param_schemas[name].default
                params[name] = default

                # Notify error callback if set
                if self._error_callback:
                    self._error_callback(name, value, e)

        return {
            "algorithm_name": self.algo_combo.get(),
            "parameters": params
        }
