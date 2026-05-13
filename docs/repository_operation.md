# Repository Operation Rules

This repository follows the Kotonoha-style issue-driven workflow.

## Principles

- Start substantive work from a GitHub Issue.
- Create a working branch for the Issue.
- Do not commit directly to `main`.
- Open a Pull Request only when explicitly instructed.
- Merge only after explicit instruction.
- Treat Issues and PRs as records of meaning change, not only task tracking.

## Branch Naming

Use the following pattern:

```text
<type>/issue-<number>-<short-description>
```

Recommended `type` values:

| type | Purpose |
|---|---|
| `docs` | documentation work |
| `spec` | schema, interface, or specification work |
| `research` | research notes or theoretical exploration |
| `process` | repository operation or management procedures |
| `fix` | typo, broken link, or minor correction |
| `refactor` | structural cleanup without behavior change |
| `experiment` | pilot or experimental work |

Current initialization branch:

```text
experiment/issue-1-initialize-scaffold
```

## PR Body Checklist

When a PR is eventually opened, include:

- linked Issue
- change summary
- rationale
- affected files and scope
- verification steps
- unresolved points
- RDE review:
  - preserved elements
  - transformed elements
  - inferred or added elements
  - unresolved elements
  - drift risks

## Truth Order

1. Issue / PR body and comments
2. Merged commits on the default branch
3. Project fields, if used
4. Labels

## Current Constraint

This repository may be edited on a working branch, but PR creation and merge must wait for explicit instruction.
