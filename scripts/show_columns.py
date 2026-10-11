"""
キャッシュ済みの StatsBomb イベントデータのカラム一覧を outputs/columns.txt に書き出すスクリプト

先に scripts/fetch_events.py を実行して data/events_2_27.pkl を作っておくこと
一度実行すれば、以降は outputs/columns.txt を開くだけでよい

実行（リポジトリの直下で）:
    uv run python scripts/show_columns.py
"""

import os

import pandas as pd

CACHE_FILE = "data/events_2_27.pkl"
OUTPUT_FILE = "outputs/columns.txt"

events = pd.read_pickle(CACHE_FILE)

# 1行に1カラム、アルファベット順
columns = sorted(events.columns.tolist())
os.makedirs("outputs", exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(columns) + "\n")

print(f"保存しました: {OUTPUT_FILE} ({len(columns)} カラム)")
