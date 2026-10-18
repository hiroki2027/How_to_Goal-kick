"""欠損・除外と確率の分母、座標境界を検証する。"""

import unittest

import numpy as np
import pandas as pd

from modules.generate_grid_map import location_to_grid
from modules.heatmaps import aggregate_results


class HeatmapTests(unittest.TestCase):
    def test_denominator_and_missing(self):
        # 除外・位置欠損は左の件数に残し、右の分母から除く。
        frame = pd.DataFrame([
            [30, 20, 70, 40, "ロスト"],
            [30, 20, 70, 40, "保持"],
            [30, 20, 120, 80, "ダイレクトアウト"],
            [30, 20, 70, 40, "除外"],
            [30, 20, np.nan, 40, "ロスト"],
            [121, 20, 70, 40, "保持"],
            [30, 20, 70, 40, "相手GK直接確保"],
        ], columns=["landing_x", "landing_y", "final_x", "final_y", "result"])
        stats = aggregate_results(frame)
        self.assertEqual(stats["counts"][6], 6)
        self.assertEqual(stats["totals"][6], 2)
        self.assertEqual(stats["direct_out"][6], 1)
        self.assertEqual(stats["direct_claim"][6], 1)
        self.assertEqual(stats["excluded"][6], 1)
        self.assertEqual(stats["missing"][6], 1)
        self.assertEqual(stats["missing_landing"], 1)
        self.assertAlmostEqual(stats["probabilities"][6].sum(), 100)
        self.assertAlmostEqual(stats["probabilities"][6, 17], 100)
        self.assertTrue(np.isnan(stats["probabilities"][0]).all())

    def test_grid_boundaries(self):
        self.assertEqual(location_to_grid([0, 0]), 0)
        self.assertEqual(location_to_grid([20, 16]), 6)
        self.assertEqual(location_to_grid([120, 80]), 29)
        self.assertEqual(location_to_grid([120, 80], opponent=True), 0)
        self.assertIsNone(location_to_grid([121, 80]))

    def test_separate_counts_with_missing_landing_and_no_distribution(self):
        # 別集計だけのグリッドは分母0。着地点欠損でも全体の別集計件数には残す。
        frame = pd.DataFrame([
            [30, 20, np.nan, np.nan, "相手GK直接確保"],
            [30, 20, np.nan, np.nan, "ダイレクトアウト"],
            [np.nan, np.nan, np.nan, np.nan, "相手GK直接確保"],
        ], columns=["landing_x", "landing_y", "final_x", "final_y", "result"])
        stats = aggregate_results(frame)
        self.assertEqual(stats["counts"][6], 2)
        self.assertEqual(stats["totals"][6], 0)
        self.assertEqual(stats["missing"][6], 0)
        self.assertEqual(stats["direct_claim"][6], 1)
        self.assertEqual(stats["direct_claim_total"], 2)
        self.assertEqual(stats["direct_out_total"], 1)
        self.assertTrue(np.isnan(stats["probabilities"][6]).all())


if __name__ == "__main__":
    unittest.main()
