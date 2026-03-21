# Photo Slideshow Solver

Solves the Google Hash Code 2019 Photo Slideshow problem using Hill Climbing optimization.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## How it works

1. Load a dataset (input file in Hash Code format)
2. Configure max iterations
3. Click "Run" to start optimization
4. View the score evolution and final slideshow

## Algorithm

Hill Climbing with slide swapping neighbors. The algorithm:
1. Generates an initial valid solution
2. Generates neighbors by swapping slides
3. Accepts only improving moves
4. Continues until max iterations or stopped

## Project Structure

```
src/
├── models/       # Photo, Slide, Slideshow
├── solver/       # Hill Climbing, Scorer
├── io/           # Parser
└── gui/          # Tkinter panels
```

## Testing

```bash
python -m pytest tests/ -v
```
