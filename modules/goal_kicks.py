"""new.definition.md に従ってゴールキックごとの判定結果を作る。"""

import math

import pandas as pd

from modules.generate_grid_map import location_to_grid


TOUCHES = {"Pass", "Clearance", "Block", "Interception", "Miscontrol", "Shot", "Carry", "Dribble"}
RESTART_PASSES = {"Throw-in", "Free Kick", "Corner", "Goal Kick", "Kick Off"}
RESTART_SHOTS = {"Free Kick", "Penalty", "Corner"}
CLAIMS = {"Collected": {"Success", "Collected Twice"}, "Keeper Sweeper": {"Claim"}, "Smother": {"Won"}}
GK_TOUCHES = {"Punch": {"In Play Safe", "In Play Danger", "Punched out"},
              "Keeper Sweeper": {"Clear"}, "Smother": {"Success In Play", "Lost In Play", "Lost Out"}}


def is_claim(event):
    return (event.get("type") == "Goal Keeper"
            and event.get("goalkeeper_outcome") in CLAIMS.get(event.get("goalkeeper_type"), set()))


def is_touch(event):
    kind = event.get("type")
    if kind in TOUCHES:
        return True
    if kind == "Ball Receipt*":
        return pd.isna(event.get("ball_receipt_outcome"))
    if kind == "Ball Recovery":
        return pd.isna(event.get("ball_recovery_recovery_failure"))
    if kind == "Duel":
        return event.get("duel_type") == "Tackle"
    if kind == "50/50":
        value = event.get("50_50")
        return isinstance(value, dict) and value.get("outcome", {}).get("name") in {
            "Won", "Success To Team", "Success To Opposition"}
    if kind == "Goal Keeper":
        return event.get("goalkeeper_outcome") in GK_TOUCHES.get(event.get("goalkeeper_type"), set())
    return False


def is_restart(event):
    return (event.get("pass_type") in RESTART_PASSES
            or event.get("shot_type") in RESTART_SHOTS
            or event.get("type") == "Referee Ball-Drop")


def coordinates(value, opponent=False):
    # 欠損・範囲外を端のグリッドに補完しない。
    try:
        x, y = float(value[0]), float(value[1])
    except (TypeError, ValueError, IndexError):
        return math.nan, math.nan
    if not (math.isfinite(x) and math.isfinite(y) and 0 <= x <= 120 and 0 <= y <= 80):
        return math.nan, math.nan
    return (120 - x, 80 - y) if opponent else (x, y)


def end_location(event):
    column = {"Pass": "pass_end_location", "Carry": "carry_end_location"}.get(event.get("type"), "location")
    return event.get(column)


def classify_sequence(gk, following, threshold=2.0):
    """時刻順検証済みの同一試合・ピリオドのイベント列を判定する。"""
    team = gk["team"]
    landing = (math.nan, math.nan)
    landed = False
    clock = None
    last_own = None
    loss_source = None
    own_touch_count = 0
    opponent_touch_count = 0
    foul = None
    drop = None
    direct = gk.get("pass_outcome") == "Out"

    def position(event, value=None):
        return coordinates(event.get("location") if value is None else value, event.get("team") != team)

    def fallback_landing(restart):
        # ファウル位置が欠損している場合だけ、定義に従って再開位置を使う。
        if foul is not None:
            point = position(foul)
            if math.isfinite(point[0]):
                return point
        return position(restart)

    def finish(event, result, reason, *, source=None, point=None, shot=False, penalty="", own_goal=""):
        source = event if source is None else source
        final = position(source) if point is None else point
        return dict(match_id=gk["match_id"], goal_kick_id=gk["id"], team=team,
                    period=gk["period"], goal_kick_time=gk["_seconds"], result=result,
                    reason=reason, decision_event_id=event["id"], decision_time=event["_seconds"],
                    position_event_id=source["id"], landing_x=landing[0], landing_y=landing[1],
                    landing_grid_id=location_to_grid(landing), final_x=final[0], final_y=final[1],
                    final_grid_id=location_to_grid(final), shot=shot, penalty=penalty, own_goal=own_goal,
                    own_touch_count=own_touch_count, opponent_touch_count=opponent_touch_count)

    # 対象タッチによる連続保持と、即終了するイベントを発生順に確認する。
    for event in following:
        kind = event.get("type")
        own = event.get("team") == team
        if kind == "Half End":
            return finish(event, "除外", "half_end", point=(math.nan, math.nan))
        if kind == "Foul Committed" and not landed:
            foul = event
        if kind == "Referee Ball-Drop":
            if drop is None:
                drop = event
            continue
        # 再開のキックとGK確保は通常の対象タッチとは分けて数える。
        touch = is_touch(event) and not is_restart(event) and not direct
        if touch:
            if own:
                own_touch_count += 1
            else:
                opponent_touch_count += 1
        # ドロップの両チーム分の行は飛ばし、最初の接触で再開チームを判断する。
        if drop is not None and (is_touch(event) or is_claim(event)):
            if not landed:
                landing = fallback_landing(drop)
            return finish(event, "保持" if own else "ロスト", "ball_drop",
                          source=drop, point=position(drop))
        if is_restart(event):
            if not landed:
                landing = position(event) if direct else fallback_landing(event)
            if direct:
                return finish(event, "ダイレクトアウト", "direct_out", point=(math.nan, math.nan))
            penalty = ("won" if own else "conceded") if event.get("shot_type") == "Penalty" else ""
            return finish(event, "保持" if own else "ロスト", "restart", penalty=penalty)
        # ダイレクトアウトは次の再開位置を取得するまで待つ。
        if direct:
            continue
        if not landed and (is_touch(event) or is_claim(event)):
            landing = position(event)
            landed = True
        if kind == "Shot" and event.get("shot_type") == "Open Play":
            return finish(event, "保持" if own else "ロスト", "shot", shot=True)
        if kind in {"Own Goal For", "Own Goal Against"}:
            scored = own if kind == "Own Goal For" else not own
            return finish(event, "保持" if scored else "ロスト", "own_goal",
                          own_goal="for" if scored else "against")
        if is_claim(event):
            if own:
                return finish(event, "保持", "goalkeeper_claim")
            if own_touch_count:
                # 相手GKの確保位置ではなく、直前の自チームのアクション終点を残す。
                return finish(event, "ロスト", "goalkeeper_claim", source=last_own,
                              point=coordinates(end_location(last_own)))
            if opponent_touch_count == 0:
                return finish(event, "相手GK直接確保", "opponent_gk_direct_claim",
                              point=(math.nan, math.nan))
            # 相手だけが触った後の確保は、対象タッチによるT秒判定を待つ。
            continue
        if not is_touch(event):
            continue
        if own:
            clock = None
            last_own = event
        elif clock is None:
            clock = event["_seconds"]
            loss_source = last_own if last_own is not None else event
        elif event["_seconds"] - clock >= threshold:
            # 自チームが触れていなければ、相手の連続保持開始位置を採用する。
            point = (coordinates(end_location(loss_source)) if last_own is not None
                     else position(loss_source))
            return finish(event, "ロスト", "opponent_control", source=loss_source, point=point)

    # 次のピリオドへは持ち越さず、不完全なイベント列も理由を付けて残す。
    return finish(gk, "除外", "period_end_without_decision", point=(math.nan, math.nan))


def analyze_events(events, threshold=2.0):
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("Tは正の有限値を指定してください")
    required = {"id", "match_id", "period", "index", "timestamp", "type", "team", "pass_type"}
    if missing := required - set(events.columns):
        raise ValueError(f"必須カラムがありません: {sorted(missing)}")
    # 巨大なデータ全体を辞書化せず、必要列を試合・ピリオド単位で処理する。
    optional = {"location", "pass_end_location", "carry_end_location", "pass_outcome", "shot_type",
                "goalkeeper_type", "goalkeeper_outcome", "ball_receipt_outcome",
                "ball_recovery_recovery_failure", "duel_type", "50_50"}
    frame = events[list(required | (optional & set(events.columns)))].copy()
    frame["_source_order"] = range(len(frame))
    frame["_seconds"] = pd.to_timedelta(frame["timestamp"]).dt.total_seconds()
    results = []
    for _, group in frame.groupby(["match_id", "period"], sort=False):
        group = group.sort_values("index", kind="stable")
        # 時刻の逆行は直前の生イベントと比較する。無視したゴールキックも除外行に残す。
        valid = group["_seconds"].notna() & ~group["_seconds"].lt(group["_seconds"].shift())
        records = group.loc[valid].to_dict("records")
        for i, event in enumerate(records):
            if event.get("pass_type") == "Goal Kick":
                result = classify_sequence(event, records[i + 1:], threshold)
                result["_source_order"] = event["_source_order"]
                results.append(result)
        for event in group.loc[~valid & group["pass_type"].eq("Goal Kick")].to_dict("records"):
            result = classify_sequence(event, [], threshold)
            result.update(reason="invalid_timestamp", _source_order=event["_source_order"])
            results.append(result)
    if not results:
        raise ValueError("ゴールキックがありません")
    output = pd.DataFrame(results).sort_values("_source_order").drop(columns="_source_order")
    output.insert(0, "id", range(1, len(output) + 1))
    for column in ("landing_grid_id", "final_grid_id"):
        output[column] = output[column].astype("Int64")
    return output.reset_index(drop=True)
