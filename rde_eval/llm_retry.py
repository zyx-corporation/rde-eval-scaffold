"""Retry and pacing helpers for live LLM API calls."""

from __future__ import annotations

import time
from collections.abc import Callable

from rde_eval.llm_client import LlmApiError, chat_completion

_RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def is_retryable_llm_error(exc: LlmApiError) -> bool:
    """Return True when *exc* looks like a transient API or network failure."""
    if exc.status_code is not None:
        return exc.status_code in _RETRYABLE_STATUS_CODES
    message = str(exc).lower()
    return message.startswith("network error:")


def retry_delay_seconds(
    exc: LlmApiError,
    *,
    attempt: int,
    backoff_sec: float,
) -> float:
    """Compute sleep duration before the next retry attempt."""
    if exc.retry_after_sec is not None and exc.retry_after_sec >= 0:
        return exc.retry_after_sec
    if attempt < 0:
        return backoff_sec
    return backoff_sec * (2**attempt)


def chat_completion_with_retry(
    messages: list[dict[str, str]],
    *,
    model: str,
    api_key: str,
    base_url: str = "https://api.openai.com/v1",
    timeout_sec: float = 120.0,
    temperature: float = 0.0,
    max_retries: int = 3,
    retry_backoff_sec: float = 1.0,
    sleep: Callable[[float], None] = time.sleep,
) -> str:
    """Call :func:`chat_completion` with finite retries on transient errors."""
    if max_retries < 0:
        raise ValueError("max_retries must be >= 0")
    if retry_backoff_sec < 0:
        raise ValueError("retry_backoff_sec must be >= 0")

    last_exc: LlmApiError | None = None
    for attempt in range(max_retries + 1):
        try:
            return chat_completion(
                messages,
                model=model,
                api_key=api_key,
                base_url=base_url,
                timeout_sec=timeout_sec,
                temperature=temperature,
            )
        except LlmApiError as exc:
            last_exc = exc
            if attempt >= max_retries or not is_retryable_llm_error(exc):
                raise
            sleep(retry_delay_seconds(exc, attempt=attempt, backoff_sec=retry_backoff_sec))

    assert last_exc is not None
    raise last_exc
