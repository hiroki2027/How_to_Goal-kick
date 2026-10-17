"""ゴールキック分析で使う6×5グリッドの生成と座標の割り当て。"""

import math

import pandas as pd


# latest.md の分割粒度に合わせ、120×80のピッチを20×16のマスに分ける。
PITCH_LENGTH = 120
PITCH_WIDTH = 80
X_BINS = 6
Y_BINS = 5
CELL_LENGTH = PITCH_LENGTH / X_BINS
CELL_WIDTH = PITCH_WIDTH / Y_BINS


def generate_grid_map() -> pd.DataFrame:
    """全30マスのID、範囲、中心座標を返す。"""
    # 件数ゼロのマスも集計表に含められるよう、全マスを生成する。
    # IDはx方向を外側、y方向を内側として0〜29を割り当てる。
    cells = []
    for grid_x in range(X_BINS):
        for grid_y in range(Y_BINS):
            cells.append({
                "grid_id": grid_x * Y_BINS + grid_y,
                "grid_x": grid_x,
                "grid_y": grid_y,
                "x_min": grid_x * CELL_LENGTH,
                "x_max": (grid_x + 1) * CELL_LENGTH,
                "y_min": grid_y * CELL_WIDTH,
                "y_max": (grid_y + 1) * CELL_WIDTH,
                "center_x": (grid_x + 0.5) * CELL_LENGTH,
                "center_y": (grid_y + 0.5) * CELL_WIDTH,
            })

    return pd.DataFrame(cells)


def location_to_grid(
    location,
    *,
    opponent: bool = False,
) -> int | None:
    """イベント座標をゴールキックチーム視点のグリッドIDに変換する。

    locationは最初のタッチ位置など、呼び出し側で決めた[x, y]を受け取る。
    相手チーム視点の座標はopponent=Trueで反転する。
    すでに視点をそろえた座標はopponent=Falseのまま渡す。
    """
    # 欠損や不正な座標は割り当てず、呼び出し側で別途件数を記録する。
    try:
        x, y = location
        x, y = float(x), float(y)
    except (TypeError, ValueError, OverflowError):
        return None

    if not (math.isfinite(x) and math.isfinite(y)):
        return None
    if not (0 <= x <= PITCH_LENGTH and 0 <= y <= PITCH_WIDTH):
        return None

    # 相手のイベント座標を、ゴールキックを蹴ったチームの視点にそろえる。
    if opponent:
        x = PITCH_LENGTH - x
        y = PITCH_WIDTH - y

    # 内部境界は次のマスに含め、外周の120・80だけ最終マスに含める。
    # 範囲外を端のマスに押し込まないよう、範囲の検証を先に行う。
    grid_x = min(int(x // CELL_LENGTH), X_BINS - 1)
    grid_y = min(int(y // CELL_WIDTH), Y_BINS - 1)

    return grid_x * Y_BINS + grid_y
