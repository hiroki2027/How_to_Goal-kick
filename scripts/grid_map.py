"""
StatsBomb オープンデータから GK のゴールキック到達地点を取得し、
縦型のサッカーコートにグリッド（ヒートマップ）でプロットするスクリプト

対象: プレミアリーグ 2015/16 シーズン（全380試合）

必要ライブラリ:
    uv add statsbombpy mplsoccer matplotlib pandas

実行（リポジトリの直下で）:
    uv run python scripts/grid_map.py
"""

import os
import warnings

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import VerticalPitch
from statsbombpy import sb
from statsbombpy.api_client import NoAuthWarning

# StatsBomb の「認証なし（オープンデータのみ）」のお知らせだけ非表示
warnings.filterwarnings("ignore", category=NoAuthWarning)

# ---------------------------------------------------------------
# 1. 大会・シーズンを選ぶ
# ---------------------------------------------------------------
COMPETITION_ID = 2  # Premier League
SEASON_ID = 27  # 2015/2016
TEAM = None  # 例: "Leicester City"。None なら全チーム

# 取得したイベントを保存するファイル（2回目以降はここから読み込む）
CACHE_FILE = f"data/events_{COMPETITION_ID}_{SEASON_ID}.pkl"

# ---------------------------------------------------------------
# 2. 試合一覧 → 全試合のイベントを取得（キャッシュあり）
# ---------------------------------------------------------------
if os.path.exists(CACHE_FILE):
    print(f"キャッシュから読み込み: {CACHE_FILE}")
    events = pd.read_pickle(CACHE_FILE)
else:
    matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID)
    events_list = []
    for i, match_id in enumerate(matches.match_id, start=1):
        print(f"\r取得中... {i}/{len(matches)} 試合", end="", flush=True)
        events_list.append(sb.events(match_id=match_id))
    print()
    events = pd.concat(events_list, ignore_index=True)
    os.makedirs("data", exist_ok=True)
    events.to_pickle(CACHE_FILE)
    print(f"保存しました: {CACHE_FILE}")

# ---------------------------------------------------------------
# 3. ゴールキックを抽出
#    type == "Pass" かつ pass_type == "Goal Kick"
# ---------------------------------------------------------------
gk = events[(events["type"] == "Pass") & (events["pass_type"] == "Goal Kick")].copy()
if TEAM:
    gk = gk[gk["team"] == TEAM]

# 到達地点 (pass_end_location = [x, y]) を分解
gk[["end_x", "end_y"]] = pd.DataFrame(gk["pass_end_location"].tolist(), index=gk.index)
# 成功/失敗 (pass_outcome が NaN なら成功)
gk["success"] = gk["pass_outcome"].isna()

print(f"ゴールキック数: {len(gk)}  成功率: {gk['success'].mean():.1%}")

# ---------------------------------------------------------------
# 4. チーム別に縦型ピッチを並べてグリッドでプロット（4 x 5 = 20チーム）
#    成功と失敗で別々の図にする
#    StatsBomb 座標系: 120 x 80。縦型では下から上へ攻撃
# ---------------------------------------------------------------
teams = sorted(gk["team"].unique())

pitch = VerticalPitch(
    pitch_type="statsbomb", line_zorder=2, pitch_color="#22312b", line_color="white"
)

# (成功かどうか, タイトル用の表記, カラーマップ, 保存ファイル名)
plots = [
    (True, "Successful", "Blues", "figures/goal_kick_grid_by_team_success.png"),
    (False, "Failed", "Reds", "figures/goal_kick_grid_by_team_fail.png"),
]

os.makedirs("figures", exist_ok=True)

for success, label, cmap, filename in plots:
    fig, axs = pitch.draw(nrows=4, ncols=5, figsize=(20, 26))

    for ax, team in zip(axs.flat, teams):
        team_gk = gk[gk["team"] == team]
        plot_gk = team_gk[team_gk["success"] == success]

        # グリッド分割: bins=(縦方向の分割数, 横方向の分割数)
        bin_stat = pitch.bin_statistic(
            plot_gk["end_x"], plot_gk["end_y"], statistic="count", bins=(6, 5)
        )

        # 本数に応じて色の濃さが変わるヒートマップ
        pitch.heatmap(bin_stat, ax=ax, cmap=cmap, edgecolors="#22312b")

        # 各マスに本数を表示
        pitch.label_heatmap(
            bin_stat,
            ax=ax,
            str_format="{:.0f}",
            color="white",
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            exclude_zeros=True,
            path_effects=[pe.withStroke(linewidth=2, foreground="black")],
        )

        # n = このチームの成功(または失敗)の本数 / 全ゴールキック数
        ax.set_title(f"{team} (n={len(plot_gk)}/{len(team_gk)})", fontsize=12)

    fig.suptitle(
        f"Premier League 2015/16 {label} Goal Kick End Locations by Team", fontsize=18
    )
    fig.savefig(filename, dpi=150, bbox_inches="tight")

plt.show()
