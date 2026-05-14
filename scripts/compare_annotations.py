#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def index_by_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record["id"]): record for record in records}


def label_of(record: dict[str, Any], *, role: str) -> str | None:
    if role == "reference":
        return record.get("human_annotation") or record.get("llm_annotation")
    if role == "candidate":
        return record.get("llm_annotation") or record.get("human_annotation")
    raise ValueError(f"unknown role: {role}")


def flag_set(record: dict[str, Any]) -> set[str]:
    return set(record.get("risk_flags") or [])


def safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 1.0 if numerator == 0 else 0.0
    return numerator / denominator


def f1_score(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def compare_annotations(
    reference_records: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    reference = index_by_id(reference_records)
    candidate = index_by_id(candidate_records)
    all_ids = sorted(set(reference) | set(candidate))

    comparable = 0
    label_matches = 0
    criticality_matches = 0
    risk_exact_matches = 0
    total_overlap = 0
    total_candidate_flags = 0
    total_reference_flags = 0
    disagreements: list[dict[str, Any]] = []
    missing_reference: list[str] = []
    missing_candidate: list[str] = []

    for sample_id in all_ids:
        ref = reference.get(sample_id)
        cand = candidate.get(sample_id)
        if ref is None:
            missing_reference.append(sample_id)
            continue
        if cand is None:
            missing_candidate.append(sample_id)
            continue

        comparable += 1
        ref_label = label_of(ref, role="reference")
        cand_label = label_of(cand, role="candidate")
        ref_criticality = ref.get("criticality")
        cand_criticality = cand.get("criticality")
        ref_flags = flag_set(ref)
        cand_flags = flag_set(cand)

        label_match = ref_label == cand_label
        criticality_match = ref_criticality == cand_criticality
        risk_exact_match = ref_flags == cand_flags

        label_matches += int(label_match)
        criticality_matches += int(criticality_match)
        risk_exact_matches += int(risk_exact_match)

        overlap = len(ref_flags & cand_flags)
        total_overlap += overlap
        total_candidate_flags += len(cand_flags)
        total_reference_flags += len(ref_flags)

        if not (label_match and criticality_match and risk_exact_match):
            disagreements.append(
                {
                    "id": sample_id,
                    "reference_label": ref_label,
                    "candidate_label": cand_label,
                    "reference_flags": sorted(ref_flags),
                    "candidate_flags": sorted(cand_flags),
                    "reference_criticality": ref_criticality,
                    "candidate_criticality": cand_criticality,
                }
            )

    precision = safe_div(total_overlap, total_candidate_flags)
    recall = safe_div(total_overlap, total_reference_flags)

    return {
        "total": len(all_ids),
        "comparable": comparable,
        "missing_reference": missing_reference,
        "missing_candidate": missing_candidate,
        "label_agreement": safe_div(label_matches, comparable),
        "criticality_agreement": safe_div(criticality_matches, comparable),
        "risk_flag_exact_agreement": safe_div(risk_exact_matches, comparable),
        "risk_flag_precision": precision,
        "risk_flag_recall": recall,
        "risk_flag_f1": f1_score(precision, recall),
        "disagreements": disagreements,
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare RDE annotation JSONL files.")
    parser.add_argument("--reference", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--source", required=False, help="Reserved for future source-aware comparison.")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = compare_annotations(
        load_jsonl(Path(args.reference)),
        load_jsonl(Path(args.candidate)),
    )
    write_json(Path(args.output), result)
    print(f"Compared {result['comparable']} records -> {args.output}")


if __name__ == "__main__":
    main()
