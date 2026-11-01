"""Edit RUN_CONFIG to define the tool_selection training experiment."""

from rl_framework import RunConfig, TrainingConfig
from tasks.tool_selection import TASK


RUN_CONFIG = RunConfig(
    task=TASK,
    training=TrainingConfig(
        # Set this to a previous run's final_model directory to continue training.
        model_name="Qwen/Qwen2.5-0.5B-Instruct",
        output_dir="runs/tool_selection",
        max_steps=60,
        warmup_steps=0,
        learning_rate=1e-5,
        train_size=2000,
        val_size=140,
        test_size=280,
        batch_size=32,
        eval_batch_size=16,
        num_generations=4,
        max_completion_length=128,
        seed=42,
        wandb=False,
    ),
    # Add RetentionSet objects here to evaluate previous capabilities.
    retention_sets=(),
)


def main():
    return RUN_CONFIG.run()


if __name__ == "__main__":
    main()
