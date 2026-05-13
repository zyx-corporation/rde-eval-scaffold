# RDE Annotation Guide

This guide defines how to annotate source-output pairs for RDE pilot studies.

## Annotation Unit

Each unit consists of:

- `source`: original text or context
- `task`: intended transformation
- `risk_context`: domain or risk setting
- `output`: generated text

Annotators should judge the output relative to the source, task, and risk context.

## Primary Labels

| Label | Use when |
|---|---|
| Preserved | Core intent, claim strength, uncertainty, and responsibility structure are preserved. |
| Authorized Transformation | The output changes the source, but the change is justified by the task and does not damage critical meaning. |
| Inferred Extension | The output adds content plausibly inferred from the source but not explicitly stated. |
| Unresolved Gap | The output leaves an important meaning difference unaddressed or cannot be confidently classified. |
| Suspicious Drift | The output changes claim strength, uncertainty, responsibility, value structure, or institutional implication in a potentially harmful way. |
| Critical Distortion | The output substantially reverses, erases, or destroys the source meaning, responsibility structure, or institutional implication. |

## Risk Flags

| Risk Flag | Meaning |
|---|---|
| claim_strength_inflation | A weak, conditional, or hypothetical claim becomes stronger or categorical. |
| uncertainty_loss | Uncertainty, limitations, conditions, or caveats are removed. |
| responsibility_shift | Responsibility moves from human, organization, or institution to AI or another actor. |
| value_simplification | Multiple values or conflicts are reduced to a single value or conclusion. |
| institutional_implication_loss | Legal, organizational, operational, or governance implications disappear. |
| context_drift | The output shifts into a different context from the source. |
| theoretical_reduction | A theoretical claim is reduced to a merely technical or operational statement. |

## Decision Procedure

1. Identify the task.
2. Compare claim strength.
3. Check uncertainty preservation.
4. Check responsibility structure.
5. Check value structure.
6. Check institutional implications.
7. Assign one primary label and any relevant risk flags.
8. Write a short explanation.

## Boundary Rules

Use `Suspicious Drift` when the output may be usable after review or revision but shows a meaningful risk.

Use `Critical Distortion` when the output should not be used as-is because it reverses, erases, or materially damages the source meaning.

Use `Inferred Extension` only when the addition is plausibly supported by the source. If the addition is not supported and changes the conclusion, use `Suspicious Drift` or `Critical Distortion`.

Use `Unresolved Gap` when the annotator cannot confidently decide, or when the output omits an issue that must be reviewed but does not clearly distort it.
