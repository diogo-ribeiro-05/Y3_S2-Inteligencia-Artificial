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
