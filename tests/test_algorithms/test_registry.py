from src.algorithms.base import BaseAlgorithm, ParameterSchema, AlgorithmResult
from src.algorithms.registry import AlgorithmRegistry
from src.algorithms import HillClimbingSolver  # Ensure HillClimbingSolver is registered
from src.models.photo import Photo


def test_registry_register():
    # Save existing algorithms
    existing = AlgorithmRegistry._algorithms.copy()

    @AlgorithmRegistry.register
    class TestAlgo(BaseAlgorithm):
        name = "Test Algo"
        parameters = []

        def solve(self, photos, callback=None, **params):
            pass

    assert "Test Algo" in AlgorithmRegistry._algorithms
    assert AlgorithmRegistry._algorithms["Test Algo"] == TestAlgo

    # Restore registry (remove test algo)
    AlgorithmRegistry._algorithms = existing


def test_registry_get_methods():
    # Save existing algorithms
    existing = AlgorithmRegistry._algorithms.copy()

    @AlgorithmRegistry.register
    class Algo1(BaseAlgorithm):
        name = "Algo One"
        parameters = []
        def solve(self, photos, callback=None, **params):
            pass

    @AlgorithmRegistry.register
    class Algo2(BaseAlgorithm):
        name = "Algo Two"
        parameters = []
        def solve(self, photos, callback=None, **params):
            pass

    assert AlgorithmRegistry.get("Algo One") == Algo1
    assert AlgorithmRegistry.get("Algo Two") == Algo2
    assert AlgorithmRegistry.get("NonExistent") is None
    # Only check the two new algos exist
    assert AlgorithmRegistry.get("Algo One") is not None
    assert AlgorithmRegistry.get("Algo Two") is not None
    assert "Algo One" in AlgorithmRegistry.get_names()
    assert "Algo Two" in AlgorithmRegistry.get_names()

    # Restore registry
    AlgorithmRegistry._algorithms = existing
