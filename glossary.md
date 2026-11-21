# Glossary - Gungho Brigade

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py` enforces it: a JP term in a line needs one of its EN forms (`/`-separated) in the English; rows
tagged `speaker` give the speaker line of dialogue boxes.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Bizley-kun, Maiko-san). Name order: Western (given name first).
- Romanisation source: official English (title screen, TIM graphics: "3on3 RUG BATTLE TOURNAMENT", "WIZARD", tale
  card titles) where it exists; no earlier fan patch exists; else natural English spelling of the katakana, Hepburn
  without macrons for Japanese names.
- Credits: English.
- Register / flavour: keep light JP flavour. Sound effects: *Bzzt* style, in asterisks.
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening.

## Style rules
- Punctuation: 「」 -> "...", 『』 -> '...' inside speech or plain capitalised name outside, ・・・/… -> ..., ！？ -> ?!
  Numbers as digits. No `/ \ ` { } | ~` (not in the font); write an em dash as `--`.
- Box: 42 chars x 3 lines incl. the speaker line (auto-wrapped by batches.py). Keep it short and spoken.
- Speech keeps its double quotes ("..."); narration, objectives and tutorial text have none.
- Voices: docs/style-reference.md.

## Characters (speaker = used for the dialogue speaker line)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ビズリィ | Bizley | 7 | speaker; hero, Gungho Brigade | Bisley / Bizzly |
| ビズリィ・レナード | Bizley Leonard | | full name | |
| マイコ | Maiko | | speaker | |
| マイコ・ヒノワ | Maiko Hinowa | | full name | |
| シャベス | Chavez | | speaker | Shaves |
| シャベス・シェルビー | Chavez Shelby | | full name | |
| ブレインズ / ブリンズ | Brains | | speaker (ブリンズ = JP typo) | |
| ダイブツ | Daibutsu | | speaker; nickname ("Great Buddha") | |
| ベティ | Betty | | speaker | |
| ベティ・デービス | Betty Davis | | full name | |
| ラルフ | Ralph | | | |
| ラルフ・ライアル | Ralph Lyall | | full name | |
| レジィ | Reggie | | | |
| レジィ・シモンズ | Reggie Simmons | | full name | |
| ジョン | John | | speaker | |
| ジョン・スミス | John Smith | | full name | |
| オールドマン | Oldman | | speaker; officer's name | |
| エスメラルダ | Esmeralda | | speaker | |
| ニーソン | Neeson | | speaker | |
| ニーソン少佐 | Major Neeson | | speaker | |
| ウィリアム・ニーソン | William Neeson | | full name | |
| マコーリフ | McAuliffe | | | |
| トーヴィー | Tovey | | speaker | |
| モーリス | Maurice | | speaker | |
| ダンカン | Duncan | | speaker | |
| アーヴィング | Irving | | speaker | |
| ベーア | Baer | | | Behr |
| ベーア大佐 | Colonel Baer | | speaker | |
| アーツタノフ | Artsutanov | | | |
| ジェニファー | Jennifer | | | |
| ジェニファー・スイフト | Jennifer Swift | | full name | |
| エミリィ | Emily | | | |
| ビリー | Billy | | | |
| マリク | Malik | | | |
| 審判 | Referee | | speaker | |
| 通信音 | Radio | | speaker (sound of a transmission) | |
| 火星の虹 | Rainbow of Mars | | speaker; also a name in 『』 | |
| ラジオ放送 | Radio Broadcast | | speaker | |
| 老人 | Elder | | speaker; old man (not Oldman) | Old Man |
| 老人の声 | Elder's Voice | | speaker | |
| パイロット | Pilot | | speaker | |
| ゴロツキ | Thug | | speaker | |
| 通信員 | Comms Officer | | speaker | |
| 衛兵 | Guard | | speaker | |
| 地球連邦大使 | Federation Ambassador | | speaker | |
| 参謀 | Staff Officer | | speaker | |
| 参謀１ | Staff Officer 1 | | speaker | |
| 参謀２ | Staff Officer 2 | | speaker | |
| 看護婦 | Nurse | | speaker | |
| 女の子 | Girl | | speaker | |
| 下士官 | NCO | | speaker | |
| 地球軍武官 | Earth Army Attache | | speaker | |
| 地球軍士官 | Earth Army Officer | | speaker | |
| 管制官 | Controller | | speaker | |
| 医師 | Doctor | | speaker | |
| 提督 | Admiral | | speaker | |
| アナウンス | Announcement | | speaker | |
| 村人 | Villager | | speaker | |
| 兵 | Soldier | | speaker | |
| 館内放送 | PA System | | speaker | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| オリュンポス | Olympus | | | |
| フォボス | Phobos | | | |
| ザイオン | Zion | | | |
| アルカディア | Arcadia | | | |
| ユーフロシーン | Euphrosyne | | | |
| サンダースロック | Thunder's Rock | | | |
| ランルザック要塞 | Lanrezac Fortress | | | |
| クォード高地 | Quad Heights | | | |
| 火星マジノ線 | Martian Maginot Line | | | |
| ディエップ | Dieppe | | | |
| アラモ | Alamo | | | |
| パヴォニス | Pavonis | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ガンホー・ブリゲイド | Gungho Brigade | | the team; official title | Gung-ho |
| ガンホー・キッド | Gungho Kid | | | |
| 火星軍 | Martian Army / Mars Army | | | |
| 地球軍 | Earth Army / Earth Forces | | | |
| 地球連邦 | Earth Federation | | | |
| 北軍 | Northern Army | | | |
| マシンレッグ | machine leg / Machine Leg | | the walking mecha class | |
| ラグバトル | Rug Battle | | official (TIM "RUG BATTLE") | Rugby |
| ラグボール | Rug Ball | | | |
| ラグライダー | Rug Rider | | | |
| プレーヤーユニット | player unit | | objectives | |
| クロームデビル | Chrome Devil | | | |
| ジャンキー | Junkie | | | |
| ドラグーン | Dragoon | | | |
| マスタング | Mustang | | | |
| マスタングＤ | Mustang D | | | |
| ガンシップ | Gunship | | | |
| アパッチ | Apache | | | |
| シャイアン | Cheyenne | | | |
| コマンドー | Commando | | | |
| コマンドシップ | Command Ship | | | |
| トマホーク | Tomahawk | | | |
| アムトラック | Amtrac | | | |
| ハーキュリーズ | Hercules | | | |
| ランダル | Randall | | handgun | |
| 『ウィザード』 | Wizard | | official TIM "WIZARD" | |
| 『クルセーダーズ』 | Crusaders | | | |
| 『ウィンゲート』 | Wingate | | | |
| 『ダンケルク』 | Dunkirk | | | |
| 『ジー・カープ』 / ジー・カープ | G-KAHP | | team name = "Gungho Kid And His Pals" (s03) | G-Carp |
| 勝利条件 | Victory | | objective label | |
| 敗北条件 | Defeat | | objective label | |
| 特殊ルール | Special rule | | objective label | |
| 総督府 | Governor's Office | | | |
| ニュー・ブラウン | New Brown | | town | |
| パヴォニス杯 | Pavonis Cup | | | |
| 『クラッシャーズ』 | Crushers | | | |
| 『水戦争』 | Water War | | | |
| マスドライバー | mass driver | | | |
| 『通信機』 | transmitter / radio | | | |

## Decisions from earlier batches
