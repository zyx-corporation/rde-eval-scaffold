from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def test_export_results_csv_columns(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    script = repo_root / "scripts" / "export_results.py"
    jsonl = tmp_path / "results.jsonl"
    jsonl.write_text(
        '{"id":"a","primary_label":"Preserved","risk_flags":[],"criticality":"low",'
        '"explanation":"x","expected_label":null,"matches_expected":null}\n',
        encoding="utf-8",
    )
    out_csv = tmp_path / "out.csv"
    proc = subprocess.run(
        [sys.executable, str(script), "--input", str(jsonl), "--output", str(out_csv)],
        cwd=str(repo_root),
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Exported" in proc.stdout

    with out_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        row = next(reader)
    assert set(row.keys()) == {
        "id",
        "primary_label",
        "risk_flags",
        "criticality",
        "explanation",
        "expected_label",
        "matches_expected",
    }
    assert row["id"] == "a"
    assert row["risk_flags"] == ""
