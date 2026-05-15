"""Tests for ``rde_eval.nli_m3`` (no transformers download in CI)."""

from __future__ import annotations

import importlib.util

import pytest

from rde_eval.nli_m3 import compute_nli_batch


def test_compute_nli_batch_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        compute_nli_batch(["a"], ["b", "c"], model_id="x")


def test_compute_nli_batch_import_error_when_transformers_missing() -> None:
    if importlib.util.find_spec("transformers") is not None:
        pytest.skip("transformers is installed; ImportError branch is not exercised")

    with pytest.raises(ImportError, match=r"\[baseline-nli\]"):
        compute_nli_batch(["x"], ["y"], model_id="facebook/roberta-large-mnli")
