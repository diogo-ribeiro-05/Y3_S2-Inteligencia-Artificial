# Photo Slideshow Solver - Design Specification

**Date:** 2026-03-21
**Project:** Google Hash Code 2019 - Photo Slideshow Problem
**Algorithm:** Hill Climbing

## Overview

A desktop application to solve the Photo Slideshow problem from Google Hash Code 2019 using the Hill Climbing optimization algorithm. The application provides a visual interface to load datasets, run the solver, visualize the slideshow, and track score evolution.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFACE (Tkinter)                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │ Dataset  │ │ Controlos│ │ Slideshow│ │ Gráficos  │  │
│  │  Panel   │ │  Panel   │ │  Viewer  │ │ Matplotlib│  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │
└───────┼────────────┼────────────┼─────────────┼────────┘
        │            │            │             │
        v            v            v             v
┌─────────────────────────────────────────────────────────┐
│                    CAMADA DE LÓGICA                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Parser (I/O) │  │ Hill Climbing│  │   Scorer     │  │
│  │              │  │   Solver     │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
        │
        v
┌─────────────────────────────────────────────────────────┐
│                    MODELO DE DADOS                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │
│  │   Photo    │  │   Slide    │  │   Slideshow    │    │
│  └────────────┘  └────────────┘  └────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Pattern:** MVC (Model-View-Controller)

## File Structure

```
Y3_S2-Inteligencia-Artificial/
├── README.md
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── photo.py        # Photo class
│   │   ├── slide.py        # Slide class
│   │   └── slideshow.py    # Slideshow class
│   ├── solver/
│   │   ├── __init__.py
│   │   ├── scorer.py       # Score calculation
│   │   └── hill_climbing.py # Hill climbing algorithm
│   ├── io/
│   │   ├── __init__.py
│   │   └── parser.py       # File I/O
│   └── gui/
│       ├── __init__.py
│       ├── app.py          # Main Tkinter application
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
│   ├── input/              # Sample datasets
│   │   └── example.txt
│   └── output/             # Generated solutions
└── requirements.txt
```

## Data Model

### Photo
```python
@dataclass
class Photo:
    id: int
    orientation: str          # 'H' or 'V'
    tags: set[str]           # Set of tags for efficient operations
```

### Slide
```python
@dataclass
class Slide:
    photos: list[Photo]      # 1 horizontal photo OR 2 vertical photos

    @property
    def tags(self) -> set[str]:
        # Union of photo tags
        # 1 photo: returns that photo's tags
        # 2 photos: returns union of tags
```

### Slideshow
```python
@dataclass
class Slideshow:
    slides: list[Slide]

    def calculate_score(self) -> int:
        # Sum of interest factors between consecutive slides

    def to_output(self, filepath: str) -> None:
        # Generate submission file in specified format

    @staticmethod
    def calculate_transition_score(s1: Slide, s2: Slide) -> int:
        # min(common_tags, tags_only_s1, tags_only_s2)
```

## Hill Climbing Algorithm

### Strategy
Generate neighboring solutions and accept only those that improve the score.

### Neighborhood Operators
1. **Swap slides:** Swap positions of two slides
2. **Swap vertical photos:** Swap vertical photos between two composite slides
3. **Add/Remove:** Add or remove a slide

### Solver Structure
```python
class HillClimbingSolver:
    def __init__(self, photos: list[Photo]):
        self.photos = photos
        self.current_solution: Slideshow
        self.history: list[int]  # Scores over time

    def generate_initial_solution(self) -> Slideshow:
        # 1. Separate H and V photos
        # 2. H slides -> 1 photo each
        # 3. V slides -> pair V photos (2 per slide)
        # 4. Random initial order

    def get_neighbor(self, solution: Slideshow) -> Slideshow:
        # Apply random operator (swap slides, etc.)

    def solve(self, max_iterations: int, callback: Callable = None) -> Slideshow:
        # Main loop:
        #   neighbor = get_neighbor(current)
        #   if neighbor.score > current.score:
        #       current = neighbor
        #   history.append(current.score)
        #   if callback: callback(iteration, current_score)
        # return current
```

### GUI Callback
The solver supports a callback function that receives `(iteration, current_score)` to enable real-time UI updates.

## User Interface

### Main Window Layout

```
┌────────────────────────────────────────────────────────────────┐
│  Photo Slideshow Solver - Hill Climbing           [_][□][×]   │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌────────────────────────────────────┐  │
│  │ DATASET PANEL   │  │      SLIDESHOW VIEWER              │  │
│  │                 │  │                                    │  │
│  │ [Load Dataset]  │  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐      │  │
│  │                 │  │  │ S0 │ │ S1 │ │ S2 │ │ S3 │ ...  │  │
│  │ File:           │  │  │cats│ │dog │ │sun │ │beach│     │  │
│  │ example.txt     │  │  └────┘ └────┘ └────┘ └────┘      │  │
│  │                 │  │                                    │  │
│  │ Photos: 1000    │  │  Tags: [cat, beach, sun, ...]      │  │
│  │ Horizontal: 600 │  │                                    │  │
│  │ Vertical: 400   │  │  Transition S0→S1: score = 5       │  │
│  └─────────────────┘  └────────────────────────────────────┘  │
│  ┌─────────────────┐  ┌────────────────────────────────────┐  │
│  │ CONTROL PANEL   │  │      STATISTICS PANEL              │  │
│  │                 │  │                                    │  │
│  │ Max Iterations: │  │     ┌─────────────────────────┐   │  │
│  │ [10000    ]     │  │     │    Score Evolution      │   │  │
│  │                 │  │     │      (Matplotlib)       │   │  │
│  │ [▶ Run] [⏹ Stop]│  │     │    ┌──────────┐        │   │  │
│  │                 │  │     │    │/\  /\    │        │   │  │
│  │ Progress:       │  │     │    │  \/  \___│        │   │  │
│  │ [██████░░░░] 60%│  │     │    └──────────┘        │   │  │
│  │                 │  │     └─────────────────────────┘   │  │
│  │ Current: 4500   │  │                                    │  │
│  │ Best: 5200      │  │  Best Score: 5200                  │  │
│  └─────────────────┘  └────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Components

#### Dataset Panel
- Load dataset button
- Display filename
- Show photo statistics (total, horizontal, vertical)

#### Slideshow Viewer
- Horizontal scrollable list of slide cards
- Each card shows: slide number, tags preview
- Click on slide to see full details
- Display transition scores between selected slides

#### Control Panel
- Max iterations input field
- Run/Stop buttons
- Progress bar
- Current score display
- Best score display

#### Statistics Panel
- Matplotlib graph showing score evolution
- Real-time updates during execution
- Best score summary

### Real-time Updates
- Separate thread for solver execution
- Callback every N iterations to update UI
- Graph updates dynamically during execution

## File Formats

### Input Format
```
N                     # Number of photos
O M tag1 tag2 ...     # Photo 0: O=orientation(H/V), M=number of tags, followed by M tags
O M tag1 tag2 ...     # Photo 1
...
```

Example:
```
4
H 3 cat beach sun
V 2 selfie smile
V 2 garden selfie
H 2 garden cat
```

- Line 1: 4 photos in collection
- Photo 0: Horizontal, 3 tags [cat, beach, sun]
- Photo 1: Vertical, 2 tags [selfie, smile]
- Photo 2: Vertical, 2 tags [garden, selfie]
- Photo 3: Horizontal, 2 tags [garden, cat]

### Output Format (Submission)
```
S           # Number of slides
id          # Slide with single horizontal photo
id1 id2     # Slide with two vertical photos
```

Example:
```
3
0
3
1 2
```

- 3 slides total
- Slide 0: Photo 0 (horizontal)
- Slide 1: Photo 3 (horizontal)
- Slide 2: Photos 1 and 2 (vertical pair)

## Dependencies

```
matplotlib>=3.5.0
```

(Tkinter is included with Python standard library)

## Scoring

For two consecutive slides S_i and S_{i+1}:
- **Common tags:** tags present in both slides
- **Only in S_i:** tags present in S_i but not S_{i+1}
- **Only in S_{i+1}:** tags present in S_{i+1} but not S_i

**Interest factor** = min(common_tags, only_in_Si, only_in_Si+1)

**Total score** = sum of all interest factors between consecutive slides
