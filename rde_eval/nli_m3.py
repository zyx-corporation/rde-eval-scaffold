"""Optional NLI baselines via Hugging Face ``transformers`` (``[baseline-nli]``)."""

from __future__ import annotations

from typing import Any


def _normalize_nli_label(name: str | int) -> str:
    return str(name).strip().lower().replace(" ", "_")


def compute_nli_batch(
    sources: list[str],
    outputs: list[str],
    *,
    model_id: str,
    batch_size: int = 8,
    max_length: int = 512,
) -> list[dict[str, Any]]:
    """Return one dict per pair (premise=`source`, hypothesis=`output`).

    Each dict matches the ``m3.nli`` subtree (see docs/milestone3_baseline_plan.md).
    ``truncated`` is true when the unpadded source–output pair exceeded ``max_length``
    tokens before truncation. Requires ``torch`` and ``transformers``.
    """

    if len(sources) != len(outputs):
        raise ValueError("sources and outputs must have the same length")

    try:
        import torch
        import torch.nn.functional as F
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as exc:
        raise ImportError(
            "transformers and torch are required. "
            "Install with: python -m pip install -e '.[baseline-nli]'"
            " (and a PyTorch wheel for your platform)"
        ) from exc

    if not sources:
        return []

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    model.eval()

    rows: list[dict[str, Any]] = []
    with torch.no_grad():
        for start in range(0, len(sources), batch_size):
            batch_sources = sources[start : start + batch_size]
            batch_outputs = outputs[start : start + batch_size]

            truncated_flags: list[bool] = []
            for s_pair, o_pair in zip(batch_sources, batch_outputs, strict=True):
                enc_no_trunc = tokenizer(
                    s_pair,
                    o_pair,
                    truncation=False,
                    add_special_tokens=True,
                )
                n_ids = len(enc_no_trunc["input_ids"])
                truncated_flags.append(n_ids > max_length)

            encoded = tokenizer(
                batch_sources,
                batch_outputs,
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors="pt",
            )
            logits = model(**encoded).logits
            probs = F.softmax(logits, dim=-1)

            for i in range(probs.shape[0]):
                id2label: dict[int, str] = {}
                raw = dict(model.config.id2label or {})
                for key, text in raw.items():
                    id2label[int(key)] = str(text)
                scores = {}
                for lid in range(probs.shape[1]):
                    lbl = id2label.get(lid, str(lid))
                    scores[_normalize_nli_label(str(lbl))] = float(probs[i, lid].item())

                pred_local = int(probs[i].argmax(dim=-1).item())
                label_key = _normalize_nli_label(str(id2label.get(pred_local, str(pred_local))))

                rows.append(
                    {
                        "method": "transformers-sequence-classification",
                        "model_id": model_id,
                        "premise": "source",
                        "hypothesis": "output",
                        "label": label_key,
                        "scores": scores,
                        "truncated": bool(truncated_flags[i]),
                    }
                )

    return rows
