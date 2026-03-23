# tests/test_experiment/test_runner.py
import random
from src.models.photo import Photo
from src.experiment.runner import ExperimentRunner, AlgorithmConfig, ExperimentResult
from src.algorithms.hill_climbing import HillClimbingSolver  # Import to trigger registration


def test_algorithm_config_creation():
    config = AlgorithmConfig(
        algorithm_name="Hill Climbing",
        parameters={"max_iterations": 5000}
    )
    assert config.algorithm_name == "Hill Climbing"
    assert config.parameters == {"max_iterations": 5000}


def test_experiment_runner_single_config():
    random.seed(42)
    photos = [
        Photo(0, 'H', {'a', 'b'}),
        Photo(1, 'H', {'a', 'c'}),
        Photo(2, 'H', {'b', 'c'}),
    ]

    runner = ExperimentRunner(photos, "test_dataset")
    configs = [
        AlgorithmConfig(algorithm_name="Hill Climbing", parameters={"max_iterations": 10})
    ]

    result = runner.run_experiment(configs, runs_per_config=2)

    assert result.dataset_name == "test_dataset"
    assert result.timestamp is not None
    assert len(result.runs) == 2
    assert all(r.config.algorithm_name == "Hill Climbing" for r in result.runs)


def test_experiment_result_summary():
    random.seed(42)
    photos = [
        Photo(0, 'H', {'a'}),
        Photo(1, 'H', {'b'}),
    ]

    runner = ExperimentRunner(photos, "test")
    configs = [AlgorithmConfig(algorithm_name="Hill Climbing", parameters={"max_iterations": 5})]
    result = runner.run_experiment(configs, runs_per_config=3)

    summary = result.get_summary()
    assert len(summary) == 1
    assert summary[0]['algorithm'] == "Hill Climbing"
    assert summary[0]['runs'] == 3
    assert 'mean_score' in summary[0]
    assert 'std_score' in summary[0]
    assert 'best_score' in summary[0]
    assert 'worst_score' in summary[0]
