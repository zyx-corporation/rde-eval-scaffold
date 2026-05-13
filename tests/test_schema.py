from __future__ import annotations

import pytest

from rde_eval.schema import Criticality, EvaluationResult, RdeLabel, RdeSample


def test_sample_from_dict_accepts_required_fields() -> None:
    sample = RdeSample.from_dict(
        {
            "id": "sample-001",
            "task": "summarization",
            "risk_context": "policy_discussion",
            "source": "This policy may reduce risk.",
            "output": "This policy reduces risk.",
        }
    )

    assert sample.id == "sample-001"
    assert sample.task == "summarization"
    assert sample.criticality is None
    assert sample.task_intent is None


def test_sample_from_dict_accepts_pilot_fields() -> None:
    sample = RdeSample.from_dict(
        {
            "id": "pilot-001",
            "task": "summarization",
            "risk_context": "policy_discussion",
            "source": "This policy may reduce risk under specific conditions.",
            "output": "This policy reduces risk.",
            "human_annotation": "Suspicious Drift",
            "risk_flags": ["uncertainty_loss", "claim_strength_inflation"],
            "criticality": "medium",
            "explanation": "条件付き表現が削除され、断定へ変化している。",
            "task_intent": "Summarize faithfully without removing caveats.",
            "reconstructed_task_intent": "Faithful risk-sensitive summarization.",
            "task_intent_notes": "The explicit task was underspecified, so risk context is used.",
            "notes": "Pilot annotation sample.",
        }
    )

    assert sample.id == "pilot-001"
    assert sample.criticality == "medium"
    assert sample.explanation == "条件付き表現が削除され、断定へ変化している。"
    assert sample.task_intent == "Summarize faithfully without removing caveats."
    assert sample.reconstructed_task_intent == "Faithful risk-sensitive summarization."
    assert sample.task_intent_notes == "The explicit task was underspecified, so risk context is used."
    assert sample.to_dict()["risk_flags"] == ["uncertainty_loss", "claim_strength_inflation"]


def test_sample_from_dict_rejects_missing_required_fields() -> None:
    with pytest.raises(ValueError):
        RdeSample.from_dict({"id": "sample-001"})


def test_evaluation_result_matches_expected() -> None:
    result = EvaluationResult(
        id="sample-001",
        primary_label=RdeLabel.SUSPICIOUS_DRIFT,
        risk_flags=["uncertainty_loss"],
        criticality=Criticality.MEDIUM,
        explanation="test",
        expected_label="Suspicious Drift",
    )

    assert result.matches_expected is True
    assert result.to_dict()["matches_expected"] is True
