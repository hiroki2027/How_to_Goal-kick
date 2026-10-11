"""
ゴールキックを起点としたプレーの流れ（その後のイベント列）を数件表示するスクリプト

ゴールキックを 0 番として、その後の N_EVENTS イベントを味方・相手すべて含めて並べる
結果は画面に表示し、同じ内容を outputs/sequences.txt にも保存する

先に scripts/fetch_events.py を実行して data/events_2_27.pkl を作っておくこと

実行（リポジトリの直下で）:
    uv run python scripts/show_sequences.py
"""

import os

import numpy as np
import pandas as pd

CACHE_FILE = "data/events_2_27.pkl"
OUTPUT_FILE = "outputs/sequences.txt"

# ---------------------------------------------------------------
# 1. 設定
# ---------------------------------------------------------------
N_EVENTS = 20  # ゴールキックの後に表示するイベント数
N_LONG = 3  # ロングのゴールキックを何件表示するか
N_SHORT = 2  # ショートのゴールキックを何件表示するか
LONG_THRESHOLD = 40  # この距離（ヤード）以上をロングとする
SEED = 0  # 乱数の種。変えると別の例が選ばれる
TEAM = None  # 例: "Leicester City"。None なら全チーム

# ---------------------------------------------------------------
# 2. データ読み込み（必要なカラムだけ）→ 試合ごとに発生順に並べる
# ---------------------------------------------------------------
COLUMNS = [
    "match_id",
    "index",
    "minute",
    "second",
    "type",
    "team",
    "player",
    "position",
    "location",
    "possession",
    "possession_team",
    "pass_type",
    "pass_height",
    "pass_length",
    "pass_end_location",
    "pass_outcome",
    "carry_end_location",
    "ball_receipt_outcome",
    "duel_type",
    "duel_outcome",
    "interception_outcome",
    "goalkeeper_type",
    "shot_outcome",
    "out",
    "under_pressure",
]

print(f"キャッシュから読み込み: {CACHE_FILE}")
events = pd.read_pickle(CACHE_FILE)[COLUMNS]
events = events.sort_values(["match_id", "index"]).reset_index(drop=True)

# ---------------------------------------------------------------
# 3. ゴールキックを抽出し、ロング・ショートからランダムに選ぶ
#    type == "Pass" かつ pass_type == "Goal Kick"
# ---------------------------------------------------------------
gk = events[(events["type"] == "Pass") & (events["pass_type"] == "Goal Kick")]
if TEAM:
    gk = gk[gk["team"] == TEAM]

long_gk = gk[gk["pass_length"] >= LONG_THRESHOLD]
short_gk = gk[gk["pass_length"] < LONG_THRESHOLD]

rng = np.random.default_rng(SEED)
picks = list(rng.choice(long_gk.index, min(N_LONG, len(long_gk)), replace=False))
picks += list(rng.choice(short_gk.index, min(N_SHORT, len(short_gk)), replace=False))


# ---------------------------------------------------------------
# 4. 表示用の関数
# ---------------------------------------------------------------
def text(value):
    """NaN なら空文字、それ以外は文字列にする"""
    return "" if pd.isna(value) else str(value)


def coord(location, is_own):
    """座標を「ゴールキックを蹴ったチームの攻撃方向」にそろえて (x,y) の文字列にする

    StatsBomb の座標はイベントを行ったチームの攻撃方向が基準なので、
    相手チームのイベントは 120 - x, 80 - y で反転する
    """
    if not isinstance(location, (list, np.ndarray)):
        return ""
    x, y = location[0], location[1]
    if not is_own:
        x, y = 120 - x, 80 - y
    return f"({x:.0f},{y:.0f})"


def detail(row, is_own):
    """イベントの補足情報（パスの種類・終点・結果など）を 1 つの文字列にまとめる"""
    end = coord(row["pass_end_location"], is_own) or coord(
        row["carry_end_location"], is_own
    )
    parts = [
        text(row["pass_type"]),
        text(row["pass_height"]),
        f"→{end}" if end else "",
        text(row["pass_outcome"]),
        text(row["ball_receipt_outcome"]),
        text(row["duel_type"]),
        text(row["duel_outcome"]),
        text(row["interception_outcome"]),
        text(row["goalkeeper_type"]),
        text(row["shot_outcome"]),
        "OUT" if row["out"] is True else "",
        "圧" if row["under_pressure"] is True else "",
    ]
    return " ".join(p for p in parts if p)


# ---------------------------------------------------------------
# 5. 各ゴールキックについて、その後のイベント列を並べる
#    自 / 敵 はゴールキックを蹴ったチームから見た表記
# ---------------------------------------------------------------
lines = [
    f"ゴールキック数: {len(gk)}  "
    f"(ロング {len(long_gk)} / ショート {len(short_gk)}、境界 {LONG_THRESHOLD} ヤード)",
    "",
    "読み方:",
    "  自 / 敵   : ゴールキックを蹴ったチームから見て、イベントを行ったチーム",
    "  座標      : ゴールキックを蹴ったチームの攻撃方向にそろえてある（x=0 が自陣ゴール）",
    "  pos#      : StatsBomb のポゼッション番号と、その保持チーム",
    "  圧        : under_pressure（相手のプレッシャーを受けている）",
    "  OUT       : そのイベントでボールが外に出た",
]

for n, start in enumerate(picks, start=1):
    kick = events.loc[start]
    own_team = kick["team"]

    # ゴールキック + その後の N_EVENTS イベント（同じ試合の中だけ）
    seq = events.iloc[start : start + N_EVENTS + 1]
    seq = seq[seq["match_id"] == kick["match_id"]]

    lines.append("")
    lines.append(
        f"=== 例{n}: match {kick['match_id']}  "
        f"{kick['minute']}:{kick['second']:02d}  "
        f"{own_team}  距離 {kick['pass_length']:.0f} ヤード ==="
    )

    for k, (_, row) in enumerate(seq.iterrows()):
        is_own = row["team"] == own_team
        side = "自" if is_own else "敵"
        pos_side = "自" if row["possession_team"] == own_team else "敵"
        position = text(row["position"]).replace("Goalkeeper", "GK")
        lines.append(
            f"{k:>2} {row['minute']:>2}:{row['second']:02d} {side} "
            f"{row['type']:<15} {text(row['player'])[:22]:<22} {position[:24]:<24} "
            f"{coord(row['location'], is_own):<9} "
            f"pos#{row['possession']}({pos_side}) {detail(row, is_own)}"
        )

output = "\n".join(lines)
print(output)

os.makedirs("outputs", exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(output + "\n")
print(f"\n保存しました: {OUTPUT_FILE}")
