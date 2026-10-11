"""
判定に使う列(goalkeeper_type / goalkeeper_outcome / duel_type / duel_outcome / 50_50)に
実際にどんな値が入っているかを確認するスクリプト

data/events_2_27.pkl を読むだけで、StatsBomb からの取得はしない
(ファイルがない場合は、先に scripts/fetch_events.py を実行する)

実行(リポジトリの直下で):
    uv run python scripts/check_event_values.py
"""

import ast
import sys
from pathlib import Path

import pandas as pd

competition_id = 2  # Premier League
season_id = 27  # 2015/2016

# fetch_events.py が保存したイベントのファイル
events_path = Path(f"data/events_{competition_id}_{season_id}.pkl")

keep_cols = [
    "match_id",
    "type",
    "goalkeeper_type",
    "goalkeeper_outcome",
    "duel_type",
    "duel_outcome",
    "50_50",
]


def load_events() -> pd.DataFrame:
    """保存済みの全試合のイベントから、必要な列だけを取り出して返す。"""
    if not events_path.exists():
        sys.exit(
            f"{events_path} がありません。先に uv run python scripts/fetch_events.py を実行してください"
        )
    events = pd.read_pickle(events_path)
    # 列自体が存在しないことがあるので、欠けた列は NaN で補う
    return events.reindex(columns=keep_cols)


def fifty_fifty_outcome(x):
    """50_50 列(辞書。文字列で入っている場合もある)から outcome の name を取り出す。"""
    if isinstance(x, str):
        try:
            x = ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return f"<parse error: {x}>"
    if isinstance(x, dict):
        return x.get("outcome", {}).get("name")
    return None


def show(title: str, s: pd.Series) -> None:
    print(f"\n=== {title} ===")
    print(s.value_counts(dropna=False).to_string())


def main() -> None:
    df = load_events()

    print("\n=== type ごとの件数(関係する type のみ)===")
    print(
        df["type"]
        .value_counts()
        .reindex(["Goal Keeper", "Duel", "50/50"])
        .fillna(0)
        .astype(int)
        .to_string()
    )

    # --- Goal Keeper ---
    gk = df[df["type"] == "Goal Keeper"]
    show("goalkeeper_type", gk["goalkeeper_type"])
    show("goalkeeper_outcome", gk["goalkeeper_outcome"])
    print("\n=== goalkeeper_type × goalkeeper_outcome ===")
    print(
        pd.crosstab(
            gk["goalkeeper_type"].fillna("NaN"), gk["goalkeeper_outcome"].fillna("NaN")
        ).to_string()
    )

    # --- Duel ---
    duel = df[df["type"] == "Duel"]
    show("duel_type", duel["duel_type"])
    show("duel_outcome", duel["duel_outcome"])
    print("\n=== duel_type × duel_outcome ===")
    print(
        pd.crosstab(
            duel["duel_type"].fillna("NaN"), duel["duel_outcome"].fillna("NaN")
        ).to_string()
    )

    # --- 50/50 ---
    ff = df[df["type"] == "50/50"]
    if ff.empty:
        print("\n=== 50/50 ===\nこのデータには 50/50 イベントがありません")
    else:
        show("50_50 の outcome", ff["50_50"].map(fifty_fifty_outcome))

    # 対象 type 以外の行に値が入っていないかの確認
    print("\n=== 対象 type 以外で値が入っている行数 ===")
    checks = {
        "goalkeeper_type": "Goal Keeper",
        "goalkeeper_outcome": "Goal Keeper",
        "duel_type": "Duel",
        "duel_outcome": "Duel",
        "50_50": "50/50",
    }
    for col, t in checks.items():
        n = (df[col].notna() & (df["type"] != t)).sum()
        print(f"{col:20s}: {n}")


if __name__ == "__main__":
    main()
