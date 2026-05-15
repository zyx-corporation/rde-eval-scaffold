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
    existing_baseline_scores: Any,
    *,
    source: str,
    output: str,
    bertscore: dict[str, Any] | None = None,
    nli: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge milestone-3 metrics under ``baseline_scores["m3"]``.

    Populate **lexical** every time. Set **bertscore** / **nli** when arguments are passed;
    omitted arguments leave existing sibling keys untouched.

    ``m3.version`` is ``\"3\"`` if ``nli`` is recorded, ``\"2\"`` if only BERTScore (no NLI),
    ``\"1\"`` if lexical only.
    """

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

    m3["lexical"] = milestone3_lexical_scores(source, output)
    if bertscore is not None:
        m3["bertscore"] = bertscore
    if nli is not None:
        m3["nli"] = nli

    if "nli" in m3:
        m3["version"] = "3"
    elif "bertscore" in m3:
        m3["version"] = "2"
    else:
        m3["version"] = M3_SCHEMA_VERSION

    base["m3"] = m3
    return base
