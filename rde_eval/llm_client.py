"""Minimal OpenAI-compatible chat completions client (stdlib only)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class LlmApiError(Exception):
    """Raised when the chat completions API returns an error or malformed payload."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


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
