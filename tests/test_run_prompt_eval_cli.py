"""Smoke tests for ``scripts/run_prompt_eval.py``."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize(
    "input_name,expected_lines",
    [
        ("data/samples.jsonl", 4),
        ("data/pilot_30.jsonl", 30),
    ],
)
def test_run_prompt_eval_stub_writes_jsonl(
    tmp_path: Path, input_name: str, expected_lines: int
) -> None:
    out = tmp_path / "prompt_out.jsonl"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_prompt_eval.py"),
        "--input",
        str(REPO_ROOT / input_name),
        "--output",
        str(out),
        "--annotation-run-id",
        "pytest-stub",
    ]
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    proc = subprocess.run(
        cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False, env=env
    )
    assert proc.returncode == 0, proc.stderr
    lines = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == expected_lines
    first = json.loads(lines[0])
    assert first["normalization_status"] == "ok"
    assert first["annotator_id"] == "stub"
    assert "raw_output" in first


def test_run_prompt_eval_replay_mode(tmp_path: Path) -> None:
    good = json.dumps(
        {
            "llm_annotation": "Suspicious Drift",
            "risk_flags": ["uncertainty_loss"],
            "criticality": "medium",
            "explanation": "test",
        }
    )
    raw_path = tmp_path / "captures.jsonl"
    raw_path.write_text(
        json.dumps({"id": "sample-001", "raw_output": good}) + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "replay_out.jsonl"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_prompt_eval.py"),
        "--input",
        str(REPO_ROOT / "data" / "samples.jsonl"),
        "--output",
        str(out),
        "--mode",
        "replay",
        "--raw-jsonl",
        str(raw_path),
        "--annotation-run-id",
        "pytest-replay",
        "--annotator-id",
        "replay-test",
    ]
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    proc = subprocess.run(
        cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False, env=env
    )
    assert proc.returncode == 0, proc.stderr
    rows = [json.loads(ln) for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(rows) == 4
    first = rows[0]
    assert first["id"] == "sample-001"
    assert first["normalization_status"] == "ok"
    assert first["llm_annotation"] == "Suspicious Drift"
    assert rows[1]["normalization_status"] == "failed"
    assert rows[1]["error_type"] == "missing_raw_output"
