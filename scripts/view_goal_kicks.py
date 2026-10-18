"""CSVからnapariで着地点と最終位置を左右に表示する。"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from modules.heatmaps import aggregate_results


def create_viewer(results, *, show=True):
    import napari
    from napari.utils.colormaps import Colormap
    from qtpy.QtWidgets import QLabel

    stats = aggregate_results(results)
    viewer = napari.Viewer(title="Goal kicks: landing → final position", show=show)
    viewer.window.resize(1400, 900)
    # xを画面の縦軸に写し、攻撃方向を下から上へそろえる。
    def image(values):
        return np.asarray(values, dtype=float).reshape(6, 5)[::-1]

    maximum = max(1, int(stats["counts"].max()))
    viewer.add_image(image(stats["counts"]), name="Landing count",
                     scale=(20, 16), translate=(10, 8), interpolation2d="nearest",
                     colormap="blues", contrast_limits=(0, maximum))
    right = viewer.add_image(np.zeros((6, 5)), name="Final heatmap (1.0 = 50%)",
                             scale=(20, 16), translate=(10, 108),
                             interpolation2d="nearest",
                             colormap=Colormap(["white", "red"], name="white_to_red"),
                             contrast_limits=(0, 1))
    centers = np.array([[110 - (g // 5) * 20, 8 + (g % 5) * 16] for g in range(30)])
    left_labels = [f"{g}\nn={stats['counts'][g]}" for g in range(30)]
    viewer.add_points(centers, size=0, features={"label": left_labels},
                      text={"string": "{label}", "size": 6,
                            "color": ["white" if n > maximum * .5 else "black"
                                      for n in stats["counts"]]},
                      name="Landing IDs and counts")
    labels = viewer.add_points(centers + [0, 100], size=0,
                               features={"label": [""] * 30},
                               text={"string": "{label}", "size": 6, "color": "black"},
                               name="Final IDs, counts and probabilities")
    # 両ピッチの外周・グリッド線を重ねてクリック範囲を明示する。
    lines = []
    for offset in (0, 100):
        lines.extend([[[r, offset], [r, offset + 80]] for r in range(0, 121, 20)])
        lines.extend([[[0, offset + c], [120, offset + c]] for c in range(0, 81, 16)])
    viewer.add_shapes(lines, shape_type="line", edge_color="gray", edge_width=.5,
                      name="Pitch grids")
    selection = viewer.add_shapes(ndim=2, shape_type="rectangle", face_color="transparent",
                                  edge_color="cyan", edge_width=2, name="Selected landing")
    info = QLabel()
    info.setWordWrap(True)
    viewer.window.add_dock_widget(info, name="Counts and legend", area="bottom")

    def select_grid(g):
        values = stats["probabilities"][g]
        # 色尺度を全グリッドで固定し、50%以上は赤にそろえる。
        # データなしは白背景とし、ラベルで確率0%と区別する。
        intensity = np.clip(values / 50.0, 0, 1) if stats["totals"][g] else np.zeros(30)
        right.data = image(intensity)
        right.visible = True
        labels.features = {"label": [f"{i}\nn={stats['transitions'][g, i]}\n{v:.1f}%"
                                         if np.isfinite(v) else f"{i}\nデータなし"
                                         for i, v in enumerate(values)]}
        row, col = centers[g] - [10, 8]
        selection.data = [np.array([[row, col], [row, col + 16],
                                    [row + 20, col + 16], [row + 20, col]])]
        info.setText(f"左: 着地点件数（青: 0〜{maximum}件） ↑ 攻撃方向 | "
                     "右: 固定尺度（白0 = 0% → 赤1.0 = 50%以上）。数値は実際の確率\n"
                     f"選択グリッド {g}: 総件数={stats['counts'][g]}, "
                     f"確率の分母={stats['totals'][g]}, "
                     f"除外={stats['excluded'][g]}, 最終位置欠損・範囲外={stats['missing'][g]} | "
                     f"全体の着地点欠損・範囲外={stats['missing_landing']}"
                     + (" | データなし" if not stats["totals"][g] else ""))

    # レイヤーの選択状態に依存せず、左ピッチをクリックして更新する。
    @viewer.mouse_drag_callbacks.append
    def on_click(_viewer, event):
        if event.button != 1:
            return
        row, col = event.position[-2:]
        if 0 <= row < 120 and 0 <= col < 80:
            select_grid((5 - int(row // 20)) * 5 + int(col // 16))

    # 既定の描画ツールでグリッドや選択枠を書き換えないようにする。
    for layer in viewer.layers:
        layer.mode = "pan_zoom"

    select_grid(int(np.argmax(stats["counts"])))
    viewer.reset_view()
    return viewer, select_grid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="results/result.csv")
    args = parser.parse_args()
    # 集計処理を再実行せず、保存済みのCSVだけを表示に使う。
    create_viewer(pd.read_csv(args.input))
    import napari
    napari.run()


if __name__ == "__main__":
    main()
