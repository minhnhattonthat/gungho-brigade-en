Gungho Brigade - English translation patch v{VERSION}
=====================================================

Unofficial English fan translation of Gungho Brigade (PlayStation, Tomy, 2000, SLPS-01902).
https://github.com/minhnhattonthat/gungho-brigade-en

This zip holds only the patch ({PATCH}) and this README. No game data is included, and
pre-patched images will never be provided: you need your own dump of the Japanese disc.

BASE IMAGE (Redump "Gungho Brigade (Japan)", single track, MODE2/2352)
  File:   Gungho Brigade (Japan).bin
  Size:   706,362,048 bytes
  CRC32:  F974BD94
  MD5:    32db47ab49de10a964361a862a89789c
  SHA-1:  695ccbdad4a0f20ca59cd0e662bb883073f45b7c
Any other dump (another revision, a different track layout, an already-patched copy) will not work.

PATCHING
  1. Apply {PATCH} to "Gungho Brigade (Japan).bin" with xdelta3 or Delta Patcher
     (https://github.com/marco-calautti/DeltaPatcher):
       xdelta3 -d -s "Gungho Brigade (Japan).bin" {PATCH} "Gungho Brigade (English).bin"
  2. Copy the original .cue next to the new .bin, rename it to "Gungho Brigade (English).cue"
     and change the FILE line inside it to "Gungho Brigade (English).bin".
  3. Check the result:  CRC32 {PATCHED_CRC32}
                        SHA-1 {PATCHED_SHA1}

PLAYING
  Tested in PCSX-Redux (nightly 32338.20261121.15) with the SCPH-5500 BIOS. Boot the patched disc from a cold
  start; savestates made with the Japanese disc carry its old text and code. Start a new game: memory-card saves
  from the Japanese game are untested. Confirm is Circle, as in the original.

WHAT IS TRANSLATED
  Story dialogue, briefings, victory/defeat conditions, tutorials ........ English
  Menus, unit/weapon/ability names, help lines, memory-card messages ..... English
  Title screen, game over, battle command buttons, prologue captions ..... English (redrawn)
  Staff roll ............................................................. English
  Video cutscenes and voiced lines ....................................... Japanese audio, no subtitles

KNOWN ISSUES
  - The battle hover box holds 10 characters, so a few unit names run words together or drop letters
    (YankApache, CloneDevil, Chrome Dvl, C Dragoon2, SuperCobra, Cmd Ship).
  - The Eqip tab Item column shows 8 characters, as in the Japanese; the row under the list shows the full name.
  - Readings of some staff names in the credits are best guesses.
  Report bugs (with a savestate or memory card if you can):
  https://github.com/minhnhattonthat/gungho-brigade-en/issues

CREDITS
  Translation, hacking and tools: minhnhattonthat.
  Made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
  Fonts: a 5-px pixel font drawn for this project; DejaVu Sans Bold (Bitstream Vera licence) for the prologue
  captions.
  Gungho Brigade is (c) Tomy. This is an unofficial fan work, not affiliated with Tomy.
