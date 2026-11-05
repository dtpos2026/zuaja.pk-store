"""Category banners (2172x724, 3:1) built from real product cut-outs.

The left 45% stays calm ivory (the theme overlays the title there); products stand on a
gold-edged ivory plinth on the right with soft contact shadows and a warm light falloff.
Usage: python3 -I make_category_banners.py <cut_dir> <out_dir>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

CUT, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
W, H = 2172, 724
IVORY = (251, 247, 237)
WARM = (242, 228, 196)
GOLD = (183, 138, 49)
GOLD_L = (229, 194, 113)

# relative real-world heights so bottles, jars and bars sit in believable proportion
REL = {"amla": 1.0, "haldi": 0.95, "rosemary": 0.9, "herbal7": 0.9, "neemwash": 0.86, "lavender": 0.86,
       "facewash": 0.72, "zafarani": 0.4, "whiteoud": 0.62, "signature": 0.7, "unisex": 0.66,
       "rosesoap": 0.42, "neemsoap": 0.45}

SETS = {
    "shampoos": ["haldi", "amla"],
    "hair-oils": ["herbal7", "rosemary"],
    "perfumes": ["unisex", "whiteoud", "signature"],
    "bath-body": ["neemsoap", "lavender", "neemwash", "rosesoap"],
    "hair-care": ["haldi", "rosemary", "amla", "herbal7"],
    "skin-care": ["zafarani", "facewash"],
    "soaps": ["rosesoap", "neemsoap"],
}


def backdrop():
    c = Image.new("RGBA", (W, H), IVORY + (255,))
    # warm light falling from the upper right
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse((W * 0.5, -H * 0.5, W * 1.2, H * 1.2), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(170))
    c = Image.composite(Image.new("RGBA", (W, H), WARM + (255,)), c, mask)
    # thin gold arc behind the products
    arc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(arc).ellipse((W * 0.6, H * 0.06, W * 0.6 + H * 1.05, H * 1.11), outline=GOLD_L + (150,), width=4)
    c.alpha_composite(arc)
    return c


def plinth(c, x0, x1, top):
    d = ImageDraw.Draw(c)
    sm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sm).rectangle((x0 + 10, top + 24, x1 + 26, H), fill=70)
    c.paste(Image.new("RGBA", (W, H), (60, 40, 10, 255)), (0, 0), sm.filter(ImageFilter.GaussianBlur(24)))
    d.rectangle((x0, top, x1, H), fill=(246, 238, 220))
    d.rectangle((x0, top, x1, top + 12), fill=(236, 224, 196))
    d.line((x0, top, x1, top), fill=GOLD, width=4)


def load(k, h):
    p = Image.open(CUT / f"{k}.png").convert("RGBA")
    p = p.crop(p.getbbox())
    return p.resize((max(1, round(p.width * h / p.height)), round(h)), Image.LANCZOS)


def build(name, keys):
    c = backdrop()
    top = int(H * 0.86)
    x0, x1 = int(W * 0.56), int(W * 0.97)
    plinth(c, x0, x1, top)
    max_h = H * 0.80
    imgs = [load(k, max_h * REL[k]) for k in keys]
    gap = 28
    total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    avail = (x1 - x0) * 0.9
    if total > avail:
        k = avail / total
        imgs = [i.resize((round(i.width * k), round(i.height * k)), Image.LANCZOS) for i in imgs]
        gap *= k
        total = avail
    x = (x0 + x1) / 2 - total / 2
    base = top + 8
    for im in imgs:
        sm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sm).ellipse((x - 6, base - 14, x + im.width + 6, base + 16), fill=120)
        c.paste(Image.new("RGBA", (W, H), (50, 32, 8, 255)), (0, 0), sm.filter(ImageFilter.GaussianBlur(12)))
        c.alpha_composite(im, (int(x), int(base - im.height)))
        x += im.width + gap
    c.convert("RGB").save(OUT / f"zuaja-category-{name}-wide-v3.png", optimize=True)


for n, k in SETS.items():
    build(n, k)
print("ok")
