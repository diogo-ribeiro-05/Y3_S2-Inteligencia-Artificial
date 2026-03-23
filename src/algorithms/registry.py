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

    @classmethod
    def clear(cls) -> None:
        """Clear all registered algorithms. Useful for testing."""
        cls._algorithms.clear()
