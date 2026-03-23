# tests/test_algorithms/test_base.py
from src.algorithms.base import ParameterSchema
from src.models.slide import Slide
from src.models.slideshow import Slideshow
from src.algorithms.base import AlgorithmResult
from src.models.photo import Photo


def test_parameter_schema_creation():
    param = ParameterSchema(
        name="max_iterations",
        type=int,
        default=10000,
        min_value=1,
        max_value=100000,
        description="Maximum iterations"
    )
    assert param.name == "max_iterations"
    assert param.type == int
    assert param.default == 10000
    assert param.min_value == 1
    assert param.max_value == 100000
    assert param.description == "Maximum iterations"


def test_algorithm_result_creation():
    slide = Slide([Photo(0, 'H', {'a'})])
    slideshow = Slideshow([slide])

    result = AlgorithmResult(
        slideshow=slideshow,
        score=100,
        execution_time=1.5,
        history=[10, 50, 100]
    )

    assert result.slideshow == slideshow
    assert result.score == 100
    assert result.execution_time == 1.5
    assert result.history == [10, 50, 100]
