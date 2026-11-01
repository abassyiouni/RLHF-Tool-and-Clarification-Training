# After supervised warm-up vs. GRPO

## validation

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 100/120 (83.33%) | 120/120 (100.00%) | +16.67 |
| action_correct | 80/120 (66.67%) | 90/120 (75.00%) | +8.33 |
| tool_choice_correct | 80/120 (66.67%) | 90/120 (75.00%) | +8.33 |
| arguments_correct | 80/120 (66.67%) | 90/120 (75.00%) | +8.33 |
| exact_match | 80/120 (66.67%) | 90/120 (75.00%) | +8.33 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify:find_flights | 5/10 (50.00%) | 10/10 (100.00%) | +50.00 |
| clarify:get_weather | 5/10 (50.00%) | 10/10 (100.00%) | +50.00 |
| clarify:search_products | 10/10 (100.00%) | 10/10 (100.00%) | +0.00 |
| clarify:track_order | 0/10 (0.00%) | 0/10 (0.00%) | +0.00 |
| clarify:translate_text | 0/10 (0.00%) | 10/10 (100.00%) | +100.00 |
| no_tool | 20/20 (100.00%) | 20/20 (100.00%) | +0.00 |
| tool:find_flights | 10/10 (100.00%) | 0/10 (0.00%) | -100.00 |
| tool:get_weather | 10/10 (100.00%) | 10/10 (100.00%) | +0.00 |
| tool:search_products | 10/10 (100.00%) | 10/10 (100.00%) | +0.00 |
| tool:track_order | 0/10 (0.00%) | 0/10 (0.00%) | +0.00 |
| tool:translate_text | 10/10 (100.00%) | 10/10 (100.00%) | +0.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 20/50 (40.00%) | 40/50 (80.00%) | +40.00 |
| precision | 20/20 (100.00%) | 40/60 (66.67%) | -33.33 |
| unnecessary_clarification_rate | 0/70 (0.00%) | 20/70 (28.57%) | +28.57 |
| correct_nonclarification_rate | 60/70 (85.71%) | 50/70 (71.43%) | -14.29 |

## test

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 218/240 (90.83%) | 198/240 (82.50%) | -8.33 |
| action_correct | 134/240 (55.83%) | 146/240 (60.83%) | +5.00 |
| tool_choice_correct | 134/240 (55.83%) | 145/240 (60.42%) | +4.58 |
| arguments_correct | 134/240 (55.83%) | 145/240 (60.42%) | +4.58 |
| exact_match | 134/240 (55.83%) | 145/240 (60.42%) | +4.58 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify:find_flights | 20/20 (100.00%) | 20/20 (100.00%) | +0.00 |
| clarify:get_weather | 10/20 (50.00%) | 20/20 (100.00%) | +50.00 |
| clarify:search_products | 0/20 (0.00%) | 0/20 (0.00%) | +0.00 |
| clarify:track_order | 0/20 (0.00%) | 0/20 (0.00%) | +0.00 |
| clarify:translate_text | 10/20 (50.00%) | 20/20 (100.00%) | +50.00 |
| no_tool | 40/40 (100.00%) | 40/40 (100.00%) | +0.00 |
| tool:find_flights | 20/20 (100.00%) | 0/20 (0.00%) | -100.00 |
| tool:get_weather | 16/20 (80.00%) | 20/20 (100.00%) | +20.00 |
| tool:search_products | 6/20 (30.00%) | 16/20 (80.00%) | +50.00 |
| tool:track_order | 12/20 (60.00%) | 0/20 (0.00%) | -60.00 |
| tool:translate_text | 0/20 (0.00%) | 9/20 (45.00%) | +45.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 40/100 (40.00%) | 61/100 (61.00%) | +21.00 |
| precision | 40/44 (90.91%) | 61/113 (53.98%) | -36.93 |
| unnecessary_clarification_rate | 4/140 (2.86%) | 52/140 (37.14%) | +34.29 |
| correct_nonclarification_rate | 114/140 (81.43%) | 85/140 (60.71%) | -20.71 |

## tool_selection_retention

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 270/280 (96.43%) | 264/280 (94.29%) | -2.14 |
| action_correct | 245/280 (87.50%) | 209/280 (74.64%) | -12.86 |
| tool_choice_correct | 245/280 (87.50%) | 209/280 (74.64%) | -12.86 |
| arguments_correct | 245/280 (87.50%) | 209/280 (74.64%) | -12.86 |
| exact_match | 245/280 (87.50%) | 209/280 (74.64%) | -12.86 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify | 5/40 (12.50%) | 40/40 (100.00%) | +87.50 |
| find_flights | 40/40 (100.00%) | 15/40 (37.50%) | -62.50 |
| get_weather | 40/40 (100.00%) | 38/40 (95.00%) | -5.00 |
| no_tool | 40/40 (100.00%) | 39/40 (97.50%) | -2.50 |
| search_products | 40/40 (100.00%) | 16/40 (40.00%) | -60.00 |
| track_order | 40/40 (100.00%) | 21/40 (52.50%) | -47.50 |
| translate_text | 40/40 (100.00%) | 40/40 (100.00%) | +0.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 5/40 (12.50%) | 40/40 (100.00%) | +87.50 |
| precision | 5/5 (100.00%) | 40/95 (42.11%) | -57.89 |
| unnecessary_clarification_rate | 0/240 (0.00%) | 55/240 (22.92%) | +22.92 |
| correct_nonclarification_rate | 240/240 (100.00%) | 169/240 (70.42%) | -29.58 |
