# Sistema Modular de Algoritmos - Design Specification

**Date:** 2026-03-23
**Project:** Photo Slideshow Solver - Refactoring para Arquitetura Modular

## Overview

Refatoração do projeto Photo Slideshow Solver para uma arquitetura plug-and-play que suporta múltiplos algoritmos de otimização, comparação batch com estatísticas, e interface gráfica com parametrização dinâmica.

## Decisões de Design

| Decisão | Escolha |
|---------|---------|
| Padrão de arquitetura | Registry Pattern para auto-descoberta |
| Modo de comparação | Batch comparison + execução individual |
| Múltiplas runs | Sim, para todos os algoritmos (fontes de aleatoriedade) |
| Parametrização | Schema dinâmico por algoritmo |
| Visualização de resultados | Tabela de estatísticas + Gráficos |
| Estrutura da interface | 3 Tabs: Explorar, Experimento, Resultados |
| Exportação | Auto-save + manual (CSV, LaTeX, relatório) |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GUI (Tkinter)                           │
│  ┌─────────┬───────────┬─────────────┐                         │
│  │Explorar │Experimento│ Resultados  │                         │
│  └─────────┴───────────┴─────────────┘                         │
│                           │                                     │
│                    AlgorithmRegistry                            │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         ▼                 ▼                 ▼                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │HillClimbing │  │Simulated    │  │Genetic      │  ...        │
│  │             │  │Annealing    │  │Algorithm    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                           │                                     │
│                    BaseAlgorithm                                │
│                           │                                     │
├───────────────────────────┴─────────────────────────────────────┤
│                      MODELOS DE DADOS                           │
│       Photo ──▶ Slide ──▶ Slideshow ──▶ AlgorithmResult         │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
src/
├── models/                    # Inalterado
│   ├── __init__.py
│   ├── photo.py
│   ├── slide.py
│   └── slideshow.py
│
├── algorithms/                # NOVO - Sistema modular
│   ├── __init__.py           # Importa todos os algoritmos
│   ├── base.py               # BaseAlgorithm, ParameterSchema, AlgorithmResult
│   ├── registry.py           # AlgorithmRegistry
│   ├── hill_climbing.py      # Implementação existente migrada
│   ├── simulated_annealing.py    # Futuro
│   └── genetic.py                # Futuro
│
├── experiment/                # NOVO - Batch comparison
│   ├── __init__.py
│   └── runner.py             # ExperimentRunner, ExperimentResult
│
├── io/                        # Inalterado
│   ├── __init__.py
│   └── parser.py
│
└── gui/
    ├── __init__.py
    ├── app.py                 # Main app com tabs
    ├── panels/
    │   ├── __init__.py
    │   ├── explore_panel.py   # NOVO - Tab "Explorar"
    │   ├── experiment_panel.py # NOVO - Tab "Experimento"
    │   ├── results_panel.py   # NOVO - Tab "Resultados"
    │   ├── dataset_panel.py   # Existente - reutilizar
    │   ├── control_panel.py   # Existente - adaptar
    │   ├── stats_panel.py     # Existente - reutilizar
    │   └── slideshow_viewer.py # Existente - reutilizar
    └── widgets/
        ├── __init__.py
        ├── slide_card.py      # Existente
        └── algorithm_config.py # NOVO - Widget de parametrização dinâmica

results/                       # NOVO - Resultados auto-saved
└── YYYY-MM-DD_HH-MM-SS/
    ├── experiment_summary.json
    ├── slideshow_HillClimbing_best.txt
    └── ...
```

## Core Components

### 1. BaseAlgorithm (base.py)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable
from src.models.photo import Photo
from src.models.slideshow import Slideshow

@dataclass
class ParameterSchema:
    """Define um parâmetro configurável de um algoritmo."""
    name: str
    type: type           # int, float, str
    default: Any
    min_value: Any = None
    max_value: Any = None
    description: str = ""

@dataclass
class AlgorithmResult:
    """Resultado de uma execução do algoritmo."""
    slideshow: Slideshow
    score: int
    execution_time: float
    history: list[int]   # Score por iteração/generation

class BaseAlgorithm(ABC):
    """Classe base para todos os algoritmos de otimização."""

    name: str                              # Nome para UI
    parameters: list[ParameterSchema]      # Schema de parâmetros

    @abstractmethod
    def solve(
        self,
        photos: list[Photo],
        callback: Callable[[int, int], None] = None,
        **params
    ) -> AlgorithmResult:
        """
        Executa o algoritmo.

        Args:
            photos: Lista de fotos do problema
            callback: Função callback(iteration, score) para UI
            **params: Parâmetros específicos do algoritmo

        Returns:
            AlgorithmResult com slideshow, score, tempo e histórico
        """
        pass

    def request_stop(self):
        """Solicita paragem do algoritmo (opcional)."""
        pass
```

### 2. AlgorithmRegistry (registry.py)

```python
from typing import Type
from src.algorithms.base import BaseAlgorithm

class AlgorithmRegistry:
    """Registry central para auto-descoberta de algoritmos."""

    _algorithms: dict[str, Type[BaseAlgorithm]] = {}

    @classmethod
    def register(cls, algo_class: Type[BaseAlgorithm]) -> Type[BaseAlgorithm]:
        """Decorator para registar um algoritmo."""
        cls._algorithms[algo_class.name] = algo_class
        return algo_class

    @classmethod
    def get(cls, name: str) -> Type[BaseAlgorithm]:
        """Obtém uma classe de algoritmo pelo nome."""
        return cls._algorithms.get(name)

    @classmethod
    def get_all(cls) -> list[Type[BaseAlgorithm]]:
        """Retorna todas as classes de algoritmos registadas."""
        return list(cls._algorithms.values())

    @classmethod
    def get_names(cls) -> list[str]:
        """Retorna nomes de todos os algoritmos registados."""
        return list(cls._algorithms.keys())
```

### 3. Exemplo de Implementação (hill_climbing.py)

```python
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
            description="Número máximo de iterações"
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
        # Migrar lógica existente
        pass

    def _get_neighbor(self, solution: Slideshow) -> Slideshow:
        # Migrar lógica existente
        pass
```

### 4. ExperimentRunner (experiment/runner.py)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional
from src.algorithms.registry import AlgorithmRegistry
from src.algorithms.base import AlgorithmResult
from src.models.photo import Photo

@dataclass
class AlgorithmConfig:
    """Configuração de um algoritmo no experimento."""
    algorithm_name: str
    parameters: dict

@dataclass
class RunResult:
    """Resultado de uma única run."""
    config: AlgorithmConfig
    result: AlgorithmResult

@dataclass
class ExperimentResult:
    """Resultado completo de um experimento."""
    dataset_name: str
    timestamp: str
    runs: list[RunResult]

    def get_summary(self) -> list[dict]:
        """Retorna estatísticas agregadas por algoritmo."""
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
    """Executa experimentos batch com múltiplas runs."""

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
        Executa todas as configurações com runs_per_config runs cada.

        Args:
            configs: Lista de configurações de algoritmos
            runs_per_config: Número de runs por configuração
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

                # Nova instância por run para reset state
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

## GUI Components

### 1. Main App (app.py)

A aplicação principal agora usa `ttk.Notebook` para tabs:

```python
import tkinter as tk
from tkinter import ttk
from src.gui.panels.explore_panel import ExplorePanel
from src.gui.panels.experiment_panel import ExperimentPanel
from src.gui.panels.results_panel import ResultsPanel

class PhotoSlideshowApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo Slideshow Solver")
        self.root.geometry("1200x800")

        self._setup_ui()

    def _setup_ui(self):
        self.notebook = ttk.Notebook(self.root)

        self.explore_panel = ExplorePanel(self.notebook, self._on_dataset_loaded)
        self.experiment_panel = ExperimentPanel(self.notebook, self._on_dataset_loaded)
        self.results_panel = ResultsPanel(self.notebook)

        self.notebook.add(self.explore_panel, text="Explorar")
        self.notebook.add(self.experiment_panel, text="Experimento")
        self.notebook.add(self.results_panel, text="Resultados")

        self.notebook.pack(expand=True, fill="both")

    def _on_dataset_loaded(self, photos, dataset_name):
        """Callback quando dataset é carregado."""
        self.explore_panel.set_dataset(photos, dataset_name)
        self.experiment_panel.set_dataset(photos, dataset_name)
```

### 2. AlgorithmConfigWidget (widgets/algorithm_config.py)

Widget reutilizável para parametrização dinâmica:

```python
import tkinter as tk
from tkinter import ttk
from src.algorithms.base import ParameterSchema
from src.algorithms.registry import AlgorithmRegistry

class AlgorithmConfigWidget(ttk.Frame):
    """Widget para configurar um algoritmo com parâmetros dinâmicos."""

    def __init__(self, parent, on_algorithm_change=None):
        super().__init__(parent)
        self.on_algorithm_change = on_algorithm_change
        self._param_widgets = {}
        self._setup_ui()

    def _setup_ui(self):
        # Dropdown de algoritmos
        ttk.Label(self, text="Algoritmo:").pack(anchor="w")
        self.algo_combo = ttk.Combobox(
            self,
            values=AlgorithmRegistry.get_names(),
            state="readonly"
        )
        self.algo_combo.pack(fill="x", pady=(0, 10))
        self.algo_combo.bind("<<ComboboxSelected>>", self._on_algo_selected)

        # Frame para parâmetros (atualizado dinamicamente)
        self.params_frame = ttk.LabelFrame(self, text="Parâmetros")
        self.params_frame.pack(fill="x", pady=10)

    def _on_algo_selected(self, event):
        algo_name = self.algo_combo.get()
        algo_class = AlgorithmRegistry.get(algo_name)
        self._build_param_fields(algo_class.parameters)

        if self.on_algorithm_change:
            self.on_algorithm_change(algo_name)

    def _build_param_fields(self, parameters: list[ParameterSchema]):
        # Limpar widgets anteriores
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        self._param_widgets.clear()

        # Criar campos para cada parâmetro
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
        """Retorna configuração atual (algoritmo + parâmetros)."""
        params = {}
        for name, (widget, ptype) in self._param_widgets.items():
            value = widget.get()
            params[name] = ptype(value)

        return {
            "algorithm_name": self.algo_combo.get(),
            "parameters": params
        }
```

### 3. Tabs

#### Tab Explorar (explore_panel.py)
- Carregar dataset
- Selecionar algoritmo (dropdown)
- Configurar parâmetros (AlgorithmConfigWidget)
- Botões Correr/Parar
- Gráfico de evolução em tempo real (matplotlib)
- Visualização do slideshow resultante

#### Tab Experimento (experiment_panel.py)
- Carregar dataset
- Configurar runs_per_config
- Lista de algoritmos a comparar (adicionar/remover)
- Botão Correr Experimento
- Progresso por algoritmo e total
- Botão Parar

#### Tab Resultados (results_panel.py)
- Seletor de experimento anterior
- Tabela de estatísticas (média, std, melhor, pior, tempo)
- Gráficos: curvas de convergência, box plots
- Botões de exportação: CSV, LaTeX, Guardar Relatório

## Results Storage

### Auto-save Format

```
results/
└── 2026-03-23_14-32-15/
    ├── experiment_summary.json     # Metadados e estatísticas
    ├── config.json                 # Configuração do experimento
    ├── convergence_HillClimbing.json
    ├── slideshow_HillClimbing_best.txt
    ├── slideshow_SimulatedAnnealing_best.txt
    └── ...
```

### experiment_summary.json

```json
{
  "dataset": "example.txt",
  "timestamp": "2026-03-23T14:32:15",
  "runs_per_config": 10,
  "results": [
    {
      "algorithm": "Hill Climbing",
      "parameters": {"max_iterations": 10000},
      "runs": 10,
      "mean_score": 4523.4,
      "std_score": 312.2,
      "best_score": 5124,
      "worst_score": 4012,
      "mean_time": 1.23
    }
  ]
}
```

## Export Formats

### CSV
```csv
Algorithm,Runs,Mean Score,Std Score,Best,Worst,Mean Time (s)
Hill Climbing,10,4523.4,312.2,5124,4012,1.23
Simulated Annealing,10,4756.8,245.6,5234,4312,1.45
Genetic Algorithm,10,4987.2,189.3,5412,4656,3.67
```

### LaTeX Table
```latex
\begin{tabular}{lrrrrrr}
\hline
Algorithm & Runs & Mean & Std & Best & Worst & Time (s) \\
\hline
Hill Climbing & 10 & 4523.4 & 312.2 & 5124 & 4012 & 1.23 \\
Simulated Annealing & 10 & 4756.8 & 245.6 & 5234 & 4312 & 1.45 \\
Genetic Algorithm & 10 & 4987.2 & 189.3 & 5412 & 4656 & 3.67 \\
\hline
\end{tabular}
```

## Migration Plan

1. **Criar nova estrutura** - `algorithms/`, `experiment/`
2. **Migrar HillClimbingSolver** - Adaptar para BaseAlgorithm
3. **Criar AlgorithmRegistry** - Com decorator de registo
4. **Criar ExperimentRunner** - Batch comparison
5. **Refatorar GUI** - 3 tabs com novos panels
6. **Implementar AlgorithmConfigWidget** - Parametrização dinâmica
7. **Implementar ResultsPanel** - Tabela + gráficos
8. **Adicionar auto-save** - Results storage
9. **Testar end-to-end** - Fluxo completo

## Dependencies

Sem novas dependências externas. Usa apenas:
- tkinter (stdlib)
- matplotlib (já existente)
- dataclasses (stdlib)
