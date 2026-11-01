from dataclasses import replace
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from rl_framework import GRPOExperiment, RetentionSet, TrainingConfig
from rl_framework.reporting import comparison_report, report_markdown, save_evaluation_report, save_comparison_report
from tasks.arithmetic import TASK as ARITHMETIC
from tasks.clarification import TASK as CLARIFICATION
from tasks.tool_selection import TASK as TOOLS
from train_arithmetic import RUN_CONFIG as ARITHMETIC_RUN
from train_clarification import RUN_CONFIG as CLARIFICATION_RUN
from train_tools import RUN_CONFIG as TOOLS_RUN


class ArithmeticTests(unittest.TestCase):
    def test_numeric_correctness_without_decimal_truncation(self):
        for text, expected, reward in (("13 * 72 = 936", "936", 1), ("936.9", "936", 0),
                                       ("answer: -6.84e2", "-684", 1), ("no answer", "0", 0),
                                       ("936, then 935", "936", 0), ("1e99999", "936", 0)):
            with self.subTest(text=text):
                self.assertEqual(ARITHMETIC.score_response(text, expected)["reward"], reward)

    def test_problem_answers_and_cross_split_uniqueness(self):
        splits = ARITHMETIC.build_splits(300, 30, 60, 42)
        seen = set()
        for rows in splits.values():
            for row in rows:
                problem = row["problem"]
                a, b, op = problem["a"], problem["b"], problem["operation"]
                expected = {"*": a * b, "+": a + b, "-": a - b}[op]
                self.assertEqual(json.loads(row["expected"]), expected)
                key = (op, min(a, b), max(a, b)) if op != "-" else (op, a, b)
                self.assertNotIn(key, seen)
                seen.add(key)
        self.assertEqual(splits, ARITHMETIC.build_splits(300, 30, 60, 42))
        with self.assertRaises(ValueError):
            ARITHMETIC.build_splits(25000, 30, 60, 42)


class FrameworkTests(unittest.TestCase):
    def test_shared_reward_adapter_dispatches_to_task(self):
        arithmetic = ARITHMETIC.reward([[{"role": "assistant", "content": "42"}]], ["42"])
        tools = TOOLS.reward([[{"role": "assistant", "content": "42"}]], ['{"action":"no_tool","tool":null,"arguments":{}}'])
        self.assertEqual(arithmetic, [1])
        self.assertEqual(tools, [0])
        with self.assertRaises(ValueError):
            ARITHMETIC.reward(["42"], [])

    def test_configured_runs_preview_without_ml_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, config, expected_train in (("arithmetic", ARITHMETIC_RUN, 2000),
                                                 ("tools", TOOLS_RUN, 2000),
                                                 ("clarification", CLARIFICATION_RUN, 960)):
                output = Path(directory) / name
                configured = replace(config, training=replace(config.training, output_dir=str(output)))
                splits = configured.preview_data()
                self.assertEqual(len(splits["train"]), expected_train)
                self.assertTrue((output / "datasets-preview.json").exists())
                self.assertIs(configured.create_experiment().task, config.task)

    def test_cross_task_retention_uses_arithmetic_scorer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prior = root / "datasets.json"
            old = ARITHMETIC.build_splits(6, 3, 3, 42)
            prior.write_text(json.dumps(old), encoding="utf-8")
            experiment = GRPOExperiment(CLARIFICATION, TrainingConfig(train_size=24, val_size=12, test_size=12),
                                        [RetentionSet("arithmetic_retention", str(prior), ARITHMETIC)])
            splits = experiment.build_datasets()
            experiment.model = Mock(training=False)
            experiment.run_dir = root
            answers = {row["prompt"][-1]["content"]: row["expected"] for row in old["test"]}
            experiment.generate = Mock(side_effect=lambda prompts: [answers[p[-1]["content"]] for p in prompts])
            with contextlib.redirect_stdout(io.StringIO()):
                metrics = experiment.evaluate(splits["arithmetic_retention"], "before", "arithmetic_retention")
            self.assertEqual(metrics["exact_match"]["correct"], 3)
            self.assertNotIn("clarification", metrics)
            report = comparison_report({"arithmetic_retention": metrics}, {"arithmetic_retention": metrics})
            self.assertIn("3/3 (100.00%)", report_markdown(report))
            self.assertNotIn("tool_choice_correct", report_markdown(report))

    def test_clarification_retains_original_tool_test_without_training_on_it(self):
        self.assertEqual(len(CLARIFICATION_RUN.retention_sets), 1)
        retention = CLARIFICATION_RUN.retention_sets[0]
        self.assertIs(retention.task, TOOLS)
        experiment = CLARIFICATION_RUN.create_experiment()
        splits = experiment.build_datasets()
        retained = splits["tool_selection_retention"]
        self.assertEqual(len(retained), 280)
        self.assertEqual(retained, TOOLS.build_splits(2000, 140, 280, 42)["test"])
        self.assertEqual(len(splits["train"]), 960)
        training_prompts = {json.dumps(row["prompt"], sort_keys=True) for row in splits["train"]}
        self.assertFalse(training_prompts & {json.dumps(row["prompt"], sort_keys=True) for row in retained})
        self.assertIs(experiment.evaluation_tasks["tool_selection_retention"], TOOLS)

    def test_reports_show_retention_regression_and_undefined_metrics(self):
        before = {"tool_selection_retention": {
            "exact_match": {"correct": 9, "total": 10, "percent": 90.0},
            "per_category": {"track_order": {"correct": 2, "total": 2, "percent": 100.0}},
            "clarification": {"precision": {"count": 0, "total": 0, "percent": None}},
        }}
        after = {"tool_selection_retention": {
            "exact_match": {"correct": 8, "total": 10, "percent": 80.0},
            "per_category": {"track_order": {"correct": 1, "total": 2, "percent": 50.0}},
            "clarification": {"precision": {"count": 1, "total": 2, "percent": 50.0}},
        }}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for phase, data in (("before", before), ("after_warmup", before), ("after", after)):
                save_evaluation_report(root, phase, data)
                self.assertEqual(json.loads((root / f"{phase}.json").read_text()), data)
                self.assertIn("tool_selection_retention", (root / f"{phase}.md").read_text())
            self.assertIn("N/A (0 cases)", (root / "before.md").read_text())
            self.assertIn("After supervised warm-up", (root / "after_warmup.md").read_text())
            comparison = save_comparison_report(root, "comparison", before, after, "Before vs. after")
            self.assertEqual(comparison["tool_selection_retention"]["exact_match"]["delta_percentage_points"], -10)
            markdown = (root / "comparison.md").read_text()
            self.assertIn("-10.00", markdown)
            self.assertIn("-50.00", markdown)
            self.assertEqual(json.loads((root / "comparison.json").read_text()), comparison)

    def test_framework_preserves_saved_tool_scoring(self):
        # Compare the refactored task scorer with recorded run artifacts when present.
        path = Path(__file__).resolve().parents[1] / "runs/20261101T190715603501Z/after_test_predictions.jsonl"
        if not path.exists():
            self.skipTest("Historical artifact is not present in this checkout")
        for line in path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            self.assertEqual(TOOLS.score_response(record["completion"], record["expected"]), record["scores"])


if __name__ == "__main__":
    unittest.main()
