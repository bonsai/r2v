# AIアニメ映画制作システム

> 生成をお呪いから科学へ、錬金術から工場へ。

棒人間・YAML・JEV・LoRA・MLアダプターを、Reference / Generation / Eval / Production System の4層へ接続する設計資料です。

## ファイル

- [HTML overview](./production-system.html) — 人が読む概要
- [SVG architecture](./production-system.svg) — アーキテクチャ図
- [Mermaid](./production-system.mmd) — フロー図
- [PlantUML](./production-system.puml) — システム構造
- [YAML](./production-system.yaml) — 機械可読な共通モデル

## 仮説

棒人間で動作を明示し、YAMLで制作仕様を固定し、LoRAでキャラクター／画風を専門化し、MLアダプターで制御能力を追加する。生成候補をJEVで根拠付き評価し、その結果を次の生成・修正条件へ戻すことで、品質・再現性・制作効率を改善できる可能性がある。

この主張は検証前の仮説であり、実験によって各要素の寄与を分離して測定する。

## 4層モデル

1. **Reference** — 物語、キャラクター、世界観、棒人間、絵コンテ、YAML仕様を正本として管理する。
2. **Generation** — モデル、LoRA、アダプター、プロンプト、パラメータ、参照版、seed、実行結果を記録して候補を生成する。
3. **Eval / JEV** — 命題・証拠・評価基準・スコア・確信度から、PASS / REVISE / REJECT / NEEDS_HUMAN_REVIEW を判断する。
4. **Production System / TPS-Gate** — 工程ゲートを制御し、合格した素材だけを次工程へ進める。失敗は原因工程へ戻す。

## PoCの比較条件

- A: 通常生成
- B: A + YAML仕様
- C: B + 棒人間／ポーズ制御
- D: C + キャラクターLoRA
- E: D + JEV評価・修正ループ

同じシーンと評価基準を用い、可能な範囲で生成条件を揃える。ポーズ一致、キャラクター一貫性、時間的連続性、初回合格率、手戻り率、合格ショットあたりコストを比較する。JEVは人間による抜き取り評価でも検証する。

## データ原則

- 構造化データを正本（canon/source of truth）とする。
- RAGは検索・取得用であり、正本の代替にしない。
- メディア本体とメタデータを分離する。
- 生成候補・採用素材・却下素材を区別する。
- 判定には根拠、評価基準、モデル／参照バージョンを紐付ける。
- LoRAとMLアダプターは異なる仕組みとして扱い、別々に比較する。


## 研究仮説の全体像

[仮説：Software Factory × R2V × TPS × ML/Kaggle](./hypothesis.md) に、着想、オールスター構成のリスク、要素ごとの役割、段階的PoC、評価指標、反証条件を記録しています。
