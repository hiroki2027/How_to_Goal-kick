# StatsBomb イベントデータ カラム説明

対象: `data/events_2_27.pkl`(プレミアリーグ 2015/16、全 380 試合、1,313,773 行、118 カラム)

- 1 行が 1 イベント(パス、シュート、ボールを受けた、など)。
- 「件数」は値が入っている行数。空(NaN)は「該当しない」か「False」の意味。
- `pass_` や `shot_` で始まるカラムは、その種類のイベントの行にだけ値が入る。
- 座標は `[x, y]`。ピッチは 120 × 80 ヤードで、x は自陣ゴール(0)から相手ゴール(120)、y は攻撃方向を向いて左(0)から右(80)。どのチームも常に x が大きい方向へ攻める形にそろっている。
- 説明は StatsBomb の仕様と実データの値をもとにまとめたもの。正式な定義は公式 PDF を参照:
  https://github.com/statsbomb/open-data/tree/master/doc

## 共通(全イベントにある項目)

| カラム | 件数 | 説明 |
|---|---:|---|
| `id` | 1,313,773 | イベントの一意な ID |
| `index` | 1,313,773 | 試合内でのイベントの通し番号(発生順) |
| `match_id` | 1,313,773 | 試合の ID(380 試合) |
| `period` | 1,313,773 | 1 = 前半、2 = 後半 |
| `minute` | 1,313,773 | 試合の経過分(後半は 45 から) |
| `second` | 1,313,773 | その分の中の秒(0〜59) |
| `timestamp` | 1,313,773 | 前半・後半それぞれの開始からの経過時間(`00:00:05.181` の形式) |
| `duration` | 973,459 | イベントの継続時間(秒) |
| `type` | 1,313,773 | イベントの種類。`Pass`, `Shot`, `Carry`, `Ball Receipt*`, `Pressure`, `Duel` など 33 種類 |
| `team` | 1,313,773 | イベントを行ったチーム名 |
| `team_id` | 1,313,773 | チームの ID |
| `player` | 1,309,036 | イベントを行った選手名 |
| `player_id` | 1,309,036 | 選手の ID |
| `position` | 1,309,036 | その時点での選手のポジション(`Goalkeeper`, `Right Center Back` など 25 種類) |
| `location` | 1,305,696 | イベントが起きた位置 `[x, y]`。パスなら蹴った位置 |
| `possession` | 1,313,773 | 試合内でのポゼッション(ひと続きのボール保持)の通し番号 |
| `possession_team` | 1,313,773 | そのポゼッションでボールを保持しているチーム名 |
| `possession_team_id` | 1,313,773 | 上記チームの ID |
| `play_pattern` | 1,313,773 | そのポゼッションが何から始まったか。`Regular Play`, `From Goal Kick`, `From Corner`, `From Throw In` など 9 種類 |
| `related_events` | 1,258,767 | 関連するイベントの ID のリスト(例: パスと、それを受けた Ball Receipt) |
| `under_pressure` | 279,690 | 相手のプレッシャーを受けながらのプレーなら True |
| `counterpress` | 42,324 | ボールを失った直後(5 秒以内)の奪い返しにいくプレーなら True |
| `off_camera` | 18,529 | 映像に映っていない間に起きたイベントなら True |
| `out` | 12,193 | そのイベントの結果、ボールがピッチの外に出たら True |
| `tactics` | 1,385 | フォーメーションと出場メンバー。`Starting XI` と `Tactical Shift` の行にだけ入る |

## パス(`type == "Pass"`)

| カラム | 件数 | 説明 |
|---|---:|---|
| `pass_type` | 81,591 | 特別な種類のパス。`Goal Kick`, `Corner`, `Free Kick`, `Throw-in`, `Kick Off`, `Recovery`, `Interception`。空なら流れの中の通常のパス |
| `pass_end_location` | 368,619 | パスの終点 `[x, y]`。成功なら受け手が受けた位置、失敗ならパスが途切れた位置 |
| `pass_outcome` | 86,240 | 失敗の内容。`Incomplete`(通らなかった), `Out`(外に出た), `Pass Offside`(オフサイド), `Unknown`, `Injury Clearance`(負傷者のために外へ出した)。**空なら成功** |
| `pass_recipient` | 340,325 | 受け手(または受け手として狙われた選手)の名前 |
| `pass_recipient_id` | 340,325 | 受け手の選手 ID |
| `pass_length` | 368,619 | パスの距離(ヤード)。蹴った位置から終点までの直線距離 |
| `pass_angle` | 368,619 | パスの方向(ラジアン)。0 が相手ゴール方向、正の値が右方向(時計回り)、負の値が左方向 |
| `pass_height` | 368,619 | パスの高さ。`Ground Pass`(地面を転がる), `Low Pass`(肩の高さより下), `High Pass`(肩の高さより上) |
| `pass_body_part` | 340,544 | 蹴った部位。`Right Foot`, `Left Foot`, `Head`, `Keeper Arm`(GK のスロー), `Drop Kick`(GK のパントキック), `Other`, `No Touch` |
| `pass_technique` | 5,061 | 蹴り方。`Inswinging`, `Outswinging`, `Straight`, `Through Ball` |
| `pass_cross` | 9,545 | クロスなら True |
| `pass_switch` | 10,488 | サイドチェンジ(ピッチを大きく横切るパス)なら True |
| `pass_through_ball` | 1,621 | スルーパスなら True |
| `pass_cut_back` | 788 | マイナス方向への折り返し(カットバック)なら True |
| `pass_inswinging` | 1,625 | ゴールに向かって曲がるボールなら True |
| `pass_outswinging` | 1,409 | ゴールから離れる方向に曲がるボールなら True |
| `pass_straight` | 406 | 曲がらないまっすぐなボールなら True |
| `pass_aerial_won` | 10,519 | 空中戦に勝って出したパス(ヘディングでのパスなど)なら True |
| `pass_deflected` | 348 | 相手に当たってコースが変わったら True |
| `pass_miscommunication` | 218 | 出し手と受け手の意図が合わなかったパスなら True |
| `pass_no_touch` | 322 | ボールに触らずにスルーして味方に流したプレーなら True |
| `pass_shot_assist` | 6,506 | シュートにつながったパス(キーパス)なら True |
| `pass_goal_assist` | 669 | ゴールにつながったパス(アシスト)なら True |
| `pass_assisted_shot_id` | 7,175 | このパスからつながったシュートのイベント ID |

## シュート(`type == "Shot"`)

| カラム | 件数 | 説明 |
|---|---:|---|
| `shot_outcome` | 9,908 | 結果。`Goal`, `Saved`(セーブ), `Blocked`(ブロック), `Off T`(枠外), `Post`(ポスト・バー), `Wayward`(大きく外れた), `Saved Off Target`, `Saved to Post` |
| `shot_statsbomb_xg` | 9,908 | StatsBomb のゴール期待値(xG)。0〜1 |
| `shot_end_location` | 9,908 | シュートの終点。`[x, y]` または高さを含む `[x, y, z]` |
| `shot_type` | 9,908 | シュートの状況。`Open Play`, `Free Kick`, `Penalty`, `Corner` |
| `shot_body_part` | 9,908 | 打った部位。`Right Foot`, `Left Foot`, `Head`, `Other` |
| `shot_technique` | 9,908 | 打ち方。`Normal`, `Volley`, `Half Volley`, `Lob`, `Diving Header`, `Overhead Kick`, `Backheel` |
| `shot_freeze_frame` | 9,835 | シュートの瞬間の各選手の位置(位置・選手・ポジション・味方かどうかのリスト) |
| `shot_key_pass_id` | 7,175 | このシュートにつながったパスのイベント ID |
| `shot_first_time` | 2,943 | ダイレクト(トラップなし)で打ったら True |
| `shot_one_on_one` | 464 | GK と 1 対 1 の状況なら True |
| `shot_open_goal` | 106 | 無人のゴールへのシュートなら True |
| `shot_aerial_won` | 909 | 空中戦に勝って打ったシュートなら True |
| `shot_deflected` | 131 | 相手に当たってコースが変わったら True |
| `shot_redirect` | 36 | 味方のシュートやパスに触ってコースを変えたシュートなら True |
| `shot_follows_dribble` | 9 | ドリブルの直後のシュートなら True |
| `shot_saved_off_target` | 45 | 枠外に飛んでいたシュートを GK が止めたら True |
| `shot_saved_to_post` | 23 | GK が触ってポストに当たったら True |

## ゴールキーパー(`type == "Goal Keeper"`)

| カラム | 件数 | 説明 |
|---|---:|---|
| `goalkeeper_type` | 11,777 | GK のプレーの種類。`Shot Faced`(シュートを受けた), `Shot Saved`, `Goal Conceded`(失点), `Collected`(キャッチ), `Punch`, `Smother`(足元に飛び込んで押さえた), `Penalty Conceded` など 14 種類 |
| `goalkeeper_outcome` | 5,134 | そのプレーの結果。`Success`, `Fail`, `In Play Safe`, `In Play Danger`, `Touched In`, `No Touch`, `Saved Twice` など 16 種類 |
| `goalkeeper_position` | 9,930 | プレー時の GK の体勢。`Set`(構えている), `Moving`(動いている), `Prone`(倒れている) |
| `goalkeeper_technique` | 3,310 | `Standing`(立ったまま)か `Diving`(飛びついた)か |
| `goalkeeper_body_part` | 2,539 | 使った部位。`Both Hands`, `Left Hand`, `Right Hand`, `Chest`, `Head`, `Left Foot`, `Right Foot` |
| `goalkeeper_end_location` | 6,637 | プレー後の GK の位置 `[x, y]` |
| `goalkeeper_punched_out` | 71 | パンチングでボールが外に出たら True |
| `goalkeeper_shot_saved_off_target` | 45 | 枠外に飛んでいたシュートを止めたら True |
| `goalkeeper_shot_saved_to_post` | 27 | セーブしたボールがポストに当たったら True |
| `goalkeeper_saved_to_post` | 1 | 同上(別表記のフラグ) |
| `goalkeeper_penalty_saved_to_post` | 1 | PK をセーブしてポストに当たったら True |
| `goalkeeper_success_in_play` | 11 | プレーが成功し、ボールがピッチ内に残ったら True |
| `goalkeeper_lost_in_play` | 6 | プレーに失敗し、ボールがピッチ内に残ったら True |
| `goalkeeper_lost_out` | 1 | プレーに失敗し、ボールが外に出たら True |

## ボールを運ぶ・受ける

| カラム | 件数 | 説明 |
|---|---:|---|
| `carry_end_location` | 276,949 | キャリー(ボールを持って運ぶ)の終点 `[x, y]`。始点は `location` |
| `ball_receipt_outcome` | 57,943 | `Incomplete` ならパスを受けられなかった。空なら受けた |
| `dribble_outcome` | 13,721 | ドリブル(相手を抜きにいくプレー)の結果。`Complete`(成功)か `Incomplete`(失敗) |
| `dribble_nutmeg` | 594 | 股抜きなら True |
| `dribble_overrun` | 860 | ボールを大きく蹴り出して相手を抜こうとしたら True |
| `dribble_no_touch` | 47 | ボールに触らずに相手をかわしたら True |
| `miscontrol_aerial_won` | 570 | 空中戦には勝ったがコントロールをミスしたら True |

## 守備

| カラム | 件数 | 説明 |
|---|---:|---|
| `duel_type` | 32,290 | デュエルの種類。`Tackle`(タックル)か `Aerial Lost`(空中戦に負けた) |
| `duel_outcome` | 15,445 | タックルの結果。`Won`, `Success In Play`, `Success Out`, `Lost In Play`, `Lost Out`(In Play / Out はボールがピッチ内に残ったか外に出たか) |
| `interception_outcome` | 8,920 | インターセプトの結果。値の種類は `duel_outcome` と同じ |
| `50_50` | 559 | こぼれ球の競り合い(五分五分のボール)の結果。`{'outcome': {...}}` の辞書 |
| `clearance_body_part` | 21,645 | クリアした部位。`Head`, `Right Foot`, `Left Foot`, `Other` |
| `clearance_head` | 11,990 | 頭でのクリアなら True |
| `clearance_right_foot` | 5,912 | 右足でのクリアなら True |
| `clearance_left_foot` | 3,615 | 左足でのクリアなら True |
| `clearance_other` | 128 | その他の部位でのクリアなら True |
| `clearance_aerial_won` | 4,847 | 空中戦に勝ってクリアしたら True |
| `block_deflection` | 386 | ブロックでボールのコースが変わっただけ(止めきれなかった)なら True |
| `block_offensive` | 309 | 攻撃側の選手によるブロックなら True |
| `block_save_block` | 56 | ゴールに入るはずのシュートをフィールドの選手がブロックしたら True |
| `ball_recovery_offensive` | 140 | 攻撃中(自チームのシュートやパスのこぼれ球)のボール回収なら True |
| `ball_recovery_recovery_failure` | 3,249 | ボール回収を試みて失敗したら True |

## ファウル・カード

| カラム | 件数 | 説明 |
|---|---:|---|
| `foul_committed_type` | 478 | 犯したファウルの種類。`Handball`, `Dangerous Play`, `Dive`, `Foul Out`, `6 Seconds` |
| `foul_committed_card` | 1,069 | ファウルで出たカード。`Yellow Card`, `Second Yellow`, `Red Card` |
| `foul_committed_advantage` | 1,316 | ファウルを犯したがアドバンテージで流されたら True |
| `foul_committed_offensive` | 304 | 攻撃側の選手が犯したファウルなら True |
| `foul_committed_penalty` | 91 | PK を与えたファウルなら True |
| `foul_won_advantage` | 1,296 | ファウルを受けたがアドバンテージで流されたら True |
| `foul_won_defensive` | 2,592 | 守備側の選手が受けたファウルなら True |
| `foul_won_penalty` | 82 | PK を獲得したファウルなら True |
| `bad_behaviour_card` | 193 | ファウル以外の行為(異議など)で出たカード。`Yellow Card`, `Red Card` |

## 交代・その他

| カラム | 件数 | 説明 |
|---|---:|---|
| `substitution_replacement` | 2,109 | 交代で入った選手の名前(`player` が出た選手) |
| `substitution_replacement_id` | 2,109 | 交代で入った選手の ID |
| `substitution_outcome` | 2,109 | 交代の理由。`Tactical`(戦術)か `Injury`(負傷) |
| `substitution_outcome_id` | 2,109 | 上記の理由の ID |
| `injury_stoppage_in_chain` | 107 | 負傷による中断が一連のプレーの中で起きたら True |
| `player_off_permanent` | 1 | 選手が退いたまま戻らなかったら True |
| `half_start_late_video_start` | 4 | 映像の開始が前半・後半の開始より遅れていたら True |
