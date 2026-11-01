"""Explicit Python configuration for a task and its training run."""

from dataclasses import dataclass
from pathlib import Path

from .config import TrainingConfig
from .experiment import GRPOExperiment
from .reporting import write_json
from .task import RetentionSet, Task


@dataclass(frozen=True)
class RunConfig:
    task: Task
    training: TrainingConfig
    retention_sets: tuple[RetentionSet, ...] = ()

    def create_experiment(self):
        return GRPOExperiment(self.task, self.training, self.retention_sets)

    def run(self):
        return self.create_experiment().run()

    def preview_data(self):
        """Build and save datasets without loading a model or importing ML libraries."""
        splits = self.create_experiment().build_datasets()
        output = Path(self.training.output_dir)
        output.mkdir(parents=True, exist_ok=True)
        write_json(output / "datasets-preview.json", splits)
        return splits
