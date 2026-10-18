"""合成イベント列で判定・位置参照元・終了条件を検証する。"""

import math
import unittest

import pandas as pd

from modules.goal_kicks import analyze_events, classify_sequence, is_touch


def event(i, seconds, team="A", kind="Pass", **kwargs):
    return dict(id=str(i), match_id=1, period=1, index=i, _seconds=seconds,
                timestamp=f"00:00:{seconds:06.3f}", team=team, type=kind,
                location=[30, 20], **kwargs)


def kick():
    return event(0, 0, pass_type="Goal Kick", pass_end_location=[50, 40])


class GoalKickTests(unittest.TestCase):
    def test_first_opponent_touch_uses_kick_endpoint(self):
        result = classify_sequence(kick(), [event(1, 3, "B"), event(2, 5, "B")])
        self.assertEqual(result["result"], "ロスト")
        self.assertEqual(result["decision_event_id"], "2")
        self.assertEqual(result["position_event_id"], "0")
        self.assertEqual((result["final_x"], result["final_y"]), (50, 40))
        self.assertEqual((result["landing_x"], result["landing_y"]), (90, 60))

    def test_clock_reset_and_latest_own_endpoint(self):
        rows = [event(1, 1, pass_end_location=[60, 40]), event(2, 2, "B"),
                event(3, 5, kind="Carry", carry_end_location=[70, 30]),
                event(4, 6, "B"), event(5, 8, "B")]
        result = classify_sequence(kick(), rows)
        self.assertEqual(result["decision_event_id"], "5")
        self.assertEqual(result["position_event_id"], "3")
        self.assertEqual((result["final_x"], result["final_y"]), (70, 30))

    def test_missing_endpoint_and_ignored_pressure(self):
        rows = [event(1, 1), event(2, 2, "B"), event(3, 3, kind="Pressure"), event(4, 4, "B")]
        result = classify_sequence(kick(), rows)
        self.assertTrue(math.isnan(result["final_x"]))
        self.assertEqual(result["position_event_id"], "1")

    def test_no_own_time_limit(self):
        rows = [event(1, 20, pass_end_location=[80, 40]), event(2, 40, "B"), event(3, 42, "B")]
        self.assertEqual(classify_sequence(kick(), rows)["reason"], "opponent_control")

    def test_shots_and_restarts(self):
        for team, expected in [("A", "保持"), ("B", "ロスト")]:
            with self.subTest(team=team):
                result = classify_sequence(kick(), [event(1, 3, team, "Shot", shot_type="Open Play")])
                self.assertEqual(result["result"], expected)
                self.assertTrue(result["shot"])
                result = classify_sequence(kick(), [event(1, 3, team, "Shot", shot_type="Penalty")])
                self.assertEqual(result["result"], expected)
                self.assertFalse(result["shot"])
                self.assertEqual(result["penalty"], "won" if team == "A" else "conceded")

    def test_claim_punch_and_fail(self):
        claim = event(1, 3, "B", "Goal Keeper", goalkeeper_type="Collected", goalkeeper_outcome="Success")
        self.assertEqual(classify_sequence(kick(), [claim])["reason"], "goalkeeper_claim")
        for outcome in ["In Play Safe", "Fail"]:
            rows = [event(1, 3, "B", "Goal Keeper", goalkeeper_type="Punch", goalkeeper_outcome=outcome),
                    event(2, 4, kind="Shot", shot_type="Open Play")]
            self.assertEqual(classify_sequence(kick(), rows)["result"], "保持")

    def test_direct_out_and_drop(self):
        gk = kick()
        gk["pass_outcome"] = "Out"
        result = classify_sequence(gk, [event(1, 8, "B", pass_type="Throw-in")])
        self.assertEqual(result["result"], "ダイレクトアウト")
        self.assertEqual(result["landing_x"], 90)
        rows = [event(1, 3, kind="Referee Ball-Drop"),
                event(2, 3, "B", "Referee Ball-Drop"), event(3, 4, "B")]
        result = classify_sequence(kick(), rows)
        self.assertEqual(result["result"], "ロスト")
        self.assertEqual(result["position_event_id"], "1")

    def test_foul_landing_and_half_end(self):
        result = classify_sequence(kick(), [event(1, 2, "B", "Foul Committed"),
                                            event(2, 5, pass_type="Free Kick")])
        self.assertEqual(result["landing_x"], 90)
        self.assertEqual(result["final_x"], 30)
        self.assertEqual(classify_sequence(kick(), [event(1, 3, kind="Half End")])["result"], "除外")

    def test_missing_foul_position_falls_back_to_restart(self):
        foul = event(1, 2, "B", "Foul Committed")
        foul["location"] = None
        result = classify_sequence(kick(), [foul, event(2, 5, pass_type="Free Kick")])
        self.assertEqual(result["landing_x"], 30)

    def test_own_goals(self):
        for team, kind, expected in [("A", "Own Goal For", "保持"), ("B", "Own Goal Against", "保持"),
                                     ("A", "Own Goal Against", "ロスト"), ("B", "Own Goal For", "ロスト")]:
            self.assertEqual(classify_sequence(kick(), [event(1, 3, team, kind)])["result"], expected)

    def test_touch_conditions(self):
        self.assertTrue(is_touch(dict(type="Duel", duel_type="Tackle", duel_outcome="Lost Out")))
        self.assertFalse(is_touch(dict(type="Ball Receipt*", ball_receipt_outcome="Incomplete")))
        self.assertTrue(is_touch({"type": "50/50", "50_50": {"outcome": {"name": "Success To Opposition"}}}))

    def test_match_period_isolation_and_reverse_time(self):
        rows = [kick(), event(1, 3, "B"), event(2, 1, kind="Carry", carry_end_location=[100, 40]),
                event(3, 5, "B"), dict(kick(), id="other", match_id=2),
                dict(event(1, 6, "B"), match_id=2, period=2)]
        results = analyze_events(pd.DataFrame(rows))
        self.assertEqual(len(results), 2)
        self.assertEqual(results.iloc[0].position_event_id, "0")
        self.assertEqual(results.iloc[1].result, "除外")


if __name__ == "__main__":
    unittest.main()
