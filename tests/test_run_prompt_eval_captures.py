"""Tests for live-mode raw capture output."""

from __future__ import annotations

import json
from pathlib import Path

from run_prompt_eval import _append_jsonl, evaluate_row

from rde_eval.prompt_template import PROMPT_VERSION_V1


def _prov() -> dict[str, str]:
    return {
        "annotator_type": "llm",
        "annotator_id": "test",
        "model": "gpt-test",
        "prompt_version": PROMPT_VERSION_V1,
        "annotation_run_id": "run-1",
    }


def test_append_jsonl_capture_roundtrip(tmp_path: Path) -> None:
    cap = tmp_path / "caps.jsonl"
    raw = json.dumps({"llm_annotation": "Preserved", "risk_flags": [], "criticality": "low"})
    _append_jsonl(cap, {"id": "p-1", "raw_output": raw})
    line = json.loads(cap.read_text(encoding="utf-8").strip())
    assert line["id"] == "p-1"
    assert line["raw_output"] == raw


def test_evaluate_row_live_returns_raw_for_replay(tmp_path: Path) -> None:
    raw = json.dumps(
        {"llm_annotation": "Preserved", "risk_flags": [], "criticality": "low"},
    )

    def fake_llm(_m: list[dict[str, str]]) -> str:
        return raw

    rec, captured = evaluate_row(
        {"id": "z", "source": "s", "output": "o"},
        mode="live",
        provenance=_prov(),
        raw_stub="",
        raw_by_id={},
        prompt_version=PROMPT_VERSION_V1,
        llm_call=fake_llm,
    )
    assert rec["normalization_status"] == "ok"
    assert captured == raw
