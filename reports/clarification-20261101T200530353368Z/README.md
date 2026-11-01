# H100 clarification training report

Run: `20261101T200530353368Z`.

Started from `Qwen/Qwen2.5-0.5B-Instruct` with 40 supervised warm-up steps and 60 GRPO steps. Clarification used 960 training, 120 validation, and 240 test examples. Retention used the 280 frozen original tool-selection test cases; those cases were never added to training.

| Metric | Before | After warm-up | After GRPO |
|---|---:|---:|---:|
| Clarification test exact match | 32.50% | 55.83% | 60.42% |
| Tool-selection retention exact match | 57.50% | 87.50% | 74.64% |
| Unnecessary clarification on clarification test (lower is better) | 0.00% | 2.86% | 37.14% |

GRPO improved clarification exact match but reduced tool-selection accuracy relative to warm-up and increased unnecessary clarification. These are synthetic benchmark results from one run, not a general reliability guarantee. Warm-up took about 3.5 seconds and GRPO about 60 seconds, excluding evaluation and saving.

## Generated reports

- [Before training](before.md)
- [After supervised warm-up](after_warmup.md)
- [After training](after.md)
- [Before vs. after](comparison.md)
- [Before vs. warm-up](warmup_comparison.md)
- [Warm-up vs. GRPO](grpo_comparison.md)

Machine-readable JSON reports, training configuration, environment versions, and runtimes are included alongside these reports. Checkpoint weights and per-example run outputs remain outside Git.
