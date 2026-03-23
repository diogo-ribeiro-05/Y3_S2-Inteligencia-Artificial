# src/experiment/runner.py
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional
from src.algorithms.registry import AlgorithmRegistry
from src.algorithms.base import AlgorithmResult
from src.models.photo import Photo


@dataclass
class AlgorithmConfig:
    """Configuration for an algorithm in an experiment."""
    algorithm_name: str
    parameters: dict


@dataclass
class RunResult:
    """Result of a single run."""
    config: AlgorithmConfig
    result: AlgorithmResult


@dataclass
class ExperimentResult:
    """Complete result of an experiment."""
    dataset_name: str
    timestamp: str
    runs: list[RunResult]

    def get_summary(self) -> list[dict]:
        """Return aggregated statistics per algorithm."""
        summaries = []
        for algo_name in set(r.config.algorithm_name for r in self.runs):
            algo_runs = [r for r in self.runs if r.config.algorithm_name == algo_name]
            scores = [r.result.score for r in algo_runs]
            times = [r.result.execution_time for r in algo_runs]

            mean_score = sum(scores) / len(scores)
            variance = sum((x - mean_score)**2 for x in scores) / len(scores)
            std_score = variance ** 0.5

            summaries.append({
                'algorithm': algo_name,
                'parameters': algo_runs[0].config.parameters,
                'runs': len(scores),
                'mean_score': mean_score,
                'std_score': std_score,
                'best_score': max(scores),
                'worst_score': min(scores),
                'mean_time': sum(times) / len(times),
                'best_result': max(algo_runs, key=lambda r: r.result.score)
            })
        return summaries


class ExperimentRunner:
    """Execute batch experiments with multiple runs."""

    def __init__(self, photos: list[Photo], dataset_name: str):
        self.photos = photos
        self.dataset_name = dataset_name
        self._stop_requested = False

    def run_experiment(
        self,
        configs: list[AlgorithmConfig],
        runs_per_config: int,
        progress_callback: Optional[Callable] = None
    ) -> ExperimentResult:
        """
        Execute all configurations with runs_per_config runs each.

        Args:
            configs: List of algorithm configurations
            runs_per_config: Number of runs per configuration
            progress_callback: callback(algo_name, run_num, runs_total, completed, total)
        """
        total_runs = len(configs) * runs_per_config
        completed_runs = 0
        all_results = []

        for config in configs:
            algo_class = AlgorithmRegistry.get(config.algorithm_name)

            for run_num in range(runs_per_config):
                if self._stop_requested:
                    break

                algorithm = algo_class()
                result = algorithm.solve(self.photos, **config.parameters)

                all_results.append(RunResult(config=config, result=result))
                completed_runs += 1

                if progress_callback:
                    progress_callback(
                        config.algorithm_name,
                        run_num + 1,
                        runs_per_config,
                        completed_runs,
                        total_runs
                    )

        return ExperimentResult(
            dataset_name=self.dataset_name,
            timestamp=datetime.now().isoformat(),
            runs=all_results
        )

    def request_stop(self):
        self._stop_requested = True
