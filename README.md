# How to Goal-kick

ゴールキックをどこに蹴るのが良いかを、着地点ごとのその後の展開（保持／ロスト）から分析するプロジェクトです。

## ドキュメント

- [docs/new.definition.md](docs/new.definition.md)：現時点の分析方針
- [docs/implement_plan.md](docs/implement_plan.md)：実装計画
- [docs/progress.md](docs/progress.md)：進捗と、日付ごとに決まったこと
- [docs/columns.md](docs/columns.md)：データのカラム一覧

## 現在の状況

- 着地点を6×5グリッドに割り当て、保持・ロスト・ダイレクトアウトを判定する。相手の連続保持時間は暫定2秒。
- 保存済みイベントから判定CSVを作成し、全チームをまとめた着地点件数と最終位置の確率をnapariで確認できる。

## スクリプト

`scripts/` にあります。リポジトリの直下で `uv run python scripts/grid_map.py` のように実行します。

- `fetch_events.py`：イベントデータを取得して `data/events_2_27.pkl` に保存する（最初に1回だけ実行）
- `grid_map.py`：チーム別にゴールキックの到達地点をグリッドで描く（図は `figures/` に保存）
- `show_columns.py`：イベントデータのカラム一覧を `outputs/columns.txt` に書き出す
- `show_sequences.py`：ゴールキックの後のイベント列を数件、`outputs/sequences.txt` に書き出す

## napariによる判定結果の確認

既存の `data/events_2_27.pkl` から判定CSVを作成します。データを再取得する必要はありません。

```sh
uv run python scripts/analyze_goal_kicks.py
```

出力先は `results/result.csv` です。`--threshold 2`、`--input`、`--output` で条件とパスを指定できます。
CSVには元イベントID、着地点、結果・判定理由、決着時刻、記録位置とその参照元イベントIDを保存します。
時間判定のロスト位置は、相手の連続保持開始直前の自チームのアクションの終点です。判定した相手タッチの位置とは区別します。

判定結果CSVの `landing_x`, `landing_y`, `final_x`, `final_y`, `result` を使って表示します。
`result` が「除外」の行と最終位置が欠損・範囲外の行は、右側の確率の分母から除きます。

```sh
uv run python scripts/view_goal_kicks.py --input results/result.csv
```

左側は着地点の件数です。グリッドをクリックすると、右側にその着地点からの最終位置の確率を表示します。
右側は白から赤の固定尺度で、0%が白、50%以上が赤（1.0）になります。各マスの数値は実際の確率（%）です。
グリッドIDは `x方向の番号 × 5 + y方向の番号`（0始まり）です。攻撃方向は下から上で、ID 0は左下です。
選択したグリッドの総件数・確率の分母・除外・位置欠損の件数は画面下部で確認できます。

判定・集計・グリッドの検証には `uv run python -m unittest discover -s tests -v` を使います。

## Data & Papers

データファイル（`data/`）と論文PDF（`papers/`）はGit管理対象外です。

### データ
[StatsBomb Open Data](https://github.com/statsbomb/open-data) を使用します。
最初に1回、次のコマンドでイベントデータを取得してください（`data/events_2_27.pkl` が作られます。全380試合ぶんで約1.5GBあり、取得には時間がかかります）。

```
uv run python scripts/fetch_events.py
```


`papers/` フォルダを作成し、PDFを配置してください。
