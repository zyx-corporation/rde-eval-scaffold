"""Tests for ``rde_eval.llm_retry``."""

from __future__ import annotations

from unittest import mock

import pytest

from rde_eval.llm_client import LlmApiError
from rde_eval.llm_retry import (
    chat_completion_with_retry,
    is_retryable_llm_error,
    retry_delay_seconds,
)


def test_is_retryable_for_429_and_5xx() -> None:
    assert is_retryable_llm_error(LlmApiError("x", status_code=429))
    assert is_retryable_llm_error(LlmApiError("x", status_code=503))
    assert not is_retryable_llm_error(LlmApiError("x", status_code=401))


def test_is_retryable_for_network_message() -> None:
    assert is_retryable_llm_error(LlmApiError("Network error: timed out"))


def test_retry_delay_prefers_retry_after_header() -> None:
    assert retry_delay_seconds(
        LlmApiError("x", status_code=429, retry_after_sec=7.5),
        attempt=2,
        backoff_sec=1.0,
    ) == pytest.approx(7.5)


def test_retry_delay_exponential_backoff() -> None:
    assert retry_delay_seconds(
        LlmApiError("x", status_code=500),
        attempt=2,
        backoff_sec=1.0,
    ) == pytest.approx(4.0)


def test_chat_completion_with_retry_succeeds_after_transient_failure() -> None:
    calls = {"n": 0}

    def fake_completion(*_a: object, **_k: object) -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            raise LlmApiError("HTTP 503: busy", status_code=503)
        return '{"llm_annotation":"Preserved"}'

    sleeps: list[float] = []

    with mock.patch("rde_eval.llm_retry.chat_completion", side_effect=fake_completion):
        text = chat_completion_with_retry(
            [{"role": "user", "content": "hi"}],
            model="m",
            api_key="k",
            max_retries=2,
            retry_backoff_sec=0.5,
            sleep=sleeps.append,
        )
    assert "Preserved" in text
    assert calls["n"] == 2
    assert len(sleeps) == 1
    assert sleeps[0] == pytest.approx(0.5)


def test_chat_completion_with_retry_raises_after_exhausted_retries() -> None:
    with mock.patch(
        "rde_eval.llm_retry.chat_completion",
        side_effect=LlmApiError("HTTP 500", status_code=500),
    ):
        with pytest.raises(LlmApiError, match="HTTP 500"):
            chat_completion_with_retry(
                [],
                model="m",
                api_key="k",
                max_retries=1,
                retry_backoff_sec=0.0,
                sleep=lambda _s: None,
            )
