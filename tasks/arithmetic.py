"""Synthetic arithmetic with an exact numeric-answer reward."""

from decimal import Decimal, InvalidOperation
import json
import random
import re

from rl_framework.task import Task

TEMPLATES = (
    ("What is {} multiplied by {}?", "*"),
    ("Calculate the product of {} and {}.", "*"),
    ("What is the product of {} and {}?", "*"),
    ("How much is {} times {}?", "*"),
    ("What is {} plus {}?", "+"),
    ("Calculate the sum of {} and {}.", "+"),
    ("What's the result of {} plus {}?", "+"),
    ("How much is {} plus {}?", "+"),
    ("What is {} minus {}?", "-"),
    ("Compute {} minus {}.", "-"),
    ("What's the result of {} minus {}?", "-"),
    ("How much is {} minus {}?", "-"),
)
NUMBER = re.compile(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)")
METRICS = ("exact_match",)


def score_response(text, expected):
    """Grade the final numeric token; decimal values are never truncated."""
    matches = NUMBER.findall(text) if isinstance(text, str) else []
    correct = False
    if matches:
        try:
            predicted = Decimal(matches[-1])
            answer = Decimal(str(expected))
            correct = predicted.is_finite() and answer.is_finite() and predicted == answer
        except (InvalidOperation, ValueError):
            pass
    return {"exact_match": float(correct), "reward": float(correct)}


def build_splits(train_size=2000, val_size=140, test_size=280, seed=42):
    """Seeded, operation-balanced splits with disjoint arithmetic operand pairs."""
    sizes = (train_size, val_size, test_size)
    if any(size < 3 for size in sizes):
        raise ValueError("Arithmetic splits need at least three examples")
    if sum((size + 2) // 3 for size in sizes) > 5050:
        raise ValueError("Requested arithmetic dataset is too large for this generator")
    rng = random.Random(seed)
    seen = set()
    splits = {}
    for name, size in zip(("train", "validation", "test"), sizes):
        rows = []
        for i in range(size):
            operation = ("*", "+", "-")[i % 3]
            limit = 100 if operation == "*" else 1000
            while True:
                a, b = rng.randrange(limit), rng.randrange(limit)
                key = (operation, min(a, b), max(a, b)) if operation in ("*", "+") else (operation, a, b)
                if key not in seen:
                    seen.add(key)
                    break
            template = rng.choice([template for template, op in TEMPLATES if op == operation])
            answer = a * b if operation == "*" else a + b if operation == "+" else a - b
            rows.append({"prompt": [{"role": "user", "content": template.format(a, b)}],
                         "expected": json.dumps(answer), "category": operation,
                         "problem": {"operation": operation, "a": a, "b": b}})
        rng.shuffle(rows)
        splits[name] = rows
    return splits


def summarize(records):
    if not records:
        raise ValueError("Cannot evaluate an empty dataset")

    def accuracy(rows):
        count = int(sum(row["scores"]["exact_match"] for row in rows))
        return {"correct": count, "total": len(rows), "percent": 100 * count / len(rows)}

    return {
        "count": len(records), "exact_match": accuracy(records),
        "mean_reward": sum(row["scores"]["reward"] for row in records) / len(records),
        "per_category": {category: accuracy([row for row in records if row["category"] == category])
                         for category in sorted({row["category"] for row in records})},
    }


TASK = Task("arithmetic", build_splits, score_response, summarize, METRICS)
