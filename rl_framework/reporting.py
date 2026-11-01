"""Task-independent JSON and Markdown comparisons of rates and counts."""

import json


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _is_rate(value):
    return isinstance(value, dict) and "percent" in value and "total" in value


def _compare(initial, final):
    delta = None if initial["percent"] is None or final["percent"] is None else final["percent"] - initial["percent"]
    return {"before": initial, "after": final, "delta_percentage_points": delta}


def comparison_report(before, after):
    """Compare top-level rates and grouped rates without knowing their meaning."""
    report = {}
    for split, initial in before.items():
        final = after[split]
        report[split] = {}
        for name, value in initial.items():
            if _is_rate(value):
                report[split][name] = _compare(value, final[name])
            elif isinstance(value, dict):
                grouped = {key: _compare(rate, final[name][key]) for key, rate in value.items() if _is_rate(rate)}
                if grouped:
                    report[split][name] = grouped
    return report


def _display(rate):
    if rate["percent"] is None:
        return "N/A (0 cases)"
    count = rate.get("correct", rate.get("count"))
    return f"{count}/{rate['total']} ({rate['percent']:.2f}%)"


def _table(rows):
    lines = ["| Metric | Before | After | Change (pp) |", "|---|---:|---:|---:|"]
    for name, row in rows.items():
        delta = row["delta_percentage_points"]
        change = "N/A" if delta is None else f"{delta:+.2f}"
        lines.append(f"| {name} | {_display(row['before'])} | {_display(row['after'])} | {change} |")
    return lines


def report_markdown(comparison, title="Training: before and after"):
    lines = [f"# {title}", ""]
    for split, results in comparison.items():
        lines += [f"## {split}", ""]
        lines += _table({name: row for name, row in results.items() if "before" in row})
        for name, rows in results.items():
            if "before" not in rows:
                lines += ["", f"### {name.replace('_', ' ')}", ""] + _table(rows)
        lines.append("")
    return "\n".join(lines)


def evaluation_markdown(metrics, title):
    """Readable snapshot, including each retention split and grouped metrics."""
    lines = [f"# {title}", ""]

    def table(values):
        rows = ["| Metric | Result |", "|---|---:|"]
        for name, value in values.items():
            if _is_rate(value):
                rows.append(f"| {name} | {_display(value)} |")
            elif isinstance(value, (int, float)):
                rows.append(f"| {name} | {value:.4f} |")
        return rows

    for split, values in metrics.items():
        lines += [f"## {split}", ""] + table(values)
        for name, group in values.items():
            if isinstance(group, dict) and not _is_rate(group):
                lines += ["", f"### {name.replace('_', ' ')}", ""] + table(group)
        lines.append("")
    return "\n".join(lines)


def save_evaluation_report(run_dir, phase, metrics):
    titles = {"before": "Before training", "after_warmup": "After supervised warm-up",
              "after": "After training"}
    write_json(run_dir / f"{phase}.json", metrics)
    (run_dir / f"{phase}.md").write_text(evaluation_markdown(metrics, titles[phase]), encoding="utf-8")


def save_comparison_report(run_dir, name, before, after, title):
    comparison = comparison_report(before, after)
    write_json(run_dir / f"{name}.json", comparison)
    (run_dir / f"{name}.md").write_text(report_markdown(comparison, title), encoding="utf-8")
    return comparison
