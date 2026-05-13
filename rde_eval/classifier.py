from __future__ import annotations

from rde_eval.schema import Criticality, EvaluationResult, RdeLabel, RdeSample


UNCERTAINTY_MARKERS = (
    "may",
    "might",
    "could",
    "possibly",
    "possible",
    "possibility",
    "uncertain",
    "unknown",
    "under specific conditions",
    "条件",
    "可能性",
    "不明",
    "未確定",
    "場合",
)

RESPONSIBILITY_MARKERS = (
    "organization",
    "organizational",
    "human",
    "institution",
    "approval",
    "accountability",
    "責任",
    "人間",
    "組織",
    "制度",
    "承認",
)

THEORY_MARKERS = (
    "meaning change",
    "semantic",
    "theoretical",
    "audit",
    "audits",
    "design philosophy",
    "意味変化",
    "意味",
    "監査",
    "設計思想",
)


def classify_sample(sample: RdeSample) -> EvaluationResult:
    """Classify a source-output pair using deterministic pilot heuristics.

    This is intentionally simple. It provides a reproducible baseline for the
    scaffold and should later be replaced or complemented by prompt-based and
    model-based classifiers.
    """

    source = sample.source.lower()
    output = sample.output.lower()
    risk_flags: list[str] = []
    explanation_parts: list[str] = []

    if _has_any(source, UNCERTAINTY_MARKERS) and not _has_any(output, UNCERTAINTY_MARKERS):
        risk_flags.append("uncertainty_loss")
        explanation_parts.append("The output appears to remove uncertainty or caveats.")

    if _has_any(source, ("may", "might", "could", "可能性")) and _has_assertive_form(output):
        risk_flags.append("claim_strength_inflation")
        explanation_parts.append("The output may strengthen a possibility claim into an assertion.")

    if _has_any(source, RESPONSIBILITY_MARKERS) and _mentions_ai_decision(output):
        risk_flags.append("responsibility_shift")
        explanation_parts.append("The output may shift decision responsibility toward AI.")

    if _has_any(source, THEORY_MARKERS) and _looks_operational_only(output):
        risk_flags.append("theoretical_reduction")
        explanation_parts.append("The output may reduce a theoretical claim into an operational statement.")

    if "value" in source and "value" not in output:
        risk_flags.append("value_simplification")
        explanation_parts.append("The output may simplify or omit value conflicts.")

    if "institution" in source and "institution" not in output:
        risk_flags.append("institutional_implication_loss")
        explanation_parts.append("The output may omit institutional implications.")

    primary_label, criticality = _label_from_flags(risk_flags)
    if not explanation_parts:
        explanation_parts.append("No major deterministic RDE risk flag was detected.")

    return EvaluationResult(
        id=sample.id,
        primary_label=primary_label,
        risk_flags=risk_flags,
        criticality=criticality,
        explanation=" ".join(explanation_parts),
        expected_label=sample.human_annotation,
    )


def _label_from_flags(risk_flags: list[str]) -> tuple[RdeLabel, Criticality]:
    if "theoretical_reduction" in risk_flags:
        return RdeLabel.CRITICAL_DISTORTION, Criticality.HIGH
    if "responsibility_shift" in risk_flags and "institutional_implication_loss" in risk_flags:
        return RdeLabel.CRITICAL_DISTORTION, Criticality.HIGH
    if risk_flags:
        return RdeLabel.SUSPICIOUS_DRIFT, Criticality.MEDIUM
    return RdeLabel.PRESERVED, Criticality.LOW


def _has_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker.lower() in text for marker in markers)


def _has_assertive_form(text: str) -> bool:
    return any(marker in text for marker in (" is ", " are ", " does ", " reduces ", "である", "する", "だ"))


def _mentions_ai_decision(text: str) -> bool:
    return "ai" in text and any(marker in text for marker in ("decide", "determine", "judgment", "判断", "決定"))


def _looks_operational_only(text: str) -> bool:
    return any(marker in text for marker in ("log", "history", "save", "store", "保存", "ログ", "履歴")) and not _has_any(
        text, THEORY_MARKERS
    )
