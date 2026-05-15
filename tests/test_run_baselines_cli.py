"""Smoke tests for ``scripts/run_baselines.py``."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

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
    assert row["baseline_scores"]["m3"]["version"] == "1"
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


def test_run_baselines_bertscore_with_mocked_batch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fake_batch(sources: list[str], outputs: list[str], *, lang: str = "en") -> list[dict]:
        assert len(sources) == len(outputs)
        return [
            {
                "precision": 0.9,
                "recall": 0.89,
                "f1": 0.895,
                "lang": lang,
                "method": "bert-score",
            }
            for _ in sources
        ]

    monkeypatch.setattr("rde_eval.bertscore_m3.compute_bertscore_batch", fake_batch)

    inp = tmp_path / "in.jsonl"
    inp.write_text(
        '{"id":"a","task":"t","risk_context":"r","source":"hello","output":"hello"}\n',
        encoding="utf-8",
    )
    out = tmp_path / "out.jsonl"

    import runpy

    monkeypatch.setattr(
        sys,
        "argv",
        ["run_baselines.py", "--input", str(inp), "--output", str(out), "--bertscore"],
    )
    runpy.run_path(str(REPO_ROOT / "scripts" / "run_baselines.py"), run_name="__main__")

    line = out.read_text(encoding="utf-8").strip().splitlines()[0]
    row = json.loads(line)
    assert row["baseline_scores"]["m3"]["version"] == "2"
    assert row["baseline_scores"]["m3"]["bertscore"]["f1"] == 0.895
