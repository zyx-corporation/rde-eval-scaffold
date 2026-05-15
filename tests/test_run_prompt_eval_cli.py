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
