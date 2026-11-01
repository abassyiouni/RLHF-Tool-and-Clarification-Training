"""Shared model lifecycle, supervised warm-up, GRPO, and paired evaluation.

Task-specific datasets and reward logic are injected via Task.
Heavy ML libraries are imported only when training or generation is requested.
"""

from dataclasses import asdict
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import time

from .config import TrainingConfig
from .task import Task
from .reporting import write_json, report_markdown, save_evaluation_report, save_comparison_report


class GRPOExperiment:
    def __init__(self, task: Task, config=None, retention_sets=()):
        self.task = task
        self.config = config or TrainingConfig()
        self.retention_sets = tuple(retention_sets)
        self.evaluation_tasks = {}
        self.model = self.tokenizer = self.trainer = None
        self.run_dir = None

    def build_datasets(self):
        c = self.config
        splits = self.task.build_splits(c.train_size, c.val_size, c.test_size, c.seed)
        self.evaluation_tasks = {name: self.task for name in splits if name != "train"}
        for retention in self.retention_sets:
            if retention.name in splits:
                raise ValueError(f"Duplicate split name: {retention.name}")
            previous = json.loads(Path(retention.path).read_text(encoding="utf-8"))
            splits[retention.name] = previous["test"]
            self.evaluation_tasks[retention.name] = retention.task
        training_prompts = {json.dumps(row["prompt"], sort_keys=True) for row in splits["train"]}
        for name, rows in splits.items():
            if not rows:
                raise ValueError(f"Empty split: {name}")
            if name != "train" and any(json.dumps(row["prompt"], sort_keys=True) in training_prompts for row in rows):
                raise ValueError(f"Training data overlaps {name}")
        return splits

    def supervised_warmup(self, rows):
        """Teach rare decisions with assistant-only cross-entropy before GRPO.

        This is supervised learning, not a reward-based update. Only the training
        split is used; evaluation data never enter the optimizer.
        """
        import random
        import torch

        rng = random.Random(self.config.seed)
        examples = []
        for row in rows:
            prefix = self.tokenizer.apply_chat_template(row["prompt"], tokenize=True, add_generation_prompt=True)
            full = self.tokenizer.apply_chat_template(
                row["prompt"] + [{"role": "assistant", "content": self.task.supervised_target(row)}], tokenize=True)
            if full[:len(prefix)] != prefix or len(full) > 1024:
                raise ValueError("Warm-up chat template boundary or length is invalid")
            examples.append((full, [-100] * len(prefix) + full[len(prefix):]))
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.config.learning_rate, weight_decay=0.0)
        self.model.train()
        losses = []
        started = time.perf_counter()
        for step in range(self.config.warmup_steps):
            selected = rng.sample(examples, min(8, len(examples)))
            width = max(len(ids) for ids, _ in selected)
            ids = [tokens + [self.tokenizer.pad_token_id] * (width - len(tokens)) for tokens, _ in selected]
            masks = [[1] * len(tokens) + [0] * (width - len(tokens)) for tokens, _ in selected]
            labels = [labels + [-100] * (width - len(labels)) for _, labels in selected]
            inputs = {name: torch.tensor(value, device=self.model.device) for name, value in
                      (("input_ids", ids), ("attention_mask", masks), ("labels", labels))}
            optimizer.zero_grad(set_to_none=True)
            loss = self.model(**inputs, use_cache=False).loss
            if not torch.isfinite(loss):
                raise RuntimeError("Non-finite supervised warm-up loss")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            optimizer.step()
            losses.append(loss.item())
            if (step + 1) % 10 == 0:
                print(f"Supervised warm-up {step + 1}/{self.config.warmup_steps}: loss={loss.item():.4f}", flush=True)
        optimizer.zero_grad(set_to_none=True)
        del optimizer
        torch.cuda.empty_cache()
        write_json(self.run_dir / "warmup_training.json", {"steps": len(losses), "losses": losses, "seconds": time.perf_counter() - started})

    def load_model(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

        if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
            raise RuntimeError("Training requires a CUDA GPU with BF16 support (such as H100).")
        set_seed(self.config.seed)
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name, padding_side="left")
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name, dtype=torch.bfloat16, attn_implementation="sdpa"
        ).to("cuda")

    def generate(self, prompts):
        import torch

        texts = [self.tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True) for prompt in prompts]
        inputs = self.tokenizer(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(self.model.device)
        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs, do_sample=False, max_new_tokens=self.config.max_completion_length,
                pad_token_id=self.tokenizer.pad_token_id, eos_token_id=self.tokenizer.eos_token_id,
                use_cache=True,
            )
        return self.tokenizer.batch_decode(outputs[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    def evaluate(self, rows, phase, split):
        task = self.evaluation_tasks.get(split, self.task)
        was_training = self.model.training
        self.model.eval()
        records = []
        started = time.perf_counter()
        try:
            for offset in range(0, len(rows), self.config.eval_batch_size):
                batch = rows[offset:offset + self.config.eval_batch_size]
                completions = self.generate([row["prompt"] for row in batch])
                if len(completions) != len(batch):
                    raise RuntimeError("Generation count does not match evaluation batch")
                for row, completion in zip(batch, completions):
                    records.append({"prompt": row["prompt"][-1]["content"], "category": row["category"],
                                    "expected": json.loads(row["expected"]), "completion": completion,
                                    "scores": task.score_response(completion, row["expected"])})
        finally:
            self.model.train(was_training)
        with (self.run_dir / f"{phase}_{split}_predictions.jsonl").open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        metrics = task.summarize(records)
        metrics["seconds"] = time.perf_counter() - started
        write_json(self.run_dir / f"{phase}_{split}_metrics.json", metrics)
        primary = metrics[task.primary_metric]
        print(f"{phase} {split}: {task.primary_metric} {primary['correct']}/{primary['total']} ({primary['percent']:.2f}%)", flush=True)
        return metrics

    def configure_training(self):
        from trl import GRPOConfig

        c = self.config
        return GRPOConfig(
            output_dir=str(self.run_dir / "checkpoints"), max_steps=c.max_steps,
            learning_rate=c.learning_rate, per_device_train_batch_size=c.batch_size,
            num_generations=c.num_generations, gradient_accumulation_steps=1,
            steps_per_generation=1, num_iterations=1, temperature=1.0, top_p=1.0,
            max_prompt_length=1024, max_completion_length=c.max_completion_length,
            beta=1e-5, loss_type="dapo", scale_rewards="none",
            bf16=True, use_vllm=False, torch_compile=False,
            gradient_checkpointing=True, gradient_checkpointing_kwargs={"use_reentrant": False},
            lr_scheduler_type="constant_with_warmup", warmup_steps=min(10, c.max_steps),
            adam_beta1=0.9, adam_beta2=0.999, weight_decay=0.0, max_grad_norm=1.0,
            logging_steps=1, report_to="wandb" if c.wandb else "none",
            eval_strategy="no", save_strategy="no", seed=c.seed, data_seed=c.seed,
        )

    def run(self):
        import torch
        from datasets import Dataset
        from transformers import set_seed
        from trl import GRPOTrainer

        c = self.config
        if int(os.environ.get("WORLD_SIZE", "1")) != 1:
            raise RuntimeError("Use one GPU and one Python process for this runner")
        splits = self.build_datasets()
        evaluation_splits = [name for name in splits if name != "train"]
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.run_dir = Path(c.output_dir) / stamp
        self.run_dir.mkdir(parents=True, exist_ok=False)
        write_json(self.run_dir / "config.json", asdict(c))
        write_json(self.run_dir / "task.json", {
            "training_task": self.task.name,
            "evaluation_tasks": {name: task.name for name, task in self.evaluation_tasks.items()},
            "retention_sources": {item.name: str(item.path) for item in self.retention_sets},
        })
        write_json(self.run_dir / "datasets.json", splits)
        print(f"Artifacts: {self.run_dir.resolve()}", flush=True)
        self.load_model()
        max_prompt_tokens = max(len(self.tokenizer.apply_chat_template(row["prompt"], tokenize=True, add_generation_prompt=True)) for rows in splits.values() for row in rows)
        if max_prompt_tokens > 1024:
            raise ValueError("A prompt exceeds the training token limit; refusing to truncate it")
        write_json(self.run_dir / "environment.json", {
            "packages": {name: importlib.metadata.version(name) for name in ("torch", "trl", "transformers", "datasets", "accelerate")},
            "gpu": torch.cuda.get_device_name(0), "cuda": torch.version.cuda,
            "max_prompt_tokens": max_prompt_tokens,
            "model_commit": getattr(self.model.config, "_commit_hash", None),
        })
        before = {split: self.evaluate(splits[split], "before", split) for split in evaluation_splits}
        save_evaluation_report(self.run_dir, "before", before)
        wandb_run = None
        try:
            if c.wandb:
                import wandb
                wandb_run = wandb.init(project=f"grpo-{self.task.name}", config=asdict(c), name=stamp)
            set_seed(c.seed)
            if c.warmup_steps:
                self.supervised_warmup(splits["train"])
                self.model.save_pretrained(self.run_dir / "warmup_model")
                self.tokenizer.save_pretrained(self.run_dir / "warmup_model")
                warmup = {split: self.evaluate(splits[split], "after_warmup", split) for split in evaluation_splits}
                save_evaluation_report(self.run_dir, "after_warmup", warmup)
                save_comparison_report(self.run_dir, "warmup_comparison", before, warmup,
                                       "Before training vs. supervised warm-up")
                set_seed(c.seed)
            self.trainer = GRPOTrainer(model=self.model, processing_class=self.tokenizer,
                                       reward_funcs=[self.task.reward], args=self.configure_training(),
                                       train_dataset=Dataset.from_list(splits["train"]))
            start = time.perf_counter()
            result = self.trainer.train()
            training_seconds = time.perf_counter() - start
            self.model = self.trainer.accelerator.unwrap_model(self.trainer.model)
            self.model.gradient_checkpointing_disable()
            after = {split: self.evaluate(splits[split], "after", split) for split in evaluation_splits}
            save_evaluation_report(self.run_dir, "after", after)
            if c.warmup_steps:
                save_comparison_report(self.run_dir, "grpo_comparison", warmup, after,
                                       "After supervised warm-up vs. GRPO")
            comparison = save_comparison_report(self.run_dir, "comparison", before, after,
                                                "Training: before and after")
            markdown = report_markdown(comparison)
            write_json(self.run_dir / "training.json", {"seconds": training_seconds, "metrics": result.metrics})
            self.trainer.save_model(str(self.run_dir / "final_model"))
            self.tokenizer.save_pretrained(self.run_dir / "final_model")
            if wandb_run:
                for split in before:
                    for metric in self.evaluation_tasks[split].metric_names:
                        for phase, data in (("before", before), ("after", after)):
                            wandb_run.summary[f"{phase}/{split}/{metric}"] = data[split][metric]["percent"]
                wandb_run.save(str(self.run_dir / "comparison.json"), base_path=str(self.run_dir))
            print(markdown, flush=True)
            print(f"Training took {training_seconds / 60:.1f} minutes. Saved model and reports: {self.run_dir.resolve()}")
            return comparison
        except BaseException:
            if wandb_run:
                wandb_run.finish(exit_code=1)
                wandb_run = None
            raise
        finally:
            if wandb_run:
                wandb_run.finish()
