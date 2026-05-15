"""Milestone 2 prompt-based evaluator helpers (normalization only; no live API).

Aligned with ``docs/prompt_evaluator_io_contract.md``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from rde_eval.schema import CRITICALITY_VALUES, KNOWN_RISK_FLAGS, PRIMARY_LABEL_VALUES

# Canonical English prompt inputs (schema authority per IO contract).
PROMPT_INPUT_CANONICAL_KEYS: tuple[str, ...] = (
    "id",
    "task",
    "risk_context",
    "source",
    "output",
    "task_intent",
    "reconstructed_task_intent",
    "task_intent_notes",
)

# Optional Japanese-first supplementary fields.
PROMPT_INPUT_JA_KEYS: tuple[str, ...] = (
    "source_ja",
    "output_ja",
    "task_intent_ja",
    "reconstructed_task_intent_ja",
    "task_intent_notes_ja",
)

REQUIRED_PROVENANCE_KEYS: tuple[str, ...] = (
    "annotator_type",
    "annotator_id",
    "model",
    "prompt_version",
    "annotation_run_id",
)


def extract_prompt_input(record: Mapping[str, Any]) -> dict[str, Any]:
    """Subset of a pilot JSONL row for prompt construction (English + optional JA)."""
    out: dict[str, Any] = {}
    for key in PROMPT_INPUT_CANONICAL_KEYS:
        if key in record and record[key] is not None:
            val = record[key]
            if isinstance(val, str) and not val.strip() and key != "id":
                continue
            out[key] = val
    for key in PROMPT_INPUT_JA_KEYS:
        if key in record and record[key] is not None:
            val = record[key]
            if isinstance(val, str) and val.strip():
                out[key] = val
    return out


def _provenance_subset(provenance: Mapping[str, Any]) -> dict[str, str]:
    missing = [k for k in REQUIRED_PROVENANCE_KEYS if not str(provenance.get(k, "")).strip()]
    if missing:
        raise ValueError(f"Missing provenance keys: {', '.join(missing)}")
    return {k: str(provenance[k]).strip() for k in REQUIRED_PROVENANCE_KEYS}


def parse_raw_model_output(raw_output: str) -> tuple[dict[str, Any] | None, str | None]:
    """Parse *raw_output* as JSON. Returns (dict, None) or (None, error_message)."""
    text = raw_output if isinstance(raw_output, str) else str(raw_output)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON: {exc}"
    if not isinstance(data, dict):
        return None, "Model JSON root must be an object"
    return data, None


def validate_llm_payload(parsed: Mapping[str, Any]) -> tuple[bool, str, str]:
    """Returns (ok, error_type, error_message)."""
    label = parsed.get("llm_annotation")
    if label is None or not str(label).strip():
        return False, "missing_field", "Missing or empty llm_annotation"
    label_s = str(label).strip()
    if label_s not in PRIMARY_LABEL_VALUES:
        return False, "invalid_label", f"Unknown llm_annotation: {label_s!r}"

    flags_raw = parsed.get("risk_flags", [])
    if flags_raw is None:
        flags_raw = []
    if not isinstance(flags_raw, list):
        return False, "invalid_type", "risk_flags must be a JSON array"
    flags = [str(f) for f in flags_raw]
    unknown = sorted({f for f in flags if f not in KNOWN_RISK_FLAGS})
    if unknown:
        return False, "invalid_risk_flag", f"Unknown risk_flags: {', '.join(unknown)}"

    crit = parsed.get("criticality")
    if crit is None or not str(crit).strip():
        return False, "missing_field", "Missing or empty criticality"
    crit_s = str(crit).strip().lower()
    if crit_s not in CRITICALITY_VALUES:
        return False, "invalid_criticality", f"Unknown criticality: {crit_s!r}"

    return True, "", ""


def build_failure_record(
    sample_id: str,
    provenance: Mapping[str, Any],
    *,
    error_type: str,
    error_message: str,
    raw_output: str,
) -> dict[str, Any]:
    """JSONL record for normalization failure (IO contract)."""
    base = _provenance_subset(provenance)
    return {
        "id": str(sample_id),
        **base,
        "normalization_status": "failed",
        "error_type": error_type,
        "error_message": error_message,
        "raw_output": raw_output,
    }


def build_success_record(
    sample_id: str,
    provenance: Mapping[str, Any],
    parsed: Mapping[str, Any],
    raw_output: str,
) -> dict[str, Any]:
    """JSONL record for successful normalization (IO contract)."""
    base = _provenance_subset(provenance)
    flags = [str(f) for f in (parsed.get("risk_flags") or [])]
    explanation = parsed.get("explanation")
    explanation_ja = parsed.get("explanation_ja")
    out: dict[str, Any] = {
        "id": str(sample_id),
        **base,
        "llm_annotation": str(parsed["llm_annotation"]).strip(),
        "risk_flags": flags,
        "criticality": str(parsed["criticality"]).strip().lower(),
        "raw_output": raw_output,
        "normalization_status": "ok",
    }
    if explanation is not None and str(explanation).strip():
        out["explanation"] = str(explanation).strip()
    if explanation_ja is not None and str(explanation_ja).strip():
        out["explanation_ja"] = str(explanation_ja).strip()
    return out


def normalize_model_output(
    sample_id: str,
    provenance: Mapping[str, Any],
    raw_output: str,
) -> dict[str, Any]:
    """Parse *raw_output*, validate payload, return success or failure record."""
    parsed, parse_err = parse_raw_model_output(raw_output)
    if parsed is None:
        return build_failure_record(
            sample_id,
            provenance,
            error_type="invalid_json",
            error_message=parse_err or "Invalid JSON",
            raw_output=raw_output,
        )

    ok, err_type, err_msg = validate_llm_payload(parsed)
    if not ok:
        return build_failure_record(
            sample_id,
            provenance,
            error_type=err_type,
            error_message=err_msg,
            raw_output=raw_output,
        )

    return build_success_record(sample_id, provenance, parsed, raw_output)


def stub_model_raw_output() -> str:
    """Deterministic JSON string used by ``--mode stub`` (no network)."""
    return json.dumps(
        {
            "llm_annotation": "Preserved",
            "risk_flags": [],
            "criticality": "low",
            "explanation": "Stub Milestone 2 evaluator (no model call).",
            "explanation_ja": "Milestone 2 スタブ（モデル未呼び出し）。",
        },
        ensure_ascii=False,
    )


def load_raw_outputs_by_id(path: str | Path) -> dict[str, str]:
    """Load ``{id: raw_output}`` from a JSONL file of replay captures.

    Each line must be a JSON object with ``id`` and ``raw_output`` (string).
    Duplicate IDs raise ``ValueError``.
    """
    p = Path(path)
    by_id: dict[str, str] = {}
    with p.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"Line {line_number}: expected JSON object")
            if "id" not in row:
                raise ValueError(f"Line {line_number}: missing 'id'")
            sample_id = str(row["id"])
            if sample_id in by_id:
                raise ValueError(f"Duplicate id in raw JSONL: {sample_id!r}")
            raw = row.get("raw_output")
            if raw is None:
                raise ValueError(f"Line {line_number}: missing 'raw_output' for id {sample_id!r}")
            by_id[sample_id] = raw if isinstance(raw, str) else json.dumps(raw, ensure_ascii=False)
    return by_id


def load_completed_ids(output_path: Path) -> set[str]:
    """Collect ``id`` values already present in a normalized output JSONL file."""
    ids: set[str] = set()
    if not output_path.is_file():
        return ids
    with output_path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and "id" in record:
                ids.add(str(record["id"]))
    return ids
