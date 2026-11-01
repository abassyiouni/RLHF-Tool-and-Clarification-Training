# Before training

## validation

| Metric | Result |
|---|---:|
| count | 120.0000 |
| valid_schema | 85/120 (70.83%) |
| action_correct | 41/120 (34.17%) |
| tool_choice_correct | 31/120 (25.83%) |
| arguments_correct | 29/120 (24.17%) |
| exact_match | 29/120 (24.17%) |
| mean_reward | 0.2458 |
| seconds | 4.3391 |

### per category

| Metric | Result |
|---|---:|
| clarify:find_flights | 0/10 (0.00%) |
| clarify:get_weather | 0/10 (0.00%) |
| clarify:search_products | 0/10 (0.00%) |
| clarify:track_order | 0/10 (0.00%) |
| clarify:translate_text | 0/10 (0.00%) |
| no_tool | 0/20 (0.00%) |
| tool:find_flights | 10/10 (100.00%) |
| tool:get_weather | 10/10 (100.00%) |
| tool:search_products | 1/10 (10.00%) |
| tool:track_order | 0/10 (0.00%) |
| tool:translate_text | 8/10 (80.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 0/50 (0.00%) |
| precision | N/A (0 cases) |
| unnecessary_clarification_rate | 0/70 (0.00%) |
| correct_nonclarification_rate | 51/70 (72.86%) |
| invalid_outputs | 35.0000 |

## test

| Metric | Result |
|---|---:|
| count | 240.0000 |
| valid_schema | 205/240 (85.42%) |
| action_correct | 99/240 (41.25%) |
| tool_choice_correct | 88/240 (36.67%) |
| arguments_correct | 78/240 (32.50%) |
| exact_match | 78/240 (32.50%) |
| mean_reward | 0.3354 |
| seconds | 7.6944 |

### per category

| Metric | Result |
|---|---:|
| clarify:find_flights | 0/20 (0.00%) |
| clarify:get_weather | 0/20 (0.00%) |
| clarify:search_products | 0/20 (0.00%) |
| clarify:track_order | 0/20 (0.00%) |
| clarify:translate_text | 0/20 (0.00%) |
| no_tool | 0/40 (0.00%) |
| tool:find_flights | 20/20 (100.00%) |
| tool:get_weather | 19/20 (95.00%) |
| tool:search_products | 20/20 (100.00%) |
| tool:track_order | 9/20 (45.00%) |
| tool:translate_text | 10/20 (50.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 0/100 (0.00%) |
| precision | N/A (0 cases) |
| unnecessary_clarification_rate | 0/140 (0.00%) |
| correct_nonclarification_rate | 121/140 (86.43%) |
| invalid_outputs | 35.0000 |

## tool_selection_retention

| Metric | Result |
|---|---:|
| count | 280.0000 |
| valid_schema | 211/280 (75.36%) |
| action_correct | 162/280 (57.86%) |
| tool_choice_correct | 162/280 (57.86%) |
| arguments_correct | 161/280 (57.50%) |
| exact_match | 161/280 (57.50%) |
| mean_reward | 0.5759 |
| seconds | 9.5966 |

### per category

| Metric | Result |
|---|---:|
| clarify | 0/40 (0.00%) |
| find_flights | 39/40 (97.50%) |
| get_weather | 34/40 (85.00%) |
| no_tool | 0/40 (0.00%) |
| search_products | 21/40 (52.50%) |
| track_order | 27/40 (67.50%) |
| translate_text | 40/40 (100.00%) |

### clarification

| Metric | Result |
|---|---:|
| recall | 0/40 (0.00%) |
| precision | N/A (0 cases) |
| unnecessary_clarification_rate | 0/240 (0.00%) |
| correct_nonclarification_rate | 188/240 (78.33%) |
| invalid_outputs | 69.0000 |
