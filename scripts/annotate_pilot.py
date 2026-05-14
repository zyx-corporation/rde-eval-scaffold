#!/usr/bin/env python3
"""
Japanese-first human annotation CLI for RDE pilot study.

Usage (English):
    python scripts/annotate_pilot.py [--input PATH] [--output PATH] [--annotator NAME]

使い方 (日本語):
    python scripts/annotate_pilot.py [--input ファイルパス] [--output 出力パス] [--annotator 名前]

Options:
    --input       Input JSONL file (default: data/pilot_30.jsonl)
                  入力JSONLファイル（デフォルト: data/pilot_30.jsonl）
    --output      Output JSONL file for annotations (default: data/annotations/annotations.jsonl)
                  注釈出力JSONLファイル（デフォルト: data/annotations/annotations.jsonl）
    --annotator   Annotator identifier (default: "anonymous")
                  注釈者識別子（デフォルト: "anonymous"）
    --no-resume   Ignore existing records in the selected output file.
                  選択した出力ファイル内の既存レコードを無視します。
    --overwrite   Delete the selected output file before starting.
                  開始前に選択した出力ファイルを削除します。

Resume mode:
    Already-annotated IDs present in the selected output file are skipped automatically.
    Other JSONL files in the same directory are ignored.
    選択した出力ファイルに存在するIDのみ、自動的にスキップされます。
    同じディレクトリ内の他のJSONLファイルは無視されます。

Canonical values:
    Labels, risk flags, and criticality are saved as English canonical values
    regardless of how they are displayed in Japanese.
    ラベル・リスクフラグ・重大度は、日本語で表示されていても英語の正規値で保存されます。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Japanese display maps
# ---------------------------------------------------------------------------

# key -> (canonical English value, Japanese display string)
LABEL_CHOICES: dict[str, tuple[str, str]] = {
    "1": ("Preserved", "保存済み — 中心的な意図・主張強度・不確実性・責任構造が保存されている"),
    "2": (
        "Authorized Transformation",
        "許可された変換 — タスクによって正当化された変化で重要な意味を損なっていない",
    ),
    "3": ("Inferred Extension", "推論的拡張 — ソースから妥当に推論可能な内容が追加されている"),
    "4": (
        "Unresolved Gap",
        "未解決のギャップ — 重要な意味差分が未処理、または自信を持って分類できない",
    ),
    "5": (
        "Suspicious Drift",
        "疑わしい逸脱 — 主張強度・不確実性・責任・価値構造が潜在的に有害な方向へ変化",
    ),
    "6": (
        "Critical Distortion",
        "重大な歪曲 — ソースの意味・責任構造・制度的含意を実質的に反転・消去・破壊",
    ),
}

# letter key -> (canonical English value, Japanese display string)
RISK_FLAG_CHOICES: dict[str, tuple[str, str]] = {
    "a": ("claim_strength_inflation", "主張強度の強化 — 弱い・条件付き主張が断定へ変化"),
    "b": ("uncertainty_loss", "不確実性の喪失 — 不確実性・限界・条件・留保が削除"),
    "c": ("responsibility_shift", "責任の移動 — 人間・組織・制度からAIへ責任が移動"),
    "d": ("value_simplification", "価値の単純化 — 複数の価値・対立が単一の結論へ縮退"),
    "e": (
        "institutional_implication_loss",
        "制度的含意の喪失 — 法的・組織的・ガバナンス上の含意が消失",
    ),
    "f": ("context_drift", "文脈の漂流 — 出力がソースとは異なる文脈へ移動"),
    "g": ("theoretical_reduction", "理論的縮退 — 理論的主張が単なる技術的・運用的記述へ縮退"),
}

CRITICALITY_CHOICES: dict[str, tuple[str, str]] = {
    "1": ("low", "低 — 誤用されても影響が限定的"),
    "2": ("medium", "中 — レビューまたは修正が必要"),
    "3": ("high", "高 — そのまま使用すべきでない、実質的な被害リスク"),
}

# ---------------------------------------------------------------------------
# Pure parsing functions (easily testable)
# ---------------------------------------------------------------------------


def parse_label_choice(key: str) -> str:
    """Return canonical English RDE label for a Japanese-menu key ("1"–"6")."""
    key = key.strip()
    if key not in LABEL_CHOICES:
        raise ValueError(f"無効な選択: {key!r}。1〜6 の数字を入力してください。")
    return LABEL_CHOICES[key][0]


def parse_risk_flags(raw: str | None) -> list[str]:
    """Parse risk flag input (letters a–g, concatenated or comma-separated).

    Returns a deduplicated list of canonical English flag identifiers.
    Empty / None / whitespace-only input returns an empty list.
    """
    if not raw or not raw.strip():
        return []

    # Normalize: remove commas and spaces, iterate characters
    normalized = raw.replace(",", "").replace(" ", "")
    seen: set[str] = set()
    result: list[str] = []
    for ch in normalized:
        if ch not in RISK_FLAG_CHOICES:
            raise ValueError(f"無効なリスクフラグ: {ch!r}。a〜g の文字を入力してください。")
        canonical = RISK_FLAG_CHOICES[ch][0]
        if canonical not in seen:
            seen.add(canonical)
            result.append(canonical)
    return result


def parse_criticality_choice(key: str) -> str:
    """Return canonical criticality value ("low"/"medium"/"high") for key "1"–"3"."""
    key = key.strip()
    if key not in CRITICALITY_CHOICES:
        raise ValueError(f"無効な選択: {key!r}。1〜3 の数字を入力してください。")
    return CRITICALITY_CHOICES[key][0]


def format_annotation(
    *,
    sample_id: str,
    human_annotation: str,
    risk_flags: list[str],
    criticality: str,
    explanation: str,
    annotator: str,
) -> dict:
    """Build an annotation record with canonical values and ISO-8601 timestamp."""
    return {
        "id": sample_id,
        "human_annotation": human_annotation,
        "risk_flags": risk_flags,
        "criticality": criticality,
        "explanation": explanation,
        "annotator": annotator,
        "annotated_at": datetime.now(tz=UTC).isoformat(),
    }


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def load_pilot_records(path: Path) -> list[dict]:
    """Load all non-blank JSONL records from *path*."""
    records: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_annotated_ids(output_path: Path) -> set[str]:
    """Collect IDs already present in the selected output JSONL file only."""
    ids: set[str] = set()
    if not output_path.exists():
        return ids
    with output_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if "id" in record:
                    ids.add(str(record["id"]))
            except json.JSONDecodeError:
                pass
    return ids


def prepare_output_file(output_path: Path, *, overwrite: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if overwrite and output_path.exists():
        output_path.unlink()


def append_annotation(output_path: Path, record: dict) -> None:
    """Append a single annotation record as one JSON line to *output_path*."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

_SEP = "─" * 60


def _print_field(label: str, value: str | None) -> None:
    if value:
        print(f"\n【{label}】")
        print(value)


def _print_record(record: dict, index: int, total: int) -> None:
    print(f"\n{_SEP}")
    print(f"  サンプル {index}/{total}  ID: {record.get('id', '?')}")
    print(_SEP)
    _print_field("タスク", record.get("task") or record.get("task_intent_ja"))
    _print_field("タスク意図 (日本語)", record.get("task_intent_ja"))
    _print_field("再構成タスク意図 (日本語)", record.get("reconstructed_task_intent_ja"))
    _print_field("タスク意図注記 (日本語)", record.get("task_intent_notes_ja"))
    _print_field("リスク文脈", record.get("risk_context"))
    _print_field("ソース (日本語)", record.get("source_ja") or record.get("source"))
    _print_field("出力 (日本語)", record.get("output_ja") or record.get("output"))
    _print_field("説明 (日本語・参考)", record.get("explanation_ja"))


def _print_label_menu() -> None:
    print("\n【Primary Label を選択してください】")
    for key, (canonical, display_ja) in LABEL_CHOICES.items():
        print(f"  {key}. {display_ja}")
        print(f"     → {canonical}")


def _print_risk_flag_menu() -> None:
    print("\n【Risk Flags を選択してください（複数可: 例 ab, a,b）。なければ Enter】")
    for key, (canonical, display_ja) in RISK_FLAG_CHOICES.items():
        print(f"  {key}. {display_ja}")
        print(f"     → {canonical}")


def _print_criticality_menu() -> None:
    print("\n【Criticality を選択してください】")
    for key, (canonical, display_ja) in CRITICALITY_CHOICES.items():
        print(f"  {key}. {display_ja}")
        print(f"     → {canonical}")


# ---------------------------------------------------------------------------
# Interactive annotation loop
# ---------------------------------------------------------------------------


def _prompt(prompt_text: str) -> str:
    """Prompt user; handle EOFError gracefully."""
    try:
        return input(prompt_text).strip()
    except EOFError:
        print("\n（入力が終了しました）")
        sys.exit(0)


def _prompt_label() -> str:
    while True:
        _print_label_menu()
        raw = _prompt("ラベル番号を入力 (1–6): ")
        try:
            return parse_label_choice(raw)
        except ValueError as exc:
            print(f"  ⚠  {exc}")


def _prompt_risk_flags() -> list[str]:
    while True:
        _print_risk_flag_menu()
        raw = _prompt("フラグ文字を入力 (例: ab / Enter でスキップ): ")
        try:
            return parse_risk_flags(raw)
        except ValueError as exc:
            print(f"  ⚠  {exc}")


def _prompt_criticality() -> str:
    while True:
        _print_criticality_menu()
        raw = _prompt("番号を入力 (1–3): ")
        try:
            return parse_criticality_choice(raw)
        except ValueError as exc:
            print(f"  ⚠  {exc}")


def _prompt_explanation() -> str:
    print("\n【説明を入力してください（日本語可）】")
    return _prompt("説明: ")


def annotate_interactively(
    records: list[dict],
    output_path: Path,
    annotator: str,
    already_done: set[str],
) -> int:
    """Run the interactive annotation loop. Returns number of new annotations written."""
    pending = [r for r in records if r.get("id") not in already_done]
    total = len(pending)

    if not pending:
        print("すべてのサンプルは既に注釈済みです。")
        return 0

    print(f"\n注釈対象: {total} 件（スキップ済み: {len(records) - total} 件）")
    print("Ctrl-C または Ctrl-D で中断できます（途中まで保存されます）。")

    count = 0
    try:
        for i, record in enumerate(pending, start=1):
            _print_record(record, i, total)

            label = _prompt_label()
            flags = _prompt_risk_flags()
            criticality = _prompt_criticality()
            explanation = _prompt_explanation()

            annotation = format_annotation(
                sample_id=record["id"],
                human_annotation=label,
                risk_flags=flags,
                criticality=criticality,
                explanation=explanation,
                annotator=annotator,
            )
            append_annotation(output_path, annotation)
            count += 1
            print(f"\n  ✓ 保存しました: {record['id']}")

    except KeyboardInterrupt:
        print(f"\n\n中断しました。{count} 件を保存済みです。")

    return count


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Japanese-first human annotation CLI for RDE pilot study.\n"
            "日本語優先 RDE パイロット研究ヒューマンアノテーション CLI。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default="data/pilot_30.jsonl",
        help="Input JSONL file / 入力JSONLファイル (default: data/pilot_30.jsonl)",
    )
    parser.add_argument(
        "--output",
        default="data/annotations/annotations.jsonl",
        help="Output JSONL file / 注釈出力ファイル (default: data/annotations/annotations.jsonl)",
    )
    parser.add_argument(
        "--annotator",
        default="anonymous",
        help="Annotator identifier / 注釈者識別子 (default: anonymous)",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore existing records in the selected output file.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete the selected output file before starting.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.no_resume and args.overwrite:
        print("エラー: --no-resume と --overwrite は同時に指定できません。", file=sys.stderr)
        sys.exit(1)

    prepare_output_file(output_path, overwrite=args.overwrite)
    records = load_pilot_records(input_path)
    already_done = set() if args.no_resume or args.overwrite else load_annotated_ids(output_path)

    count = annotate_interactively(
        records=records,
        output_path=output_path,
        annotator=args.annotator,
        already_done=already_done,
    )

    print(f"\n完了。新規注釈数: {count} 件 → {output_path}")


if __name__ == "__main__":
    main()
