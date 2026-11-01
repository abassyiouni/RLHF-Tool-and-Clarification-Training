"""Small task interface: data and grading belong outside the training engine."""

from dataclasses import dataclass
import json
from typing import Callable


@dataclass(frozen=True)
class Task:
    name: str
    build_splits: Callable
    score_response: Callable
    summarize: Callable
    metric_names: tuple[str, ...]
    primary_metric: str = "exact_match"

    def reward(self, completions, expected, **kwargs):
        """TRL-compatible adapter shared by every task."""
        if len(completions) != len(expected):
            raise ValueError("Completions and targets must have equal lengths")
        rewards = []
        for completion, answer in zip(completions, expected):
            if isinstance(completion, list):
                text = completion[0].get("content", "") if len(completion) == 1 else ""
            else:
                text = completion
            rewards.append(self.score_response(text, answer)["reward"])
        return rewards

    def supervised_target(self, row):
        answer = row["expected"]
        return answer if isinstance(answer, str) else json.dumps(answer)


@dataclass(frozen=True)
class RetentionSet:
    """Evaluate a previous test split with its own task's scorer."""

    name: str
    path: str
    task: Task
