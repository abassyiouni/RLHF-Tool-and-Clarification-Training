import json
from pathlib import Path
import tempfile
import unittest

from tasks.clarification import build_clarification_splits
from rl_framework import GRPOExperiment, RetentionSet, TrainingConfig
from rl_framework.reporting import comparison_report, report_markdown
from tasks.clarification import TASK
from tasks.tool_selection import TASK as TOOL_TASK
from tasks.tool_selection import parse_response, score_response, summarize, target


class ClarificationTests(unittest.TestCase):
    def test_split_balance_pairing_and_template_separation(self):
        splits = build_clarification_splits()
        all_prompts = []
        templates = []
        groups = []
        for split, size in (("train", 960), ("validation", 120), ("test", 240)):
            rows = splits[split]
            self.assertEqual(len(rows), size)
            actions = [json.loads(row["expected"])["action"] for row in rows]
            self.assertEqual(actions.count("clarify"), size * 5 // 12)
            self.assertEqual(actions.count("tool"), size * 5 // 12)
            self.assertEqual(actions.count("no_tool"), size * 2 // 12)
            templates.append({row["template_id"] for row in rows})
            groups.append({row["pair_id"] for row in rows})
            all_prompts.extend(row["prompt"][-1]["content"] for row in rows)
            for row in rows:
                self.assertIsNotNone(parse_response(row["expected"]))
            for group in groups[-1]:
                cases = [json.loads(row["expected"]) for row in rows if row["pair_id"] == group]
                complete_tools = {case["tool"] for case in cases if case["action"] == "tool"}
                clarify_tools = {case["tool"] for case in cases if case["action"] == "clarify"}
                self.assertEqual(complete_tools, clarify_tools)
                self.assertEqual(len(complete_tools), 5)
        self.assertEqual(len(all_prompts), len(set(all_prompts)))
        for i in range(3):
            for j in range(i):
                self.assertFalse(templates[i] & templates[j])
                self.assertFalse(groups[i] & groups[j])
        self.assertEqual(splits, build_clarification_splits())

    def test_reject_invalid_sizes(self):
        for size in (0, 13, 1212):
            with self.assertRaises(ValueError):
                build_clarification_splits(train_size=size)

    def test_overclarifying_does_not_game_metrics(self):
        records = []
        for expected in (target("clarify", "track_order"), target("tool", "track_order", order_id="A"), target("no_tool")):
            completion = json.dumps(target("clarify", "track_order"))
            records.append({"category": expected["action"], "expected": expected, "completion": completion,
                            "scores": score_response(completion, expected)})
        summary = summarize(records)
        self.assertEqual(summary["clarification"]["recall"]["percent"], 100)
        self.assertAlmostEqual(summary["clarification"]["precision"]["percent"], 100 / 3)
        self.assertEqual(summary["clarification"]["unnecessary_clarification_rate"]["percent"], 100)
        self.assertAlmostEqual(summary["exact_match"]["percent"], 100 / 3)

    def test_invalid_outputs_cannot_count_as_correct_nonclarification(self):
        expected = target("no_tool")
        row = {"category": "no_tool", "expected": expected, "completion": "invalid",
               "scores": score_response("invalid", expected)}
        summary = summarize([row])
        self.assertEqual(summary["clarification"]["correct_nonclarification_rate"]["percent"], 0)
        self.assertIsNone(summary["clarification"]["precision"]["percent"])
        report = comparison_report({"test": summary}, {"test": summary})
        self.assertIn("N/A (0 cases)", report_markdown(report))

    def test_retention_set_not_in_training(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "datasets.json"
            from tasks.tool_selection import build_splits
            old = build_splits(7, 7, 7)
            path.write_text(json.dumps(old), encoding="utf-8")
            experiment = GRPOExperiment(TASK, TrainingConfig(train_size=24, val_size=12, test_size=12),
                                        [RetentionSet("retention_test", str(path), TOOL_TASK)])
            new = experiment.build_datasets()
            self.assertEqual(new["retention_test"], old["test"])
            self.assertEqual(len(new["train"]), 24)
            path.write_text(json.dumps({"test": new["train"]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                experiment.build_datasets()


if __name__ == "__main__":
    unittest.main()
