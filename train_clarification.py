"""Edit RUN_CONFIG to define the clarification training experiment."""

from rl_framework import RetentionSet, RunConfig, TrainingConfig
from tasks.clarification import TASK
from tasks.tool_selection import TASK as TOOL_SELECTION_TASK, RETENTION_DATASET


RUN_CONFIG = RunConfig(
    task=TASK,
    training=TrainingConfig(
        # Set this to a previous run's final_model directory to continue training.
        model_name="Qwen/Qwen2.5-0.5B-Instruct",
        output_dir="runs/clarification",
        max_steps=60,
        warmup_steps=40,
        learning_rate=1e-5,
        train_size=960,
        val_size=120,
        test_size=240,
        batch_size=32,
        eval_batch_size=16,
        num_generations=4,
        max_completion_length=128,
        seed=42,
        wandb=False,
    ),
    # Evaluate the original tool-selection test cases at every evaluation phase.
    # These examples never enter the training batches.
    retention_sets=(
        RetentionSet(
            name="tool_selection_retention",
            path=str(RETENTION_DATASET),
            task=TOOL_SELECTION_TASK,
        ),
    ),
)


def main():
    return RUN_CONFIG.run()


if __name__ == "__main__":
    main()
