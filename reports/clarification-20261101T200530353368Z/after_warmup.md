# After supervised warm-up

## validation

| Metric | Result |
|---|---:|
| count | 120.0000 |
| valid_schema | 100/120 (83.33%) |
| action_correct | 80/120 (66.67%) |
| tool_choice_correct | 80/120 (66.67%) |
| arguments_correct | 80/120 (66.67%) |
| exact_match | 80/120 (66.67%) |
| mean_reward | 0.6667 |
| seconds | 5.0654 |

### per category

| Metric | Result |
|---|---:|
| clarify:find_flights | 5/10 (50.00%) |
| clarify:get_weather | 5/10 (50.00%) |
| clarify:search_products | 10/10 (100.00%) |
| clarify:track_order | 0/10 (0.00%) |
| clarify:translate_text | 0/10 (0.00%) |
| no_tool | 20/20 (100.00%) |
| tool:find_flights | 10/10 (100.00%) |
| tool:get_weather | 10/10 (100.00%) |
| tool:search_products | 10/10 (100.00%) |
| tool:track_order | 0/10 (0.00%) |
| tool:translate_text | 10/10 (100.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 20/50 (40.00%) |
| precision | 20/20 (100.00%) |
| unnecessary_clarification_rate | 0/70 (0.00%) |
| correct_nonclarification_rate | 60/70 (85.71%) |
| invalid_outputs | 20.0000 |

## test

| Metric | Result |
|---|---:|
| count | 240.0000 |
| valid_schema | 218/240 (90.83%) |
| action_correct | 134/240 (55.83%) |
| tool_choice_correct | 134/240 (55.83%) |
| arguments_correct | 134/240 (55.83%) |
| exact_match | 134/240 (55.83%) |
| mean_reward | 0.5583 |
| seconds | 8.3669 |

### per category

| Metric | Result |
|---|---:|
| clarify:find_flights | 20/20 (100.00%) |
| clarify:get_weather | 10/20 (50.00%) |
| clarify:search_products | 0/20 (0.00%) |
| clarify:track_order | 0/20 (0.00%) |
| clarify:translate_text | 10/20 (50.00%) |
| no_tool | 40/40 (100.00%) |
| tool:find_flights | 20/20 (100.00%) |
| tool:get_weather | 16/20 (80.00%) |
| tool:search_products | 6/20 (30.00%) |
| tool:track_order | 12/20 (60.00%) |
| tool:translate_text | 0/20 (0.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 40/100 (40.00%) |
| precision | 40/44 (90.91%) |
| unnecessary_clarification_rate | 4/140 (2.86%) |
| correct_nonclarification_rate | 114/140 (81.43%) |
| invalid_outputs | 22.0000 |

## tool_selection_retention

| Metric | Result |
|---|---:|
| count | 280.0000 |
| valid_schema | 270/280 (96.43%) |
| action_correct | 245/280 (87.50%) |
| tool_choice_correct | 245/280 (87.50%) |
| arguments_correct | 245/280 (87.50%) |
| exact_match | 245/280 (87.50%) |
| mean_reward | 0.8750 |
| seconds | 10.5794 |

### per category

| Metric | Result |
|---|---:|
| clarify | 5/40 (12.50%) |
| find_flights | 40/40 (100.00%) |
| get_weather | 40/40 (100.00%) |
| no_tool | 40/40 (100.00%) |
| search_products | 40/40 (100.00%) |
| track_order | 40/40 (100.00%) |
| translate_text | 40/40 (100.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 5/40 (12.50%) |
| precision | 5/5 (100.00%) |
| unnecessary_clarification_rate | 0/240 (0.00%) |
| correct_nonclarification_rate | 240/240 (100.00%) |
| invalid_outputs | 10.0000 |
