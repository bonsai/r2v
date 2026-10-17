# サーベイ管理表：R2V制作システムの費用対効果と構成要素除外

このサーベイの目的は、関連研究を列挙することではなく、比較実験で「どの要素が何に効き、どれが不要か」を決めるための指標・課題セット・実験設計を抽出すること。

## 初期文献

| 分野 | 文献 | 本研究への用途 | 確認すべき限界 |
|---|---|---|---|
| 動画評価 | [VBench (CVPR 2024)](https://openaccess.thecvf.com/content/CVPR2024/html/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.html) | 多次元の品質指標を設計 | 指標が人間の制作上の合格判定を十分に表すか |
| 動画評価 | [EvalCrafter (CVPR 2024)](https://evalcrafter.github.io/) | 評価軸・ベンチマーク設計 | 本研究のR2V課題に適用できるか |
| 人間整合評価 | [Video-Bench (CVPR 2025)](https://mlanthology.org/cvpr/2025/han2025cvpr-videobench/) | 自動評価と人間判断の比較 | 評価者・モデル・課題分布への依存 |
| 顔の一貫性 | [Face Consistency Benchmark (2025)](https://arxiv.org/abs/2505.11425) | キャラクター同一性の測定 | 顔以外の衣装・全身・スタイルをカバーするか |
| Subject-to-Video | [OpenS2V-Nexus (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/dae77d03bd51a5acfe8519848a3af6c9-Abstract-Datasets_and_Benchmarks_Track.html) | 被写体一貫性と評価セット | データ・モデルの利用条件、実験対象との適合 |
| 長尺生成 | [Long-Video Storytelling Survey (ICCV 2025 workshop)](https://research.adobe.com/publication/a-survey-on-long-video-storytelling-generation-architectures-consistency-and-cinematic-quality/) | ショット単位から長尺へ拡張する際の論点 | 短いPoCへの適用範囲 |
| 制御効率 | [ControlNeXt (2024)](https://arxiv.org/abs/2408.06070) | 制御方式と計算効率の比較 | 実験対象モデルとの互換性、再現性 |

## サーベイ抽出項目

各論文から次を記録する。

- 問題設定、研究質問、想定利用者
- モデル、データセット、タスク、ショット長
- 比較ベースライン、アブレーション、試行数
- 品質指標と人間評価の設計
- 推論・学習コスト、GPU時間、再生成・後処理コスト
- 結果の効果量、ばらつき、統計的検定
- 失敗例、限界、再現可能なコード・データの有無
- ライセンス、利用規約、商用利用可否

## 研究ギャップ候補（要検証）

1. 既存評価ベンチマークは生成品質を測るが、制作工程のレビュー工数や採用ショットあたり総費用まで一貫して測っているとは限らない。
2. 制御機構の品質向上だけでなく、追加計算・学習・レビュー費用を含む限界寄与の比較が、本研究の焦点になり得る。
3. JEV型の評価・修正ループを、TPS型ゲートと合わせて工程KPIへ接続する設計を評価する。
4. ただし、これらを「既存研究にない」と主張する前に、体系的な文献検索と引用追跡で先行研究を確認する。

## 構成要素を除外する実験原則

- 主要指標、最小実用効果、除外基準を結果を見る前に決める。
- 1要素ずつ追加する実験と、最良構成から1要素ずつ外す実験を両方行う。
- 品質だけでなく、推論・学習・評価・人間レビューを含む総コストを計測する。
- 効果がないのか、試行数が足りず判断できないのかを分ける。
- 相互作用があり得る要素（例：LoRA×ポーズ制御）は、必要な場合に限り要因実験を追加する。
- 失敗例も報告し、最終評価データを調整に流用しない。
