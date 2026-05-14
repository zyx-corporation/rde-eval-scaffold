# テスト方針

本リポジトリは、RDE実験用スキャフォールド向けに調整された Kotonoha-style テスト方針に従います。

## 目的

テストの目的は以下です。

- deterministic scaffold の挙動維持
- schema compatibility の維持
- reproducibility の維持
- 実装挙動における意味ドリフトの検出
- repository state と milestone scope の乖離防止

本テスト方針は、RDEの実証的妥当性を主張するものではありません。

## 対象

現在の対象:

- Python 3.12+
- pytest
- Ruff
- GitHub Actions CI

Milestone 1 では semantic intelligence ではなく deterministic scaffold behavior を重視します。

## TDD 方針

本リポジトリは軽量な TDD（Test-Driven Development）方針を採用します。

推奨フロー:

1. expected behavior を定義
2. テストを追加または更新
3. 実装を追加または変更
4. deterministic reproducibility を確認
5. 挙動変更時は documentation を更新

behavior-changing implementation work は、原則として同一 Issue または PR 内で tests を伴うべきです。

## 例外

以下では TDD は必須ではありません。

- documentation-only changes
- repository management tasks
- exploratory research notes
- issue decomposition 中の temporary scaffolding
- non-production と明示された experimental spikes

tests を後回しにする場合は、PR または Issue に以下を記載します。

- tests deferred の理由
- 将来の expected test coverage
- unresolved risks

## テスト層

### 1. Schema Validation Tests

検証対象:

- required fields
- optional fields
- `baseline_scores` placeholder behavior
- `risk_flags` validation
- `human_annotation` normalization
- JSON-compatible serialization

### 2. Deterministic Classifier Tests

検証対象:

- deterministic heuristic behavior
- reproducible risk-flag generation
- stable primary label mapping
- deterministic `context_drift` behavior

### 3. Evaluator and Pipeline Tests

検証対象:

- JSONL loading
- invalid JSON handling
- invalid schema handling
- deterministic JSONL output
- stable serialization ordering
- round-trip evaluation behavior

### 4. Export Tests

検証対象:

- CSV export correctness
- output field consistency
- `EvaluationResult.to_dict()` との整合

## CI 方針

GitHub Actions CI は以下を実行します。

```bash
ruff check .
ruff format --check .
pytest
```

CI は Python 3.12 のみを対象とします。

## Drift-Control Review

主要 PR には以下を含めるべきです。

- preserved elements
- transformed elements
- inferred or added elements
- unresolved elements
- drift risks

## 非目標

現時点では以下は対象外です。

- semantic correctness の証明
- RDE の実証的検証
- intelligence measurement
- LLM reasoning benchmark
- prompt-based evaluator validation
- human annotation review の代替
