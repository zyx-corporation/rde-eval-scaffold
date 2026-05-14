from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RdeLabel(StrEnum):
    PRESERVED = "Preserved"
    AUTHORIZED_TRANSFORMATION = "Authorized Transformation"
    INFERRED_EXTENSION = "Inferred Extension"
    UNRESOLVED_GAP = "Unresolved Gap"
    SUSPICIOUS_DRIFT = "Suspicious Drift"
    CRITICAL_DISTORTION = "Critical Distortion"


PRIMARY_LABEL_VALUES = frozenset(member.value for member in RdeLabel)


class Criticality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


KNOWN_RISK_FLAGS = {
    "claim_strength_inflation",
    "uncertainty_loss",
    "responsibility_shift",
    "value_simplification",
    "institutional_implication_loss",
    "context_drift",
    "theoretical_reduction",
}


def _validate_risk_flags(flags: list[str]) -> None:
    unknown = sorted({str(f) for f in flags if str(f) not in KNOWN_RISK_FLAGS})
    if unknown:
        raise ValueError(f"Unknown risk_flags: {', '.join(unknown)}")


def _normalize_human_annotation(raw: Any) -> str | None:
    if raw is None:
        return None
    label = str(raw).strip()
    if not label:
        return None
    if label not in PRIMARY_LABEL_VALUES:
        raise ValueError(
            f"Invalid human_annotation {raw!r}; expected one of {sorted(PRIMARY_LABEL_VALUES)}"
        )
    return label


def _assert_json_compatible(value: Any, *, field_name: str) -> None:
    """Reject types that JSON cannot represent (Milestone 1 baseline placeholder guard)."""

    if value is None or isinstance(value, (bool, int, float, str)):
        return
    if isinstance(value, list):
        for item in value:
            _assert_json_compatible(item, field_name=field_name)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{field_name} object keys must be strings")
            _assert_json_compatible(item, field_name=field_name)
        return
    raise ValueError(f"{field_name} must be JSON-compatible; got {type(value).__name__}")


@dataclass(frozen=True)
class RdeSample:
    id: str
    task: str
    risk_context: str
    source: str
    output: str
    human_annotation: str | None = None
    risk_flags: list[str] = field(default_factory=list)
    criticality: str | None = None
    explanation: str | None = None
    task_intent: str | None = None
    reconstructed_task_intent: str | None = None
    task_intent_notes: str | None = None
    notes: str | None = None
    baseline_scores: Any | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RdeSample:
        required = ["id", "task", "risk_context", "source", "output"]
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ValueError(f"Missing required sample fields: {', '.join(missing)}")

        risk_flags = [str(f) for f in (data.get("risk_flags") or [])]
        _validate_risk_flags(risk_flags)
        human_annotation = _normalize_human_annotation(data.get("human_annotation"))

        baseline_raw = data.get("baseline_scores")
        if baseline_raw is not None:
            _assert_json_compatible(baseline_raw, field_name="baseline_scores")

        return cls(
            id=str(data["id"]),
            task=str(data["task"]),
            risk_context=str(data["risk_context"]),
            source=str(data["source"]),
            output=str(data["output"]),
            human_annotation=human_annotation,
            risk_flags=risk_flags,
            criticality=data.get("criticality"),
            explanation=data.get("explanation"),
            task_intent=data.get("task_intent"),
            reconstructed_task_intent=data.get("reconstructed_task_intent"),
            task_intent_notes=data.get("task_intent_notes"),
            notes=data.get("notes"),
            baseline_scores=baseline_raw,
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "task": self.task,
            "risk_context": self.risk_context,
            "source": self.source,
            "output": self.output,
            "human_annotation": self.human_annotation,
            "risk_flags": self.risk_flags,
            "criticality": self.criticality,
            "explanation": self.explanation,
            "task_intent": self.task_intent,
            "reconstructed_task_intent": self.reconstructed_task_intent,
            "task_intent_notes": self.task_intent_notes,
            "notes": self.notes,
        }
        if self.baseline_scores is not None:
            result["baseline_scores"] = self.baseline_scores
        return result


@dataclass(frozen=True)
class EvaluationResult:
    id: str
    primary_label: RdeLabel
    risk_flags: list[str]
    criticality: Criticality
    explanation: str
    expected_label: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "primary_label": self.primary_label.value,
            "risk_flags": self.risk_flags,
            "criticality": self.criticality.value,
            "explanation": self.explanation,
            "expected_label": self.expected_label,
            "matches_expected": self.matches_expected,
        }

    @property
    def matches_expected(self) -> bool | None:
        if self.expected_label is None:
            return None
        return self.primary_label.value == self.expected_label
