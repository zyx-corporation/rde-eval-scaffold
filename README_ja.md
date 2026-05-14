# rde-eval-scaffold

Resonant Deviation Evaluator（RDE）フレームワークを評価するための実験用スキャフォールドです。

RDEは、source context と generated output の間で生じる意味変化を監査するための枠組みです。このリポジトリはRDEの本番実装ではありません。source-output pairの構築、RDEラベルの付与、baseline evaluatorとの比較、meaning driftの分析を行うための最小限の実験パイプラインを提供します。

## 目的

- RDEのための小さく再現可能な評価スキャフォールドを提供する。
- 要約、リライト、仕様書変換に関するpilot studyを支援する。
- 意味変化を、structured labels、risk flags、criticality、task intent notes、explanationsとして表現する。
- semantic similarity、natural language inference、factuality evaluation、generic LLM-as-a-judgeなどのbaseline手法と、RDE形式の判断を比較できるようにする。

## 対象外

- 本リポジトリは本番用のRDE engineではない。
- safety filter、policy filter、factuality evaluatorを置き換えるものではない。
- RDEが大規模に検証済みであるとは主張しない。
- 現時点ではOpenAyane、Kotonoha、SLS、vector DB、UI統合は含まない。

## 実行環境

本リポジトリは Python 3.12 以上を対象とします。
