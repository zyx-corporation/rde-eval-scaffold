"""Tests for optional BERTScore batch helper (no real ``bert-score`` install required)."""

from __future__ import annotations

import sys
import types

import pytest


def _install_stub_bert_score_module() -> None:
    """Register a minimal fake ``bert_score`` so ``bertscore_m3`` can load."""

    stub = types.ModuleType("bert_score")

    class _T:
        def __init__(self, v: float) -> None:
            self._v = v

        def item(self) -> float:
            return self._v

    def score(outputs: list[str], sources: list[str], lang: str = "en") -> tuple:  # noqa: ARG001
        n = len(sources)
        return (
            [_T(0.1 + i) for i in range(n)],
            [_T(0.2 + i) for i in range(n)],
            [_T(0.3 + i) for i in range(n)],
        )

    stub.score = score
    sys.modules["bert_score"] = stub


def _remove_stub_bert_score_module() -> None:
    sys.modules.pop("bert_score", None)


def test_compute_bertscore_batch_returns_row_dicts() -> None:
    _install_stub_bert_score_module()
    try:
        from rde_eval.bertscore_m3 import compute_bertscore_batch

        out = compute_bertscore_batch(["s"], ["o"], lang="en")
        assert len(out) == 1
        assert out[0]["f1"] == pytest.approx(0.3)
        assert out[0]["method"] == "bert-score"
    finally:
        _remove_stub_bert_score_module()


def test_compute_bertscore_batch_length_mismatch() -> None:
    from rde_eval.bertscore_m3 import compute_bertscore_batch

    with pytest.raises(ValueError, match="same length"):
        compute_bertscore_batch(["a"], ["b", "c"])


def test_compute_bertscore_batch_import_error_message() -> None:
    import importlib.util

    if importlib.util.find_spec("bert_score") is not None:
        pytest.skip("bert-score is installed; ImportError branch is not exercised")

    assert "bert_score" not in sys.modules
    from rde_eval.bertscore_m3 import compute_bertscore_batch

    with pytest.raises(ImportError, match=r"\[baseline\]"):
        compute_bertscore_batch(["x"], ["y"])
