"""Zuaja PK logo files: profile pictures (dark/light), transparent logos, editable SVGs.

Usage: python3 -I make_logo_pack.py <original_logo_image> <out_dir>
"""
import sys
from pathlib import Path

import numpy as np
import potrace
from PIL import Image, ImageDraw, ImageOps

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
(OUT / "editable").mkdir(parents=True, exist_ok=True)
INK = (17, 17, 17)
CREAM = (243, 234, 215)
GOLD_A, GOLD_B = (176, 128, 40), (236, 205, 130)
DARK_BG = (14, 13, 11)

g = ImageOps.exif_transpose(Image.open(SRC)).convert("L")
alpha = ImageOps.invert(g).point(lambda v: 0 if v < 40 else min(255, int((v - 40) * 255 / 180)))
alpha = alpha.crop(alpha.getbbox())
W, H = alpha.size
icon_h = int(H * 0.585)  # top part of the stacked logo is the Z/J mark


def colourise(top_fill, bottom_fill):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    top = top_fill(W, icon_h)
    bot = Image.new("RGBA", (W, H - icon_h), bottom_fill + (255,))
    im.paste(top, (0, 0))
    im.paste(bot, (0, icon_h))
    im.putalpha(alpha)
    return im


def gold(w, h):
    grad = Image.linear_gradient("L").resize((w, h))
    a = Image.new("RGBA", (w, h), GOLD_A + (255,))
    b = Image.new("RGBA", (w, h), GOLD_B + (255,))
    return Image.composite(a, b, grad)


def solid(c):
    return lambda w, h: Image.new("RGBA", (w, h), c + (255,))


light_logo = colourise(solid(INK), INK)
dark_logo = colourise(gold, CREAM)
for name, im in [("zuaja-logo-for-light-background", light_logo), ("zuaja-logo-for-dark-background", dark_logo)]:
    big = im.resize((2000, round(H * 2000 / W)), Image.LANCZOS)
    big.save(OUT / "editable" / f"{name}.png", optimize=True)


def profile(bg, logo_im, name):
    S = 1080
    c = Image.new("RGBA", (S, S), bg + (255,))
    w = int(S * 0.56)  # stays inside a round crop
    lg = logo_im.resize((w, round(H * w / W)), Image.LANCZOS)
    c.alpha_composite(lg, ((S - lg.width) // 2, (S - lg.height) // 2))
    c.convert("RGB").save(OUT / name, optimize=True)
    return c


profile(DARK_BG, dark_logo, "zuaja-profile-dark-1080.png")
profile((255, 255, 255), light_logo, "zuaja-profile-light-1080.png")

# vector trace: two groups (mark and wordmark) so colours can be changed separately
bitmap = np.asarray(alpha) > 110


def trace(mask):
    paths = potrace.Bitmap(mask).trace(turdsize=6, alphamax=1.0, opttolerance=0.2)
    out = []
    for curve in paths:
        s = curve.start_point
        d = [f"M{s.x:.1f},{s.y:.1f}"]
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f},{seg.c.y:.1f}L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        d.append("Z")
        out.append("".join(d))
    return " ".join(out)


top_mask = bitmap.copy()
top_mask[icon_h:, :] = False
bot_mask = bitmap.copy()
bot_mask[:icon_h, :] = False
d_top, d_bot = trace(top_mask), trace(bot_mask)


def svg(mark_fill, word_fill, bg=None, size=None, defs=""):
    if size:
        S = size
        w = S * 0.56
        k = w / W
        tx, ty = (S - w) / 2, (S - H * k) / 2
        head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">{defs}'
        body = (f'<rect id="background" width="{S}" height="{S}" fill="{bg}"/>' if bg else "")
        body += f'<g transform="translate({tx:.1f},{ty:.1f}) scale({k:.5f})">'
    else:
        head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}'
        body = "<g>"
    body += f'<g id="logo-mark"><path fill-rule="evenodd" fill="{mark_fill}" d="{d_top}"/></g>'
    body += f'<g id="logo-wordmark"><path fill-rule="evenodd" fill="{word_fill}" d="{d_bot}"/></g></g>'
    return head + body + "</svg>\n"


gold_defs = '<defs><linearGradient id="gold-gradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b08028"/><stop offset="1" stop-color="#eccd82"/></linearGradient></defs>'
(OUT / "editable" / "zuaja-logo-for-light-background.svg").write_text(svg("#111111", "#111111"), encoding="utf-8")
(OUT / "editable" / "zuaja-logo-for-dark-background.svg").write_text(svg("url(#gold-gradient)", "#f3ead7", defs=gold_defs), encoding="utf-8")
(OUT / "editable" / "zuaja-profile-dark-template.svg").write_text(svg("url(#gold-gradient)", "#f3ead7", bg="#0e0d0b", size=1080, defs=gold_defs), encoding="utf-8")
(OUT / "editable" / "zuaja-profile-light-template.svg").write_text(svg("#111111", "#111111", bg="#ffffff", size=1080), encoding="utf-8")

(OUT / "README.md").write_text("""# Zuaja PK: logo aur profile files

| File | Kis ke liye |
| --- | --- |
| `zuaja-profile-dark-1080.png` | **Facebook, Instagram, TikTok profile picture (yehi lagayein).** Kaali background, gold nishaan + cream huroof. |
| `zuaja-profile-light-1080.png` | Safed background wali version: Highlights ke covers, safed ads, packaging card. |
| `editable/zuaja-profile-dark-template.svg` | Profile picture ka editable template (rang badalne ke liye). |
| `editable/zuaja-profile-light-template.svg` | Light version ka editable template. |
| `editable/zuaja-logo-for-light-background.svg` / `.png` | Sirf logo (transparent background), safed ya halki background par. |
| `editable/zuaja-logo-for-dark-background.svg` / `.png` | Sirf logo (transparent background), kaali ya gehri background par. |

## Rang kaise badlein

* **Canva:** Upload par SVG file dalein, logo par click karein, upar "Colors" se rang badlein.
* **Illustrator, Affinity, Inkscape, Figma:** SVG khulti hai; shapes vector hain.
* File ke andar hisse (groups) hain: `background` (profile templates mein), `logo-mark` (upar Z/J ka nishaan) aur `logo-wordmark` ("ZUAJA.PK" aur "POWERED BY SK"). Gold ka gradient `gold-gradient` mein hai; sada rang chahiye to us hisse ka fill ek rang kar dein.
* Logo gol crop mein kata na jaye is liye profile picture mein woh darmiyan mein chhota rakha gaya hai.

## Dhyan dein

Ye vectors aap ki di hui original logo tasveer (1254 pixel) se trace kiye gaye hain. Profile, post aur ads mein saaf aur tez hain, lekin bohat bade banner par kinaron par chhoti si na-hamwari ho sakti hai. Agar original logo ki asli vector file (AI, SVG, EPS) mile to wahi master banegi.
""", encoding="utf-8")
print("ok")
