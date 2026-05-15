"""Smoke tests for ``scripts/run_baselines.py``."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_run_baselines_merges_m3(tmp_path: Path) -> None:
    inp = tmp_path / "in.jsonl"
    inp.write_text(
        '{"id":"a","task":"t","risk_context":"r","source":"hello world",'
        '"output":"hello","extra":1}\n',
        encoding="utf-8",
    )
    out = tmp_path / "out.jsonl"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_baselines.py"),
        "--input",
        str(inp),
        "--output",
        str(out),
    ]
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    proc = subprocess.run(
        cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False, env=env
    )
    assert proc.returncode == 0, proc.stderr
    line = out.read_text(encoding="utf-8").strip().splitlines()[0]
    row = json.loads(line)
    assert row["extra"] == 1
    assert "m3" in row["baseline_scores"]
    assert row["baseline_scores"]["m3"]["lexical"]["method"] == "difflib.SequenceMatcher"


def test_run_baselines_rejects_missing_field(tmp_path: Path) -> None:
    inp = tmp_path / "bad.jsonl"
    inp.write_text('{"id":"x","task":"t","risk_context":"r","source":"s"}\n', encoding="utf-8")
    out = tmp_path / "out.jsonl"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_baselines.py"),
        "--input",
        str(inp),
        "--output",
        str(out),
    ]
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    proc = subprocess.run(
        cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False, env=env
    )
    assert proc.returncode == 1
