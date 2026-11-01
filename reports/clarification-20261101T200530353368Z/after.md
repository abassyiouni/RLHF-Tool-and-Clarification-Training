# After training

## validation

| Metric | Result |
|---|---:|
| count | 120.0000 |
| valid_schema | 120/120 (100.00%) |
| action_correct | 90/120 (75.00%) |
| tool_choice_correct | 90/120 (75.00%) |
| arguments_correct | 90/120 (75.00%) |
| exact_match | 90/120 (75.00%) |
| mean_reward | 0.7500 |
| seconds | 4.5752 |

### per category

| Metric | Result |
|---|---:|
| clarify:find_flights | 10/10 (100.00%) |
| clarify:get_weather | 10/10 (100.00%) |
| clarify:search_products | 10/10 (100.00%) |
| clarify:track_order | 0/10 (0.00%) |
| clarify:translate_text | 10/10 (100.00%) |
| no_tool | 20/20 (100.00%) |
| tool:find_flights | 0/10 (0.00%) |
| tool:get_weather | 10/10 (100.00%) |
| tool:search_products | 10/10 (100.00%) |
| tool:track_order | 0/10 (0.00%) |
| tool:translate_text | 10/10 (100.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 40/50 (80.00%) |
| precision | 40/60 (66.67%) |
| unnecessary_clarification_rate | 20/70 (28.57%) |
| correct_nonclarification_rate | 50/70 (71.43%) |
| invalid_outputs | 0.0000 |

## test

| Metric | Result |
|---|---:|
| count | 240.0000 |
| valid_schema | 198/240 (82.50%) |
| action_correct | 146/240 (60.83%) |
| tool_choice_correct | 145/240 (60.42%) |
| arguments_correct | 145/240 (60.42%) |
| exact_match | 145/240 (60.42%) |
| mean_reward | 0.6042 |
| seconds | 8.3462 |

### per category

| Metric | Result |
|---|---:|
| clarify:find_flights | 20/20 (100.00%) |
| clarify:get_weather | 20/20 (100.00%) |
| clarify:search_products | 0/20 (0.00%) |
| clarify:track_order | 0/20 (0.00%) |
| clarify:translate_text | 20/20 (100.00%) |
| no_tool | 40/40 (100.00%) |
| tool:find_flights | 0/20 (0.00%) |
| tool:get_weather | 20/20 (100.00%) |
| tool:search_products | 16/20 (80.00%) |
| tool:track_order | 0/20 (0.00%) |
| tool:translate_text | 9/20 (45.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 61/100 (61.00%) |
| precision | 61/113 (53.98%) |
| unnecessary_clarification_rate | 52/140 (37.14%) |
| correct_nonclarification_rate | 85/140 (60.71%) |
| invalid_outputs | 42.0000 |

## tool_selection_retention

| Metric | Result |
|---|---:|
| count | 280.0000 |
| valid_schema | 264/280 (94.29%) |
| action_correct | 209/280 (74.64%) |
| tool_choice_correct | 209/280 (74.64%) |
| arguments_correct | 209/280 (74.64%) |
| exact_match | 209/280 (74.64%) |
| mean_reward | 0.7464 |
| seconds | 10.9352 |

### per category

| Metric | Result |
|---|---:|
| clarify | 40/40 (100.00%) |
| find_flights | 15/40 (37.50%) |
| get_weather | 38/40 (95.00%) |
| no_tool | 39/40 (97.50%) |
| search_products | 16/40 (40.00%) |
| track_order | 21/40 (52.50%) |
| translate_text | 40/40 (100.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 40/40 (100.00%) |
| precision | 40/95 (42.11%) |
| unnecessary_clarification_rate | 55/240 (22.92%) |
| correct_nonclarification_rate | 169/240 (70.42%) |
| invalid_outputs | 16.0000 |
