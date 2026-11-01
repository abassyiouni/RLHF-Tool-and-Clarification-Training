# Training: before and after

## validation

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 85/120 (70.83%) | 120/120 (100.00%) | +29.17 |
| action_correct | 41/120 (34.17%) | 90/120 (75.00%) | +40.83 |
| tool_choice_correct | 31/120 (25.83%) | 90/120 (75.00%) | +49.17 |
| arguments_correct | 29/120 (24.17%) | 90/120 (75.00%) | +50.83 |
| exact_match | 29/120 (24.17%) | 90/120 (75.00%) | +50.83 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify:find_flights | 0/10 (0.00%) | 10/10 (100.00%) | +100.00 |
| clarify:get_weather | 0/10 (0.00%) | 10/10 (100.00%) | +100.00 |
| clarify:search_products | 0/10 (0.00%) | 10/10 (100.00%) | +100.00 |
| clarify:track_order | 0/10 (0.00%) | 0/10 (0.00%) | +0.00 |
| clarify:translate_text | 0/10 (0.00%) | 10/10 (100.00%) | +100.00 |
| no_tool | 0/20 (0.00%) | 20/20 (100.00%) | +100.00 |
| tool:find_flights | 10/10 (100.00%) | 0/10 (0.00%) | -100.00 |
| tool:get_weather | 10/10 (100.00%) | 10/10 (100.00%) | +0.00 |
| tool:search_products | 1/10 (10.00%) | 10/10 (100.00%) | +90.00 |
| tool:track_order | 0/10 (0.00%) | 0/10 (0.00%) | +0.00 |
| tool:translate_text | 8/10 (80.00%) | 10/10 (100.00%) | +20.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 0/50 (0.00%) | 40/50 (80.00%) | +80.00 |
| precision | N/A (0 cases) | 40/60 (66.67%) | N/A |
| unnecessary_clarification_rate | 0/70 (0.00%) | 20/70 (28.57%) | +28.57 |
| correct_nonclarification_rate | 51/70 (72.86%) | 50/70 (71.43%) | -1.43 |

## test

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 205/240 (85.42%) | 198/240 (82.50%) | -2.92 |
| action_correct | 99/240 (41.25%) | 146/240 (60.83%) | +19.58 |
| tool_choice_correct | 88/240 (36.67%) | 145/240 (60.42%) | +23.75 |
| arguments_correct | 78/240 (32.50%) | 145/240 (60.42%) | +27.92 |
| exact_match | 78/240 (32.50%) | 145/240 (60.42%) | +27.92 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify:find_flights | 0/20 (0.00%) | 20/20 (100.00%) | +100.00 |
| clarify:get_weather | 0/20 (0.00%) | 20/20 (100.00%) | +100.00 |
| clarify:search_products | 0/20 (0.00%) | 0/20 (0.00%) | +0.00 |
| clarify:track_order | 0/20 (0.00%) | 0/20 (0.00%) | +0.00 |
| clarify:translate_text | 0/20 (0.00%) | 20/20 (100.00%) | +100.00 |
| no_tool | 0/40 (0.00%) | 40/40 (100.00%) | +100.00 |
| tool:find_flights | 20/20 (100.00%) | 0/20 (0.00%) | -100.00 |
| tool:get_weather | 19/20 (95.00%) | 20/20 (100.00%) | +5.00 |
| tool:search_products | 20/20 (100.00%) | 16/20 (80.00%) | -20.00 |
| tool:track_order | 9/20 (45.00%) | 0/20 (0.00%) | -45.00 |
| tool:translate_text | 10/20 (50.00%) | 9/20 (45.00%) | -5.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 0/100 (0.00%) | 61/100 (61.00%) | +61.00 |
| precision | N/A (0 cases) | 61/113 (53.98%) | N/A |
| unnecessary_clarification_rate | 0/140 (0.00%) | 52/140 (37.14%) | +37.14 |
| correct_nonclarification_rate | 121/140 (86.43%) | 85/140 (60.71%) | -25.71 |

## tool_selection_retention

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 211/280 (75.36%) | 264/280 (94.29%) | +18.93 |
| action_correct | 162/280 (57.86%) | 209/280 (74.64%) | +16.79 |
| tool_choice_correct | 162/280 (57.86%) | 209/280 (74.64%) | +16.79 |
| arguments_correct | 161/280 (57.50%) | 209/280 (74.64%) | +17.14 |
| exact_match | 161/280 (57.50%) | 209/280 (74.64%) | +17.14 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify | 0/40 (0.00%) | 40/40 (100.00%) | +100.00 |
| find_flights | 39/40 (97.50%) | 15/40 (37.50%) | -60.00 |
| get_weather | 34/40 (85.00%) | 38/40 (95.00%) | +10.00 |
| no_tool | 0/40 (0.00%) | 39/40 (97.50%) | +97.50 |
| search_products | 21/40 (52.50%) | 16/40 (40.00%) | -12.50 |
| track_order | 27/40 (67.50%) | 21/40 (52.50%) | -15.00 |
| translate_text | 40/40 (100.00%) | 40/40 (100.00%) | +0.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 0/40 (0.00%) | 40/40 (100.00%) | +100.00 |
| precision | N/A (0 cases) | 40/95 (42.11%) | N/A |
| unnecessary_clarification_rate | 0/240 (0.00%) | 55/240 (22.92%) | +22.92 |
| correct_nonclarification_rate | 188/240 (78.33%) | 169/240 (70.42%) | -7.92 |
