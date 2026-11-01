"""Synthetic tool-routing data and deterministic, content-based grading."""

import json
from pathlib import Path
import random

from rl_framework.task import Task

# Frozen test split from the first tool-selection run, shipped with the package.
RETENTION_DATASET = Path(__file__).with_name("data") / "tool_selection_retention.json"

TOOLS = {
    "get_weather": {"description": "Get current weather", "arguments": ["city", "unit"]},
    "track_order": {"description": "Look up order delivery status", "arguments": ["order_id"]},
    "search_products": {"description": "Search a product catalog", "arguments": ["query"]},
    "find_flights": {"description": "Find flights between cities", "arguments": ["origin", "destination"]},
    "translate_text": {"description": "Translate supplied text", "arguments": ["text", "target_language"]},
}
SYSTEM_PROMPT = """Select the correct tool for the user's request. Output only JSON.
Available tools and required string arguments:
- get_weather(city, unit): current weather. unit is celsius or fahrenheit.
- track_order(order_id): delivery status of an order.
- search_products(query): search the product catalog.
- find_flights(origin, destination): find flights between two cities.
- translate_text(text, target_language): translate text into a language.

Always use exactly these keys: action, tool, arguments.
action is "tool" for a complete request, "clarify" when an argument is missing,
or "no_tool" for general explanations or advice. Never guess a missing argument.
Copy argument values exactly from the request, including language names, NOT language codes.
For clarify use the intended tool name and empty arguments. For no_tool use null and empty arguments.
Do not execute the tool. No prose, markdown, or extra fields.

Examples:
User: Current weather in Zurich in celsius.
Output: {"action":"tool","tool":"get_weather","arguments":{"city":"Zurich","unit":"celsius"}}
User: Track order ZZ-9000.
Output: {"action":"tool","tool":"track_order","arguments":{"order_id":"ZZ-9000"}}
User: Search products for "wooden desk".
Output: {"action":"tool","tool":"search_products","arguments":{"query":"wooden desk"}}
User: Find flights from Zurich to Brussels.
Output: {"action":"tool","tool":"find_flights","arguments":{"origin":"Zurich","destination":"Brussels"}}
User: Translate "Good morning" into Polish.
Output: {"action":"tool","tool":"translate_text","arguments":{"text":"Good morning","target_language":"Polish"}}
User: Find flights departing from Zurich.
Output: {"action":"clarify","tool":"find_flights","arguments":{}}
User: Explain what a weather forecast means.
Output: {"action":"no_tool","tool":null,"arguments":{}}
"""

LABELS = tuple(TOOLS) + ("no_tool", "clarify")
METRICS = ("valid_schema", "action_correct", "tool_choice_correct", "arguments_correct", "exact_match")


def target(action, tool=None, **arguments):
    return {"action": action, "tool": tool, "arguments": arguments}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def parse_response(text):
    try:
        obj = json.loads(text, object_pairs_hook=_unique_object)
    except (ValueError, TypeError, RecursionError):
        return None
    if not isinstance(obj, dict) or set(obj) != {"action", "tool", "arguments"}:
        return None
    action, tool, args = obj["action"], obj["tool"], obj["arguments"]
    if not isinstance(action, str) or not isinstance(args, dict):
        return None
    if action == "no_tool":
        return obj if tool is None and args == {} else None
    if not isinstance(tool, str) or tool not in TOOLS:
        return None
    if action == "clarify":
        return obj if args == {} else None
    if action != "tool" or set(args) != set(TOOLS[tool]["arguments"]):
        return None
    if not all(isinstance(v, str) and v.strip() for v in args.values()):
        return None
    if tool == "get_weather" and args["unit"] not in ("celsius", "fahrenheit"):
        return None
    return obj


def score_response(text, expected):
    """No format-only reward; argument credit requires the correct action/tool."""
    if isinstance(expected, str):
        expected = json.loads(expected)
    obj = parse_response(text)
    scores = {metric: 0.0 for metric in METRICS}
    scores["reward"] = 0.0
    if obj is None:
        return scores
    scores["valid_schema"] = 1.0
    action_ok = obj["action"] == expected["action"]
    choice_ok = action_ok and obj["tool"] == expected["tool"]
    args_ok = choice_ok and obj["arguments"] == expected["arguments"]
    scores.update(action_correct=float(action_ok), tool_choice_correct=float(choice_ok),
                  arguments_correct=float(args_ok), exact_match=float(args_ok))
    scores["reward"] = 0.25 * choice_ok + 0.75 * args_ok
    return scores


def reward_tool_selection(completions, expected, **kwargs):
    if len(completions) != len(expected):
        raise ValueError("Completions and targets must have equal lengths")
    rewards = []
    for completion, answer in zip(completions, expected):
        if isinstance(completion, list):
            text = completion[0].get("content", "") if len(completion) == 1 else ""
        else:
            text = completion
        rewards.append(score_response(text, answer)["reward"])
    return rewards


def build_splits(train_size=2000, val_size=140, test_size=280, seed=42):
    """Stratified, reproducible split of unique prompts; templates are shared."""
    sizes = (train_size, val_size, test_size)
    if any(size < len(LABELS) for size in sizes):
        raise ValueError("Each split needs at least seven examples")
    cities = ["Paris", "London", "Tokyo", "Berlin", "Madrid", "Rome", "Lisbon", "Oslo",
              "Dublin", "Prague", "Vienna", "Warsaw", "Athens", "Helsinki", "Stockholm",
              "Cairo", "Nairobi", "Lagos", "Sydney", "Melbourne", "Toronto", "Vancouver",
              "Boston", "Chicago", "Seattle", "Miami", "Denver", "Austin", "Lima",
              "Bogota", "Santiago", "Seoul", "Bangkok", "Hanoi", "Delhi", "Mumbai",
              "Jakarta", "Manila", "Dubai", "Doha"]
    products = [f"{adjective} {noun}" for adjective in
                ("wireless", "portable", "red", "blue", "compact", "lightweight", "black", "white", "small", "large")
                for noun in ("headphones", "speakers", "keyboards", "lamps", "backpacks", "chargers", "watches", "cameras", "monitors", "microphones")]
    phrases = [f"Please bring the {color} {item}." for color in
               ("red", "blue", "green", "yellow", "black", "white", "purple", "orange")
               for item in ("bag", "book", "box", "cup", "coat", "chair", "folder", "bottle", "hat", "umbrella")]
    pools = {label: [] for label in LABELS}

    def add(label, question, answer):
        pools[label].append({"prompt": [{"role": "system", "content": SYSTEM_PROMPT},
                                          {"role": "user", "content": question}],
                             "expected": json.dumps(answer, sort_keys=True), "category": label})

    for city in cities:
        for unit in ("celsius", "fahrenheit"):
            for template in ("Get current weather in {c} in {u}.", "What is the weather in {c}, in {u}?",
                             "Check today's weather for {c}; use {u}.", "Show the current {u} weather for {c}.",
                             "Look up current conditions in {c} in {u}.", "Fetch weather for {c}, using {u}."):
                add("get_weather", template.format(c=city, u=unit), target("tool", "get_weather", city=city, unit=unit))
    for i in range(800):
        order = f"AB-{1000 + i}"
        for template in ("Track order {}.", "Where is order {}?", "Check delivery status of order {}."):
            add("track_order", template.format(order), target("tool", "track_order", order_id=order))
    for query in products:
        for template in ('Search products for "{}".', 'Find items matching "{}".', 'Look in the catalog for "{}".',
                         'Search the catalog using the query "{}".', 'Show products matching "{}".'):
            add("search_products", template.format(query), target("tool", "search_products", query=query))
    for origin in cities:
        for destination in cities:
            if origin != destination:
                add("find_flights", f"Find flights from {origin} to {destination}.", target("tool", "find_flights", origin=origin, destination=destination))
    for phrase in phrases:
        for language in ("French", "Spanish", "German", "Japanese", "Italian", "Arabic"):
            add("translate_text", f'Translate "{phrase}" into {language}.', target("tool", "translate_text", text=phrase, target_language=language))
    topics = ("weather forecasts", "airline tickets", "order tracking", "language translation", "online shopping",
              "flight connections", "delivery estimates", "product catalogs", "temperature units", "return policies")
    for topic in topics:
        for audience in ("students", "travelers", "teachers", "parents", "shoppers", "beginners", "tourists", "children", "new employees", "retirees"):
            for template in ("Explain {} to {}.", "Write a general introduction to {} for {}.", "Define {} in plain language for {}.",
                             "Give general advice about {} for {}.", "Describe the basics of {} for {}."):
                add("no_tool", template.format(topic, audience), target("no_tool"))
    for city in cities:
        for template in ("Find flights departing from {}.", "Find flights arriving in {}.", "Look up weather in {}."):
            tool = "get_weather" if "weather" in template else "find_flights"
            add("clarify", template.format(city), target("clarify", tool))
    for phrase in phrases:
        for template in ('Translate "{}".', 'Please translate this text: "{}".', 'Use the translation tool for "{}".', 'Give me a translation of "{}".'):
            add("clarify", template.format(phrase), target("clarify", "translate_text"))

    rng = random.Random(seed)
    splits = {name: [] for name in ("train", "validation", "test")}
    for index, label in enumerate(LABELS):
        pool = pools[label]
        rng.shuffle(pool)
        offset = 0
        for name, size in zip(splits, sizes):
            count = size // len(LABELS) + (index < size % len(LABELS))
            if offset + count > len(pool):
                raise ValueError(f"Not enough unique {label} examples for requested sizes")
            splits[name].extend(pool[offset:offset + count])
            offset += count
    for rows in splits.values():
        rng.shuffle(rows)
    return splits


def summarize(records):
    if not records:
        raise ValueError("Cannot evaluate an empty dataset")
    summary = {"count": len(records)}
    for metric in METRICS:
        count = sum(record["scores"][metric] for record in records)
        summary[metric] = {"correct": int(count), "total": len(records), "percent": 100 * count / len(records)}
    summary["mean_reward"] = sum(r["scores"]["reward"] for r in records) / len(records)
    summary["per_category"] = {}
    for label in sorted({r["category"] for r in records}):
        subset = [r for r in records if r["category"] == label]
        correct = sum(r["scores"]["exact_match"] for r in subset)
        summary["per_category"][label] = {"correct": int(correct), "total": len(subset), "percent": 100 * correct / len(subset)}
    if all("expected" in record and "completion" in record for record in records):
        tp = fp = fn = tn = invalid = needed = not_needed = 0
        for record in records:
            expected = record["expected"]
            if isinstance(expected, str):
                expected = json.loads(expected)
            needs_clarification = expected["action"] == "clarify"
            parsed = parse_response(record["completion"])
            asks = parsed is not None and parsed["action"] == "clarify"
            needed += needs_clarification
            not_needed += not needs_clarification
            invalid += parsed is None
            tp += needs_clarification and asks
            fn += needs_clarification and not asks
            fp += not needs_clarification and asks
            tn += not needs_clarification and parsed is not None and not asks

        def rate(numerator, denominator):
            return {"count": numerator, "total": denominator,
                    "percent": 100 * numerator / denominator if denominator else None}

        summary["clarification"] = {
            "recall": rate(tp, needed),
            "precision": rate(tp, tp + fp),
            "unnecessary_clarification_rate": rate(fp, not_needed),
            "correct_nonclarification_rate": rate(tn, not_needed),
            "invalid_outputs": invalid,
            "counts": {"true_positive": tp, "false_positive": fp, "false_negative": fn, "true_negative": tn},
        }
    return summary


TASK = Task("tool_selection", build_splits, score_response, summarize, METRICS)
