"""Minimal OpenAI-compatible chat completions client (stdlib only)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from typing import Any


def _parse_retry_after_header(value: str | None) -> float | None:
    if not value or not value.strip():
        return None
    stripped = value.strip()
    try:
        return max(0.0, float(stripped))
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(stripped)
    except (TypeError, ValueError, OverflowError):
        return None
    return max(0.0, retry_at.timestamp() - time.time())


def _http_error_retry_after(exc: urllib.error.HTTPError) -> float | None:
    headers = exc.headers
    if headers is None:
        return None
    raw = headers.get("Retry-After")
    return _parse_retry_after_header(raw)


class LlmApiError(Exception):
    """Raised when the chat completions API returns an error or malformed payload."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retry_after_sec: float | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after_sec = retry_after_sec


def _parse_assistant_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LlmApiError("API response missing choices")
    first = choices[0]
    if not isinstance(first, dict):
        raise LlmApiError("API response choice is not an object")
    message = first.get("message")
    if not isinstance(message, dict):
        raise LlmApiError("API response missing message")
    content = message.get("content")
    if content is None:
        raise LlmApiError("API response missing message.content")
    return str(content)


def chat_completion(
    messages: list[dict[str, str]],
    *,
    model: str,
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
    timeout_sec: float = 120.0,
    temperature: float = 0.0,
) -> str:
    """POST to ``/chat/completions`` and return assistant message content."""
    if not api_key.strip():
        raise LlmApiError("API key is empty")
    if not model.strip():
        raise LlmApiError("Model name is empty")

    url = f"{base_url.rstrip('/')}/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            raw_bytes = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LlmApiError(
            f"HTTP {exc.code}: {detail[:500]}",
            status_code=exc.code,
            retry_after_sec=_http_error_retry_after(exc),
        ) from exc
    except urllib.error.URLError as exc:
        raise LlmApiError(f"Network error: {exc.reason}") from exc

    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise LlmApiError(f"API response is not JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise LlmApiError("API response root must be a JSON object")
    return _parse_assistant_content(payload)
