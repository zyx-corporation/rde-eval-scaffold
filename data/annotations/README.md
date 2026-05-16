# Annotations directory

- **`annotations.jsonl`** — primary **human** pilot adjudication (30 rows, aligned with `data/pilot_30.jsonl` by `id`).
- **`pilot_30_deepseek.jsonl`** — **LLM candidate** annotations (not human gold); use as **`--candidate`** with human reference when analyzing agreement.
- **`pilot_30_reference_placeholder.jsonl`** — **not gold**, synthetic rows for tooling smoke tests (`reference_placeholder: true`). Do **not** use for empirical conclusions; see GitHub **`#58`**.
- Comparisons preserve **human** vs **candidate** separation; **`compare_annotations.py`** must not adjudicate merges.
