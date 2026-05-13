RDE_CLASSIFIER_PROMPT = """
You are evaluating meaning change between a source and an output.

Return JSON with:
- primary_label
- risk_flags
- criticality
- explanation

Labels:
- Preserved
- Authorized Transformation
- Inferred Extension
- Unresolved Gap
- Suspicious Drift
- Critical Distortion

Risk flags:
- claim_strength_inflation
- uncertainty_loss
- responsibility_shift
- value_simplification
- institutional_implication_loss
- context_drift
- theoretical_reduction
""".strip()
