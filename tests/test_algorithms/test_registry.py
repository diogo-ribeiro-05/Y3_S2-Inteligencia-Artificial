from src.algorithms.base import BaseAlgorithm, ParameterSchema, AlgorithmResult
from src.algorithms.registry import AlgorithmRegistry
from src.models.photo import Photo


@AlgorithmRegistry.register
class MockAlgorithm(BaseAlgorithm):
    name = "Mock Algorithm"
    parameters = []

    def solve(self, photos, callback=None, **params):
        return AlgorithmResult(
            slideshow=None,
            score=0,
            execution_time=0.0,
            history=[]
        )


def test_registry_register():
    # Clear registry for test isolation
    AlgorithmRegistry._algorithms = {}

    @AlgorithmRegistry.register
    class TestAlgo(BaseAlgorithm):
        name = "Test Algo"
        parameters = []

        def solve(self, photos, callback=None, **params):
            pass

    assert "Test Algo" in AlgorithmRegistry._algorithms
    assert AlgorithmRegistry._algorithms["Test Algo"] == TestAlgo


def test_registry_get_methods():
    AlgorithmRegistry._algorithms = {}

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
    assert len(AlgorithmRegistry.get_all()) == 2
    assert set(AlgorithmRegistry.get_names()) == {"Algo One", "Algo Two"}
