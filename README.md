# How to Goal-kick

ゴールキックをどこに蹴るのが良いかを、着地点ごとのその後の展開（保持／ロスト）から分析するプロジェクトです。

## ドキュメント

- [latest.md](latest.md)：現時点の分析方針（最新版）
- [progress.md](progress.md)：進捗と、日付ごとに決まったこと
- [docs/columns.md](docs/columns.md)：データのカラム一覧

## 現在の状況（10/7 時点）

- ゴールキックが最初に触られた位置を 6×5 のグリッドに割り当て、その後の展開を「保持 / ロスト / シュート / 直接タッチ」に分類して、グリッドごとに比べる。
- 判定は時間ベース（T 秒間保持したチームで決着）。10/4 までのアクション数ベースの方針は廃止した。
- 判定と集計の実装、結果の図の作成はこれから。決まったことと未決事項は [latest.md](latest.md) を参照。

## スクリプト

`scripts/` にあります。リポジトリの直下で `uv run python scripts/grid_map.py` のように実行します。

- `grid_map.py`：イベントデータを取得して `data/events_2_27.pkl` に保存し、チーム別にゴールキックの到達地点をグリッドで描く（図は `figures/` に保存）
- `show_columns.py`：イベントデータのカラム一覧を `outputs/columns.txt` に書き出す
- `show_sequences.py`：ゴールキックの後のイベント列を数件、`outputs/sequences.txt` に書き出す

## Data & Papers

データファイル（`data/`）と論文PDF（`papers/`）はGit管理対象外です。

### データ
[StatsBomb Open Data](https://github.com/statsbomb/open-data) を使用します。
`data/` フォルダを作成し、そこに配置してください。


`papers/` フォルダを作成し、PDFを配置してください。
