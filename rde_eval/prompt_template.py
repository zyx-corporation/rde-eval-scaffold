"""Milestone 2 prompt template v1 (text only; no API client).

Aligned with ``docs/prompt_evaluator_io_contract.md`` and ``docs/annotation_guide.md``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

PROMPT_VERSION_V1 = "rde-prompt-eval-v1"

SYSTEM_PROMPT_V1 = (
    "You are an RDE (Resonant Deviation Evaluator) annotation assistant.\n\n"
    "Judge the generated output relative to the source, task, and risk context.\n"
    "Assign exactly one primary label, zero or more risk flags, and a criticality level.\n\n"
    "Respond with a single JSON object only (no markdown fences, no commentary).\n"
    "Required keys:\n"
    "- llm_annotation (string): one of Preserved, Authorized Transformation, "
    "Inferred Extension, Unresolved Gap, Suspicious Drift, Critical Distortion\n"
    "- risk_flags (array of strings): subset of claim_strength_inflation, "
    "uncertainty_loss, responsibility_shift, value_simplification, "
    "institutional_implication_loss, context_drift, theoretical_reduction\n"
    "- criticality (string): low, medium, or high\n"
    "- explanation (string): short rationale in English\n"
    "- explanation_ja (string, optional): short rationale in Japanese\n"
)


def _append_block(lines: list[str], title: str, value: Any) -> None:
    if value is None:
        return
    text = str(value).strip()
    if text:
        lines.append(f"{title}:\n{text}")


def build_user_prompt(prompt_input: Mapping[str, Any]) -> str:
    """Build the user message body from a prompt-input dict (see ``extract_prompt_input``)."""
    lines: list[str] = ["Annotate the following source-output pair."]
    _append_block(lines, "ID", prompt_input.get("id"))
    _append_block(lines, "Task", prompt_input.get("task"))
    _append_block(lines, "Risk context", prompt_input.get("risk_context"))
    _append_block(lines, "Task intent", prompt_input.get("task_intent"))
    _append_block(
        lines,
        "Reconstructed task intent",
        prompt_input.get("reconstructed_task_intent"),
    )
    _append_block(lines, "Task intent notes", prompt_input.get("task_intent_notes"))
    _append_block(lines, "Source (English)", prompt_input.get("source"))
    _append_block(lines, "Output (English)", prompt_input.get("output"))
    _append_block(lines, "Source (Japanese)", prompt_input.get("source_ja"))
    _append_block(lines, "Output (Japanese)", prompt_input.get("output_ja"))
    lines.append("Return the JSON object described in the system instructions.")
    return "\n\n".join(lines)


def build_chat_messages(
    prompt_input: Mapping[str, Any],
    *,
    prompt_version: str = PROMPT_VERSION_V1,
) -> list[dict[str, str]]:
    """OpenAI-style message list for a future live caller."""
    if prompt_version != PROMPT_VERSION_V1:
        raise ValueError(f"Unsupported prompt_version: {prompt_version!r}")
    return [
        {"role": "system", "content": SYSTEM_PROMPT_V1},
        {"role": "user", "content": build_user_prompt(prompt_input)},
    ]


def serialize_chat_messages(messages: list[dict[str, str]]) -> str:
    """Stable JSON string for logging or replay fixtures."""
    return json.dumps(messages, ensure_ascii=False, indent=2)
