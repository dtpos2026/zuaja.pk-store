"""Round 'Shop by Category' tiles from the studio cut-outs: ivory disc, gold ring, products grouped in the centre.
Usage: python3 -I make_category_tiles.py <out_dir> <name>=<cutout1>,<cutout2>,... ...
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 800
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)


def disc():
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.hypot(x - S * 0.5, y - S * 0.42) / (S * 0.62)
    top = np.array([255, 251, 241]); bot = np.array([241, 226, 196])
    t = np.clip(d, 0, 1)[..., None]
    img = Image.fromarray((top * (1 - t) + bot * t).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S - 1, S - 1), fill=255)
    c = Image.new("RGBA", (S, S), (0, 0, 0, 0)); c.paste(img, (0, 0), m)
    ring = Image.new("RGBA", (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(ring)
    g.ellipse((10, 10, S - 11, S - 11), outline=(196, 147, 47, 255), width=8)
    g.ellipse((26, 26, S - 27, S - 27), outline=(229, 194, 113, 160), width=2)
    c.alpha_composite(ring)
    return c, m


for arg in sys.argv[2:]:
    name, srcs = arg.split("=", 1)
    ps = []
    for s in srcs.split(","):
        p = Image.open(s).convert("RGBA"); ps.append(p.crop(p.getbbox()))
    n = len(ps)
    H = S * (0.66 if n > 1 else 0.64)
    ps = [p.resize((round(p.width * H / p.height), round(H)), Image.LANCZOS) for p in ps]
    gap = (int(S * 0.015) if n == 2 else -int(S * 0.035)) if n > 1 else 0
    total = sum(p.width for p in ps) + gap * (n - 1)
    if total > S * 0.84:
        k = S * 0.84 / total
        ps = [p.resize((round(p.width * k), round(p.height * k)), Image.LANCZOS) for p in ps]
        total = sum(p.width for p in ps) + gap * (n - 1)
    c, mask = disc()
    base = int(S * 0.84)
    # soft floor shadow
    sh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sh).ellipse((S / 2 - total * 0.52, base - 14, S / 2 + total * 0.52, base + 16), fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    shadow = Image.new("RGBA", (S, S), (90, 60, 20, 0)); shadow.putalpha(sh)
    c.alpha_composite(shadow)
    # middle item in front and slightly taller when there are three
    order = list(range(n))
    if n == 3: order = [0, 2, 1]
    xs, x = [], (S - total) // 2
    for p in ps: xs.append(x); x += p.width + gap
    for i in order:
        p = ps[i]
        if n == 3 and i == 1:
            p = p.resize((round(p.width * 1.08), round(p.height * 1.08)), Image.LANCZOS)
            px = xs[i] - round(p.width * 0.04)
        else:
            px = xs[i]
        c.alpha_composite(p, (px, base - p.height))
    clip = Image.new("RGBA", (S, S), (0, 0, 0, 0)); clip.paste(c, (0, 0), mask)
    # transparent corners keep the tile round even without CSS
    clip.save(out / f"{name}.png", optimize=True)
    print(name, (out / f"{name}.png").stat().st_size // 1024, "KB")
