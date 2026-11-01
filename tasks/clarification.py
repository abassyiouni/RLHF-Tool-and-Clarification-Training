"""Paired incomplete/complete requests with split-specific phrasing and entities."""

import json
import random

from rl_framework.task import Task
from .tool_selection import METRICS, SYSTEM_PROMPT, score_response, summarize, target


def build_clarification_splits(train_size=960, val_size=120, test_size=240, seed=123):
    """Each group contains five incomplete, five complete, and two no-tool requests.

    Template families, names, city pools, and IDs are disjoint between splits.
    This remains a synthetic benchmark, not an independent real-world dataset.
    """
    sizes = (train_size, val_size, test_size)
    if any(n < 12 or n % 12 for n in sizes):
        raise ValueError("Clarification split sizes must be positive multiples of 12")
    city_sets = (
        ["Paris", "London", "Tokyo", "Berlin", "Madrid", "Rome", "Lisbon", "Oslo"],
        ["Cairo", "Nairobi", "Lagos", "Sydney", "Melbourne", "Toronto", "Vancouver", "Boston"],
        ["Seoul", "Bangkok", "Hanoi", "Delhi", "Mumbai", "Jakarta", "Manila", "Dubai"],
    )
    first_sets = (
        ["Maya", "Leo", "Nora", "Owen", "Iris", "Evan", "Zoe", "Finn", "Ruby", "Adam"],
        ["Sofia", "Arun", "Elena", "Tariq", "Lena", "Hugo", "Milo", "Sara", "Noel", "Amir"],
        ["Priya", "Mateo", "Aisha", "Luca", "Yuki", "Nadia", "Oscar", "Mina", "Ravi", "Ella"],
    )
    surnames = ["Chen", "Patel", "Silva", "Kim", "Lopez", "Brown", "Jones", "Martin", "Garcia", "Wilson"]
    # Templates are chosen by split, never randomly mixed across splits.
    templates = (
        {
            "weather_full": "Check current weather in {city} using {unit}.",
            "weather_city": "Check current weather using {unit}.",
            "weather_unit": "Check current weather in {city}.",
            "order_full": "Check the delivery status for order {order}.",
            "order_missing": "Check the delivery status for my order.",
            "search_full": 'Search the product catalog for "{query}".',
            "search_missing": "Search the product catalog for me.",
            "flights_full": "Look for flights from {city} to {destination}.",
            "flights_origin": "Look for flights to {destination}.",
            "flights_destination": "Look for flights from {city}.",
            "translate_full": 'Translate "{text}" into {language}.',
            "translate_text": "Translate some text into {language}.",
            "translate_language": 'Translate "{text}".',
            "no_order": "Explain how order tracking works.",
            "no_weather": "Explain the difference between celsius and fahrenheit.",
        },
        {
            "weather_full": "Give me the current conditions for {city}, with temperatures in {unit}.",
            "weather_city": "Give me current conditions with temperatures in {unit}.",
            "weather_unit": "Give me the current conditions for {city}.",
            "order_full": "Where has shipment {order} got to?",
            "order_missing": "Where has my shipment got to?",
            "search_full": 'Locate catalog listings matching "{query}".',
            "search_missing": "Locate some catalog listings for me.",
            "flights_full": "Show air travel options leaving {city} and arriving in {destination}.",
            "flights_origin": "Show air travel options arriving in {destination}.",
            "flights_destination": "Show air travel options leaving {city}.",
            "translate_full": 'Convert the phrase "{text}" to {language}.',
            "translate_text": "Convert a phrase to {language}.",
            "translate_language": 'Convert the phrase "{text}" to another language.',
            "no_order": "What does an order tracking number represent?",
            "no_weather": "How do the celsius and fahrenheit scales differ?",
        },
        {
            "weather_full": "What's it like outside in {city} right now? Report it in {unit}.",
            "weather_city": "What's it like outside right now? Report it in {unit}.",
            "weather_unit": "What's it like outside in {city} right now?",
            "order_full": "I'd like an update on parcel {order}.",
            "order_missing": "I'd like an update on my parcel.",
            "search_full": 'See what the store has for the search term "{query}".',
            "search_missing": "See what the store has for the thing I want.",
            "flights_full": "I want to fly out of {city} and land in {destination}; find options.",
            "flights_origin": "I want to land in {destination}; find flight options.",
            "flights_destination": "I want to fly out of {city}; find options.",
            "translate_full": 'How would you say "{text}" in {language}?',
            "translate_text": "Could you translate something into {language}?",
            "translate_language": 'How would you say "{text}" in a different language?',
            "no_order": "Teach me what delivery tracking is used for.",
            "no_weather": "Describe why there are different temperature scales.",
        },
    )
    splits = {}
    rng = random.Random(seed)
    for split_index, (split, size) in enumerate(zip(("train", "validation", "test"), sizes)):
        if size // 12 > 100:
            raise ValueError("At most 1,200 examples per clarification split are supported")
        rows = []
        cities, names, template = city_sets[split_index], first_sets[split_index], templates[split_index]
        for i in range(size // 12):
            name = f"{names[i % 10]} {surnames[i // 10]}"
            values = {
                "city": cities[i % len(cities)], "destination": cities[(i + 3) % len(cities)],
                "unit": ("celsius", "fahrenheit")[i % 2],
                "order": f"CL{split_index}-{7000 + i}",
                "query": f"{('small', 'blue', 'portable')[split_index]} {('lamps', 'bags', 'speakers', 'chairs')[i % 4]}",
                "text": f"Please collect package {split_index}-{i}.",
                "language": ("French", "Spanish", "German", "Japanese")[i % 4],
            }

            def add(key, answer):
                request = template[key].format(**values)
                # A realistic irrelevant identity varies missing-argument requests
                # without telling the model which decision is expected.
                question = f"My name is {name}. {request}"
                category = answer["action"] if answer["action"] == "no_tool" else f"{answer['action']}:{answer['tool']}"
                rows.append({"prompt": [{"role": "system", "content": SYSTEM_PROMPT},
                                         {"role": "user", "content": question}],
                             "expected": json.dumps(answer, sort_keys=True), "category": category,
                             "template_id": f"{split}:{key}", "pair_id": f"{split}:{i}"})

            add("weather_full", target("tool", "get_weather", city=values["city"], unit=values["unit"]))
            add("weather_city" if i % 2 else "weather_unit", target("clarify", "get_weather"))
            add("order_full", target("tool", "track_order", order_id=values["order"]))
            add("order_missing", target("clarify", "track_order"))
            add("search_full", target("tool", "search_products", query=values["query"]))
            add("search_missing", target("clarify", "search_products"))
            add("flights_full", target("tool", "find_flights", origin=values["city"], destination=values["destination"]))
            add("flights_origin" if i % 2 else "flights_destination", target("clarify", "find_flights"))
            add("translate_full", target("tool", "translate_text", text=values["text"], target_language=values["language"]))
            add("translate_text" if i % 2 else "translate_language", target("clarify", "translate_text"))
            add("no_order", target("no_tool"))
            add("no_weather", target("no_tool"))
        rng.shuffle(rows)
        splits[split] = rows
    return splits


TASK = Task("clarification", build_clarification_splits, score_response, summarize, METRICS)
