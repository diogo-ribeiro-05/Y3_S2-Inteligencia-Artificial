# Photo Slideshow Solver

Sistema modular para resolver o problema Google Hash Code 2019 Photo Slideshow usando algoritmos de otimização.

## Instalação

```bash
pip install -r requirements.txt
```

## Utilização

```bash
python main.py
```

A aplicação tem 3 tabs:

1. **Explorar** - Executar um único algoritmo com visualização em tempo real
2. **Experimento** - Comparar múltiplos algoritmos com várias runs cada
3. **Resultados** - Ver estatísticas, gráficos e exportar (CSV, LaTeX, JSON)

## Arquitetura do Projeto

```
src/
├── algorithms/           # Sistema modular de algoritmos
│   ├── __init__.py      # Exporta classes públicas
│   ├── base.py          # BaseAlgorithm, ParameterSchema, AlgorithmResult
│   ├── registry.py      # AlgorithmRegistry (auto-descoberta)
│   └── hill_climbing.py # Implementação do Hill Climbing
│
├── experiment/           # Sistema de experimentos batch
│   ├── __init__.py
│   └── runner.py        # ExperimentRunner, AlgorithmConfig, ExperimentResult
│
├── models/               # Modelos de dados
│   ├── photo.py         # Photo (id, orientation, tags)
│   ├── slide.py         # Slide (1-2 photos)
│   └── slideshow.py     # Slideshow (lista de slides)
│
├── io/                   # Input/Output
│   └── parser.py        # parse_input(), write_output()
│
└── gui/                  # Interface gráfica
    ├── app.py           # Main app com 3-tab Notebook
    ├── panels/
    │   ├── explore_panel.py     # Tab Explorar
    │   ├── experiment_panel.py  # Tab Experimento
    │   └── results_panel.py     # Tab Resultados
    └── widgets/
        └── algorithm_config.py  # Widget de parametrização dinâmica
```

## Como Adicionar um Novo Algoritmo

### Passo 1: Criar o ficheiro

Criar um novo ficheiro em `src/algorithms/`, por exemplo `simulated_annealing.py`:

```python
import time
import random
from typing import Callable
from src.algorithms.base import BaseAlgorithm, ParameterSchema, AlgorithmResult
from src.algorithms.registry import AlgorithmRegistry
from src.models.photo import Photo
from src.models.slide import Slide
from src.models.slideshow import Slideshow


@AlgorithmRegistry.register  # Isto regista automaticamente o algoritmo!
class SimulatedAnnealingSolver(BaseAlgorithm):
    name = "Simulated Annealing"  # Nome que aparece na UI

    # Definir parâmetros configuráveis
    parameters = [
        ParameterSchema(
            name="max_iterations",
            type=int,
            default=10000,
            min_value=1,
            max_value=1000000,
            description="Número máximo de iterações"
        ),
        ParameterSchema(
            name="initial_temperature",
            type=float,
            default=1000.0,
            min_value=0.1,
            max_value=10000.0,
            description="Temperatura inicial"
        ),
        ParameterSchema(
            name="cooling_rate",
            type=float,
            default=0.995,
            min_value=0.9,
            max_value=0.9999,
            description="Taxa de arrefecimento"
        ),
        ParameterSchema(
            name="use_restart",
            type=bool,
            default=True,
            description="Reiniciar com nova solução se estagnar"
        ),
        ParameterSchema(
            name="neighbor_strategy",
            type=str,
            default="swap",
            options=["swap", "insert", "reverse", "random"],
            description="Estratégia de geração de vizinhos"
        ),
    ]

    def __init__(self):
        self._stop_requested = False

    def solve(
        self,
        photos: list[Photo],
        callback: Callable[[int, int], None] = None,
        **params
    ) -> AlgorithmResult:
        """Executa o algoritmo."""
        start_time = time.time()
        self._stop_requested = False

        # Obter parâmetros com defaults
        max_iterations = params.get("max_iterations", 10000)
        temperature = params.get("initial_temperature", 1000.0)
        cooling_rate = params.get("cooling_rate", 0.995)
        use_restart = params.get("use_restart", True)
        neighbor_strategy = params.get("neighbor_strategy", "swap")

        # Gerar solução inicial
        current = self._generate_initial_solution(photos)
        current_score = current.calculate_score()
        best = current
        best_score = current_score
        history = [current_score]

        # Loop principal
        for iteration in range(max_iterations):
            if self._stop_requested:
                break

            # Gerar vizinho
            neighbor = self._get_neighbor(current)
            neighbor_score = neighbor.calculate_score()

            # Aceitar ou rejeitar
            delta = neighbor_score - current_score
            if delta > 0 or random.random() < pow(2.718, delta / temperature):
                current = neighbor
                current_score = neighbor_score
                if current_score > best_score:
                    best = current
                    best_score = current_score

            # Arrefecer
            temperature *= cooling_rate
            history.append(current_score)

            if callback:
                callback(iteration, current_score)

        execution_time = time.time() - start_time

        return AlgorithmResult(
            slideshow=best,
            score=best_score,
            execution_time=execution_time,
            history=history
        )

    def request_stop(self):
        """Parar o algoritmo (chamado pela UI)."""
        self._stop_requested = True

    def _generate_initial_solution(self, photos: list[Photo]) -> Slideshow:
        """Gerar solução inicial válida."""
        # Ver HillClimbingSolver para implementação completa
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
        """Gerar solução vizinha (swap de slides)."""
        if len(solution.slides) < 2:
            return solution
        new_slides = solution.slides.copy()
        i, j = random.sample(range(len(new_slides)), 2)
        new_slides[i], new_slides[j] = new_slides[j], new_slides[i]
        return Slideshow(new_slides)
```

### Passo 2: Importar no `__init__.py`

Adicionar em `src/algorithms/__init__.py`:

```python
from src.algorithms.simulated_annealing import SimulatedAnnealingSolver

__all__ = [..., 'SimulatedAnnealingSolver']
```

### Passo 3: Pronto!

O algoritmo aparece automaticamente:
- No dropdown da tab **Explorar**
- Nas checkboxes da tab **Experimento**
- Nas estatísticas da tab **Resultados**

O decorator `@AlgorithmRegistry.register` faz toda a magia de registo automático.

## Tipos de Parâmetros Suportados

| Tipo | Widget na UI | Campos Relevantes | Exemplo |
|------|-------------|-------------------|---------|
| `int` | Spinbox | `min_value`, `max_value` | `type=int, min_value=1, max_value=1000` |
| `float` | Spinbox | `min_value`, `max_value` | `type=float, min_value=0.0, max_value=1.0` |
| `bool` | Checkbox | - | `type=bool, default=True` |
| `str` + `options` | Dropdown | `options=["a", "b"]` | `type=str, options=["greedy", "random"]` |
| `str` sem `options` | Caixa de texto | - | `type=str, default="output.txt"` |

### Exemplos

```python
# Inteiro com limites
ParameterSchema(
    name="max_iterations",
    type=int,
    default=1000,
    min_value=1,
    max_value=100000,
    description="Número máximo de iterações"
)

# Float com limites
ParameterSchema(
    name="learning_rate",
    type=float,
    default=0.01,
    min_value=0.001,
    max_value=1.0,
    description="Taxa de aprendizagem"
)

# Booleano (checkbox)
ParameterSchema(
    name="use_cache",
    type=bool,
    default=True,
    description="Ativar cache de cálculos"
)

# String com opções (dropdown)
ParameterSchema(
    name="strategy",
    type=str,
    default="balanced",
    options=["greedy", "random", "balanced"],
    description="Estratégia de seleção"
)

# String simples (caixa de texto)
ParameterSchema(
    name="output_prefix",
    type=str,
    default="result",
    description="Prefixo dos ficheiros de output"
)
```

## Checklist para Novos Algoritmos

- [ ] Criar classe que herda de `BaseAlgorithm`
- [ ] Definir `name: str` (nome na UI)
- [ ] Definir `parameters: list[ParameterSchema]`
- [ ] Implementar `solve(photos, callback, **params) -> AlgorithmResult`
- [ ] Implementar `request_stop()` (opcional, para paragem antecipada)
- [ ] Adicionar decorator `@AlgorithmRegistry.register`
- [ ] Importar no `__init__.py`

## Testes

```bash
python -m pytest tests/ -v
```

## Estrutura de Classes

```
BaseAlgorithm (abstract)
├── name: str
├── parameters: list[ParameterSchema]
├── solve(photos, callback, **params) -> AlgorithmResult
└── request_stop()

ParameterSchema
├── name: str
├── type: type (int, float, str, bool)
├── default: Any
├── min_value: Any (optional, para int/float)
├── max_value: Any (optional, para int/float)
├── description: str
└── options: list[str] (optional, para str com dropdown)

AlgorithmResult
├── slideshow: Slideshow
├── score: int
├── execution_time: float
└── history: list[int]

AlgorithmRegistry (class methods)
├── register(cls, algo_class) -> decorator
├── get(cls, name) -> AlgorithmClass
├── get_all(cls) -> list[AlgorithmClass]
├── get_names(cls) -> list[str]
└── clear(cls) -> None
```

## Formato de Input

O parser espera ficheiros no formato Hash Code:

```
N               # número de fotos
H M tag1 tag2   # foto 0: Horizontal, M tags, lista de tags
V 3 tagA tagB   # foto 1: Vertical, 3 tags
...
```

## Exportação

A tab Resultados suporta:
- **CSV** - Para análise em Excel/Sheets
- **LaTeX** - Tabela pronta para relatórios
- **JSON** - Relatório completo com slideshows
