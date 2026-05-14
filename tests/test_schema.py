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
    expected_notes = "The explicit task was underspecified, so risk context is used."
    assert sample.task_intent_notes == expected_notes
    assert sample.to_dict()["risk_flags"] == ["uncertainty_loss", "claim_strength_inflation"]


def test_sample_from_dict_accepts_baseline_scores_placeholder() -> None:
    sample = RdeSample.from_dict(
        {
            "id": "pilot-002",
            "task": "summarization",
            "risk_context": "policy_discussion",
            "source": "x",
            "output": "y",
            "baseline_scores": {"bertscore": {"f1": 0.42}},
        }
    )
    assert sample.baseline_scores == {"bertscore": {"f1": 0.42}}
    assert "baseline_scores" in sample.to_dict()


def test_sample_to_dict_omits_null_baseline_scores() -> None:
    sample = RdeSample.from_dict(
        {
            "id": "pilot-003",
            "task": "summarization",
            "risk_context": "policy_discussion",
            "source": "x",
            "output": "y",
        }
    )
    assert "baseline_scores" not in sample.to_dict()


def test_sample_from_dict_rejects_unknown_risk_flag() -> None:
    with pytest.raises(ValueError, match="Unknown risk_flags"):
        RdeSample.from_dict(
            {
                "id": "bad-flags",
                "task": "summarization",
                "risk_context": "policy_discussion",
                "source": "x",
                "output": "y",
                "risk_flags": ["not_a_real_flag"],
            }
        )


def test_sample_from_dict_rejects_invalid_human_annotation() -> None:
    with pytest.raises(ValueError, match="Invalid human_annotation"):
        RdeSample.from_dict(
            {
                "id": "bad-label",
                "task": "summarization",
                "risk_context": "policy_discussion",
                "source": "x",
                "output": "y",
                "human_annotation": "Made Up Label",
            }
        )


def test_sample_from_dict_rejects_non_json_baseline_scores() -> None:
    with pytest.raises(ValueError, match="baseline_scores"):
        RdeSample.from_dict(
            {
                "id": "bad-baseline",
                "task": "summarization",
                "risk_context": "policy_discussion",
                "source": "x",
                "output": "y",
                "baseline_scores": object(),
            }
        )


def test_sample_from_dict_strips_blank_human_annotation() -> None:
    sample = RdeSample.from_dict(
        {
            "id": "blank-label",
            "task": "summarization",
            "risk_context": "policy_discussion",
            "source": "x",
            "output": "y",
            "human_annotation": "   ",
        }
    )
    assert sample.human_annotation is None


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
