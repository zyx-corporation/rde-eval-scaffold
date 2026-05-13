# Repository Operation Rules

このリポジトリは、Kotonoha系のIssue駆動ワークフローに従います。

## 基本原則

- 実質的な作業はGitHub Issueから開始する。
- Issueごとに作業ブランチを作成する。
- `main` へ直接commitしない。
- Pull Requestは明示的な指示がある場合のみ作成する。
- mergeは明示的な指示がある場合のみ実施する。
- IssuesとPRは、単なるタスク管理ではなく「意味変化の履歴」として扱う。

## ブランチ命名

以下の形式を推奨する。

```text
<type>/issue-<number>-<short-description>
```

推奨される `type`:

| type | 用途 |
|---|---|
| `docs` | ドキュメント作業 |
| `spec` | schema、interface、specification |
| `research` | 研究メモ、理論検討 |
| `process` | repository運用・管理 |
| `fix` | typoや小修正 |
| `refactor` | 振る舞いを変えない構造整理 |
| `experiment` | pilot studyや実験 |
| `schema` | dataset schemaやannotation schemaの変更 |

## PR本文チェック項目

PRを作成する場合、以下を含める。

- 関連Issue
- 変更概要
- 変更理由
- 影響範囲
- 確認手順
- 未解決事項
- RDE Review:
  - preserved elements
  - transformed elements
  - inferred or added elements
  - unresolved elements
  - drift risks

## Truth Order

1. Issue / PR body and comments
2. default branchへmergeされたcommit
3. Project fields（使用する場合）
4. labels

## 現在の制約

このリポジトリでは、PR作成およびmergeは、明示的な指示がある場合のみ実施する。
