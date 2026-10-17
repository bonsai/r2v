# AIアニメ映画制作システム

> 生成をお呪いから科学へ、錬金術から工場へ。

棒人間・YAML・JEV・LoRA・MLアダプターを、Reference / Generation / Eval / Production System の4層へ接続する設計資料です。

## ファイル

- [HTML overview](./production-system.html) — 人が読む概要
- [SVG architecture](./production-system.svg) — アーキテクチャ図
- [Mermaid](./production-system.mmd) — フロー図
- [PlantUML](./production-system.puml) — システム構造
- [YAML](./production-system.yaml) — 機械可読な共通モデル
- [papers.yaml](../../papers.yaml) — 文献カタログ

## 仮説

棒人間で動作を明示し、YAMLで制作仕様を固定し、LoRAでキャラクター／画風を専門化し、MLアダプターで制御能力を追加する。生成候補をJEVで根拠付き評価し、その結果を次の生成・修正条件へ戻すことで、品質・再現性・制作効率を改善できる可能性がある。

この主張は検証前の仮説であり、実験によって各要素の寄与を分離して測定する。全要素を一度に投入しない。

## 4層モデル

1. **Reference** — 物語、キャラクター、世界観、棒人間、絵コンテ、YAML仕様を正本として管理する。
2. **Generation** — モデル、LoRA、アダプター、プロンプト、パラメータ、参照版、seed、実行結果を記録して候補を生成する。
3. **Eval / JEV** — 命題・証拠・評価基準・スコア・確信度から、PASS / REVISE / REJECT / NEEDS_HUMAN_REVIEW を判断する。
4. **Production System / TPS-Gate** — 工程ゲートを制御し、合格した素材だけを次工程へ進める。失敗は原因工程へ戻す。

## 初期PoCは3条件に限定

- **A: Baseline** — 既存R2Vモデルで通常生成。
- **B: Pose control** — Aに棒人間／ポーズ制御を追加。
- **C: JEV loop** — BにJEV評価と修正ループを追加。

YAMLは全条件共通の記録・再現基盤とし、その効果は初期実験で独立に主張しない。LoRA、追加MLアダプター、TPSゲート、Kaggleでの拡張は、初期実験の結果と必要性を確認してから別の実験として追加する。

## 人間とAIの評価を分けて検証

- **自動化候補:** 背景の物体数、色、位置、画面内の有無など、明示可能で比較的機械判定しやすい整合性。
- **人間の確認を必須にする領域:** 顔、手、演技、感情、画風、構図の意図、「惜しいが気持ち悪い」破綻。
- **禁止事項:** JEVのPASSだけで最終採用しない。人間との不一致を記録し、誤PASS率と人間レビューとの一致度を測定する。

## データ原則

- 構造化データを正本（canon/source of truth）とする。
- RAGは検索・取得用であり、正本の代替にしない。
- メディア本体とメタデータを分離する。
- 生成候補・採用素材・却下素材を区別する。
- 判定には根拠、評価基準、モデル／参照バージョンを紐付ける。
- LoRAとMLアダプターは異なる仕組みとして扱い、別々に比較する。

## 研究仮説と論文

- [仮説：Software Factory × R2V × TPS × ML/Kaggle](./hypothesis.md)
- [論文構成案](./paper-outline.md)
- [課題画像・ショット選定と実証データ計画](./dataset-and-evidence-plan.md)
- [Kaggle実験プロトコル](./kaggle-experiment-protocol.md)
- [論文企画書（LaTeX）](./paper-proposal.tex)
- [参考文献データベース（BibTeX）](./references.bib)
- [文献サーベイ・構成要素除外の設計](./survey-and-ablation.md)

## nwman — LAN-only network

- [HTML](./nwman/network.html)
- [SVG](./nwman/network.svg)
- [Mermaid](./nwman/network.mmd)
- [PlantUML](./nwman/network.puml)
- [Topology YAML](./nwman/network.yaml)
- [設計原則・Kubernetes移行方針](./nwman/README.md)
