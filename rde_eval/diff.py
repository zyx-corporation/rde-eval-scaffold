from __future__ import annotations

from dataclasses import dataclass

from rde_eval.analyzers import analyze_output, analyze_source
from rde_eval.schema import RdeSample


@dataclass(frozen=True)
class SemanticDiff:
    uncertainty_removed: bool
    responsibility_marker_removed: bool
    theoretical_marker_removed: bool


def build_semantic_diff(sample: RdeSample) -> SemanticDiff:
    source = analyze_source(sample)
    output = analyze_output(sample)
    return SemanticDiff(
        uncertainty_removed=source.has_uncertainty and not output.has_uncertainty,
        responsibility_marker_removed=(
            source.has_responsibility_marker and not output.has_responsibility_marker
        ),
        theoretical_marker_removed=(
            source.has_theoretical_marker and not output.has_theoretical_marker
        ),
    )
