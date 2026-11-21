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
