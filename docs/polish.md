# Polish list

Minor issues and open questions from translation and review. Tick (`[x]`) when resolved; release needs no unticked line.
Phase 9 (2026-11-22) closed every line: fixed, or kept with the reason after `->`.

- [x] s14 "Mars Year 168" vs s17/s29 "166": JP as is; confirm intended or a JP slip. -> kept as the JP (faithful; no
  source to say which is right).
- [x] ルブルー = "Le Bleu" (s19): guessed spelling. -> kept (French-style place name fits the setting; no official
  English).
- [x] s08_0d5c/0d88, s16_0250 (and s21_0238): JP ends in a stray "v"; dropped. -> kept dropped (no glyph meaning).
- [x] s25_0d90: JP has 30 spaces + "・・" before {n} (layout junk?); dropped, check the s25 objective screen. -> s25 tour
  sheets passed visual QA (phase 8).
- [x] s31_01d0: JP typo クローンデビル ("Clone Devil"); translated "Chrome Devil". -> not a typo: the s31 Chrome Devil is a
  fake (s31_0880) and Clone Devil is its unit (pilot_067, gunho_01eb8); now "Victory: Destroy the Clone Devil".
- [x] s20_0f18: JP "ＸＸＸ村長" (dev placeholder); translated "the village chief". -> kept.
- [x] s35 credit name readings unverified (Hepburn guesses): Ichiro Ideto, Madaraya, Suzuka Ayakoju (彩恋寿鈴鹿),
  Suguri Yokota (横田村主), Lee Mi-geon (李美鍵), Koki Nakamura (中村光輝), Yoshio Osawa (大沢縁雄), Yutaka Izuishi (出石沃).
  -> kept as best-effort readings (D2: Hepburn when no official source); README notes credit readings may be off.
- [x] s35 staff roll ("roll" form, 48 x 6 assumed in tools/batches.py): measure line count at the s35 warp. -> moot:
  the s35 overlay roll is never drawn in play (the s35 warp plays the ENDING.BIN roll, phase 8).
- [x] s00_0078 "- Battle scenes/Shortened/Status display" vs config table_00430/00440: aligned (D14, "Fast battles").
- [x] s31_01d0: "Clone Devil" is a real unit (gunho_01eb8, pilot_067), so the JP may not be a typo; recheck. -> fixed,
  see above.
- [x] ending_*: same unverified readings as s35; ending_104/147 笹森満 = Mitsuru Sasamori while s35 has 笹森健二 (JP
  differs). ending_073/074 and 146/147: names reflowed across rows to keep 48 chars. -> kept as the JP; roll shots
  e34 clean.
- [x] Unseen context, verify in game: gunho_8165e 欠 "Absent", gunho_819a4 ﾅｸﾞｯﾃ "Punch", gunho_819c4 "  ...",
  table_00168-00194 Melee/Ground/Trailer/Remove, menumv/slps pre-release notice (likely unused). -> kept; textcover
  and menu QA never reached them, meaning is clear from the JP.
- [x] s06_0894 "As it was, it wasn't even a fifth." vague -> now "Those figures aren't even a fifth of it."
- [x] s35_00c4 sound test "GB2F ... (Battle Screen)": JP repeats 戦闘画面 for the F track; kept as JP (never drawn).
- [x] s35_09a4 debug credit 田中福岡柴田耕平 rendered "Tanaka Fukuoka Kohei Shibata": JP has no separators, split
  unverified. -> kept (s35 overlay text is never drawn; the ENDING.BIN roll has the names split, ending_232).
- [x] s08_03bc drops the "GF Line" alias (only "Martian Maginot Line" kept, 42x3 fit). -> kept (box is fixed 42x3).
- [x] ヤー rendered "Yah!" throughout (s08, s20, s26, s33, s34). -> kept: a battle cry, reads fine.
- [x] Victory/Defeat rows: continuation-line indent lost on auto-wrap. -> fixed in phase 8 (9-space indent like JP).
- [x] gunho_821dc 両手利き: "Ambidextrous" ran over the battle Ability box (11 chars, phase 8 shot); "Ambidexter" stays.
- [x] gunho_8204c ﾗｸﾞﾎﾞｰﾙ "Rug Ball" is a guess at the weapon name. -> kept (closest reading; s02 tutorial matches).
- [x] Small-font names still short (D12): hover box 10 chars: YankApache, CloneDevil, Chrome Dvl, C Dragoon2,
  SuperCobra, Cmd Ship; slot-11 rows Condenser, Cond Round, 20@MG, 30@MG, Mag names, Shock Atk, Msl Guard; pool rows
  Dual / Dual W, Morph, Away. -> accepted under D12 (the window holds 10 chars; widening the hover box is code work
  with no spare room on screen); every full name is in the dialogue and glossary.
- [x] Small font at 6 px: STATUS pilot name centred for 8 px per char (sits n px right of centre); weapon-list budget
  (12) a guess. -> accepted: cosmetic, the name stays inside the panel (14-char ruler measured); weapon list passed
  the phase 8 menu gate with the stress save.
- [x] Small font: add `.`, `-`, `&`, `'` glyphs and restore "Cmd. Ship", "Anti-Missile", "Chavez & Ralph". -> accepted
  as is (D9/D12 spellings without them read fine).
- [x] table_00440 短縮 = "Cut": done another way (D14): row 1 "Fast", row 2 blank; s00_0078 / s05_13c0 say "Fast".
- [x] Eqip tab Item column cuts names at 8 chars (game limit). -> D16: the two pairs that cut to the same text now
  drop their space so the cut stays distinct like the JP cut (88@GunL71 / 88@GunL56 -> "88@GunL7" / "88@GunL5",
  RandallMag / Randall75@ -> "RandallM" / "Randall7"); the weapon row under the list shows the full name.
- [x] D11 trims (phase 7, lighter wording to fit): story verdicts re-read in the phase 9 story pass (all ok).
