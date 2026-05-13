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


@dataclass(frozen=True)
class RdeSample:
    id: str
    task: str
    risk_context: str
    source: str
    output: str
    human_annotation: str | None = None
    risk_flags: list[str] = field(default_factory=list)
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RdeSample":
        required = ["id", "task", "risk_context", "source", "output"]
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise ValueError(f"Missing required sample fields: {', '.join(missing)}")
        return cls(
            id=str(data["id"]),
            task=str(data["task"]),
            risk_context=str(data["risk_context"]),
            source=str(data["source"]),
            output=str(data["output"]),
            human_annotation=data.get("human_annotation"),
            risk_flags=list(data.get("risk_flags") or []),
            notes=data.get("notes"),
        )


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
