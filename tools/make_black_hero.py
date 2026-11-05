"""Black-background product shots in the style of the client's samples (1024x1536, product centred,
full height, no floor). Dark bottles get a soft rim light so they separate from the black.

Usage: python3 -I make_black_hero.py <out_dir> <logo_for_dark_png> <key>=<cutout.png> ...
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageFilter

OUT, LOGO = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1024, 1536


def rim(p):
    a = p.getchannel("A")
    grow = a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(10))
    edge = ImageChops.subtract(grow, a.filter(ImageFilter.MinFilter(3)))
    edge = edge.point(lambda v: int(v * 0.55))
    glow = Image.new("RGBA", p.size, (235, 225, 205, 0))
    glow.putalpha(edge)
    return glow


def place(p):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    p = p.crop(p.getbbox())
    r = min(H * 0.90 / p.height, W * 0.80 / p.width)
    p = p.resize((round(p.width * r), round(p.height * r)), Image.LANCZOS)
    pad = 40
    big = Image.new("RGBA", (p.width + pad * 2, p.height + pad * 2), (0, 0, 0, 0))
    big.paste(p, (pad, pad))
    lum = np.asarray(p.convert("L"), np.float32)[np.asarray(p.getchannel("A")) > 128].mean()
    x, y = (W - big.width) // 2, (H - big.height) // 2
    if lum < 110:  # dark product: add rim light so it reads on black
        c.alpha_composite(rim(big), (x, y))
    c.alpha_composite(big, (x, y))
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    w = int(W * 0.2)
    lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.6)))
    m = int(W * 0.035)
    c.alpha_composite(lg, (W - w - m, H - lg.height - m))
    return c.convert("RGB")


for arg in sys.argv[3:]:
    key, src = arg.split("=", 1)
    place(Image.open(src).convert("RGBA")).save(OUT / f"{key}.jpg", quality=92, optimize=True, progressive=True)
    print(key)
