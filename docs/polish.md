# Polish list

Minor issues and open questions from translation and review. Tick (`[x]`) when resolved; release needs no unticked line.

- [ ] s14 "Mars Year 168" vs s17/s29 "166": JP as is; confirm intended or a JP slip.
- [ ] ルブルー = "Le Bleu" (s19): guessed spelling.
- [ ] s08_0d5c/0d88, s16_0250 (and s21_0238): JP ends in a stray "v"; dropped.
- [ ] s25_0d90: JP has 30 spaces + "・・" before {n} (layout junk?); dropped, check the s25 objective screen.
- [ ] s31_01d0: JP typo クローンデビル ("Clone Devil"); translated "Chrome Devil".
- [ ] s20_0f18: JP "ＸＸＸ村長" (dev placeholder); translated "the village chief".
- [ ] s35 credit name readings unverified (Hepburn guesses): Ichiro Ideto, Madaraya, Suzuka Ayakoju (彩恋寿鈴鹿),
  Suguri Yokota (横田村主), Lee Mi-geon (李美鍵), Koki Nakamura (中村光輝), Yoshio Osawa (大沢縁雄), Yutaka Izuishi (出石沃).
- [ ] s35 staff roll ("roll" form, 48 x 6 assumed in tools/batches.py): measure line count at the s35 warp.
- [ ] s00_0078 "- Battle scenes/Shortened/Status display" vs config table_00430/00440 "Battle"/"Fast" (s05_13c0 now
  says Battle "Fast"): find where s00_0078 shows and align the terms.
- [ ] s31_01d0: "Clone Devil" is a real unit (gunho_01eb8, pilot_067), so the JP may not be a typo; recheck.
- [ ] ending_*: same unverified readings as s35; ending_104/147 笹森満 = Mitsuru Sasamori while s35 has 笹森健二 (JP
  differs). ending_073/074 and 146/147: names reflowed across rows to keep 48 chars.
- [ ] Unseen context, verify in game: gunho_8165e 欠 "Absent", gunho_819a4 ﾅｸﾞｯﾃ "Punch", gunho_819c4 "  ...",
  table_00168-00194 Melee/Ground/Trailer/Remove, menumv/slps pre-release notice (likely unused).
- [ ] s06_0894 "As it was, it wasn't even a fifth." vague (= the falsified figures cover under a fifth).
- [ ] s35_00c4 sound test "GB2F ... (Battle Screen)": JP repeats 戦闘画面 for the F track (GB1F is 操作画面); kept as JP.
- [ ] s35_09a4 debug credit 田中福岡柴田耕平 rendered "Tanaka Fukuoka Kohei Shibata": JP has no separators, split unverified.
- [ ] s08_03bc drops the "GF Line" alias (only "Martian Maginot Line" kept, 42x3 fit); restore if a wider box comes.
- [ ] ヤー rendered "Yah!" throughout (s08, s20, s26, s33, s34); consider "Yeah!" / "Ja!" in a style pass.
- [ ] Victory/Defeat rows: continuation-line indent is lost when auto-wrap breaks a line itself (e.g. s10 "or wipe out the/enemy", s30_00a4); cosmetic, check on the objective screen in phase 8.
- [x] gunho_821dc 両手利き: "Ambidextrous" ran over the battle Ability box (11 chars, phase 8 shot); "Ambidexter" stays.
- [ ] gunho_8204c ﾗｸﾞﾎﾞｰﾙ "Rug Ball" is a guess at the weapon name; check the weapon in battle.
- [ ] Small-font names still short (D12; the pool names Commando, Tomahawk (C), Apache A/B/A2/B2, Cheyenne, Mustang
  H/D, Rug Ball, 75@Rifle, Critical, Double Tap, Ambidextrous, Fixed, No Equip, Left/Right Arm, Maintenance are back
  in full). Hover box 10 chars: YankApache, CloneDevil, Chrome Dvl, C Dragoon2, SuperCobra, Cmd Ship (slot 11). Slot
  11 (rows 0x1d80-0x1f30, word-only refs, could be pooled like 0x82024): Condenser, Cond Round, 20@MG, 30@MG,
  88D2/88PM/88@/90@/75@ Mag, Shock Atk, Msl Guard; pool rows Dual / Dual W, Morph, Away (欠). Widening the hover box
  (GUNHO.EXE 0x80023040 caller) would restore the first six.
- [ ] Small font at 6 px: STATUS pilot name is centred for 8 px per char, so it sits n px right of centre (patch the
  centring in TABLE.BIN to 3n); weapon-list budget (12) is a guess from the 8-px shot, measure it.
- [ ] Small font: add `.`, `-`, `&`, `'` glyphs (GAMEDATA 265 +0x3274 and the TABLE/MENU.DAT +0x29000 copy) and
  restore "Cmd. Ship", "Anti-Missile", "Chavez & Ralph".
- [x] table_00440 短縮 = "Cut": done another way (D14): row 1 "Fast", row 2 blank; s00_0078 / s05_13c0 say "Fast".
- [ ] Eqip tab Item column cuts names at 8 chars (game limit; JP names fit 8 glyphs): Condenser, 57@Railgun,
  88@Gun L71/L56 (both show "88@Gun L"), Randall Mag, Cond Round, 20@Gatling, 90@HE Gun, Randall 75@. The weapon
  row under the list shows the full name. Fix = raise the copy limit in TABLE.BIN (room for ~9 before the count) or
  8-char names; decide in phase 9.
- [ ] D11 trims (phase 7, lighter wording to fit): s06, s11, s14, s20, s21, s26, s27; story verdicts for those
  chapters (and s00, s05) are stale: re-read in the phase 9 story pass.
