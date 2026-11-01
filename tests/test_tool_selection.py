import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from rl_framework import GRPOExperiment, TrainingConfig
from rl_framework.reporting import comparison_report, report_markdown
from tasks.tool_selection import TASK
from tasks.tool_selection import LABELS, build_splits, parse_response, reward_tool_selection, score_response, summarize, target


class RewardTests(unittest.TestCase):
    def setUp(self):
        self.expected = target("tool", "track_order", order_id="AB-1391")

    def test_correct_call_ignores_whitespace_and_key_order(self):
        response = ' {"arguments": {"order_id": "AB-1391"}, "tool": "track_order", "action": "tool"} '
        self.assertEqual(score_response(response, self.expected)["reward"], 1)

    def test_wrong_value_only_gets_tool_credit(self):
        scores = score_response(json.dumps(target("tool", "track_order", order_id="AB-1392")), self.expected)
        self.assertEqual(scores["reward"], 0.25)
        self.assertEqual(scores["tool_choice_correct"], 1)
        self.assertEqual(scores["arguments_correct"], 0)
        self.assertEqual(scores["exact_match"], 0)

    def test_valid_format_wrong_tool_earns_nothing(self):
        scores = score_response(json.dumps(target("tool", "search_products", query="AB-1391")), self.expected)
        self.assertEqual(scores["valid_schema"], 1)
        self.assertEqual(scores["action_correct"], 1)
        self.assertEqual(scores["reward"], 0)

    def test_invalid_and_adversarial_outputs(self):
        good = json.dumps(self.expected)
        bad = ["", "null", "[]", "123", "true", "{}", "prefix " + good, good + good,
               "```json\n" + good + "\n```", good.replace('"AB-1391"', '1391'),
               good.replace('"AB-1391"', 'null'), good.replace('"AB-1391"', '""'),
               good.replace('"order_id": "AB-1391"', '"order_id": "wrong", "order_id": "AB-1391"'),
               json.dumps({**self.expected, "extra": True}),
               json.dumps(target("tool", "track_order")),
               json.dumps(target("tool", "track_order", order_id="AB-1391", extra="value")),
               json.dumps(target("tool", "unknown", order_id="AB-1391")),
               json.dumps({"action": [], "tool": [], "arguments": {}}),
               json.dumps(target("tool", "get_weather", city="Paris", unit="kelvin"))]
        for text in bad:
            with self.subTest(text=text):
                self.assertIsNone(parse_response(text))
                self.assertTrue(all(value == 0 for value in score_response(text, self.expected).values()))

    def test_no_tool_and_clarification_are_distinct(self):
        for expected in (target("no_tool"), target("clarify", "find_flights")):
            self.assertEqual(score_response(json.dumps(expected), expected)["reward"], 1)
        self.assertEqual(score_response(json.dumps(target("no_tool")), target("clarify", "find_flights"))["reward"], 0)
        self.assertIsNone(parse_response(json.dumps(target("no_tool", "find_flights"))))
        self.assertIsNone(parse_response(json.dumps(target("clarify", "find_flights", origin="Paris"))))

    def test_trl_callback_handles_conversation_and_plain_text(self):
        good = json.dumps(self.expected)
        self.assertEqual(reward_tool_selection(
            completions=[[{"role": "assistant", "content": good}], "bad", good],
            expected=[good] * 3, prompts=[[]] * 3, trainer_state=None), [1, 0, 1])
        with self.assertRaises(ValueError):
            reward_tool_selection([good], [])


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.splits = build_splits()

    def test_balanced_sizes_and_valid_targets(self):
        for split, expected_size in (("train", 2000), ("validation", 140), ("test", 280)):
            rows = self.splits[split]
            self.assertEqual(len(rows), expected_size)
            counts = [sum(r["category"] == label for r in rows) for label in LABELS]
            self.assertLessEqual(max(counts) - min(counts), 1)
            for row in rows:
                self.assertEqual(score_response(row["expected"], row["expected"])["reward"], 1)
                self.assertEqual([p["role"] for p in row["prompt"]], ["system", "user"])

    def test_no_duplicate_prompts_across_or_within_splits(self):
        prompts = [row["prompt"][-1]["content"] for rows in self.splits.values() for row in rows]
        self.assertEqual(len(prompts), len(set(prompts)))

    def test_seed_reproducibility(self):
        self.assertEqual(self.splits, build_splits())
        self.assertNotEqual(self.splits["test"], build_splits(seed=43)["test"])

    def test_invalid_sizes_fail_instead_of_repeating_samples(self):
        with self.assertRaises(ValueError):
            build_splits(test_size=0)
        with self.assertRaises(ValueError):
            build_splits(train_size=100000)


class EvaluationTests(unittest.TestCase):
    def test_metrics_count_invalid_outputs_and_report_percentage_points(self):
        expected = target("tool", "track_order", order_id="AB-1391")
        correct = {"category": "track_order", "scores": score_response(json.dumps(expected), expected)}
        wrong = {"category": "track_order", "scores": score_response("invalid", expected)}
        before = summarize([correct, wrong])
        after = summarize([correct, correct])
        self.assertEqual(before["exact_match"], {"correct": 1, "total": 2, "percent": 50.0})
        report = comparison_report({"test": before}, {"test": after})
        self.assertEqual(report["test"]["exact_match"]["delta_percentage_points"], 50)
        self.assertIn("1/2 (50.00%)", report_markdown(report))
        self.assertIn("2/2 (100.00%)", report_markdown(report))

    def test_evaluation_batches_and_saves_every_prediction(self):
        rows = build_splits(7, 7, 7)["test"]
        experiment = GRPOExperiment(TASK, TrainingConfig(eval_batch_size=3))
        experiment.model = Mock(training=True)
        answers = {row["prompt"][-1]["content"]: row["expected"] for row in rows}
        experiment.generate = Mock(side_effect=lambda prompts: [answers[p[-1]["content"]] for p in prompts])
        with tempfile.TemporaryDirectory() as directory:
            experiment.run_dir = Path(directory)
            with contextlib.redirect_stdout(io.StringIO()):
                metrics = experiment.evaluate(rows, "before", "test")
            self.assertEqual(metrics["exact_match"]["correct"], 7)
            self.assertEqual(experiment.generate.call_count, 3)
            self.assertEqual(len((Path(directory) / "before_test_predictions.jsonl").read_text().splitlines()), 7)
            self.assertTrue((Path(directory) / "before_test_metrics.json").exists())
        experiment.model.train.assert_called_once_with(True)

    def test_evaluation_restores_mode_on_generation_failure(self):
        experiment = GRPOExperiment(TASK)
        experiment.model = Mock(training=False)
        experiment.generate = Mock(side_effect=RuntimeError("generation failed"))
        with self.assertRaises(RuntimeError):
            experiment.evaluate(build_splits(7, 7, 7)["test"], "before", "test")
        experiment.model.train.assert_called_once_with(False)

    def test_invalid_training_batch(self):
        for values in ({"batch_size": 7}, {"max_steps": 0}, {"eval_batch_size": 0}, {"num_generations": 1}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                TrainingConfig(**values)


if __name__ == "__main__":
    unittest.main()
