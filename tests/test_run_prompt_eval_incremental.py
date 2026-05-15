"""Tests for incremental live output in ``run_prompt_eval``."""

from __future__ import annotations

import json
from pathlib import Path

from run_prompt_eval import run_evaluation_records

from rde_eval.prompt_eval import stub_model_raw_output
from rde_eval.prompt_template import PROMPT_VERSION_V1


def _prov() -> dict[str, str]:
    return {
        "annotator_type": "llm",
        "annotator_id": "test",
        "model": "gpt-test",
        "prompt_version": PROMPT_VERSION_V1,
        "annotation_run_id": "run-1",
    }


def test_live_mode_appends_output_incrementally(tmp_path: Path) -> None:
    out = tmp_path / "live_out.jsonl"
    out.write_text('{"id":"old"}\n', encoding="utf-8")

    raw = json.dumps(
        {"llm_annotation": "Preserved", "risk_flags": [], "criticality": "low"},
    )
    rows = [
        {"id": "r1", "source": "a", "output": "b"},
        {"id": "r2", "source": "c", "output": "d"},
    ]

    def fake_llm(_m: list[dict[str, str]]) -> str:
        return raw

    processed, ok_count, skipped = run_evaluation_records(
        rows,
        mode="live",
        output_path=out,
        provenance=_prov(),
        raw_stub=stub_model_raw_output(),
        raw_by_id={},
        prompt_version=PROMPT_VERSION_V1,
        llm_call=fake_llm,
    )
    assert processed == 2
    assert ok_count == 2
    assert skipped == 0
    lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2
    assert json.loads(lines[0])["id"] == "r1"
    assert "old" not in out.read_text(encoding="utf-8")


def test_stub_mode_writes_batch_at_end(tmp_path: Path) -> None:
    out = tmp_path / "stub_out.jsonl"
    processed, ok_count, skipped = run_evaluation_records(
        [{"id": "s1", "source": "x", "output": "y"}],
        mode="stub",
        output_path=out,
        provenance=_prov(),
        raw_stub=stub_model_raw_output(),
        raw_by_id={},
        prompt_version="rde-prompt-eval-stub-v1",
        llm_call=None,
    )
    assert processed == 1
    assert ok_count == 1
    assert skipped == 0
    assert out.exists()


def test_live_resume_skips_completed_ids_and_appends(tmp_path: Path) -> None:
    out = tmp_path / "live_resume.jsonl"
    existing = {
        "id": "r1",
        "normalization_status": "ok",
        "llm_annotation": "Preserved",
        "risk_flags": [],
        "criticality": "low",
    }
    out.write_text(json.dumps(existing, ensure_ascii=False) + "\n", encoding="utf-8")

    raw = json.dumps(
        {"llm_annotation": "Preserved", "risk_flags": [], "criticality": "low"},
    )
    rows = [
        {"id": "r1", "source": "a", "output": "b"},
        {"id": "r2", "source": "c", "output": "d"},
    ]

    def fake_llm(_m: list[dict[str, str]]) -> str:
        return raw

    processed, ok_count, skipped = run_evaluation_records(
        rows,
        mode="live",
        output_path=out,
        provenance=_prov(),
        raw_stub=stub_model_raw_output(),
        raw_by_id={},
        prompt_version=PROMPT_VERSION_V1,
        llm_call=fake_llm,
        resume=True,
    )
    assert processed == 1
    assert ok_count == 1
    assert skipped == 1

    lines = [json.loads(ln) for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 2
    assert lines[0]["id"] == "r1"
    assert lines[1]["id"] == "r2"


def test_live_resume_skips_ids_in_captures_without_duplicating(tmp_path: Path) -> None:
    out = tmp_path / "out.jsonl"
    cap = tmp_path / "cap.jsonl"
    cap.write_text(
        json.dumps({"id": "r1", "raw_output": '{"llm_annotation":"Preserved"}'}) + "\n",
        encoding="utf-8",
    )

    raw = json.dumps(
        {"llm_annotation": "Preserved", "risk_flags": [], "criticality": "low"},
    )
    rows = [
        {"id": "r1", "source": "a", "output": "b"},
        {"id": "r2", "source": "c", "output": "d"},
    ]
    calls: list[str] = []

    def fake_llm(_m: list[dict[str, str]]) -> str:
        calls.append("call")
        return raw

    processed, ok_count, skipped = run_evaluation_records(
        rows,
        mode="live",
        output_path=out,
        provenance=_prov(),
        raw_stub=stub_model_raw_output(),
        raw_by_id={},
        prompt_version=PROMPT_VERSION_V1,
        llm_call=fake_llm,
        captures_path=cap,
        resume=True,
    )
    assert processed == 1
    assert ok_count == 1
    assert skipped == 1
    assert calls == ["call"]
    cap_lines = [json.loads(ln) for ln in cap.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(cap_lines) == 2
    assert sum(1 for row in cap_lines if row["id"] == "r1") == 1
    assert cap_lines[-1]["id"] == "r2"
    out_lines = [json.loads(ln) for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(out_lines) == 1
    assert out_lines[0]["id"] == "r2"
