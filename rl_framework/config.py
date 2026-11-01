"""Shared model, optimization, and dataset-size settings."""

from dataclasses import dataclass


@dataclass
class TrainingConfig:
    model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"
    output_dir: str = "runs"
    max_steps: int = 60
    learning_rate: float = 1e-5
    train_size: int = 2000
    val_size: int = 140
    test_size: int = 280
    batch_size: int = 32
    eval_batch_size: int = 16
    num_generations: int = 4
    max_completion_length: int = 128
    seed: int = 42
    wandb: bool = False
    warmup_steps: int = 0

    def __post_init__(self):
        if self.warmup_steps < 0:
            raise ValueError("Warm-up steps cannot be negative")
        if self.max_steps < 1 or self.learning_rate <= 0:
            raise ValueError("Steps and learning rate must be positive")
        if self.num_generations < 2 or self.batch_size < 1 or self.batch_size % self.num_generations:
            raise ValueError("Batch size must be a positive multiple of num_generations >= 2")
        if self.eval_batch_size < 1 or self.max_completion_length < 1:
            raise ValueError("Evaluation batch size and completion length must be positive")
