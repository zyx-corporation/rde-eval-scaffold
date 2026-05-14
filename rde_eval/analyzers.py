from __future__ import annotations

from dataclasses import dataclass

from rde_eval.schema import RdeSample


@dataclass(frozen=True)
class TextAnalysis:
    has_uncertainty: bool
    has_responsibility_marker: bool
    has_theoretical_marker: bool


def analyze_source(sample: RdeSample) -> TextAnalysis:
    return _analyze_text(sample.source)


def analyze_output(sample: RdeSample) -> TextAnalysis:
    return _analyze_text(sample.output)


def _analyze_text(text: str) -> TextAnalysis:
    lowered = text.lower()
    return TextAnalysis(
        has_uncertainty=any(
            marker in lowered for marker in ("may", "might", "possible", "可能性", "不明")
        ),
        has_responsibility_marker=any(
            marker in lowered for marker in ("responsibility", "accountability", "責任", "承認")
        ),
        has_theoretical_marker=any(
            marker in lowered for marker in ("meaning", "semantic", "意味", "監査")
        ),
    )
