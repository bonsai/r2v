# 実験プロトコル：KaggleでのR2V評価

## ゴール

研究仮説を検証できる実証データを作る。Kaggleを使う場合も、Notebookを実行したこと自体を成果とはせず、再現可能なログと評価結果を成果物とする。

## 実験単位

一つの task_id は「参照画像・短い動作／ショット仕様・モデル条件・生成結果・評価」をまとめた単位とする。

## 先に決めること

- 研究質問と一次評価指標
- 課題ショットの採用基準とライセンス
- ベースラインモデルと実行可能性
- 条件ごとの試行回数と停止条件
- JEVと人間の評価手順
- 計算時間・GPU使用量・コストの記録方法

## 実行ステップ

1. **Environment smoke test:** 依存関係、GPU、VRAM、推論時間、モデル利用規約を確認する。
2. **Dataset audit:** 出典、ライセンス、ファイル整合性、重複、データ漏洩を確認する。
3. **Baseline:** 最小課題セットで生成し、失敗も含めて記録する。
4. **Structured specification:** YAMLだけを追加し、仕様再現性を確認する。
5. **Pose control:** 棒人間／ポーズ条件を追加する。
6. **LoRA ablation:** LoRAの有無を比較する。
7. **Adapter ablation:** 制御アダプターの有無を比較する。
8. **Evaluation loop:** JEVの判定と修正ループを追加し、人間レビューと照合する。
9. **TPS gates:** 工程ゲート導入前後の手戻り・待ち時間・合格率を比較する。
10. **Aggregation:** 生ログからテーブルと図を再生成し、論文のResultsへ渡す。

## 再現性ルール

- コード、Notebook、YAML、モデルID、依存関係、データ版を記録する。
- seedを使える場合は記録し、seedを固定しても完全な決定性が保証されるとは限らないことを明記する。
- 失敗、タイムアウト、メモリ不足も記録する。
- 結果を見てから都合よく課題を削除しない。
- 一次指標と分析方法を先に決め、探索的分析は探索的と明記する。
- ベースラインと追加要素以外の条件を可能な範囲で揃える。

## Notebook構成

- `00_environment_check.ipynb`
- `01_dataset_audit.ipynb`
- `02_baseline.ipynb`
- `03_yaml_reproducibility.ipynb`
- `04_pose_control.ipynb`
- `05_lora_ablation.ipynb`
- `06_adapter_ablation.ipynb`
- `07_jev_human_eval.ipynb`
- `08_tps_metrics.ipynb`
- `09_results_aggregation.ipynb`

## 停止条件

最初のsmoke testで、モデルの利用条件・計算資源・推論時間が実験の目的に合わない場合は、無理に全実験を走らせず別モデル／別データへ切り替える。計算資源の消費量ではなく、研究質問に答える情報を優先する。
