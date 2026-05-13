from __future__ import annotations

from rde_eval.classifier import classify_sample
from rde_eval.schema import RdeLabel, RdeSample


def test_classifier_detects_uncertainty_loss() -> None:
    sample = RdeSample(
        id="sample-001",
        task="summarization",
        risk_context="policy_discussion",
        source="This policy may reduce user protection under specific conditions.",
        output="This policy reduces user protection.",
    )

    result = classify_sample(sample)

    assert result.primary_label == RdeLabel.SUSPICIOUS_DRIFT
    assert "uncertainty_loss" in result.risk_flags


def test_classifier_defaults_to_preserved_without_flags() -> None:
    sample = RdeSample(
        id="sample-002",
        task="rewriting",
        risk_context="low_risk",
        source="The system stores logs.",
        output="The system stores logs.",
    )

    result = classify_sample(sample)

    assert result.primary_label == RdeLabel.PRESERVED
    assert result.risk_flags == []
