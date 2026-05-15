"""Tests for ``rde_eval.prompt_template``."""

from __future__ import annotations

import json

import pytest

from rde_eval.prompt_eval import extract_prompt_input
from rde_eval.prompt_template import (
    PROMPT_VERSION_V1,
    build_chat_messages,
    build_user_prompt,
)


def test_build_user_prompt_includes_english_and_japanese() -> None:
    row = extract_prompt_input(
        {
            "id": "p-1",
            "task": "summarization",
            "risk_context": "policy",
            "source": "English source",
            "output": "English output",
            "source_ja": "日本語ソース",
        }
    )
    text = build_user_prompt(row)
    assert "English source" in text
    assert "日本語ソース" in text
    assert "Return the JSON object" in text


def test_build_chat_messages_v1_shape() -> None:
    messages = build_chat_messages({"id": "x", "source": "s", "output": "o"})
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Preserved" in messages[0]["content"]


def test_build_chat_messages_rejects_unknown_version() -> None:
    with pytest.raises(ValueError, match="Unsupported prompt_version"):
        build_chat_messages({}, prompt_version="unknown-v9")


def test_prompt_version_constant_matches_io_contract_example() -> None:
    assert PROMPT_VERSION_V1 == "rde-prompt-eval-v1"


def test_build_user_prompt_serializable_in_messages() -> None:
    messages = build_chat_messages(
        {
            "id": "p",
            "task": "t",
            "risk_context": "r",
            "source": "s",
            "output": "o",
        }
    )
    json.dumps(messages, ensure_ascii=False)
