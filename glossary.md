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
| デズモンド・オールドマン | Desmond Oldman | | full name (staff roll cast) | |
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
| レイモンド・トーヴィー | Raymond Tovey | | Vice Admiral, Union Space Force, Dunkirk commander (s06) | |
| ベティ・クリムゾン | Betty Crimson | | Betty's old sniper alias (s15) | |
| ダンカン | Duncan | | speaker; thug turned bandit (s15) | |

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
| ダーラ高地 | Darra Highlands | | s14 landing site | |
| マコーリフ砦 | Fort McAuliffe | | at the foot of Olympus; John's father | |
| スキアパレリ・カタパルト | Schiaparelli Catapult | | s09 | |
| サントス川 | Santos River | | s12 sim | |
| ルブルー | Le Bleu | | Betty's sniper debut (s19) | |
| マリク鉱山村 | Malik mining village | | s19 | |
| チタ | Chita | | Oldman's home (s06) | |

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
| クロームデビル | Chrome Devil / Chrome Dvl | | Chrome Dvl only as the unit name in the battle hover box (10 chars, D12) | |
| ジャンキー | Junkie | | | |
| ドラグーン | Dragoon | | | |
| マスタング | Mustang | | | |
| マスタングＤ | Mustang D | | | |
| ガンシップ | Gunship | | | |
| アパッチ | Apache | | | |
| シャイアン | Cheyenne | | | |
| コマンドー | Commando | | | |
| コマンドシップ | Command Ship / Cmd Ship | | Cmd Ship only as the unit name (11-byte slot, hover box 10 chars, D12) | |
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
| 外惑星連合 | Outer Planets Union / Union | | | |
| 火星暦 | Mars Year | | dates ("Mars Year 168") in narration and the prologue captions (tools/gfx_captions.py) | |
| 火星歴 | Mars Century | | the calendar's name, prologue caption | |
| 外惑星自治区 | Outer Planets Autonomous Zone | | prologue caption | |
| 火星諸州連合 | Union of Martian States | | prologue caption | |
| 火星連合 | Mars Union | | prologue caption | |
| 南部連合 | Southern Confederation | | prologue caption (101st Cavalry Brigade's side) | |
| 地球連邦平和実施軍 | Earth Federation peace forces | | prologue caption | |
| ジャンクス・ラッシュ | Junk Rush | | prologue caption | |
| 『失われた大隊』 | Lost Battalion | | prologue caption | |
| 連合宙軍 | Union Space Force | | | |
| ジャンク | Junk | | alien wreckage the Junkies are named after (s06) | |
| １０１騎兵旅団 | 101st Cavalry Brigade | | Oldman's brigade, called the Gungho Brigade | |
| ドラグーン２ | Dragoon 2 | | | |
| マスタングＨ | Mustang H | | Maiko's one-off custom | |
| スーパーコブラ | Super Cobra / SuperCobra | | SuperCobra only as the unit name (hover box 10 chars, D12) | |
| エゼキエル | Ezekiel | | enemy unit | |
| ロスコウ | Roscoe | | enemy unit | |
| ハンバー | Humber | | enemy artillery | |
| バッファロー | Buffalo | | | |
| ピーシューター | Peashooter | | | |
| ホークアイ | Hawkeye | | | |
| エクスキューショナー | Executioner | | Betty rumour (s19) | |
| 地球急行 | Earth Express | | evacuation shuttle | |
| 「射撃」 | Shoot | | unit command | |
| 「格闘」 | Melee | | unit command | |
| 戦闘コマンドボタン | command buttons | | graphics (tools/gfx_labels.py, D13): 射撃 Shoot, 格闘 Melee, アイテム Item, 変形 Morph, 特殊 Special, 装備 Equip, 終了 End; ユニットリスト Unit List, セーブ Save, シナリオ目的 Goals, コンフィグ Config, プロット終了 End Plot. Dialogue naming a button uses these; 「ＳＰ」 stays "SP" | |
| クリア条件 | Goal | | objective label (sim stages) | |
| 特殊条件 | Special condition | | objective label (s27) | |
| 作戦目的 | Objective | | objective label (s29; bare 目的： in s30-s31 too) | |
| ブラックジャック | Blackjack | | Junkie commander unit (s20) | |
| フューリー | Fury | | unit (s25 defeat line) | |
| ゲオルグ | Georg | | enemy unit (s30) | |
| ジェイコブ | Jacob | | enemy unit (s30) | |
| フランシス | Francis | | enemy unit (s31) | |
| 『Ｗ（ビッグ・ダブリュー）』 / 『Ｗ』 | 'W' (Big W) / 'W' | | Earth codename for the Wizard (s21, s31) | |
| 送信機 / 受信機 | sender / receiver | | transmitter halves: Wizard / 12 Crusader leaders (s29) | |
| 外宇宙連合 | Union | | JP variant of 外惑星連合 (s29) | |
| エスメラルダ・スイフト | Esmeralda Swift | | (s29) | |
| ザイオン渓谷 | Zion Canyon | | (s27-s34) | |
| ホイヘンス | Huygens | | (s29) | |
| カイツブリ | Grebe | | callsign "Grebe 180 Squadron" (s34) | |
| 第８２空挺師団 | 82nd Airborne Division | | (s31) | |
| ｍｍ (`@` glyph in names) | @ | | weapon calibre: "57@Railgun" | |
| ｺﾝﾃﾞﾝｻｰｶﾞﾝ / ｺﾝﾃﾞﾝｻｰﾀﾞﾝ | Condenser Gun / Condenser Round / Condenser / Cond Round | 11 | weapon / ammo; small-font names (no `.` glyph): Condenser, Cond Round | |
| ﾏｶﾞｼﾞﾝ | Magazine / Mag | | small-font item names: "88D2 Mag" (slot 11) | |
| 整備中 / ｾｲﾋﾞﾁｭｳ | Servicing / serviced / Maint | | unit state; small-font names "Mustang H Maint", "Maint" (slots 7-19) | Under repair |
| ﾁｮｳｾｲ / ｼｭｳﾘ | Adjust / Repair | | skills: repair 1/3, 2/3 of damage | |
| ｸｲｯｸﾄﾞﾛｰ / ｸｲｯｸﾛｰﾄﾞ / ｸｲｯｸｼｮｯﾄ / ｸｲｯｸ | Quick Draw / Quick Load / Quick Shot / Quick | | skills | |
| ｽﾅｲﾌﾟｼｮｯﾄ | Snipe Shot | | skill | |
| ｼﾞｭｳﾘﾝ / ﾄﾂｹﾞｷ / ﾘｶﾊﾞｰ / ｸﾘﾃｨｶﾙ | Trample / Charge / Recover / Critical / Crit | 7 | skills (7-byte slots: "Crit") | |
| ﾘｮｳﾃｳﾁ / ﾘｮｳﾃｳﾁW / Wﾀｯﾌﾟ | Dual Shot / Dual Shot W / Double Tap / Dual / Dual W / DblTap | 7 | skills (two Randalls / two-handed gun); skill-name slots: Dual, Dual W, DblTap | Akimbo |
| ﾘｮｳﾃｷｷ | Ambidexter / Ambidex | 7 | skill ("Ambidex" in the 7-byte slot) | |
| ヒダリウデ / ﾋﾀﾞﾘｳﾃﾞ | Left | 7 | equipment part slot (Eqip tab Part column: 7 chars) | Left Arm |
| ミギウデ / ﾐｷﾞｳﾃﾞ | Right | 7 | equipment part slot | Right Arm |
| ｿｳﾋﾞﾌｶ | Locked | 7 | part slot that can't be equipped | No Equip |
| 0ｷｮﾘｼｬｹﾞｷ | Point Blank | | skill | |
| 変形 / ｲﾄﾞｳｹｲﾀｲ / ｼｬｹﾞｷｹｲﾀｲ | Transform / Move Mode / Shoot Mode | | | |
| 電撃 / ﾃﾞﾝｹﾞｷｺｳｹﾞｷ / ﾃﾞﾝｹﾞｷﾎﾞｳｷﾞｮ | shock / Shock Attack / Shock Guard | | | |
| ﾕｳﾄﾞｳﾎﾞｳｷﾞｮ / ﾚｰｻﾞｰﾑｺｳ | Anti-Missile / Laser Proof / Msl Guard | | skills; small-font name "Msl Guard" (no `-` glyph) | |
| 行動ポイント | action points | | (not "AP": s05 "AP rounds" = armour-piercing) | |
| ｼﾞｹｲﾀﾞﾝｲﾝ / ｸｳﾃｲ / ﾑｼﾞﾝ | Vigilante / Paratrooper / Unmanned | | pilot names | |
| メモリーカード | Memory Card / card | | "card" when a fullwidth message must be short (2 bytes per letter) | |
| ○戦闘シーン | Fast / Battle | 6 | config option row 1 = "Fast" (whole option: shortened battle scenes ON/OFF; D14). GUNHO font: no fullwidth J Q R V Y Z b f j q v x y | |
| 短縮 | Fast | 3 | config row 2 left blank: it draws over the open "Config" button (D14); dialogue names the option "Fast" | Cut |

## Decisions from earlier batches
