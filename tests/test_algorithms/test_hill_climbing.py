# tests/test_algorithms/test_hill_climbing.py
import random
from src.models.photo import Photo
from src.algorithms.hill_climbing import HillClimbingSolver
from src.algorithms.registry import AlgorithmRegistry


def test_hill_climbing_registered():
    assert "Hill Climbing" in AlgorithmRegistry.get_names()
    algo_class = AlgorithmRegistry.get("Hill Climbing")
    assert algo_class == HillClimbingSolver


def test_hill_climbing_has_parameters():
    algo_class = AlgorithmRegistry.get("Hill Climbing")
    param_names = [p.name for p in algo_class.parameters]
    assert "max_iterations" in param_names


def test_hill_climbing_solve_returns_algorithm_result():
    random.seed(42)
    photos = [
        Photo(0, 'H', {'a', 'b'}),
        Photo(1, 'H', {'a', 'c'}),
        Photo(2, 'H', {'b', 'c'}),
    ]
    algo = HillClimbingSolver()
    result = algo.solve(photos, max_iterations=100)

    assert result.slideshow is not None
    assert result.score >= 0
    assert result.execution_time >= 0
    assert len(result.history) == 100


def test_hill_climbing_callback():
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]
    algo = HillClimbingSolver()
    callback_calls = []

    def callback(iteration, score):
        callback_calls.append((iteration, score))

    algo.solve(photos, max_iterations=5, callback=callback)

    assert len(callback_calls) == 5
