"""Tests for live-mode evaluation helpers in ``run_prompt_eval``."""

from __future__ import annotations

import json

from run_prompt_eval import evaluate_row

from rde_eval.prompt_eval import extract_prompt_input
from rde_eval.prompt_template import PROMPT_VERSION_V1, build_chat_messages


def _prov() -> dict[str, str]:
    return {
        "annotator_type": "llm",
        "annotator_id": "test",
        "model": "gpt-test",
        "prompt_version": PROMPT_VERSION_V1,
        "annotation_run_id": "run-1",
    }


def test_evaluate_row_live_success() -> None:
    row = {
        "id": "p-1",
        "task": "summarization",
        "risk_context": "x",
        "source": "s",
        "output": "o",
    }
    raw = json.dumps(
        {
            "llm_annotation": "Preserved",
            "risk_flags": [],
            "criticality": "low",
            "explanation": "ok",
        }
    )

    def fake_llm(messages: list[dict[str, str]]) -> str:
        assert messages[0]["role"] == "system"
        assert "p-1" in messages[1]["content"]
        return raw

    rec, raw_capture = evaluate_row(
        row,
        mode="live",
        provenance=_prov(),
        raw_stub="",
        raw_by_id={},
        prompt_version=PROMPT_VERSION_V1,
        llm_call=fake_llm,
    )
    assert rec["normalization_status"] == "ok"
    assert rec["llm_annotation"] == "Preserved"
    assert raw_capture == raw


def test_evaluate_row_live_api_error_becomes_failure_record() -> None:
    from rde_eval.llm_client import LlmApiError

    def boom(_messages: list[dict[str, str]]) -> str:
        raise LlmApiError("HTTP 500: server error", status_code=500)

    rec, raw_capture = evaluate_row(
        {"id": "x", "source": "s", "output": "o"},
        mode="live",
        provenance=_prov(),
        raw_stub="",
        raw_by_id={},
        prompt_version=PROMPT_VERSION_V1,
        llm_call=boom,
    )
    assert rec["normalization_status"] == "failed"
    assert rec["error_type"] == "api_error"
    assert raw_capture is None


def test_build_chat_messages_uses_extracted_input() -> None:
    row = extract_prompt_input(
        {
            "id": "z",
            "task": "t",
            "risk_context": "r",
            "source": "en",
            "output": "out",
            "source_ja": "日",
        }
    )
    msgs = build_chat_messages(row, prompt_version=PROMPT_VERSION_V1)
    assert "日" in msgs[1]["content"]
