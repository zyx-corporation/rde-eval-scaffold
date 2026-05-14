from __future__ import annotations

import json
from pathlib import Path

import pytest

from rde_eval.evaluator import evaluate_samples, load_samples, write_results
from rde_eval.schema import Criticality, EvaluationResult, RdeLabel


def test_load_samples_rejects_invalid_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"id": "x",}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="line 1"):
        load_samples(bad)


def test_load_samples_propagates_schema_errors(tmp_path: Path) -> None:
    bad = tmp_path / "bad_schema.jsonl"
    bad.write_text(
        '{"id":"a","task":"t","risk_context":"r","source":"s","output":"o","risk_flags":["nope"]}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="line 1"):
        load_samples(bad)


def test_write_results_is_deterministic(tmp_path: Path) -> None:
    path = tmp_path / "out.jsonl"
    result = EvaluationResult(
        id="sample-001",
        primary_label=RdeLabel.PRESERVED,
        risk_flags=[],
        criticality=Criticality.LOW,
        explanation="ok",
        expected_label=None,
    )
    write_results(path, [result])
    first = path.read_text(encoding="utf-8")
    write_results(path, [result])
    second = path.read_text(encoding="utf-8")
    assert first == second
    parsed = json.loads(first.strip())
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_evaluate_samples_round_trip(tmp_path: Path) -> None:
    src = tmp_path / "in.jsonl"
    src.write_text(
        '{"id":"z","task":"t","risk_context":"r","source":"same","output":"same"}\n',
        encoding="utf-8",
    )
    samples = load_samples(src)
    results = evaluate_samples(samples)
    assert len(results) == 1
    out = tmp_path / "out.jsonl"
    write_results(out, results)
    line = out.read_text(encoding="utf-8").strip()
    data = json.loads(line)
    assert data["id"] == "z"
    assert data["primary_label"] == "Preserved"
