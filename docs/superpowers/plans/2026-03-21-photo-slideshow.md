# Photo Slideshow Solver Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a desktop application to solve the Hash Code 2019 Photo Slideshow problem using Hill Climbing optimization with a Tkinter + Matplotlib GUI.

**Architecture:** MVC pattern with data models (Photo, Slide, Slideshow), solver layer (Scorer, Hill Climbing), I/O layer (Parser), and GUI layer (Tkinter panels + Matplotlib charts).

**Tech Stack:** Python 3.10+, Tkinter, Matplotlib

---

## File Structure

```
Y3_S2-Inteligencia-Artificial/
├── main.py
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── photo.py
│   │   ├── slide.py
│   │   └── slideshow.py
│   ├── solver/
│   │   ├── __init__.py
│   │   ├── scorer.py
│   │   └── hill_climbing.py
│   ├── io/
│   │   ├── __init__.py
│   │   └── parser.py
│   └── gui/
│       ├── __init__.py
│       ├── app.py
│       ├── panels/
│       │   ├── __init__.py
│       │   ├── dataset_panel.py
│       │   ├── control_panel.py
│       │   ├── slideshow_viewer.py
│       │   └── stats_panel.py
│       └── widgets/
│           ├── __init__.py
│           └── slide_card.py
├── data/
│   ├── input/
│   │   └── example.txt
│   └── output/
└── tests/
    ├── __init__.py
    ├── test_models/
    │   ├── __init__.py
    │   ├── test_photo.py
    │   ├── test_slide.py
    │   └── test_slideshow.py
    ├── test_solver/
    │   ├── __init__.py
    │   ├── test_scorer.py
    │   └── test_hill_climbing.py
    └── test_io/
        ├── __init__.py
        └── test_parser.py
```

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/models/__init__.py`
- Create: `src/solver/__init__.py`
- Create: `src/io/__init__.py`
- Create: `src/gui/__init__.py`
- Create: `src/gui/panels/__init__.py`
- Create: `src/gui/widgets/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models/__init__.py`
- Create: `tests/test_solver/__init__.py`
- Create: `tests/test_io/__init__.py`
- Create: `data/input/example.txt`
- Create: `data/output/.gitkeep`

- [ ] **Step 1: Create requirements.txt**

```python
matplotlib>=3.5.0
```

- [ ] **Step 2: Create all __init__.py files**

Create empty `__init__.py` files in each package directory.

- [ ] **Step 3: Create sample input file**

```
4
H 3 cat beach sun
V 2 selfie smile
V 2 garden selfie
H 2 garden cat
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt src/ tests/ data/
git commit -m "chore: setup project structure"
```

---

## Task 2: Photo Model

**Files:**
- Create: `src/models/photo.py`
- Create: `tests/test_models/test_photo.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_photo.py
from src.models.photo import Photo


def test_photo_creation():
    photo = Photo(id=0, orientation='H', tags={'cat', 'beach', 'sun'})
    assert photo.id == 0
    assert photo.orientation == 'H'
    assert photo.tags == {'cat', 'beach', 'sun'}


def test_photo_is_horizontal():
    photo = Photo(id=0, orientation='H', tags=set())
    assert photo.is_horizontal == True
    assert photo.is_vertical == False


def test_photo_is_vertical():
    photo = Photo(id=1, orientation='V', tags=set())
    assert photo.is_vertical == True
    assert photo.is_horizontal == False


def test_photo_tag_count():
    photo = Photo(id=0, orientation='H', tags={'a', 'b', 'c'})
    assert photo.tag_count == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_models/test_photo.py -v`
Expected: FAIL with import error

- [ ] **Step 3: Write minimal implementation**

```python
# src/models/photo.py
from dataclasses import dataclass


@dataclass
class Photo:
    id: int
    orientation: str
    tags: set[str]

    @property
    def is_horizontal(self) -> bool:
        return self.orientation == 'H'

    @property
    def is_vertical(self) -> bool:
        return self.orientation == 'V'

    @property
    def tag_count(self) -> int:
        return len(self.tags)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_models/test_photo.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/models/photo.py tests/test_models/test_photo.py
git commit -m "feat: add Photo model with tests"
```

---

## Task 3: Slide Model

**Files:**
- Create: `src/models/slide.py`
- Create: `tests/test_models/test_slide.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_slide.py
import pytest
from src.models.photo import Photo
from src.models.slide import Slide


def test_slide_single_horizontal():
    photo = Photo(id=0, orientation='H', tags={'cat', 'beach'})
    slide = Slide(photos=[photo])
    assert slide.tags == {'cat', 'beach'}
    assert slide.is_horizontal_slide == True


def test_slide_two_vertical():
    photo1 = Photo(id=1, orientation='V', tags={'selfie', 'smile'})
    photo2 = Photo(id=2, orientation='V', tags={'garden', 'selfie'})
    slide = Slide(photos=[photo1, photo2])
    assert slide.tags == {'selfie', 'smile', 'garden'}
    assert slide.is_vertical_slide == True


def test_slide_invalid_vertical_single():
    photo = Photo(id=1, orientation='V', tags={'a'})
    with pytest.raises(ValueError, match="Vertical photos must be paired"):
        Slide(photos=[photo])


def test_slide_invalid_two_horizontal():
    photo1 = Photo(id=0, orientation='H', tags={'a'})
    photo2 = Photo(id=1, orientation='H', tags={'b'})
    with pytest.raises(ValueError, match="Cannot combine two horizontal photos"):
        Slide(photos=[photo1, photo2])


def test_slide_invalid_mixed():
    photo1 = Photo(id=0, orientation='H', tags={'a'})
    photo2 = Photo(id=1, orientation='V', tags={'b'})
    with pytest.raises(ValueError, match="Cannot mix horizontal and vertical"):
        Slide(photos=[photo1, photo2])


def test_slide_photo_ids():
    photo1 = Photo(id=1, orientation='V', tags={'a'})
    photo2 = Photo(id=2, orientation='V', tags={'b'})
    slide = Slide(photos=[photo1, photo2])
    assert slide.photo_ids == [1, 2]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_models/test_slide.py -v`
Expected: FAIL with import error

- [ ] **Step 3: Write minimal implementation**

```python
# src/models/slide.py
from dataclasses import dataclass
from src.models.photo import Photo


@dataclass
class Slide:
    photos: list[Photo]

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if len(self.photos) == 0:
            raise ValueError("Slide must contain at least one photo")

        if len(self.photos) == 1:
            if self.photos[0].is_vertical:
                raise ValueError("Vertical photos must be paired (2 per slide)")
            return

        if len(self.photos) == 2:
            if self.photos[0].is_horizontal and self.photos[1].is_horizontal:
                raise ValueError("Cannot combine two horizontal photos in one slide")
            if self.photos[0].is_horizontal or self.photos[1].is_horizontal:
                raise ValueError("Cannot mix horizontal and vertical photos in one slide")
            return

        raise ValueError("Slide cannot contain more than 2 photos")

    @property
    def tags(self) -> set[str]:
        result = set()
        for photo in self.photos:
            result.update(photo.tags)
        return result

    @property
    def is_horizontal_slide(self) -> bool:
        return len(self.photos) == 1 and self.photos[0].is_horizontal

    @property
    def is_vertical_slide(self) -> bool:
        return len(self.photos) == 2

    @property
    def photo_ids(self) -> list[int]:
        return [p.id for p in self.photos]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_models/test_slide.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/models/slide.py tests/test_models/test_slide.py
git commit -m "feat: add Slide model with validation and tests"
```

---

## Task 4: Transition Score (Scorer)

**Files:**
- Create: `src/solver/scorer.py`
- Create: `tests/test_solver/test_scorer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_solver/test_scorer.py
from src.models.photo import Photo
from src.models.slide import Slide
from src.solver.scorer import calculate_transition_score


def test_transition_score_common_only():
    # Both slides share tags, nothing unique
    s1 = Slide([Photo(0, 'H', {'a', 'b'})])
    s2 = Slide([Photo(1, 'H', {'a', 'b'})])
    # common=2, only_s1=0, only_s2=0 -> min=0
    assert calculate_transition_score(s1, s2) == 0


def test_transition_score_balanced():
    # Balanced transition: equal common, s1-only, s2-only
    s1 = Slide([Photo(0, 'H', {'a', 'b', 'c'})])
    s2 = Slide([Photo(1, 'H', {'a', 'b', 'd'})])
    # common={a,b}=2, only_s1={c}=1, only_s2={d}=1 -> min=1
    assert calculate_transition_score(s1, s2) == 1


def test_transition_score_different_tags():
    # Completely different tags
    s1 = Slide([Photo(0, 'H', {'cat', 'dog'})])
    s2 = Slide([Photo(1, 'H', {'sun', 'moon'})])
    # common=0, only_s1=2, only_s2=2 -> min=0
    assert calculate_transition_score(s1, s2) == 0


def test_transition_score_example_from_problem():
    # From the problem statement example
    s1 = Slide([Photo(3, 'H', {'garden', 'cat'})])
    s2 = Slide([
        Photo(1, 'V', {'selfie', 'smile'}),
        Photo(2, 'V', {'garden', 'selfie'})
    ])
    # s1 tags: {garden, cat}
    # s2 tags: {selfie, smile, garden}
    # common={garden}=1, only_s1={cat}=1, only_s2={selfie,smile}=2 -> min=1
    assert calculate_transition_score(s1, s2) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_solver/test_scorer.py -v`
Expected: FAIL with import error

- [ ] **Step 3: Write minimal implementation**

```python
# src/solver/scorer.py
from src.models.slide import Slide


def calculate_transition_score(s1: Slide, s2: Slide) -> int:
    """
    Calculate interest factor between two consecutive slides.
    Interest factor = min(common_tags, tags_only_in_s1, tags_only_in_s2)
    """
    tags1 = s1.tags
    tags2 = s2.tags

    common = len(tags1 & tags2)
    only_s1 = len(tags1 - tags2)
    only_s2 = len(tags2 - tags1)

    return min(common, only_s1, only_s2)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_solver/test_scorer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/solver/scorer.py tests/test_solver/test_scorer.py
git commit -m "feat: add transition score calculator with tests"
```

---

## Task 5: Slideshow Model

**Files:**
- Create: `src/models/slideshow.py`
- Create: `tests/test_models/test_slideshow.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models/test_slideshow.py
import pytest
from src.models.photo import Photo
from src.models.slide import Slide
from src.models.slideshow import Slideshow


def test_slideshow_empty_score():
    slideshow = Slideshow(slides=[])
    assert slideshow.calculate_score() == 0


def test_slideshow_single_slide_score():
    slide = Slide([Photo(0, 'H', {'cat'})])
    slideshow = Slideshow(slides=[slide])
    assert slideshow.calculate_score() == 0  # No transitions


def test_slideshow_two_slides_score():
    s1 = Slide([Photo(0, 'H', {'a', 'b', 'c'})])
    s2 = Slide([Photo(1, 'H', {'a', 'b', 'd'})])
    slideshow = Slideshow(slides=[s1, s2])
    # common=2, only_s1=1, only_s2=1 -> min=1
    assert slideshow.calculate_score() == 1


def test_slideshow_three_slides_score():
    s0 = Slide([Photo(0, 'H', {'cat', 'beach', 'sun'})])
    s1 = Slide([Photo(3, 'H', {'garden', 'cat'})])
    s2 = Slide([
        Photo(1, 'V', {'selfie', 'smile'}),
        Photo(2, 'V', {'garden', 'selfie'})
    ])
    slideshow = Slideshow(slides=[s0, s1, s2])
    # s0->s1: common={cat}=1, only_s0={beach,sun}=2, only_s1={garden}=1 -> min=1
    # s1->s2: common={garden}=1, only_s1={cat}=1, only_s2={selfie,smile}=2 -> min=1
    # total = 2
    assert slideshow.calculate_score() == 2


def test_slideshow_to_output_string():
    s0 = Slide([Photo(0, 'H', {'cat'})])
    s1 = Slide([Photo(3, 'H', {'garden'})])
    s2 = Slide([Photo(1, 'V', {'a'}), Photo(2, 'V', {'b'})])
    slideshow = Slideshow(slides=[s0, s1, s2])

    output = slideshow.to_output_string()
    lines = output.strip().split('\n')
    assert lines[0] == '3'
    assert lines[1] == '0'
    assert lines[2] == '3'
    assert lines[3] == '1 2'


def test_slideshow_slide_count():
    slideshow = Slideshow(slides=[Slide([Photo(0, 'H', {'a'})])])
    assert len(slideshow) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_models/test_slideshow.py -v`
Expected: FAIL with import error

- [ ] **Step 3: Write minimal implementation**

```python
# src/models/slideshow.py
from dataclasses import dataclass
from src.models.slide import Slide
from src.solver.scorer import calculate_transition_score


@dataclass
class Slideshow:
    slides: list[Slide]

    def calculate_score(self) -> int:
        """Sum of interest factors between consecutive slides."""
        if len(self.slides) < 2:
            return 0

        total = 0
        for i in range(len(self.slides) - 1):
            total += calculate_transition_score(self.slides[i], self.slides[i + 1])
        return total

    def to_output_string(self) -> str:
        """Generate submission file content."""
        lines = [str(len(self.slides))]
        for slide in self.slides:
            lines.append(' '.join(str(pid) for pid in slide.photo_ids))
        return '\n'.join(lines) + '\n'

    def __len__(self) -> int:
        return len(self.slides)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_models/test_slideshow.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/models/slideshow.py tests/test_models/test_slideshow.py
git commit -m "feat: add Slideshow model with scoring and output"
```

---

## Task 6: Parser (Input)

**Files:**
- Create: `src/io/parser.py`
- Create: `tests/test_io/test_parser.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_io/test_parser.py
import pytest
from src.io.parser import parse_input


def test_parse_input_example():
    content = """4
H 3 cat beach sun
V 2 selfie smile
V 2 garden selfie
H 2 garden cat
"""
    photos = parse_input(content)

    assert len(photos) == 4

    assert photos[0].id == 0
    assert photos[0].orientation == 'H'
    assert photos[0].tags == {'cat', 'beach', 'sun'}

    assert photos[1].id == 1
    assert photos[1].orientation == 'V'
    assert photos[1].tags == {'selfie', 'smile'}

    assert photos[2].id == 2
    assert photos[2].orientation == 'V'
    assert photos[2].tags == {'garden', 'selfie'}

    assert photos[3].id == 3
    assert photos[3].orientation == 'H'
    assert photos[3].tags == {'garden', 'cat'}


def test_parse_input_from_file(tmp_path):
    content = """2
H 1 dog
V 2 cat mouse
"""
    filepath = tmp_path / "test.txt"
    filepath.write_text(content)

    photos = parse_input(filepath.read_text())
    assert len(photos) == 2


def test_parse_input_invalid_format():
    content = "invalid"
    with pytest.raises(ValueError):
        parse_input(content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_io/test_parser.py -v`
Expected: FAIL with import error

- [ ] **Step 3: Write minimal implementation**

```python
# src/io/parser.py
from src.models.photo import Photo


def parse_input(content: str) -> list[Photo]:
    """Parse input file content into Photo objects."""
    lines = content.strip().split('\n')

    if not lines:
        raise ValueError("Empty input")

    try:
        n = int(lines[0])
    except ValueError:
        raise ValueError("First line must be number of photos")

    photos = []
    for i, line in enumerate(lines[1:n+1]):
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid photo format on line {i+1}")

        orientation = parts[0]
        tag_count = int(parts[1])
        tags = set(parts[2:2+tag_count])

        photos.append(Photo(id=i, orientation=orientation, tags=tags))

    return photos


def write_output(slideshow, filepath: str) -> None:
    """Write slideshow to output file."""
    with open(filepath, 'w') as f:
        f.write(slideshow.to_output_string())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_io/test_parser.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/io/parser.py tests/test_io/test_parser.py
git commit -m "feat: add input parser with tests"
```

---

## Task 7: Hill Climbing Solver - Initial Solution

**Files:**
- Create: `src/solver/hill_climbing.py`
- Create: `tests/test_solver/test_hill_climbing.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_solver/test_hill_climbing.py
from src.models.photo import Photo
from src.solver.hill_climbing import HillClimbingSolver


def test_generate_initial_solution_horizontal_only():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
        Photo(2, 'H', {'c'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    assert len(solution) == 3
    # All photos should be used
    used_ids = set()
    for slide in solution.slides:
        used_ids.update(slide.photo_ids)
    assert used_ids == {0, 1, 2}


def test_generate_initial_solution_vertical_pairing():
    photos = [
        Photo(0, 'V', {'a'}),
        Photo(1, 'V', {'b'}),
        Photo(2, 'V', {'c'}),
        Photo(3, 'V', {'d'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    # 4 vertical photos = 2 slides
    assert len(solution) == 2
    for slide in solution.slides:
        assert slide.is_vertical_slide
        assert len(slide.photo_ids) == 2


def test_generate_initial_solution_mixed():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'V', {'b'}),
        Photo(2, 'V', {'c'}),
        Photo(3, 'H', {'d'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    # 2 horizontal + 2 vertical (paired) = 3 slides
    assert len(solution) == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_solver/test_hill_climbing.py -v`
Expected: FAIL with import error

- [ ] **Step 3: Write minimal implementation**

```python
# src/solver/hill_climbing.py
import random
from typing import Callable
from src.models.photo import Photo
from src.models.slide import Slide
from src.models.slideshow import Slideshow


class HillClimbingSolver:
    def __init__(self, photos: list[Photo]):
        self.photos = photos
        self.history: list[int] = []
        self._stop_requested = False

    def generate_initial_solution(self) -> Slideshow:
        """Generate initial valid solution."""
        horizontal = [p for p in self.photos if p.is_horizontal]
        vertical = [p for p in self.photos if p.is_vertical]

        slides = []

        # Create horizontal slides (1 photo each)
        for photo in horizontal:
            slides.append(Slide([photo]))

        # Create vertical slides (2 photos each)
        random.shuffle(vertical)
        for i in range(0, len(vertical) - 1, 2):
            slides.append(Slide([vertical[i], vertical[i + 1]]))

        # Shuffle all slides for random initial order
        random.shuffle(slides)

        return Slideshow(slides)

    def request_stop(self):
        """Request the solver to stop."""
        self._stop_requested = True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_solver/test_hill_climbing.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/solver/hill_climbing.py tests/test_solver/test_hill_climbing.py
git commit -m "feat: add HillClimbingSolver initial solution generation"
```

---

## Task 8: Hill Climbing Solver - Neighbors

**Files:**
- Modify: `src/solver/hill_climbing.py`
- Modify: `tests/test_solver/test_hill_climbing.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_solver/test_hill_climbing.py

def test_get_neighbor_swap_slides():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
        Photo(2, 'H', {'c'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    neighbor = solver._swap_slides(solution)

    # Should have same number of slides
    assert len(neighbor) == len(solution)
    # Should contain same photo IDs
    original_ids = set()
    neighbor_ids = set()
    for s in solution.slides:
        original_ids.update(s.photo_ids)
    for s in neighbor.slides:
        neighbor_ids.update(s.photo_ids)
    assert original_ids == neighbor_ids


def test_get_neighbor_preserves_validity():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'V', {'b'}),
        Photo(2, 'V', {'c'}),
    ]
    solver = HillClimbingSolver(photos)
    solution = solver.generate_initial_solution()

    neighbor = solver._swap_slides(solution)
    # Verify all slides are still valid
    for slide in neighbor.slides:
        assert slide.is_horizontal_slide or slide.is_vertical_slide
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_solver/test_hill_climbing.py -v`
Expected: FAIL with AttributeError

- [ ] **Step 3: Write minimal implementation**

```python
# Add to src/solver/hill_climbing.py

import copy

def _swap_slides(self, solution: Slideshow) -> Slideshow:
    """Swap two random slides."""
    if len(solution.slides) < 2:
        return solution

    new_slides = solution.slides.copy()
    i, j = random.sample(range(len(new_slides)), 2)
    new_slides[i], new_slides[j] = new_slides[j], new_slides[i]

    return Slideshow(new_slides)

def get_neighbor(self, solution: Slideshow) -> Slideshow:
    """Generate a neighbor solution."""
    return self._swap_slides(solution)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_solver/test_hill_climbing.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/solver/hill_climbing.py tests/test_solver/test_hill_climbing.py
git commit -m "feat: add neighbor generation via slide swapping"
```

---

## Task 9: Hill Climbing Solver - Main Loop

**Files:**
- Modify: `src/solver/hill_climbing.py`
- Modify: `tests/test_solver/test_hill_climbing.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to tests/test_solver/test_hill_climbing.py

def test_solve_improves_or_maintains_score():
    random.seed(42)  # For reproducibility
    photos = [
        Photo(0, 'H', {'a', 'b', 'c'}),
        Photo(1, 'H', {'a', 'b', 'd'}),
        Photo(2, 'H', {'a', 'c', 'd'}),
        Photo(3, 'H', {'b', 'c', 'd'}),
    ]
    solver = HillClimbingSolver(photos)
    initial = solver.generate_initial_solution()
    initial_score = initial.calculate_score()

    final = solver.solve(max_iterations=100)
    final_score = final.calculate_score()

    # Score should improve or stay same
    assert final_score >= initial_score


def test_solve_populates_history():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]
    solver = HillClimbingSolver(photos)
    solver.solve(max_iterations=10)

    assert len(solver.history) == 10


def test_solve_callback():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]
    solver = HillClimbingSolver(photos)
    callback_calls = []

    def callback(iteration, score):
        callback_calls.append((iteration, score))

    solver.solve(max_iterations=5, callback=callback)

    assert len(callback_calls) == 5


def test_solve_can_be_stopped():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]
    solver = HillClimbingSolver(photos)

    def stop_early(iteration, score):
        if iteration >= 3:
            solver.request_stop()

    result = solver.solve(max_iterations=100, callback=stop_early)

    # Should have stopped early
    assert len(solver.history) < 100
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_solver/test_hill_climbing.py -v`
Expected: FAIL with AttributeError

- [ ] **Step 3: Write minimal implementation**

```python
# Add to HillClimbingSolver class in src/solver/hill_climbing.py

def solve(
    self,
    max_iterations: int = 10000,
    callback: Callable[[int, int], None] = None
) -> Slideshow:
    """
    Run hill climbing optimization.

    Args:
        max_iterations: Maximum number of iterations
        callback: Optional callback(iteration, score) for UI updates

    Returns:
        Best slideshow found
    """
    self._stop_requested = False
    self.history = []

    current = self.generate_initial_solution()
    current_score = current.calculate_score()

    for iteration in range(max_iterations):
        if self._stop_requested:
            break

        neighbor = self.get_neighbor(current)
        neighbor_score = neighbor.calculate_score()

        if neighbor_score > current_score:
            current = neighbor
            current_score = neighbor_score

        self.history.append(current_score)

        if callback:
            callback(iteration, current_score)

    return current
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_solver/test_hill_climbing.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/solver/hill_climbing.py tests/test_solver/test_hill_climbing.py
git commit -m "feat: add main hill climbing loop with callback support"
```

---

## Task 10: GUI - Main Application Window

**Files:**
- Create: `src/gui/app.py`
- Create: `main.py`

- [ ] **Step 1: Create main application skeleton**

```python
# src/gui/app.py
import tkinter as tk
from tkinter import ttk


class PhotoSlideshowApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo Slideshow Solver - Hill Climbing")
        self.root.geometry("1200x800")

        self._setup_ui()

    def _setup_ui(self):
        # Main container with grid
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Placeholder panels (will be replaced in later tasks)
        self.dataset_frame = ttk.LabelFrame(self.root, text="Dataset", padding=10)
        self.dataset_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.slideshow_frame = ttk.LabelFrame(self.root, text="Slideshow", padding=10)
        self.slideshow_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        self.control_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding=10)
        self.stats_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)


def create_app() -> tk.Tk:
    """Create and return the main application window."""
    root = tk.Tk()
    app = PhotoSlideshowApp(root)
    return root
```

- [ ] **Step 2: Create entry point**

```python
# main.py
from src.gui.app import create_app


def main():
    root = create_app()
    root.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run to verify GUI opens**

Run: `python main.py`
Expected: Window opens with 4 labeled panels

- [ ] **Step 4: Commit**

```bash
git add src/gui/app.py main.py
git commit -m "feat: add main GUI application skeleton"
```

---

## Task 11: GUI - Dataset Panel

**Files:**
- Create: `src/gui/panels/dataset_panel.py`
- Modify: `src/gui/app.py`

- [ ] **Step 1: Create dataset panel**

```python
# src/gui/panels/dataset_panel.py
import tkinter as tk
from tkinter import ttk, filedialog
from typing import Callable, Optional
from src.io.parser import parse_input


class DatasetPanel(ttk.Frame):
    def __init__(self, parent, on_dataset_loaded: Callable[[list], None]):
        super().__init__(parent)
        self.on_dataset_loaded = on_dataset_loaded
        self.photos = None
        self.filename = None

        self._setup_ui()

    def _setup_ui(self):
        # Load button
        self.load_btn = ttk.Button(self, text="Load Dataset", command=self._load_file)
        self.load_btn.pack(anchor="w", pady=5)

        # File info
        self.file_label = ttk.Label(self, text="No file loaded")
        self.file_label.pack(anchor="w", pady=2)

        # Statistics
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(anchor="w", fill="x")

        self.total_label = ttk.Label(self.stats_frame, text="Photos: -")
        self.total_label.pack(anchor="w")

        self.horizontal_label = ttk.Label(self.stats_frame, text="Horizontal: -")
        self.horizontal_label.pack(anchor="w")

        self.vertical_label = ttk.Label(self.stats_frame, text="Vertical: -")
        self.vertical_label.pack(anchor="w")

    def _load_file(self):
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
            self.filename = filepath.split('/')[-1]

            self._update_stats()
            self.on_dataset_loaded(self.photos)

        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load file: {e}")

    def _update_stats(self):
        self.file_label.config(text=f"File: {self.filename}")

        total = len(self.photos)
        horizontal = sum(1 for p in self.photos if p.is_horizontal)
        vertical = total - horizontal

        self.total_label.config(text=f"Photos: {total}")
        self.horizontal_label.config(text=f"Horizontal: {horizontal}")
        self.vertical_label.config(text=f"Vertical: {vertical}")
```

- [ ] **Step 2: Integrate into app**

```python
# Update src/gui/app.py
# Replace the dataset_frame section with:

from src.gui.panels.dataset_panel import DatasetPanel

# In _setup_ui, replace dataset_frame with:
self.dataset_panel = DatasetPanel(self.root, self._on_dataset_loaded)
self.dataset_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

# Add method:
def _on_dataset_loaded(self, photos):
    self.photos = photos
    print(f"Loaded {len(photos)} photos")
```

- [ ] **Step 3: Test manually**

Run: `python main.py`
Expected: Load Dataset button works, shows stats after loading

- [ ] **Step 4: Commit**

```bash
git add src/gui/panels/dataset_panel.py src/gui/app.py
git commit -m "feat: add dataset panel with file loading"
```

---

## Task 12: GUI - Control Panel

**Files:**
- Create: `src/gui/panels/control_panel.py`
- Modify: `src/gui/app.py`

- [ ] **Step 1: Create control panel**

```python
# src/gui/panels/control_panel.py
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ControlPanel(ttk.Frame):
    def __init__(self, parent, on_run: Callable, on_stop: Callable):
        super().__init__(parent)
        self.on_run = on_run
        self.on_stop = on_stop
        self._is_running = False

        self._setup_ui()

    def _setup_ui(self):
        # Iterations input
        iter_frame = ttk.Frame(self)
        iter_frame.pack(anchor="w", fill="x", pady=5)

        ttk.Label(iter_frame, text="Max Iterations:").pack(side="left")
        self.iterations_var = tk.StringVar(value="10000")
        self.iterations_entry = ttk.Entry(iter_frame, textvariable=self.iterations_var, width=10)
        self.iterations_entry.pack(side="left", padx=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(anchor="w", fill="x", pady=10)

        self.run_btn = ttk.Button(btn_frame, text="▶ Run", command=self._run_clicked)
        self.run_btn.pack(side="left", padx=2)

        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop", command=self._stop_clicked, state="disabled")
        self.stop_btn.pack(side="left", padx=2)

        # Progress bar
        ttk.Label(self, text="Progress:").pack(anchor="w", pady=(10, 0))
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=5)

        # Scores
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        self.current_label = ttk.Label(self, text="Current: -")
        self.current_label.pack(anchor="w")

        self.best_label = ttk.Label(self, text="Best: -")
        self.best_label.pack(anchor="w")

    def _run_clicked(self):
        self._is_running = True
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.on_run()

    def _stop_clicked(self):
        self._is_running = False
        self.on_stop()

    def get_iterations(self) -> int:
        try:
            return int(self.iterations_var.get())
        except ValueError:
            return 10000

    def update_progress(self, iteration: int, max_iterations: int, current_score: int, best_score: int):
        progress = (iteration / max_iterations) * 100
        self.progress_var.set(progress)
        self.current_label.config(text=f"Current: {current_score}")
        self.best_label.config(text=f"Best: {best_score}")

    def reset(self):
        self._is_running = False
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress_var.set(0)
        self.current_label.config(text="Current: -")
        self.best_label.config(text="Best: -")

    def set_running(self, running: bool):
        self._is_running = running
        if running:
            self.run_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        else:
            self.run_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
```

- [ ] **Step 2: Integrate into app**

```python
# Update src/gui/app.py imports and setup
from src.gui.panels.control_panel import ControlPanel

# Replace control_frame with:
self.control_panel = ControlPanel(self.root, self._on_run, self._on_stop)
self.control_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

# Add methods:
def _on_run(self):
    if not self.photos:
        tk.messagebox.showwarning("Warning", "Please load a dataset first")
        return
    # Will implement solver logic in next task
    print("Run clicked")

def _on_stop(self):
    print("Stop clicked")
```

- [ ] **Step 3: Test manually**

Run: `python main.py`
Expected: Control panel with iteration input, run/stop buttons, progress bar

- [ ] **Step 4: Commit**

```bash
git add src/gui/panels/control_panel.py src/gui/app.py
git commit -m "feat: add control panel with run/stop buttons"
```

---

## Task 13: GUI - Statistics Panel (Matplotlib)

**Files:**
- Create: `src/gui/panels/stats_panel.py`
- Modify: `src/gui/app.py`

- [ ] **Step 1: Create statistics panel**

```python
# src/gui/panels/stats_panel.py
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
```

- [ ] **Step 2: Integrate into app**

```python
# Update src/gui/app.py
from src.gui.panels.stats_panel import StatsPanel

# Replace stats_frame with:
self.stats_panel = StatsPanel(self.root)
self.stats_panel.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
```

- [ ] **Step 3: Test manually**

Run: `python main.py`
Expected: Stats panel with empty matplotlib chart

- [ ] **Step 4: Commit**

```bash
git add src/gui/panels/stats_panel.py src/gui/app.py
git commit -m "feat: add statistics panel with matplotlib chart"
```

---

## Task 14: GUI - Slideshow Viewer

**Files:**
- Create: `src/gui/widgets/slide_card.py`
- Create: `src/gui/panels/slideshow_viewer.py`
- Modify: `src/gui/app.py`

- [ ] **Step 1: Create slide card widget**

```python
# src/gui/widgets/slide_card.py
import tkinter as tk
from tkinter import ttk
from src.models.slide import Slide


class SlideCard(ttk.Frame):
    def __init__(self, parent, slide: Slide, index: int, on_click: callable = None):
        super().__init__(parent, relief="raised", borderwidth=2)
        self.slide = slide
        self.index = index
        self.on_click = on_click

        self._setup_ui()

    def _setup_ui(self):
        # Slide number
        ttk.Label(self, text=f"S{self.index}", font=("Arial", 10, "bold")).pack()

        # Photo IDs
        ids = " + ".join(str(pid) for pid in self.slide.photo_ids)
        ttk.Label(self, text=f"[{ids}]", font=("Arial", 8)).pack()

        # Tag count
        ttk.Label(self, text=f"{len(self.slide.tags)} tags", font=("Arial", 8)).pack()

        # Make clickable
        if self.on_click:
            self.bind("<Button-1>", lambda e: self.on_click(self.index))
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda e: self.on_click(self.index))
```

- [ ] **Step 2: Create slideshow viewer**

```python
# src/gui/panels/slideshow_viewer.py
import tkinter as tk
from tkinter import ttk
from src.models.slideshow import Slideshow
from src.gui.widgets.slide_card import SlideCard
from src.solver.scorer import calculate_transition_score


class SlideshowViewer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.slideshow = None
        self.selected_index = None
        self.cards = []

        self._setup_ui()

    def _setup_ui(self):
        # Scrollable frame for slides
        canvas = tk.Canvas(self, height=150)
        scrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")

        # Details panel
        self.details_frame = ttk.LabelFrame(self, text="Slide Details", padding=10)
        self.details_frame.pack(fill="x", pady=5)

        self.tags_label = ttk.Label(self.details_frame, text="Tags: -")
        self.tags_label.pack(anchor="w")

        self.transition_label = ttk.Label(self.details_frame, text="Transition: -")
        self.transition_label.pack(anchor="w")

    def load_slideshow(self, slideshow: Slideshow):
        """Load and display a slideshow."""
        self.slideshow = slideshow
        self.selected_index = None

        # Clear existing cards
        for card in self.cards:
            card.destroy()
        self.cards = []

        # Create new cards
        for i, slide in enumerate(slideshow.slides):
            card = SlideCard(self.scroll_frame, slide, i, self._on_slide_clicked)
            card.pack(side="left", padx=5, pady=5)
            self.cards.append(card)

    def _on_slide_clicked(self, index: int):
        """Handle slide selection."""
        self.selected_index = index
        slide = self.slideshow.slides[index]

        # Update details
        tags_str = ", ".join(sorted(slide.tags))
        self.tags_label.config(text=f"Tags: [{tags_str}]")

        # Show transition score to next slide
        if index < len(self.slideshow.slides) - 1:
            next_slide = self.slideshow.slides[index + 1]
            score = calculate_transition_score(slide, next_slide)
            self.transition_label.config(text=f"Transition S{index}→S{index+1}: score = {score}")
        else:
            self.transition_label.config(text="Transition: (last slide)")

    def clear(self):
        """Clear the viewer."""
        for card in self.cards:
            card.destroy()
        self.cards = []
        self.slideshow = None
        self.tags_label.config(text="Tags: -")
        self.transition_label.config(text="Transition: -")
```

- [ ] **Step 3: Integrate into app**

```python
# Update src/gui/app.py
from src.gui.panels.slideshow_viewer import SlideshowViewer

# Replace slideshow_frame with:
self.slideshow_viewer = SlideshowViewer(self.root)
self.slideshow_viewer.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
```

- [ ] **Step 4: Test manually**

Run: `python main.py`
Expected: Slideshow viewer panel with scrollable area

- [ ] **Step 5: Commit**

```bash
git add src/gui/widgets/slide_card.py src/gui/panels/slideshow_viewer.py src/gui/app.py
git commit -m "feat: add slideshow viewer with clickable slide cards"
```

---

## Task 15: Connect Solver to GUI

**Files:**
- Modify: `src/gui/app.py`

- [ ] **Step 1: Add threading and solver integration**

```python
# Update src/gui/app.py with full implementation
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from src.gui.panels.dataset_panel import DatasetPanel
from src.gui.panels.control_panel import ControlPanel
from src.gui.panels.stats_panel import StatsPanel
from src.gui.panels.slideshow_viewer import SlideshowViewer
from src.solver.hill_climbing import HillClimbingSolver


class PhotoSlideshowApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Photo Slideshow Solver - Hill Climbing")
        self.root.geometry("1200x800")

        self.photos = None
        self.solver = None
        self.best_score = 0

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

    def _on_dataset_loaded(self, photos):
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
            def callback(iteration, score):
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

    def _update_ui(self, iteration, max_iter, score):
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
    root = tk.Tk()
    app = PhotoSlideshowApp(root)
    return root
```

- [ ] **Step 2: Test end-to-end**

Run: `python main.py`
Expected:
1. Load dataset works
2. Run starts solver
3. Progress updates
4. Chart updates in real-time
5. Slideshow displays result

- [ ] **Step 3: Commit**

```bash
git add src/gui/app.py
git commit -m "feat: connect solver to GUI with threading"
```

---

## Task 16: Final Testing and Cleanup

- [ ] **Step 1: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 2: Test with example dataset**

Run: `python main.py`
- Load `data/input/example.txt`
- Run with 1000 iterations
- Verify score improves
- Verify slideshow displays correctly

- [ ] **Step 3: Update README**

```bash
git add README.md
git commit -m "docs: update README with usage instructions"
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete Photo Slideshow Solver with Hill Climbing and GUI"
```

---

## Summary

This plan creates a complete Photo Slideshow Solver application:

1. **Data Models** (Tasks 2-5): Photo, Slide, Slideshow with full validation
2. **Scoring** (Task 4): Transition score calculator
3. **Parser** (Task 6): Input file parsing
4. **Solver** (Tasks 7-9): Hill climbing with neighbors and callbacks
5. **GUI** (Tasks 10-15): Full Tkinter + Matplotlib interface
6. **Integration** (Tasks 15-16): Threading, real-time updates, final testing

Total: ~16 tasks with ~80 steps following TDD approach.
