# Before training vs. supervised warm-up

## validation

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 85/120 (70.83%) | 100/120 (83.33%) | +12.50 |
| action_correct | 41/120 (34.17%) | 80/120 (66.67%) | +32.50 |
| tool_choice_correct | 31/120 (25.83%) | 80/120 (66.67%) | +40.83 |
| arguments_correct | 29/120 (24.17%) | 80/120 (66.67%) | +42.50 |
| exact_match | 29/120 (24.17%) | 80/120 (66.67%) | +42.50 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify:find_flights | 0/10 (0.00%) | 5/10 (50.00%) | +50.00 |
| clarify:get_weather | 0/10 (0.00%) | 5/10 (50.00%) | +50.00 |
| clarify:search_products | 0/10 (0.00%) | 10/10 (100.00%) | +100.00 |
| clarify:track_order | 0/10 (0.00%) | 0/10 (0.00%) | +0.00 |
| clarify:translate_text | 0/10 (0.00%) | 0/10 (0.00%) | +0.00 |
| no_tool | 0/20 (0.00%) | 20/20 (100.00%) | +100.00 |
| tool:find_flights | 10/10 (100.00%) | 10/10 (100.00%) | +0.00 |
| tool:get_weather | 10/10 (100.00%) | 10/10 (100.00%) | +0.00 |
| tool:search_products | 1/10 (10.00%) | 10/10 (100.00%) | +90.00 |
| tool:track_order | 0/10 (0.00%) | 0/10 (0.00%) | +0.00 |
| tool:translate_text | 8/10 (80.00%) | 10/10 (100.00%) | +20.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 0/50 (0.00%) | 20/50 (40.00%) | +40.00 |
| precision | N/A (0 cases) | 20/20 (100.00%) | N/A |
| unnecessary_clarification_rate | 0/70 (0.00%) | 0/70 (0.00%) | +0.00 |
| correct_nonclarification_rate | 51/70 (72.86%) | 60/70 (85.71%) | +12.86 |

## test

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 205/240 (85.42%) | 218/240 (90.83%) | +5.42 |
| action_correct | 99/240 (41.25%) | 134/240 (55.83%) | +14.58 |
| tool_choice_correct | 88/240 (36.67%) | 134/240 (55.83%) | +19.17 |
| arguments_correct | 78/240 (32.50%) | 134/240 (55.83%) | +23.33 |
| exact_match | 78/240 (32.50%) | 134/240 (55.83%) | +23.33 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify:find_flights | 0/20 (0.00%) | 20/20 (100.00%) | +100.00 |
| clarify:get_weather | 0/20 (0.00%) | 10/20 (50.00%) | +50.00 |
| clarify:search_products | 0/20 (0.00%) | 0/20 (0.00%) | +0.00 |
| clarify:track_order | 0/20 (0.00%) | 0/20 (0.00%) | +0.00 |
| clarify:translate_text | 0/20 (0.00%) | 10/20 (50.00%) | +50.00 |
| no_tool | 0/40 (0.00%) | 40/40 (100.00%) | +100.00 |
| tool:find_flights | 20/20 (100.00%) | 20/20 (100.00%) | +0.00 |
| tool:get_weather | 19/20 (95.00%) | 16/20 (80.00%) | -15.00 |
| tool:search_products | 20/20 (100.00%) | 6/20 (30.00%) | -70.00 |
| tool:track_order | 9/20 (45.00%) | 12/20 (60.00%) | +15.00 |
| tool:translate_text | 10/20 (50.00%) | 0/20 (0.00%) | -50.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 0/100 (0.00%) | 40/100 (40.00%) | +40.00 |
| precision | N/A (0 cases) | 40/44 (90.91%) | N/A |
| unnecessary_clarification_rate | 0/140 (0.00%) | 4/140 (2.86%) | +2.86 |
| correct_nonclarification_rate | 121/140 (86.43%) | 114/140 (81.43%) | -5.00 |

## tool_selection_retention

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| valid_schema | 211/280 (75.36%) | 270/280 (96.43%) | +21.07 |
| action_correct | 162/280 (57.86%) | 245/280 (87.50%) | +29.64 |
| tool_choice_correct | 162/280 (57.86%) | 245/280 (87.50%) | +29.64 |
| arguments_correct | 161/280 (57.50%) | 245/280 (87.50%) | +30.00 |
| exact_match | 161/280 (57.50%) | 245/280 (87.50%) | +30.00 |

### per category

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| clarify | 0/40 (0.00%) | 5/40 (12.50%) | +12.50 |
| find_flights | 39/40 (97.50%) | 40/40 (100.00%) | +2.50 |
| get_weather | 34/40 (85.00%) | 40/40 (100.00%) | +15.00 |
| no_tool | 0/40 (0.00%) | 40/40 (100.00%) | +100.00 |
| search_products | 21/40 (52.50%) | 40/40 (100.00%) | +47.50 |
| track_order | 27/40 (67.50%) | 40/40 (100.00%) | +32.50 |
| translate_text | 40/40 (100.00%) | 40/40 (100.00%) | +0.00 |

### clarification

| Metric | Before | After | Change (pp) |
|---|---:|---:|---:|
| recall | 0/40 (0.00%) | 5/40 (12.50%) | +12.50 |
| precision | N/A (0 cases) | 5/5 (100.00%) | N/A |
| unnecessary_clarification_rate | 0/240 (0.00%) | 0/240 (0.00%) | +0.00 |
| correct_nonclarification_rate | 188/240 (78.33%) | 240/240 (100.00%) | +21.67 |
