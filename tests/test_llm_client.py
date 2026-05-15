"""Tests for ``rde_eval.llm_client``."""

from __future__ import annotations

import json
from unittest import mock

import pytest

from rde_eval.llm_client import LlmApiError, chat_completion


def _fake_response(payload: dict) -> mock.MagicMock:
    body = json.dumps(payload).encode("utf-8")
    resp = mock.MagicMock()
    resp.read.return_value = body
    resp.__enter__ = mock.Mock(return_value=resp)
    resp.__exit__ = mock.Mock(return_value=False)
    return resp


def test_chat_completion_returns_assistant_content() -> None:
    payload = {
        "choices": [{"message": {"content": '{"llm_annotation":"Preserved"}'}}],
    }
    with mock.patch(
        "urllib.request.urlopen",
        return_value=_fake_response(payload),
    ) as urlopen:
        text = chat_completion(
            [{"role": "user", "content": "hi"}],
            model="gpt-test",
            api_key="sk-test",
        )
    assert "Preserved" in text
    request = urlopen.call_args[0][0]
    assert request.full_url.endswith("/chat/completions")
    assert request.get_header("Authorization") == "Bearer sk-test"


def test_chat_completion_raises_on_http_error() -> None:
    import urllib.error

    err = urllib.error.HTTPError(
        url="http://x",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=mock.Mock(read=mock.Mock(return_value=b'{"error":"bad key"}')),
    )
    with mock.patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(LlmApiError, match="HTTP 401"):
            chat_completion([{"role": "user", "content": "x"}], model="m", api_key="k")


def test_chat_completion_parses_retry_after_on_429() -> None:
    import urllib.error

    err = urllib.error.HTTPError(
        url="http://x",
        code=429,
        msg="Too Many Requests",
        hdrs={"Retry-After": "2"},
        fp=mock.Mock(read=mock.Mock(return_value=b'{"error":"rate limit"}')),
    )
    with mock.patch("urllib.request.urlopen", side_effect=err):
        with pytest.raises(LlmApiError) as exc_info:
            chat_completion([{"role": "user", "content": "x"}], model="m", api_key="k")
    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after_sec == pytest.approx(2.0)


def test_chat_completion_rejects_empty_api_key() -> None:
    with pytest.raises(LlmApiError, match="API key is empty"):
        chat_completion([], model="m", api_key="  ")
