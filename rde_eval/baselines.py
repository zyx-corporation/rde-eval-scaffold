"""Milestone 3 baseline helpers (deterministic, dependency-free)."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any

M3_LEXICAL_METHOD = "difflib.SequenceMatcher"
M3_SCHEMA_VERSION = "1"


def lexical_sequence_ratio(source: str, output: str) -> float:
    """Return ``SequenceMatcher`` ratio in ``[0.0, 1.0]`` for ``source`` vs ``output``."""

    return float(SequenceMatcher(a=source, b=output).ratio())


def milestone3_lexical_scores(source: str, output: str) -> dict[str, Any]:
    """Structured lexical baseline subtree for ``baseline_scores["m3"]["lexical"]``."""

    return {
        "sequence_ratio": lexical_sequence_ratio(source, output),
        "method": M3_LEXICAL_METHOD,
    }


def merge_milestone3_baseline(
    existing_baseline_scores: Any, *, source: str, output: str
) -> dict[str, Any]:
    """Return new ``baseline_scores`` dict with ``m3.version`` / ``m3.lexical`` merged in."""

    base: dict[str, Any]
    if isinstance(existing_baseline_scores, dict):
        base = dict(existing_baseline_scores)
    else:
        base = {}

    m3: dict[str, Any]
    if isinstance(base.get("m3"), dict):
        m3 = dict(base["m3"])
    else:
        m3 = {}

    m3["version"] = M3_SCHEMA_VERSION
    m3["lexical"] = milestone3_lexical_scores(source, output)
    base["m3"] = m3
    return base
