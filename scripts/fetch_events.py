"""
StatsBomb オープンデータから全試合のイベントを取得し、data/events_2_27.pkl に保存するだけのスクリプト

対象: プレミアリーグ 2015/16 シーズン（全380試合）
すでにファイルがある場合は何もしない（取り直したいときはファイルを消してから実行する）

実行（リポジトリの直下で）:
    uv run python scripts/fetch_events.py
"""

import os
import warnings

import pandas as pd
from statsbombpy import sb
from statsbombpy.api_client import NoAuthWarning

# StatsBomb の「認証なし（オープンデータのみ）」のお知らせだけ非表示
warnings.filterwarnings("ignore", category=NoAuthWarning)

COMPETITION_ID = 2  # Premier League
SEASON_ID = 27  # 2015/2016

# 取得したイベントを保存するファイル
CACHE_FILE = f"data/events_{COMPETITION_ID}_{SEASON_ID}.pkl"

if os.path.exists(CACHE_FILE):
    print(f"すでにあります: {CACHE_FILE}")
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
