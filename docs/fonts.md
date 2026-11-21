# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/font5.txt | drawn for this project (2026-11-21) | MIT, same as repo | yes | digraph glyphs of both 11x11 fonts (tools/digraph.py) | - |
| fonts/DejaVuSans-Bold.ttf | DejaVu Fonts 2.37 as shipped in matplotlib 3.8.3 (mpl-data/fonts/ttf), https://dejavu-fonts.github.io | Bitstream Vera licence + public-domain DejaVu changes (fonts/LICENSE_DEJAVU) | yes: rendered pixels only go into the patch (the licence allows embedding; the TTF itself isn't shipped) | prologue history captions in FACE.DAT (tools/gfx_captions.py) | none |
