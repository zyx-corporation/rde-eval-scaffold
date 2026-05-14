"""Experimental scaffold for Resonant Deviation Evaluator pilot studies."""

from rde_eval.classifier import classify_sample
from rde_eval.evaluator import evaluate_samples
from rde_eval.schema import EvaluationResult, HumanAnnotationRecord, RdeLabel, RdeSample

__all__ = [
    "EvaluationResult",
    "HumanAnnotationRecord",
    "RdeLabel",
    "RdeSample",
    "classify_sample",
    "evaluate_samples",
]
