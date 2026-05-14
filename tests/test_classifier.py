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


def test_classifier_detects_context_drift_between_domains() -> None:
    sample = RdeSample(
        id="sample-ctx",
        task="rewriting",
        risk_context="research_communication",
        source="The study tests the hypothesis under a controlled experiment.",
        output="The stock price jumped after the investor earnings report.",
    )

    result = classify_sample(sample)

    assert "context_drift" in result.risk_flags
    assert result.primary_label == RdeLabel.SUSPICIOUS_DRIFT


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
