"""判定結果から着地点件数と最終位置の条件付き確率を集計する。"""

import numpy as np
import pandas as pd

from modules.generate_grid_map import location_to_grid


def aggregate_results(results: pd.DataFrame) -> dict:
    # CSVのIDを信用して範囲外座標を押し込まないよう、座標から再計算する。
    landing = results.apply(lambda r: location_to_grid([r.landing_x, r.landing_y]), axis=1)
    final = results.apply(lambda r: location_to_grid([r.final_x, r.final_y]), axis=1)
    counts = np.zeros(30, dtype=int)
    transitions = np.zeros((30, 30), dtype=int)
    excluded = np.zeros(30, dtype=int)
    missing = np.zeros(30, dtype=int)
    for i in range(len(results)):
        if pd.isna(landing.iloc[i]):
            continue
        g = int(landing.iloc[i])
        counts[g] += 1
        if results.iloc[i].result == "除外":
            excluded[g] += 1
        elif pd.isna(final.iloc[i]):
            missing[g] += 1
        else:
            transitions[g, int(final.iloc[i])] += 1
    # 分母が0の行はNaNとし、確率0と区別する。
    totals = transitions.sum(axis=1)
    probabilities = np.full((30, 30), np.nan)
    np.divide(transitions * 100, totals[:, None], out=probabilities,
              where=totals[:, None] > 0)
    return dict(counts=counts, transitions=transitions, probabilities=probabilities,
                totals=totals, excluded=excluded, missing=missing,
                missing_landing=int(landing.isna().sum()))
