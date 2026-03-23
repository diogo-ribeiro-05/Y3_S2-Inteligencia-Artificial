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


def test_request_stop_halts_execution():
    """Test that request_stop() halts execution mid-experiment and returns partial results."""
    random.seed(42)
    photos = [
        Photo(0, 'H', {'a', 'b'}),
        Photo(1, 'H', {'a', 'c'}),
        Photo(2, 'H', {'b', 'c'}),
    ]

    runner = ExperimentRunner(photos, "test_dataset")
    configs = [
        AlgorithmConfig(algorithm_name="Hill Climbing", parameters={"max_iterations": 100})
    ]

    # Track progress and request stop after first run
    run_count = [0]

    def progress_callback(algo_name, run_num, runs_total, completed, total):
        run_count[0] = completed
        # Request stop after first run completes
        if completed == 1:
            runner.request_stop()

    result = runner.run_experiment(configs, runs_per_config=5, progress_callback=progress_callback)

    # Verify that execution stopped early
    assert len(result.runs) < 5, "Experiment should have been stopped before completing all runs"
    assert len(result.runs) >= 1, "At least one run should have completed"
    assert run_count[0] >= 1, "Progress callback should have been called at least once"

    # Verify partial results are valid
    assert result.dataset_name == "test_dataset"
    assert result.timestamp is not None
    assert all(r.config.algorithm_name == "Hill Climbing" for r in result.runs)
    assert all(r.result.score >= 0 for r in result.runs)
    assert all(r.result.execution_time > 0 for r in result.runs)


def test_multiple_configurations():
    """Test experiment with multiple different algorithm configurations."""
    random.seed(42)
    photos = [
        Photo(0, 'H', {'a', 'b'}),
        Photo(1, 'H', {'a', 'c'}),
        Photo(2, 'H', {'b', 'c'}),
        Photo(3, 'V', {'a', 'd'}),
        Photo(4, 'V', {'b', 'd'}),
    ]

    runner = ExperimentRunner(photos, "test_dataset")

    # Test multiple configurations with different parameters
    configs = [
        AlgorithmConfig(algorithm_name="Hill Climbing", parameters={"max_iterations": 10}),
        AlgorithmConfig(algorithm_name="Hill Climbing", parameters={"max_iterations": 50}),
        AlgorithmConfig(algorithm_name="Hill Climbing", parameters={"max_iterations": 100}),
    ]

    result = runner.run_experiment(configs, runs_per_config=2)

    # Verify all configurations were run
    assert len(result.runs) == 6, "Should have 2 runs for each of 3 configurations"

    # Group results by configuration
    config_results = {}
    for run in result.runs:
        max_iter = run.config.parameters["max_iterations"]
        if max_iter not in config_results:
            config_results[max_iter] = []
        config_results[max_iter].append(run)

    # Verify each configuration has correct number of runs
    assert len(config_results[10]) == 2, "Should have 2 runs with max_iterations=10"
    assert len(config_results[50]) == 2, "Should have 2 runs with max_iterations=50"
    assert len(config_results[100]) == 2, "Should have 2 runs with max_iterations=100"

    # Verify summary groups by algorithm name (not individual parameter sets)
    summary = result.get_summary()
    assert len(summary) == 1, "Summary should group all Hill Climbing configurations together"
    assert summary[0]['algorithm'] == "Hill Climbing"
    assert summary[0]['runs'] == 6, "Summary should include all 6 runs across all configurations"

    # Verify all runs have valid results
    assert all(r.result.score >= 0 for r in result.runs)
    assert all(r.result.execution_time > 0 for r in result.runs)
