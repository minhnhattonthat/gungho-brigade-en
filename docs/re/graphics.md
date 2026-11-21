# Graphics text survey (phase 1 done 2026-11-21)

**Japanese drawn as graphics (redraw list):** (1) FACE.DAT prologue history stills, ~23 captions (below);
(2) GAMEDATA entry 265 +0x131c battle command-menu labels (12); (3) small 8x12 font half-width kana, GAMEDATA
entry 265 +0x3274 and TABLE/MENU.DAT +0x29000 (only if names need extra glyphs; Latin already present);
(4) TABLE/MENU.DAT +0x18800 `体験版` (likely unused, confirm). Everything else surveyed is English or textless.

Static sweep: `python -X utf8 tools/timscan.py work/gfx/sweep <files>` (run from work/disc/tree) renders every TIM
into labelled sheets + `index.tsv`. Run 2026-11-21 over TABLE.BIN, MOVIE.BIN, ENDING.BIN, GAMEDATA.DAT,
TABLE/{MENU,OVTABLE,OPENING}.DAT, SCENFILE.DAT, FACE.DAT, MENU.EXE, GUNHO.EXE: 5,493 TIMs, 45 sheets.
No TIMs in GUNHO.EXE, MENU*.EXE, MOVIE.BIN, ENDING.BIN. Skipped: 24-bpp TIMs and images under 16x16 in both
dimensions (printed by the script; GAMEDATA has ~1,000 8x8/12x12 ones that are icons/glyphs - review in a second pass
with `--min 8`).

## Sheets reviewed
| Sheet | Japanese found | Notes |
|---|---|---|
| MENU_DAT_00 (TABLE/MENU.DAT) | +0x18800 `体験版` ("Trial version", 80x32 4bpp) - probably unused in retail; +0x29000 small font 128x132 4bpp has half-width katakana rows (name entry / save font) | logo, title menu, GAME SAVE / TUNE UP / STATUS / NEXT TALE, MOVIE COMMAND, PLAY EP/SP, MOVIE LOAD, EXIT, Now loading: all English already |

| FACE_DAT_00-25 (FACE.DAT) | **prologue history stills with burned-in SJIS captions** (8bpp 320x240, mostly greyscale fades of colour stills): 0x23e000 西暦2220年、火星地球化計画完了 · 0x251000 同年、火星暦(Mars Century)制定 · 0x28a000 火星暦46年、外惑星自治区へ食料輸出開始 · 0x29d000 同年、軌道エレベーター『アーツタノフ』着工 · 0x2d6000 81年、外惑星自治区、地球連邦より離脱 · 0x2e9000 同年、外惑星連合成立 · 0x2fc000 100年、火星諸州連合、火星政府樹立を宣言 · 0x335000 149年、ガラクタ(ジャンク)発見 · 0x348000 ジャンクス・ラッシュの発生 · 0x381000 150年、火星総人口150万人を突破 · 0x394000 156年、ホイヘンス地下湖発見 · 0x3cd000 163年、火星内戦(通称、水戦争)勃発。… · 0x3e0000 165年、地球連邦平和実施軍、内戦に干渉。… · 0x419000 同年、薬物中毒(ジャンキー)マシンレッグ目撃事件… · 0x42c000 消息不明マシンレッグの機数が… · 0x465000 166年、南部連合101騎兵旅団、… · 0x478000 同旅団壊滅。南部諸州、停戦に合意。 · 0x48b000 火星内戦終結。 · 0x4ea000 104年、『アーツタノフ』完成 · 0x4fd000 同年、火星連合、地球連邦より独立 · 0x510000 105年、『アーツタノフ』999地球年租借条約締結 · 0x549000 / 0x55c000 火星暦168年. ~23 stills; offsets read off 2x-downscaled composites (work/gfx/comp/c0-c1): confirm each with a zoomed render before redrawing. | Everything else English or textless: logo stills "GUNGHO BRIGADE", 0x22b000 "3on3 RUG BATTLE TOURNAMENT", "CLASSIFIED", "WIZARD" screens, map W-markers, all 26 tale cards (0xf8b800-0x1354800, "tale N <title>"), "Tune in to the Next Tale" maps with English place names (0x13b3800-0x151c800), "Game over" / "Map clear!" (0xd4000/0xd6000), Sign / TOMY logos. Portraits (84x82) textless. |
| GAMEDATA entry 265 (0x36081c-0x36c17e, battle UI; rendered work/gfx/gd265) | **+0x131c 96x140 4bpp: battle command menu labels** 射撃 格闘 アイテム 変形 特殊 装備 終了 / ユニットリスト セーブ シナリオ目的 コンフィグ プロット終了 (12 labels, 2 blank buttons). +0x3274 128x132: small 8x12 name font (ASCII digits/A-Z/a-z + half-width kana, text.md) | +0x63ca 256x64 status-window labels (Pilot Unit1 Unit2 Eqip Level Exp Gunshot Fight Mobility Ability Skill HP Armor Move Property Weapon Power Range Ammo Damage Part Item) English already; icons, ON/OFF, Power/Range/Hit/SP boxes English; +0x7e4 (file 0x361000) 52x98 battle-menu icon set (SP GO END) English. The command-label TIM exists only here (pixel search over every disc file: one hit, GAMEDATA 0x361b78). The TABLE/MENU.DAT +0x29000 TIM (+0x291e4 was inside it) is a byte-identical copy of the small font, not the labels: redraw/extend both copies together |
| GAMEDATA_DAT rest (`--min 8 --dedupe --zoom 2`, work/gfx/gd2, 22 sheets, all reviewed 2026-11-21 via 2x2 composites work/gfx/comp/gd_0-4) | none | entries 0-264 = unit model textures (decals "101", "BRIGADE101", "GUNGHO BRIGADE", star emblem: English), 0x262800-0x27e800 80x80 8bpp pilot portraits (textless), effects. Every gd2 TIM is below 0x36c17e (entry 265 end) |
| SCENFILE_DAT_00-12 (work/gfx/sweep, composites comp/c7-c8 + sheet 12) | none | map tiles, skyboxes, terrain; town building signs English ("BUFFALO BILL'S INN", "WONDER WORLD", "BLACKSMITH'S SHOP", "YOUNGER'S RENT", "MARS GRAND LINE", "Sign/TONY/SOMY") |
| Between-tale menu screens (GAME SAVE / TUNE UP / STATUS / NEXT TALE) | static TIMs English (MENU_DAT_00); runtime text unchecked | reach with the phase-2 debug tool and confirm in game (phase 8 tour) |
| OPENING/OVTABLE/TABLE_BIN | see below | |

Battle-screen VRAM (work/qa/vram1, `tools/psxvram.py` renders a dump): UI texture page at VRAM x=320 y=0 4bpp holds
entry 265's TIMs. Name/ability text is the small font, help line the 11x11 kanji font (text.md).

## Seen in game (tour, original disc)
| Screen | Japanese | Source guess |
|---|---|---|
| Battle unit status window (tale 1, explore3 f001680) | pilot name, ability/skill names, help line | **verified** text, not graphics: names = half-width cp932 (small font), help line = SJIS (11x11 font); labels English TIM |
| Battle command menu (tale 1, explore3 f001440) | 射撃 格闘 ... | **verified** TIM: GAMEDATA entry 265 +0x131c (matched VRAM bytes to file) |
| Unit name plate under portrait (explore3 f002160) | katakana name | small font, half-width string (same renderer as status window) - **guess** |
| Tutorial message box | SCENFILE text (font-drawn) | text, not graphics |
