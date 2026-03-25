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
    options: list[str] | None = None  # For str type: list of allowed values (dropdown)


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
