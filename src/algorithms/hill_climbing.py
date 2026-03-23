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
        history = []

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
