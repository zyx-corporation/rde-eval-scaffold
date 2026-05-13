from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from rde_eval.classifier import classify_sample
from rde_eval.schema import EvaluationResult, RdeSample


def load_samples(path: str | Path) -> list[RdeSample]:
    samples: list[RdeSample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                data = json.loads(stripped)
                samples.append(RdeSample.from_dict(data))
            except Exception as exc:  # noqa: BLE001 - keep CLI error context simple.
                raise ValueError(f"Invalid JSONL sample at line {line_number}: {exc}") from exc
    return samples


def evaluate_samples(samples: Iterable[RdeSample]) -> list[EvaluationResult]:
    return [classify_sample(sample) for sample in samples]


def write_results(path: str | Path, results: Iterable[EvaluationResult]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
