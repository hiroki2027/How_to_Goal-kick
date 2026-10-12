# ゴールキック後のロスト位置の定義

## 目的

ゴールキック後にボールをロストした位置を記録し、最初に触られた位置（着地点）との関係を調べる。

## 保持・ロスト

- ゴールキックを蹴った時点で「保持」のラベルを付ける。自チームが保持を続けても追跡を終了しない。
- 相手の連続保持時間を **T = 2 秒（暫定）** とする。
- 相手の最初のタッチから時計を開始する。自チームがタッチをしたらリセットし、次の相手タッチから数え直す。
- 相手の時計の起点から T 秒以上経過した後、相手の最初の対象タッチで「ロスト」を確定し、そのイベントから遡り一番最新の自チームのアクションの `location` を記録する。
- T 秒経過後でも、相手の次のタッチより先に自チームが触れたらロストを確定しない。
- 記録位置は、ちょうど T 秒後の位置ではなく、ロストを確定したタッチの位置とする（元の定義書と同じ）。

## 元の定義書から引き継ぐ判定

### タッチ

ゴールキック自体を除き、次のイベントを数える。一瞬のタッチでも時計を切り替える。

| イベント | 条件 |
| --- | --- |
| `Pass`, `Clearance`, `Block`, `Interception`, `Miscontrol`, `Shot`, `Carry`, `Dribble` | 条件なし |
| `Ball Receipt*` | `ball_receipt_outcome` が NaN（成功） |
| `Ball Recovery` | `ball_recovery_recovery_failure` が NaN（成功） |
| `Duel` | `duel_type == "Tackle"`。勝敗は問わない |
| `50/50` | `50_50["outcome"]["name"]` が `Won` / `Success To Team` / `Success To Opposition` |
| `Goal Keeper` | 下表の「通常タッチ」に該当 |

上記以外は数えない（失敗した受け・回収、空中戦の敗者、`Pressure`、`Dispossessed`、ファウルなど）。成功の NaN は `isna()` で判定する。

### シュート・オウンゴール

- 流れの中のシュート（`shot_type == "Open Play"`）で終了する。自チームによるシュートならなら保持、相手によるシュートならロストとし、`shot=True` とシュート位置を記録する。
- オウンゴールで終了する。自チームの得点なら保持・`own_goal="for"`、失点ならロスト・`own_goal="against"`。位置はそれぞれ `Own Goal For` / `Own Goal Against` の位置。

### プレー停止・再開

- 外に出た・ファウル・オフサイドなどは、再開チームで終了する。自チームなら保持、相手ならロスト。位置は再開位置。
- 再開は `pass_type` が `Throw-in` / `Free Kick` / `Corner` / `Goal Kick` / `Kick Off`、`shot_type` が `Free Kick` / `Penalty` / `Corner`、または `Referee Ball-Drop`。
- `Recovery` / `Interception` のパスは再開ではない。ファウルイベントだけでは終了しない（アドバンテージに対応）。
- ドロップボールは、その後の最初のタッチのチームで判定し、ドロップ位置を記録する。
- 再開がシュートでも `shot=False`。PK（`shot_type == "Penalty"`）は、自チームの再開なら `penalty="won"`、相手なら `penalty="conceded"`。
- 誰も触らず外に出た場合は「ダイレクトアウト」として別分類する。ゴールキックの `pass_outcome == "Out"` で判定する。

### GKの確保・弾き出し

`type == "Goal Keeper"` を次のとおり扱う。

| `goalkeeper_type` | `goolkeeper_outcome`の値のうち確保（即終了）として扱う値 | `goolkeeper_outcome`の値のうち通常タッチとして扱う値 |
| --- | --- | --- |
| `Collected` | `Success` / `Collected Twice` | なし |
| `Punch` | なし | `In Play Safe` / `In Play Danger` / `Punched out` |
| `Keeper Sweeper` | `Claim` | `Clear` |
| `Smother` | `Won` | `Success In Play` / `Lost In Play` / `Lost Out` |

- 確保は自チームなら保持、相手ならロストとし、そのGKイベントの位置を記録する。
- 通常タッチは時計の開始・リセットだけ行う。外に出た場合は再開チームで終了する。
- `Fail` は接触が不明なので無視する。表にないGKイベントは判定に使わない。足での `Pass` / `Carry` は通常の対象タッチ。

### 観測期間・優先順位

- 観測期間は考慮しない。自チームのプレーが終わり「ロスト」判定が出るまで追跡をする。

### 時刻・座標・着地点

- `timestamp` を `period` ごとに秒へ変換し、`period`・`index` 順に処理する。時刻順には並べ替えず、直前より時刻が戻る行は無視する。
- 終了前にハーフが終わった場合は除外する。
- 全位置はゴールキックを蹴ったチーム視点。相手の座標は `(120-x, 80-y)` に反転する。
- ピッチは120×80、グリッドは6×5（幅20×16）。`x >= 60` は敵陣、それ未満は自陣。図の攻撃方向は下から上。
- 着地点は最初の対象タッチの位置。誰も触らず外に出たら再開位置、ファウルなら `Foul Committed` の位置（なければ `Free Kick` の再開位置）。それ以外は欠損として件数を残す。
- 決着位置はイベントの `location`（開始位置）を使う。

## 記録

- ゴールキックの識別情報、着地点、結果ラベル、決着時刻・位置、判定理由を記録する。
- `shot` は通常 `False`、`penalty`・`own_goal` は該当しなければ空欄とする。
- ロスト以外の終了結果も残し、ロスト件数・割合の分母を確認できるようにする。
