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
