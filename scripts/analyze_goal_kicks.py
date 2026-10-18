"""保存済みのイベントデータからゴールキックの判定結果をCSVに保存する。"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from modules.goal_kicks import analyze_events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/events_2_27.pkl"))
    parser.add_argument("--output", type=Path, default=Path("results/result.csv"))
    parser.add_argument("--threshold", type=float, default=2.0)
    args = parser.parse_args()
    # 既存データだけを使い、不在時に意図せず再ダウンロードしない。
    if not args.input.is_file():
        parser.error("入力がありません。uv run python scripts/fetch_events.py で取得してください")
    results = analyze_events(pd.read_pickle(args.input), args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)
    print(f"保存: {args.output} ({len(results)}件)")
    print(results.groupby(["result", "reason"]).size().to_string())


if __name__ == "__main__":
    main()
