# annotate_pilot CLI — Usage Guide

`scripts/annotate_pilot.py` is a Japanese-first interactive command-line tool
for human annotation of RDE pilot study samples.

---

## Quick start

```bash
python scripts/annotate_pilot.py
```

This reads `data/pilot_30.jsonl` and writes annotations to
`data/annotations/annotations.jsonl`.

---

## Options

| Option | Default | Description |
|---|---|---|
| `--input PATH` | `data/pilot_30.jsonl` | Input JSONL file to annotate |
| `--output PATH` | `data/annotations/annotations.jsonl` | Output JSONL file for annotation results |
| `--annotator NAME` | `anonymous` | Annotator identifier stored in each record |

Examples:

```bash
# Custom annotator name
python scripts/annotate_pilot.py --annotator alice

# Custom paths
python scripts/annotate_pilot.py \
  --input data/pilot_30.jsonl \
  --output data/annotations/alice_session1.jsonl \
  --annotator alice
```

---

## Resume mode

Already-annotated IDs are detected automatically by scanning all `*.jsonl`
files in the output file's parent directory. Duplicate annotation is skipped
without any extra flags.

```bash
# First session — annotates records 1–10 then interrupts with Ctrl-C
python scripts/annotate_pilot.py --output data/annotations/alice.jsonl --annotator alice

# Second session — picks up from record 11 automatically
python scripts/annotate_pilot.py --output data/annotations/alice.jsonl --annotator alice
```

---

## Annotation workflow

For each record, the tool displays the following Japanese fields:

| Field | Display label |
|---|---|
| `task_intent_ja` | タスク意図 (日本語) |
| `reconstructed_task_intent_ja` | 再構成タスク意図 (日本語) |
| `task_intent_notes_ja` | タスク意図注記 (日本語) |
| `risk_context` | リスク文脈 |
| `source_ja` | ソース (日本語) |
| `output_ja` | 出力 (日本語) |
| `explanation_ja` | 説明 (日本語・参考) |

Then prompts the annotator for three choices and a free-text explanation:

### 1. Primary label (1–6)

```
1. 保存済み                → Preserved
2. 許可された変換          → Authorized Transformation
3. 推論的拡張              → Inferred Extension
4. 未解決のギャップ        → Unresolved Gap
5. 疑わしい逸脱            → Suspicious Drift
6. 重大な歪曲              → Critical Distortion
```

Enter a single digit.

### 2. Risk flags (letters a–g, combinable)

```
a. 主張強度の強化          → claim_strength_inflation
b. 不確実性の喪失          → uncertainty_loss
c. 責任の移動              → responsibility_shift
d. 価値の単純化            → value_simplification
e. 制度的含意の喪失        → institutional_implication_loss
f. 文脈の漂流              → context_drift
g. 理論的縮退              → theoretical_reduction
```

Enter one or more letters concatenated (`ab`) or comma-separated (`a,b`).
Press Enter to skip (no risk flags).

### 3. Criticality (1–3)

```
1. 低    → low
2. 中    → medium
3. 高    → high
```

Enter a single digit.

### 4. Explanation

Free-text explanation. Japanese is accepted and encouraged.

---

## Output format

Each annotation is saved as one JSON line:

```json
{
  "id": "pilot-sum-001",
  "human_annotation": "Suspicious Drift",
  "risk_flags": ["claim_strength_inflation", "uncertainty_loss"],
  "criticality": "medium",
  "explanation": "条件付き表現が削除され、可能性の主張が断定へ変化している。",
  "annotator": "alice",
  "annotated_at": "2026-05-14T09:00:00+00:00"
}
```

### Canonical-value rule

All saved values use canonical English identifiers regardless of the Japanese
display labels shown during annotation:

- `human_annotation` — one of the six `RdeLabel` values
- `risk_flags` — list of `KNOWN_RISK_FLAGS` identifiers
- `criticality` — `low`, `medium`, or `high`

---

## Interrupting and saving

Press **Ctrl-C** at any time to stop. Records annotated so far are already
saved; the next session will resume from where you left off.

---

## Running tests

```bash
python -m pytest tests/test_annotate_pilot.py -v
```

32 unit tests cover choice parsing, output format, I/O helpers, and resume
behavior.
