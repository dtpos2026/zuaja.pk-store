"""Studio-style e-commerce packshots from real product cut-outs (label pixels are never regenerated).

Retouch: white balance from the product's own pixels, gentle contrast/clarity, edge feather.
Staging: pure white 1500x1500, product centred at ~80% height, soft contact shadow and a faint
floor reflection, like a studio shoot.
Usage: python3 -I make_studio.py <out_dir> <key>=<cutout.png>[:raw] ...
  ":raw" skips colour retouching (for images that are already retouched).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
S = 1500


def retouch(p):
    rgb = p.convert("RGB")
    a = np.asarray(p.getchannel("A")) > 200
    arr = np.asarray(rgb).astype(np.float32)
    if a.sum() > 500:
        px = arr[a]
        lo, hi = np.percentile(px, 0.6, axis=0), np.percentile(px, 99.4, axis=0)
        arr = np.clip((arr - lo) / np.maximum(hi - lo, 1) * 255, 0, 255)
        m = arr[a].mean(0)
        arr = np.clip(arr * (m.mean() / m) ** 0.6, 0, 255)  # partial gray-world: keeps product colour honest
    rgb = Image.fromarray(arr.astype(np.uint8))
    rgb = ImageEnhance.Color(rgb).enhance(1.08)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.04)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    out = rgb.convert("RGBA")
    out.putalpha(p.getchannel("A"))
    return out


def feather(p):
    a = p.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    p = p.copy()
    p.putalpha(a)
    return p


def stage(p):
    c = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    p = p.crop(p.getbbox())
    r = min(S * 0.80 / p.height, S * 0.62 / p.width)
    p = p.resize((round(p.width * r), round(p.height * r)), Image.LANCZOS)
    x = (S - p.width) // 2
    base = int(S * 0.86)
    y = base - p.height
    # faint reflection
    refl = p.transpose(Image.FLIP_TOP_BOTTOM)
    rh = int(p.height * 0.22)
    refl = refl.crop((0, 0, p.width, rh))
    grad = Image.linear_gradient("L").resize((p.width, rh)).point(lambda v: int((255 - v) * 0.16))
    refl.putalpha(ImageChops.multiply(refl.getchannel("A"), grad))
    c.alpha_composite(refl, (x, base + 2))
    # contact shadow + soft ambient shadow
    for spread, blur, alpha in ((0.55, 40, 60), (0.98, 10, 120)):
        m = Image.new("L", (S, S), 0)
        w = p.width * spread
        ImageDraw.Draw(m).ellipse((S / 2 - w / 2 - 20, base - 10, S / 2 + w / 2 + 20, base + 14), fill=alpha)
        c.paste(Image.new("RGBA", (S, S), (40, 32, 24, 255)), (0, 0), m.filter(ImageFilter.GaussianBlur(blur)))
    c.alpha_composite(p, (x, y))
    return c.convert("RGB")


for arg in sys.argv[2:]:
    key, src = arg.split("=", 1)
    raw = src.endswith(":raw")
    src = src[:-4] if raw else src
    p = Image.open(src).convert("RGBA")
    p = feather(p if raw else retouch(p))
    stage(p).save(OUT / f"{key}.png", optimize=True)
    print(key)
