# RLHF Tool and Clarification Training

A reusable Python training framework with separate arithmetic, tool-selection, and clarification pipelines. Every run measures the incoming model and trained model on identical held-out examples, then saves reports and checkpoints.

## Configuration in Python

Each pipeline file contains an explicit `RUN_CONFIG`. Edit that object to select the starting model, dataset sizes, supervised warm-up steps, GRPO steps, optimizer settings, tracking, and retention evaluations. There are no command-line options or installed console commands. Importing a pipeline does not start training.

```text
train_arithmetic.py    # Arithmetic RUN_CONFIG and main()
train_tools.py         # Tool-selection RUN_CONFIG and main()
train_clarification.py # Clarification RUN_CONFIG and main()
rl_framework/
  run.py              # RunConfig: task + training settings + retention sets
  experiment.py       # Shared model loading, warm-up, GRPO, evaluation
  config.py           # TrainingConfig fields and validation
  task.py             # Task and RetentionSet interfaces
  reporting.py        # Before/after reports
tasks/
  arithmetic.py       # Arithmetic data and reward
  tool_selection.py   # Tool routing data and reward
  clarification.py    # Complete/incomplete requests; shared tool scoring
  data/tool_selection_retention.json  # Frozen original tool-selection test set
```

Use a Linux CUDA GPU environment with Python 3.10-3.13 and BF16 support, such as the H100 pod. Install with `python -m pip install -e .`.

Run the configured experiment from Python or your IDE:

```python
from train_arithmetic import RUN_CONFIG

comparison = RUN_CONFIG.run()
```

Alternatively, execute `train_arithmetic.py` directly with your IDE's Run action. Its `main()` invokes the same configuration. Each pipeline currently starts from Qwen/Qwen2.5-0.5B-Instruct independently; continuing a previous run is an explicit configuration choice.

### Tool-selection retention in clarification

`train_clarification.RUN_CONFIG.retention_sets` includes `tool_selection_retention` by default, using the tool-selection task's scorer. The package contains all 280 original tool-selection test cases from run `20261101T190715603501Z` in `tasks/data/tool_selection_retention.json`, so evaluation works locally and on Runpod without machine-specific paths. These are the exact original test cases, not newly sampled examples. They are evaluated before training, after supervised warm-up (when enabled), and after GRPO, and are never used in training batches.

The starting model is still explicitly controlled by `RUN_CONFIG.training.model_name`. Set it to the trained tool model's `final_model` directory when continuing that model; selecting a retention set does not change the model being trained.

### Arithmetic followed by clarification

After arithmetic completes, set the clarification configuration's `model_name` to the printed run directory's `final_model`. Append the arithmetic test set to `retention_sets` in that same file to retain both capabilities:

```python
from rl_framework import RetentionSet
from tasks.arithmetic import TASK as ARITHMETIC

# Inside RUN_CONFIG.training:
# model_name="runs/arithmetic/<actual-run-id>/final_model",

# Inside RUN_CONFIG:
# retention_sets=(
#     ...  # Keep the existing tool_selection_retention entry.
#     RetentionSet(
#         name="arithmetic_retention",
#         path="runs/arithmetic/<actual-run-id>/datasets.json",
#         task=ARITHMETIC,
#     ),
# ),
```

Then run `train_clarification.main()` or its `RUN_CONFIG.run()`. This continues the model weights with a fresh optimizer and measures arithmetic before and after clarification using its own scorer. For a different tool-selection test set, update the existing retention entry's `path` to that run's `datasets.json`. Existing checkpoints remain usable.

Retention data never enter training. Measuring retention does not prevent forgetting; replay, performance gates, and automatic checkpoint selection are not implemented.

Preview configured datasets without ML dependencies or a GPU:

```python
from train_clarification import RUN_CONFIG

splits = RUN_CONFIG.preview_data()
```

For optional W&B tracking, install `python -m pip install -e '.[tracking]'`, authenticate with W&B, and set `wandb=True` in the training configuration. Reports are always saved locally. Run CPU checks with `python -m unittest discover -s tests -v`.

## Tasks and defaults

| Pipeline | Train / validation / test | Supervised warm-up | GRPO steps |
|---|---|---:|---:|
| Arithmetic | 2000 / 140 / 280 | 0 | 60 |
| Tool selection | 2000 / 140 / 280 | 0 | 60 |
| Clarification | 960 / 120 / 240 | 40 | 60 |

Shared defaults: Qwen/Qwen2.5-0.5B-Instruct, learning rate 1e-5, 32 completions per batch, four generations per prompt, BF16, DAPO loss, and no reward standard-deviation scaling. Evaluations use greedy decoding and a 128-token output limit. The runner supports one GPU/process. These are short pilot runs, not a complete pass through the training dataset.

**Arithmetic:** addition, subtraction, and multiplication with disjoint operand pairs across splits. Reward is 1 when the last numeric token equals the answer, otherwise 0. This restored arithmetic implementation checks numeric equality without the earlier integer truncation behavior: `936.9` is incorrect for `936`. It checks the final number, not the reasoning. Templates are shared across splits, so this measures generalization to new operands within these templates.

**Tool selection:** select `get_weather`, `track_order`, `search_products`, `find_flights`, or `translate_text`, ask for clarification, or choose no tool. Outputs use `{"action":"tool","tool":"track_order","arguments":{"order_id":"AB-1391"}}`. Reward is 1 for exact structured correctness, 0.25 for correct action/tool with incorrect arguments, and 0 otherwise. Seven fixed demonstrations appear in both baseline and final evaluation. Tools are not executed.

**Clarification:** includes incomplete requests, complete requests, and no-tool requests. The training set contains 400 incomplete, 400 complete, and 160 no-tool examples. Split sizes must be multiples of 12. Validation/test phrasing and entity pools differ from training. This task reuses tool-selection scoring and includes clarification recall, precision, unnecessary-clarification rate, and per-category exact match. A clarification decision must name the correct tool for exact match. The model selects an action; it does not compose a clarification question. Weather units are required by this benchmark's tool contract.

Warm-up is assistant-only supervised cross-entropy on training examples, followed by GRPO. Set `warmup_steps=0` to disable it. All datasets are synthetic and are not evidence of general real-world reliability.

## Python API

```python
from rl_framework import GRPOExperiment, RetentionSet, TrainingConfig
from tasks.arithmetic import TASK as ARITHMETIC
from tasks.clarification import TASK as CLARIFICATION

experiment = GRPOExperiment(
    task=CLARIFICATION,
    config=TrainingConfig(
        model_name="runs/arithmetic/<run-id>/final_model",
        output_dir="runs/clarification",
        train_size=960, val_size=120, test_size=240,
        warmup_steps=40,
    ),
    retention_sets=[RetentionSet(
        "arithmetic_retention",
        "runs/arithmetic/<run-id>/datasets.json",
        ARITHMETIC,
    )],
)
comparison = experiment.run()
```

To add a task, define a `Task` with `build_splits`, `score_response`, `summarize`, and `metric_names`, then call `GRPOExperiment` from a small entry-point file. Dataset rows contain a chat-message `prompt`, JSON-encoded string `expected`, and `category`. The scorer accepts generated text and the encoded target, returning `reward` and metrics. The summarizer receives evaluation records and returns aggregate metrics; see the arithmetic task for the smallest example. Import that task directly wherever it is selected for training or retention evaluation.

## Artifacts

Reports are generated automatically by the shared framework for every pipeline; no separate reporting command is needed. Each run writes a unique timestamped directory (for example, `runs/clarification/<run-id>/`) with:

- `config.json`, `task.json`, `environment.json`, and `datasets.json` for reproducibility.
- `before.md` / `before.json` immediately after baseline evaluation, then `after.md` / `after.json` after training.
- `comparison.md` / `comparison.json` with before/after counts, percentages, and percentage-point changes for the training task and every retention set. Per-example predictions are also saved.
- `final_model/` with the trained model and tokenizer, plus `training.json` with runtime.
- When warm-up is enabled: `warmup_model/`, `after_warmup.md` / `after_warmup.json`, `warmup_comparison.*`, and `grpo_comparison.*` to distinguish supervised gains from RL gains.
- When retention is configured: a separate retention split in the same reports, scored by its own task.

Models and run outputs are excluded from Git. Existing run directories are preserved. Historical runs made before this refactor did not save a warm-up checkpoint.

## Latest H100 run

The [generated clarification and retention reports](reports/clarification-20261101T200530353368Z/README.md) include the baseline, supervised warm-up, final GRPO results, and comparisons from the latest full run. Clarification test exact match rose from 32.50% to 60.42%. Tool-selection retention rose from 57.50% to 74.64% overall, but fell from 87.50% after warm-up. The reports also show increased unnecessary clarification after GRPO.

## Historical pilot results

These measurements precede the framework refactor. The original 60-step tool-selection run improved test exact match from 161/280 (57.50%) to 240/280 (85.71%), while clarification remained 0/40. Training alone took 54.2 seconds on the H100.

The subsequent clarification pilot used 40 supervised steps and 60 GRPO steps:

| Metric | Incoming model | After warm-up | After GRPO |
|---|---:|---:|---:|
| New test exact match | 51.25% | 65.83% | 65.00% |
| New test clarification recall | 0.00% | 100.00% | 85.00% |
| New test unnecessary clarification | 0.00% | 42.14% | 27.86% |
| Original tool test exact match | 85.71% | 98.21% | 88.57% |

Final clarification exact match was 56/100; recall was higher because 29 other clarification decisions named the wrong tool. Warm-up supplied the main gain; GRPO reduced excessive clarification but lost some correct decisions. Warm-up took 3.5 seconds and GRPO 59.7 seconds, excluding evaluation and saving. These results motivate retaining separate evaluations for both capabilities.
