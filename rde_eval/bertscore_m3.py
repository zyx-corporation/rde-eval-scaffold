"""Optional BERTScore baselines (requires ``pip install -e '.[baseline]'``)."""

from __future__ import annotations

from typing import Any


def compute_bertscore_batch(
    sources: list[str],
    outputs: list[str],
    *,
    lang: str = "en",
) -> list[dict[str, Any]]:
    """Return one JSON-serializable dict per row (precision, recall, f1).

    ``sources`` and ``outputs`` must be the same length. Uses the ``bert_score``
    library (candidate = ``output``, reference = ``source``).
    """

    if len(sources) != len(outputs):
        raise ValueError("sources and outputs must have the same length")

    try:
        from bert_score import score as bert_score
    except ImportError as exc:
        raise ImportError(
            "The 'bert-score' package is required. "
            "Install with: python -m pip install -e '.[baseline]'"
        ) from exc

    if not sources:
        return []

    precision_t, recall_t, f1_t = bert_score(outputs, sources, lang=lang)

    return [
        {
            "precision": float(precision_t[i].item()),
            "recall": float(recall_t[i].item()),
            "f1": float(f1_t[i].item()),
            "lang": lang,
            "method": "bert-score",
        }
        for i in range(len(sources))
    ]
