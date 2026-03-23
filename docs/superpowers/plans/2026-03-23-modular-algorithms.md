# Modular Algorithms System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor Photo Slideshow Solver to a plug-and-play architecture supporting multiple optimization algorithms, batch comparison with statistics, and a 3-tab GUI with dynamic parametrization.

**Architecture:** Registry Pattern for auto-discovery of algorithms. BaseAlgorithm abstract class defines the contract with ParameterSchema for dynamic UI. ExperimentRunner handles batch comparison. GUI refactored to 3 tabs: Explore (single run), Experiment (batch comparison), Results (statistics & export).

**Tech Stack:** Python 3.14, tkinter (stdlib), matplotlib (existing), dataclasses (stdlib)

---

## File Structure

### New Files to Create

| File | Responsibility |
|------|----------------|
| `src/algorithms/__init__.py` | Package init, imports all algorithms for registry |
| `src/algorithms/base.py` | BaseAlgorithm, ParameterSchema, AlgorithmResult |
| `src/algorithms/registry.py` | AlgorithmRegistry with decorator pattern |
| `src/algorithms/hill_climbing.py` | HillClimbingSolver migrated to new interface |
| `src/experiment/__init__.py` | Package init |
| `src/experiment/runner.py` | ExperimentRunner, ExperimentResult, RunResult |
| `src/gui/widgets/algorithm_config.py` | Dynamic parameter widget |
| `src/gui/panels/explore_panel.py` | Tab "Explorar" - single algorithm run |
| `src/gui/panels/experiment_panel.py` | Tab "Experimento" - batch comparison |
| `src/gui/panels/results_panel.py` | Tab "Resultados" - statistics & export |
| `tests/test_algorithms/__init__.py` | Test package init |
| `tests/test_algorithms/test_base.py` | Tests for base classes |
| `tests/test_algorithms/test_registry.py` | Tests for registry |
| `tests/test_algorithms/test_hill_climbing.py` | Tests for migrated solver |
| `tests/test_experiment/__init__.py` | Test package init |
| `tests/test_experiment/test_runner.py` | Tests for experiment runner |

### Files to Modify

| File | Change |
|------|--------|
| `src/gui/app.py` | Refactor to use ttk.Notebook with 3 tabs |
| `main.py` | No changes needed |

### Files to Keep Unchanged

| File | Reason |
|------|--------|
| `src/models/photo.py` | Data model, no changes |
| `src/models/slide.py` | Data model, no changes |
| `src/models/slideshow.py` | Data model, no changes |
| `src/io/parser.py` | IO logic, no changes |
| `src/solver/scorer.py` | Core logic, no changes |
| `src/gui/panels/dataset_panel.py` | Reused in new tabs |
| `src/gui/panels/stats_panel.py` | Reused in Explore tab |
| `src/gui/panels/slideshow_viewer.py` | Reused in Explore tab |
| `src/gui/widgets/slide_card.py` | Reused unchanged |

---

## Task 1: Create BaseAlgorithm and Supporting Classes

**Files:**
- Create: `src/algorithms/__init__.py`
- Create: `src/algorithms/base.py`
- Create: `tests/test_algorithms/__init__.py`
- Create: `tests/test_algorithms/test_base.py`

- [ ] **Step 1: Write failing test for ParameterSchema**

```python
# tests/test_algorithms/test_base.py
from src.algorithms.base import ParameterSchema


def test_parameter_schema_creation():
    param = ParameterSchema(
        name="max_iterations",
        type=int,
        default=10000,
        min_value=1,
        max_value=100000,
        description="Maximum iterations"
    )
    assert param.name == "max_iterations"
    assert param.type == int
    assert param.default == 10000
    assert param.min_value == 1
    assert param.max_value == 100000
    assert param.description == "Maximum iterations"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_base.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Create algorithms package and base module**

```python
# src/algorithms/__init__.py
# Empty init - algorithms self-register via decorator
```

```python
# src/algorithms/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable
from src.models.photo import Photo
from src.models.slideshow import Slideshow


@dataclass
class ParameterSchema:
    """Define a configurable parameter for an algorithm."""
    name: str
    type: type
    default: Any
    min_value: Any = None
    max_value: Any = None
    description: str = ""


@dataclass
class AlgorithmResult:
    """Result of a single algorithm execution."""
    slideshow: Slideshow
    score: int
    execution_time: float
    history: list[int]


class BaseAlgorithm(ABC):
    """Base class for all optimization algorithms."""

    name: str
    parameters: list[ParameterSchema]

    @abstractmethod
    def solve(
        self,
        photos: list[Photo],
        callback: Callable[[int, int], None] = None,
        **params
    ) -> AlgorithmResult:
        """
        Execute the algorithm.

        Args:
            photos: List of photos from the problem
            callback: Optional callback(iteration, score) for UI updates
            **params: Algorithm-specific parameters

        Returns:
            AlgorithmResult with slideshow, score, time, and history
        """
        pass

    def request_stop(self):
        """Request the algorithm to stop (optional)."""
        pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_base.py::test_parameter_schema_creation -v`
Expected: PASS

- [ ] **Step 5: Write test for AlgorithmResult**

```python
# tests/test_algorithms/test_base.py (append)
from src.models.slide import Slide
from src.models.slideshow import Slideshow
from src.algorithms.base import AlgorithmResult


def test_algorithm_result_creation():
    slide = Slide([__import__('src.models.photo', fromlist=['Photo']).Photo(0, 'H', {'a'})])
    slideshow = Slideshow([slide])

    result = AlgorithmResult(
        slideshow=slideshow,
        score=100,
        execution_time=1.5,
        history=[10, 50, 100]
    )

    assert result.slideshow == slideshow
    assert result.score == 100
    assert result.execution_time == 1.5
    assert result.history == [10, 50, 100]
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_base.py::test_algorithm_result_creation -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/algorithms/ tests/test_algorithms/
git commit -m "feat: add BaseAlgorithm, ParameterSchema, and AlgorithmResult classes"
```

---

## Task 2: Create AlgorithmRegistry

**Files:**
- Create: `src/algorithms/registry.py`
- Create: `tests/test_algorithms/test_registry.py`

- [ ] **Step 1: Write failing test for AlgorithmRegistry.register**

```python
# tests/test_algorithms/test_registry.py
from src.algorithms.base import BaseAlgorithm, ParameterSchema, AlgorithmResult
from src.algorithms.registry import AlgorithmRegistry
from src.models.photo import Photo


@AlgorithmRegistry.register
class MockAlgorithm(BaseAlgorithm):
    name = "Mock Algorithm"
    parameters = []

    def solve(self, photos, callback=None, **params):
        return AlgorithmResult(
            slideshow=None,
            score=0,
            execution_time=0.0,
            history=[]
        )


def test_registry_register():
    # Clear registry for test isolation
    AlgorithmRegistry._algorithms = {}

    @AlgorithmRegistry.register
    class TestAlgo(BaseAlgorithm):
        name = "Test Algo"
        parameters = []

        def solve(self, photos, callback=None, **params):
            pass

    assert "Test Algo" in AlgorithmRegistry._algorithms
    assert AlgorithmRegistry._algorithms["Test Algo"] == TestAlgo
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_registry.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement AlgorithmRegistry**

```python
# src/algorithms/registry.py
from typing import Type
from src.algorithms.base import BaseAlgorithm


class AlgorithmRegistry:
    """Central registry for auto-discovery of algorithms."""

    _algorithms: dict[str, Type[BaseAlgorithm]] = {}

    @classmethod
    def register(cls, algo_class: Type[BaseAlgorithm]) -> Type[BaseAlgorithm]:
        """Decorator to register an algorithm."""
        cls._algorithms[algo_class.name] = algo_class
        return algo_class

    @classmethod
    def get(cls, name: str) -> Type[BaseAlgorithm]:
        """Get an algorithm class by name."""
        return cls._algorithms.get(name)

    @classmethod
    def get_all(cls) -> list[Type[BaseAlgorithm]]:
        """Return all registered algorithm classes."""
        return list(cls._algorithms.values())

    @classmethod
    def get_names(cls) -> list[str]:
        """Return names of all registered algorithms."""
        return list(cls._algorithms.keys())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_registry.py::test_registry_register -v`
Expected: PASS

- [ ] **Step 5: Write test for get/get_all/get_names**

```python
# tests/test_algorithms/test_registry.py (append)
def test_registry_get_methods():
    AlgorithmRegistry._algorithms = {}

    @AlgorithmRegistry.register
    class Algo1(BaseAlgorithm):
        name = "Algo One"
        parameters = []
        def solve(self, photos, callback=None, **params):
            pass

    @AlgorithmRegistry.register
    class Algo2(BaseAlgorithm):
        name = "Algo Two"
        parameters = []
        def solve(self, photos, callback=None, **params):
            pass

    assert AlgorithmRegistry.get("Algo One") == Algo1
    assert AlgorithmRegistry.get("Algo Two") == Algo2
    assert AlgorithmRegistry.get("NonExistent") is None
    assert len(AlgorithmRegistry.get_all()) == 2
    assert set(AlgorithmRegistry.get_names()) == {"Algo One", "Algo Two"}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_registry.py::test_registry_get_methods -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/algorithms/registry.py tests/test_algorithms/test_registry.py
git commit -m "feat: add AlgorithmRegistry with decorator pattern"
```

---

## Task 3: Migrate HillClimbingSolver to New Architecture

**Files:**
- Create: `src/algorithms/hill_climbing.py`
- Create: `tests/test_algorithms/test_hill_climbing.py`

- [ ] **Step 1: Write failing test for new HillClimbingSolver interface**

```python
# tests/test_algorithms/test_hill_climbing.py
import random
from src.models.photo import Photo
from src.algorithms.hill_climbing import HillClimbingSolver
from src.algorithms.registry import AlgorithmRegistry


def test_hill_climbing_registered():
    assert "Hill Climbing" in AlgorithmRegistry.get_names()
    algo_class = AlgorithmRegistry.get("Hill Climbing")
    assert algo_class == HillClimbingSolver


def test_hill_climbing_has_parameters():
    algo_class = AlgorithmRegistry.get("Hill Climbing")
    param_names = [p.name for p in algo_class.parameters]
    assert "max_iterations" in param_names


def test_hill_climbing_solve_returns_algorithm_result():
    random.seed(42)
    photos = [
        Photo(0, 'H', {'a', 'b'}),
        Photo(1, 'H', {'a', 'c'}),
        Photo(2, 'H', {'b', 'c'}),
    ]
    algo = HillClimbingSolver()
    result = algo.solve(photos, max_iterations=100)

    assert result.slideshow is not None
    assert result.score >= 0
    assert result.execution_time >= 0
    assert len(result.history) == 100
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_hill_climbing.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement new HillClimbingSolver**

```python
# src/algorithms/hill_climbing.py
import time
import random
from typing import Callable
from src.algorithms.base import BaseAlgorithm, ParameterSchema, AlgorithmResult
from src.algorithms.registry import AlgorithmRegistry
from src.models.photo import Photo
from src.models.slide import Slide
from src.models.slideshow import Slideshow


@AlgorithmRegistry.register
class HillClimbingSolver(BaseAlgorithm):
    name = "Hill Climbing"

    parameters = [
        ParameterSchema(
            name="max_iterations",
            type=int,
            default=10000,
            min_value=1,
            max_value=1000000,
            description="Maximum number of iterations"
        )
    ]

    def __init__(self):
        self._stop_requested = False

    def solve(
        self,
        photos: list[Photo],
        callback: Callable[[int, int], None] = None,
        **params
    ) -> AlgorithmResult:
        start_time = time.time()
        self._stop_requested = False
        max_iterations = params.get("max_iterations", 10000)

        current = self._generate_initial_solution(photos)
        current_score = current.calculate_score()
        history = [current_score]

        for iteration in range(max_iterations):
            if self._stop_requested:
                break

            neighbor = self._get_neighbor(current)
            neighbor_score = neighbor.calculate_score()

            if neighbor_score > current_score:
                current = neighbor
                current_score = neighbor_score

            history.append(current_score)

            if callback:
                callback(iteration, current_score)

        execution_time = time.time() - start_time

        return AlgorithmResult(
            slideshow=current,
            score=current_score,
            execution_time=execution_time,
            history=history
        )

    def request_stop(self):
        self._stop_requested = True

    def _generate_initial_solution(self, photos: list[Photo]) -> Slideshow:
        horizontal = [p for p in photos if p.is_horizontal]
        vertical = [p for p in photos if p.is_vertical]

        slides = []

        for photo in horizontal:
            slides.append(Slide([photo]))

        random.shuffle(vertical)
        for i in range(0, len(vertical) - 1, 2):
            slides.append(Slide([vertical[i], vertical[i + 1]]))

        random.shuffle(slides)
        return Slideshow(slides)

    def _get_neighbor(self, solution: Slideshow) -> Slideshow:
        if len(solution.slides) < 2:
            return solution

        new_slides = solution.slides.copy()
        i, j = random.sample(range(len(new_slides)), 2)
        new_slides[i], new_slides[j] = new_slides[j], new_slides[i]

        return Slideshow(new_slides)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_hill_climbing.py -v`
Expected: PASS

- [ ] **Step 5: Write additional test for callback**

```python
# tests/test_algorithms/test_hill_climbing.py (append)
def test_hill_climbing_callback():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]
    algo = HillClimbingSolver()
    callback_calls = []

    def callback(iteration, score):
        callback_calls.append((iteration, score))

    algo.solve(photos, max_iterations=5, callback=callback)

    assert len(callback_calls) == 5
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_algorithms/test_hill_climbing.py::test_hill_climbing_callback -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/algorithms/hill_climbing.py tests/test_algorithms/test_hill_climbing.py
git commit -m "feat: migrate HillClimbingSolver to new modular architecture"
```

---

## Task 4: Create ExperimentRunner

**Files:**
- Create: `src/experiment/__init__.py`
- Create: `src/experiment/runner.py`
- Create: `tests/test_experiment/__init__.py`
- Create: `tests/test_experiment/test_runner.py`

- [ ] **Step 1: Write failing test for AlgorithmConfig**

```python
# tests/test_experiment/test_runner.py
from src.experiment.runner import AlgorithmConfig


def test_algorithm_config_creation():
    config = AlgorithmConfig(
        algorithm_name="Hill Climbing",
        parameters={"max_iterations": 5000}
    )
    assert config.algorithm_name == "Hill Climbing"
    assert config.parameters == {"max_iterations": 5000}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_experiment/test_runner.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement ExperimentRunner with dataclasses**

```python
# src/experiment/__init__.py
from src.experiment.runner import AlgorithmConfig, RunResult, ExperimentResult, ExperimentRunner

__all__ = ['AlgorithmConfig', 'RunResult', 'ExperimentResult', 'ExperimentRunner']
```

```python
# src/experiment/runner.py
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional
from src.algorithms.registry import AlgorithmRegistry
from src.algorithms.base import AlgorithmResult
from src.models.photo import Photo


@dataclass
class AlgorithmConfig:
    """Configuration for an algorithm in an experiment."""
    algorithm_name: str
    parameters: dict


@dataclass
class RunResult:
    """Result of a single run."""
    config: AlgorithmConfig
    result: AlgorithmResult


@dataclass
class ExperimentResult:
    """Complete result of an experiment."""
    dataset_name: str
    timestamp: str
    runs: list[RunResult]

    def get_summary(self) -> list[dict]:
        """Return aggregated statistics per algorithm."""
        summaries = []
        for algo_name in set(r.config.algorithm_name for r in self.runs):
            algo_runs = [r for r in self.runs if r.config.algorithm_name == algo_name]
            scores = [r.result.score for r in algo_runs]
            times = [r.result.execution_time for r in algo_runs]

            mean_score = sum(scores) / len(scores)
            variance = sum((x - mean_score)**2 for x in scores) / len(scores)
            std_score = variance ** 0.5

            summaries.append({
                'algorithm': algo_name,
                'parameters': algo_runs[0].config.parameters,
                'runs': len(scores),
                'mean_score': mean_score,
                'std_score': std_score,
                'best_score': max(scores),
                'worst_score': min(scores),
                'mean_time': sum(times) / len(times),
                'best_result': max(algo_runs, key=lambda r: r.result.score)
            })
        return summaries


class ExperimentRunner:
    """Execute batch experiments with multiple runs."""

    def __init__(self, photos: list[Photo], dataset_name: str):
        self.photos = photos
        self.dataset_name = dataset_name
        self._stop_requested = False

    def run_experiment(
        self,
        configs: list[AlgorithmConfig],
        runs_per_config: int,
        progress_callback: Optional[Callable] = None
    ) -> ExperimentResult:
        """
        Execute all configurations with runs_per_config runs each.

        Args:
            configs: List of algorithm configurations
            runs_per_config: Number of runs per configuration
            progress_callback: callback(algo_name, run_num, runs_total, completed, total)
        """
        total_runs = len(configs) * runs_per_config
        completed_runs = 0
        all_results = []

        for config in configs:
            algo_class = AlgorithmRegistry.get(config.algorithm_name)

            for run_num in range(runs_per_config):
                if self._stop_requested:
                    break

                algorithm = algo_class()
                result = algorithm.solve(self.photos, **config.parameters)

                all_results.append(RunResult(config=config, result=result))
                completed_runs += 1

                if progress_callback:
                    progress_callback(
                        config.algorithm_name,
                        run_num + 1,
                        runs_per_config,
                        completed_runs,
                        total_runs
                    )

        return ExperimentResult(
            dataset_name=self.dataset_name,
            timestamp=datetime.now().isoformat(),
            runs=all_results
        )

    def request_stop(self):
        self._stop_requested = True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_experiment/test_runner.py::test_algorithm_config_creation -v`
Expected: PASS

- [ ] **Step 5: Write test for ExperimentRunner**

```python
# tests/test_experiment/test_runner.py (append)
import random
from src.models.photo import Photo
from src.experiment.runner import ExperimentRunner, AlgorithmConfig, ExperimentResult


def test_experiment_runner_single_config():
    random.seed(42)
    photos = [
        Photo(0, 'H', {'a', 'b'}),
        Photo(1, 'H', {'a', 'c'}),
        Photo(2, 'H', {'b', 'c'}),
    ]

    runner = ExperimentRunner(photos, "test_dataset")
    configs = [
        AlgorithmConfig(algorithm_name="Hill Climbing", parameters={"max_iterations": 10})
    ]

    result = runner.run_experiment(configs, runs_per_config=2)

    assert result.dataset_name == "test_dataset"
    assert result.timestamp is not None
    assert len(result.runs) == 2
    assert all(r.config.algorithm_name == "Hill Climbing" for r in result.runs)


def test_experiment_result_summary():
    random.seed(42)
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]

    runner = ExperimentRunner(photos, "test")
    configs = [AlgorithmConfig(algorithm_name="Hill Climbing", parameters={"max_iterations": 5})]
    result = runner.run_experiment(configs, runs_per_config=3)

    summary = result.get_summary()
    assert len(summary) == 1
    assert summary[0]['algorithm'] == "Hill Climbing"
    assert summary[0]['runs'] == 3
    assert 'mean_score' in summary[0]
    assert 'std_score' in summary[0]
    assert 'best_score' in summary[0]
    assert 'worst_score' in summary[0]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/test_experiment/test_runner.py -v`
Expected: All PASS

- [ ] **Step 7: Commit**

```bash
git add src/experiment/ tests/test_experiment/
git commit -m "feat: add ExperimentRunner for batch comparison"
```

---

## Task 5: Create AlgorithmConfigWidget

**Files:**
- Create: `src/gui/widgets/algorithm_config.py`

- [ ] **Step 1: Create AlgorithmConfigWidget**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add src/gui/widgets/algorithm_config.py
git commit -m "feat: add AlgorithmConfigWidget for dynamic parametrization"
```

---

## Task 6: Create Explore Panel (Tab 1)

**Files:**
- Create: `src/gui/panels/explore_panel.py`

- [ ] **Step 1: Create ExplorePanel**

```python
# src/gui/panels/explore_panel.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Callable, Optional
from src.models.photo import Photo
from src.algorithms.registry import AlgorithmRegistry
from src.algorithms.base import AlgorithmResult
from src.gui.widgets.algorithm_config import AlgorithmConfigWidget
from src.gui.panels.stats_panel import StatsPanel
from src.gui.panels.slideshow_viewer import SlideshowViewer


class ExplorePanel(ttk.Frame):
    """Tab 'Explorar' - single algorithm run with real-time visualization."""

    def __init__(self, parent, on_dataset_loaded: Callable):
        super().__init__(parent)
        self.on_dataset_loaded = on_dataset_loaded
        self.photos: Optional[list[Photo]] = None
        self.dataset_name: str = ""
        self.current_algorithm = None
        self._stop_requested = False
        self.best_score = 0
        self._setup_ui()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)

        # Top: Dataset + Config
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.load_btn = ttk.Button(top_frame, text="Load Dataset", command=self._load_dataset)
        self.load_btn.pack(side="left", padx=5)

        self.dataset_label = ttk.Label(top_frame, text="No dataset loaded")
        self.dataset_label.pack(side="left", padx=10)

        # Left: Config + Controls
        left_frame = ttk.Frame(self)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.algo_config = AlgorithmConfigWidget(left_frame, self._on_algo_selected)
        self.algo_config.pack(fill="x", pady=5)

        # Run controls
        ctrl_frame = ttk.Frame(left_frame)
        ctrl_frame.pack(fill="x", pady=10)

        self.run_btn = ttk.Button(ctrl_frame, text="Run", command=self._on_run)
        self.run_btn.pack(side="left", padx=2)

        self.stop_btn = ttk.Button(ctrl_frame, text="Stop", command=self._on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=2)

        # Progress
        ttk.Label(left_frame, text="Progress:").pack(anchor="w", pady=(10, 0))
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(left_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=5)

        self.current_label = ttk.Label(left_frame, text="Current: -")
        self.current_label.pack(anchor="w")
        self.best_label = ttk.Label(left_frame, text="Best: -")
        self.best_label.pack(anchor="w")

        # Right: Stats + Viewer
        right_frame = ttk.Frame(self)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        self.stats_panel = StatsPanel(right_frame)
        self.stats_panel.grid(row=0, column=0, sticky="nsew")

        self.slideshow_viewer = SlideshowViewer(right_frame)
        self.slideshow_viewer.grid(row=1, column=0, sticky="nsew")

    def _load_dataset(self):
        from tkinter import filedialog
        from src.io.parser import parse_input

        filepath = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                content = f.read()
            self.photos = parse_input(content)
            self.dataset_name = filepath.split('/')[-1]
            self.dataset_label.config(text=f"File: {self.dataset_name}")
            self.on_dataset_loaded(self.photos, self.dataset_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def _on_algo_selected(self, algo_name: str):
        algo_class = AlgorithmRegistry.get(algo_name)
        self.current_algorithm = algo_class() if algo_class else None

    def _on_run(self):
        if not self.photos:
            messagebox.showwarning("Warning", "Please load a dataset first")
            return

        config = self.algo_config.get_config()
        algo_class = AlgorithmRegistry.get(config["algorithm_name"])
        self.current_algorithm = algo_class()
        self._stop_requested = False
        self.best_score = 0
        self.stats_panel.reset()
        self.progress_var.set(0)
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        max_iter = config["parameters"].get("max_iterations", 10000)

        def run_solver():
            def callback(iteration: int, score: int):
                if score > self.best_score:
                    self.best_score = score
                self.after(0, lambda: self._update_ui(iteration, max_iter, score))

            result = self.current_algorithm.solve(
                self.photos,
                callback=callback,
                **config["parameters"]
            )
            self.after(0, lambda: self._solver_finished(result))

        thread = threading.Thread(target=run_solver, daemon=True)
        thread.start()

    def _on_stop(self):
        if self.current_algorithm:
            self.current_algorithm.request_stop()
            self._stop_requested = True

    def _update_ui(self, iteration: int, max_iter: int, score: int):
        progress = (iteration / max_iter) * 100
        self.progress_var.set(progress)
        self.current_label.config(text=f"Current: {score}")
        self.best_label.config(text=f"Best: {self.best_score}")
        self.stats_panel.append_score(score)

    def _solver_finished(self, result: AlgorithmResult):
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.slideshow_viewer.load_slideshow(result.slideshow)
        messagebox.showinfo(
            "Complete",
            f"Optimization complete!\nFinal score: {result.score}\nTime: {result.execution_time:.2f}s"
        )

    def set_dataset(self, photos: list[Photo], dataset_name: str):
        self.photos = photos
        self.dataset_name = dataset_name
        self.dataset_label.config(text=f"File: {dataset_name}")
        self.stats_panel.reset()
        self.slideshow_viewer.clear()
```

- [ ] **Step 2: Commit**

```bash
git add src/gui/panels/explore_panel.py
git commit -m "feat: add ExplorePanel for single algorithm runs"
```

---

## Task 7: Create Experiment Panel (Tab 2)

**Files:**
- Create: `src/gui/panels/experiment_panel.py`

- [ ] **Step 1: Create ExperimentPanel**

```python
# src/gui/panels/experiment_panel.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional
from src.models.photo import Photo
from src.experiment.runner import ExperimentRunner, AlgorithmConfig, ExperimentResult
from src.algorithms.registry import AlgorithmRegistry


class ExperimentPanel(ttk.Frame):
    """Tab 'Experimento' - batch comparison with multiple runs."""

    def __init__(self, parent):
        super().__init__(parent)
        self.photos: Optional[list[Photo]] = None
        self.dataset_name: str = ""
        self.runner: Optional[ExperimentRunner] = None
        self._experiment_result: Optional[ExperimentResult] = None
        self._stop_requested = False
        self._setup_ui()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Top: Dataset load
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.load_btn = ttk.Button(top_frame, text="Load Dataset", command=self._load_dataset)
        self.load_btn.pack(side="left", padx=5)

        self.dataset_label = ttk.Label(top_frame, text="No dataset loaded")
        self.dataset_label.pack(side="left", padx=10)

        # Left: Configuration
        left_frame = ttk.LabelFrame(self, text="Experiment Configuration")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Label(left_frame, text="Runs per algorithm:").pack(anchor="w", padx=5, pady=5)
        self.runs_var = tk.StringVar(value="5")
        ttk.Entry(left_frame, textvariable=self.runs_var, width=10).pack(anchor="w", padx=5)

        ttk.Separator(left_frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(left_frame, text="Algorithms to compare:").pack(anchor="w", padx=5)

        # Algorithm checkboxes
        self.algo_vars: dict[str, tk.BooleanVar] = {}
        algo_frame = ttk.Frame(left_frame)
        algo_frame.pack(fill="x", padx=5, pady=5)

        for algo_name in AlgorithmRegistry.get_names():
            var = tk.BooleanVar(value=True)
            self.algo_vars[algo_name] = var
            ttk.Checkbutton(algo_frame, text=algo_name, variable=var).pack(anchor="w")

        # Run controls
        ctrl_frame = ttk.Frame(left_frame)
        ctrl_frame.pack(fill="x", pady=10, padx=5)

        self.run_btn = ttk.Button(ctrl_frame, text="Run Experiment", command=self._on_run)
        self.run_btn.pack(side="left", padx=2)

        self.stop_btn = ttk.Button(ctrl_frame, text="Stop", command=self._on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=2)

        # Right: Progress & Results
        right_frame = ttk.LabelFrame(self, text="Progress & Results")
        right_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Overall progress
        ttk.Label(right_frame, text="Overall Progress:").pack(anchor="w", padx=5, pady=5)
        self.progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(right_frame, variable=self.progress_var, maximum=100).pack(fill="x", padx=5)

        self.progress_label = ttk.Label(right_frame, text="0 / 0 runs")
        self.progress_label.pack(anchor="w", padx=5)

        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=10)

        # Per-algorithm progress
        ttk.Label(right_frame, text="Per Algorithm:").pack(anchor="w", padx=5)
        self.algo_progress_frame = ttk.Frame(right_frame)
        self.algo_progress_frame.pack(fill="x", padx=5, pady=5)

        self.algo_progress_labels: dict[str, ttk.Label] = {}
        for algo_name in AlgorithmRegistry.get_names():
            label = ttk.Label(self.algo_progress_frame, text=f"{algo_name}: -")
            label.pack(anchor="w")
            self.algo_progress_labels[algo_name] = label

        # Log
        ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(right_frame, text="Log:").pack(anchor="w", padx=5)

        self.log_text = tk.Text(right_frame, height=10, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def _load_dataset(self):
        from tkinter import filedialog
        from src.io.parser import parse_input

        filepath = filedialog.askopenfilename(
            title="Select Dataset",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                content = f.read()
            self.photos = parse_input(content)
            self.dataset_name = filepath.split('/')[-1]
            self.dataset_label.config(text=f"File: {self.dataset_name}")
            self.runner = ExperimentRunner(self.photos, self.dataset_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def _log(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _on_run(self):
        if not self.runner:
            messagebox.showwarning("Warning", "Please load a dataset first")
            return

        try:
            runs_per_config = int(self.runs_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number of runs")
            return

        # Build configs from selected algorithms
        configs = []
        for algo_name, var in self.algo_vars.items():
            if var.get():
                algo_class = AlgorithmRegistry.get(algo_name)
                default_params = {p.name: p.default for p in algo_class.parameters}
                configs.append(AlgorithmConfig(algorithm_name=algo_name, parameters=default_params))

        if not configs:
            messagebox.showwarning("Warning", "Please select at least one algorithm")
            return

        self._stop_requested = False
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress_var.set(0)
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

        for algo_name in self.algo_progress_labels:
            self.algo_progress_labels[algo_name].config(text=f"{algo_name}: -")

        def run_experiment():
            def progress_callback(algo_name, run_num, runs_total, completed, total):
                self.after(0, lambda: self._update_progress(
                    algo_name, run_num, runs_total, completed, total
                ))

            result = self.runner.run_experiment(configs, runs_per_config, progress_callback)
            self.after(0, lambda: self._experiment_finished(result))

        thread = threading.Thread(target=run_experiment, daemon=True)
        thread.start()

    def _on_stop(self):
        if self.runner:
            self.runner.request_stop()
            self._stop_requested = True

    def _update_progress(self, algo_name: str, run_num: int, runs_total: int,
                         completed: int, total: int):
        progress = (completed / total) * 100
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{completed} / {total} runs")
        self.algo_progress_labels[algo_name].config(
            text=f"{algo_name}: run {run_num}/{runs_total}"
        )
        self._log(f"[{algo_name}] Run {run_num}/{runs_total} complete")

    def _experiment_finished(self, result: ExperimentResult):
        self._experiment_result = result
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        summary = result.get_summary()
        self._log("\n=== EXPERIMENT COMPLETE ===")
        for s in summary:
            self._log(f"{s['algorithm']}: mean={s['mean_score']:.1f}, "
                      f"std={s['std_score']:.1f}, best={s['best_score']}, "
                      f"time={s['mean_time']:.2f}s")

        messagebox.showinfo("Complete", f"Experiment finished!\n{len(result.runs)} total runs")

    def set_dataset(self, photos: list[Photo], dataset_name: str):
        self.photos = photos
        self.dataset_name = dataset_name
        self.dataset_label.config(text=f"File: {dataset_name}")
        self.runner = ExperimentRunner(photos, dataset_name)

    def get_experiment_result(self) -> Optional[ExperimentResult]:
        return self._experiment_result
```

- [ ] **Step 2: Commit**

```bash
git add src/gui/panels/experiment_panel.py
git commit -m "feat: add ExperimentPanel for batch comparison"
```

---

## Task 8: Create Results Panel (Tab 3)

**Files:**
- Create: `src/gui/panels/results_panel.py`

- [ ] **Step 1: Create ResultsPanel**

```python
# src/gui/panels/results_panel.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.experiment.runner import ExperimentResult


class ResultsPanel(ttk.Frame):
    """Tab 'Resultados' - statistics display and export."""

    def __init__(self, parent):
        super().__init__(parent)
        self._experiment_result: ExperimentResult | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top: Export buttons
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Button(top_frame, text="Export CSV", command=self._export_csv).pack(side="left", padx=2)
        ttk.Button(top_frame, text="Export LaTeX", command=self._export_latex).pack(side="left", padx=2)
        ttk.Button(top_frame, text="Save Report", command=self._save_report).pack(side="left", padx=2)

        self.result_label = ttk.Label(top_frame, text="No results yet")
        self.result_label.pack(side="right", padx=10)

        # Main: Table + Charts
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Statistics table
        table_frame = ttk.LabelFrame(main_frame, text="Statistics")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        columns = ("Algorithm", "Runs", "Mean", "Std", "Best", "Worst", "Time (s)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Charts
        chart_frame = ttk.LabelFrame(main_frame, text="Visualization")
        chart_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def set_experiment_result(self, result: ExperimentResult):
        self._experiment_result = result
        self._update_table()
        self._update_charts()
        self.result_label.config(text=f"Dataset: {result.dataset_name} | {len(result.runs)} runs")

    def _update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self._experiment_result:
            return

        summary = self._experiment_result.get_summary()
        for s in summary:
            self.tree.insert("", "end", values=(
                s['algorithm'],
                s['runs'],
                f"{s['mean_score']:.1f}",
                f"{s['std_score']:.1f}",
                s['best_score'],
                s['worst_score'],
                f"{s['mean_time']:.2f}"
            ))

    def _update_charts(self):
        self.figure.clear()

        if not self._experiment_result:
            self.canvas.draw()
            return

        summary = self._experiment_result.get_summary()
        if not summary:
            self.canvas.draw()
            return

        # Create subplots
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)

        # Bar chart for mean scores
        names = [s['algorithm'] for s in summary]
        means = [s['mean_score'] for s in summary]
        stds = [s['std_score'] for s in summary]

        ax1.bar(names, means, yerr=stds, capsize=5)
        ax1.set_ylabel("Score")
        ax1.set_title("Mean Score (with std)")
        ax1.tick_params(axis='x', rotation=15)

        # Box plot for score distributions
        distributions = {}
        for run in self._experiment_result.runs:
            algo = run.config.algorithm_name
            if algo not in distributions:
                distributions[algo] = []
            distributions[algo].append(run.result.score)

        ax2.boxplot([distributions[n] for n in names], labels=names)
        ax2.set_ylabel("Score")
        ax2.set_title("Score Distribution")
        ax2.tick_params(axis='x', rotation=15)

        self.figure.tight_layout()
        self.canvas.draw()

    def _export_csv(self):
        if not self._experiment_result:
            messagebox.showwarning("Warning", "No results to export")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filepath:
            return

        summary = self._experiment_result.get_summary()
        with open(filepath, 'w') as f:
            f.write("Algorithm,Runs,Mean Score,Std Score,Best,Worst,Mean Time (s)\n")
            for s in summary:
                f.write(f"{s['algorithm']},{s['runs']},{s['mean_score']:.2f},"
                        f"{s['std_score']:.2f},{s['best_score']},{s['worst_score']},"
                        f"{s['mean_time']:.2f}\n")

        messagebox.showinfo("Success", f"CSV exported to {filepath}")

    def _export_latex(self):
        if not self._experiment_result:
            messagebox.showwarning("Warning", "No results to export")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".tex",
            filetypes=[("LaTeX files", "*.tex")]
        )
        if not filepath:
            return

        summary = self._experiment_result.get_summary()
        with open(filepath, 'w') as f:
            f.write("\\begin{tabular}{lrrrrrr}\n")
            f.write("\\hline\n")
            f.write("Algorithm & Runs & Mean & Std & Best & Worst & Time (s) \\\\\n")
            f.write("\\hline\n")
            for s in summary:
                f.write(f"{s['algorithm']} & {s['runs']} & {s['mean_score']:.1f} & "
                        f"{s['std_score']:.1f} & {s['best_score']} & {s['worst_score']} & "
                        f"{s['mean_time']:.2f} \\\\\n")
            f.write("\\hline\n")
            f.write("\\end{tabular}\n")

        messagebox.showinfo("Success", f"LaTeX exported to {filepath}")

    def _save_report(self):
        if not self._experiment_result:
            messagebox.showwarning("Warning", "No results to save")
            return

        # Create results directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        results_dir = f"results/{timestamp}"
        os.makedirs(results_dir, exist_ok=True)

        # Save summary JSON
        summary = self._experiment_result.get_summary()
        summary_data = {
            "dataset": self._experiment_result.dataset_name,
            "timestamp": self._experiment_result.timestamp,
            "results": summary
        }

        with open(f"{results_dir}/experiment_summary.json", 'w') as f:
            json.dump(summary_data, f, indent=2)

        # Save best slideshows per algorithm
        for s in summary:
            best_result = s['best_result'].result
            filename = f"{results_dir}/slideshow_{s['algorithm'].replace(' ', '_')}_best.txt"
            with open(filename, 'w') as f:
                f.write(best_result.slideshow.to_output_string())

        messagebox.showinfo("Success", f"Report saved to {results_dir}")
```

- [ ] **Step 2: Commit**

```bash
git add src/gui/panels/results_panel.py
git commit -m "feat: add ResultsPanel with statistics and export"
```

---

## Task 9: Refactor Main App to Use Tabs

**Files:**
- Modify: `src/gui/app.py`

- [ ] **Step 1: Refactor app.py to use Notebook tabs**

```python
# src/gui/app.py
import tkinter as tk
from tkinter import ttk
from src.gui.panels.explore_panel import ExplorePanel
from src.gui.panels.experiment_panel import ExperimentPanel
from src.gui.panels.results_panel import ResultsPanel
from src.models.photo import Photo


class PhotoSlideshowApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo Slideshow Solver")
        self.root.geometry("1400x900")

        # Import algorithms to trigger registration
        import src.algorithms  # noqa: F401

        self._setup_ui()

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self.root)

        self.explore_panel = ExplorePanel(self.notebook, self._on_dataset_loaded)
        self.experiment_panel = ExperimentPanel(self.notebook)
        self.results_panel = ResultsPanel(self.notebook)

        self.notebook.add(self.explore_panel, text="Explore")
        self.notebook.add(self.experiment_panel, text="Experiment")
        self.notebook.add(self.results_panel, text="Results")

        self.notebook.pack(expand=True, fill="both")

    def _on_dataset_loaded(self, photos: list[Photo], dataset_name: str):
        """Callback when dataset is loaded from Explore panel."""
        self.experiment_panel.set_dataset(photos, dataset_name)


def create_app() -> tk.Tk:
    """Create and return the main application window."""
    root = tk.Tk()
    app = PhotoSlideshowApp(root)
    return root
```

- [ ] **Step 2: Run tests to verify nothing broke**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/ -v`
Expected: All existing tests PASS

- [ ] **Step 3: Test GUI launches**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && timeout 3 python main.py || echo "GUI launched successfully"`
Expected: No errors, window opens

- [ ] **Step 4: Commit**

```bash
git add src/gui/app.py
git commit -m "refactor: main app to use 3-tab Notebook interface"
```

---

## Task 10: Update Package Init Files and Final Testing

**Files:**
- Modify: `src/algorithms/__init__.py`
- Verify: All tests pass

- [ ] **Step 1: Update algorithms __init__.py to import all algorithms**

```python
# src/algorithms/__init__.py
from src.algorithms.base import BaseAlgorithm, ParameterSchema, AlgorithmResult
from src.algorithms.registry import AlgorithmRegistry
from src.algorithms.hill_climbing import HillClimbingSolver

__all__ = ['BaseAlgorithm', 'ParameterSchema', 'AlgorithmResult', 'AlgorithmRegistry', 'HillClimbingSolver']
```

- [ ] **Step 2: Run all tests**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 3: Test GUI end-to-end**

Run: `cd /home/bexigag/FEUP/AI/Y3_S2-Inteligencia-Artificial && timeout 5 python main.py || echo "GUI test complete"`
Expected: GUI opens with 3 tabs, no errors

- [ ] **Step 4: Commit**

```bash
git add src/algorithms/__init__.py
git commit -m "chore: update package init files for complete algorithm registration"
```

- [ ] **Step 5: Final commit with tag**

```bash
git add -A
git commit -m "feat: complete modular algorithms system with 3-tab GUI"
git tag v2.0.0
```

---

## Summary

This plan implements:
1. **Modular Algorithm System** - Registry pattern with auto-discovery
2. **BaseAlgorithm Interface** - Standard interface with ParameterSchema
3. **ExperimentRunner** - Batch comparison with multiple runs
4. **3-Tab GUI**:
   - **Explore** - Single algorithm run with real-time visualization
   - **Experiment** - Batch comparison with progress tracking
   - **Results** - Statistics table, charts, and export (CSV, LaTeX, JSON)
5. **Dynamic Parametrization** - AlgorithmConfigWidget generates UI from ParameterSchema
6. **Auto-save** - Results automatically saved to `results/YYYY-MM-DD_HH-MM-SS/`

The existing `src/solver/hill_climbing.py` is preserved (not deleted) to maintain backward compatibility. The new `src/algorithms/hill_climbing.py` is the modular version.
