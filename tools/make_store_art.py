"""Store artwork in Zuaja branding (ivory, ink, gold): hero slides (desktop + mobile),
category circles and promo banners, built from the real retouched product cut-outs.

Usage: python3 -I make_store_art.py <cutouts_dir> <logo_light_png> <fonts_dir> <out_dir>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

CUT, LOGO, FONTS, OUT = (Path(p) for p in sys.argv[1:5])
OUT.mkdir(parents=True, exist_ok=True)
IVORY = (251, 246, 236)
IVORY2 = (242, 230, 204)
INK = (23, 23, 23)
GOLD = (176, 128, 40)
GOLD_L = (229, 194, 113)

REL = {"amla-reetha-shampoo-200ml": 1.0, "haldi-badam-shampoo-100ml": 0.92, "rosemary-hair-scalp-oil-100ml": 0.88,
       "7-herbal-oils-blend-100ml": 0.88, "zuaja-pk-herbal-face-wash-haldi-80-ml": 0.8, "zafarani-cream": 0.46,
       "neem-handwash-bodywash-100ml": 0.9, "zuaja-pk-lavender-hand-body-wash-with-lavender-extract-100-ml": 0.9,
       "rose-body-wash-100ml": 0.9, "rose-soap": 0.42, "neem-soap": 0.44,
       "zuaja-pk-premium-white-oud-perfume-50-ml": 0.72, "zuaja-pk-premium-perfume-50-ml": 0.74, "premium-perfume": 0.7,
       "zuaja-pk-premium-white-oud-perfume-tester": 0.5}


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONTS / f"{name}.ttf"), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


ACCENT = (240, 214, 160)


def bg(W, H, glow_x=0.68, glow_y=0.5, accent=None):
    """White light theme with a soft pastel glow behind the products."""
    acc = np.array(accent or ACCENT, np.float32)
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    base = np.ones((H, W, 3), np.float32) * 255
    d = np.sqrt(((x - glow_x) * W / H) ** 2 + (y - glow_y) ** 2)
    t = (np.clip(1 - d / 0.62, 0, 1) ** 1.6)[..., None] * 0.55
    img = base * (1 - t) + acc * t
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")


def load(k, h):
    p = Image.open(CUT / f"{k}.png").convert("RGBA")
    p = p.crop(p.getbbox())
    return p.resize((max(1, round(p.width * h / p.height)), round(h)), Image.LANCZOS)


def group(c, keys, cx, base, max_h, max_w):
    ims = [load(k, max_h * (REL.get(k, 0.85) if len(keys) > 1 else 1.0)) for k in keys]
    gap = max_w * 0.025
    total = sum(i.width for i in ims) + gap * (len(ims) - 1)
    if total > max_w:
        s = max_w / total
        ims = [i.resize((max(1, round(i.width * s)), max(1, round(i.height * s))), Image.LANCZOS) for i in ims]
        gap *= s
        total = max_w
    W, H = c.size
    # gold ring + plinth line behind the group
    tall = max(i.height for i in ims)
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cyr = base - tall * 0.55
    r = min(max(total * 0.55, tall * 0.62), cyr - 6, H - cyr - 6)
    ImageDraw.Draw(ring).ellipse((cx - r, cyr - r, cx + r, cyr + r), outline=GOLD_L + (160,), width=max(2, W // 700))
    c.alpha_composite(ring)
    x = cx - total / 2
    for i in ims:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse((x - 6, base - 10, x + i.width + 6, base + 12), fill=120)
        c.paste(Image.new("RGBA", (W, H), (70, 55, 30, 255)), (0, 0), m.filter(ImageFilter.GaussianBlur(10)))
        refl = i.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, i.width, int(i.height * 0.16)))
        g = Image.linear_gradient("L").resize(refl.size).point(lambda v: int((255 - v) * 0.16))
        refl.putalpha(ImageChops.multiply(refl.getchannel("A"), g))
        c.alpha_composite(refl, (int(x), int(base + 1)))
        c.alpha_composite(i, (int(x), int(base - i.height)))
        x += i.width + gap


def text_block(c, x, y, kicker, title_lines, sub, cta, scale, align="left", max_w=None):
    d = ImageDraw.Draw(c)
    fk = font("Jost", int(26 * scale), 600)
    ft = font("Cinzel", int(70 * scale), 600)
    fs = font("Jost", int(30 * scale), 400)
    fb = font("Jost", int(26 * scale), 600)

    def put(txt, f, fill, yy, tracking=0.0):
        w = sum(d.textlength(ch, font=f) for ch in txt) + f.size * tracking * (len(txt) - 1)
        xx = x if align == "left" else x - w / 2
        for ch in txt:
            d.text((xx, yy), ch, font=f, fill=fill)
            xx += d.textlength(ch, font=f) + f.size * tracking
        return w

    put(kicker.upper(), fk, GOLD, y, 0.2)
    y += int(52 * scale)
    for line in title_lines:
        while max_w and d.textlength(line, font=ft) > max_w and ft.size > 30:
            ft = font("Cinzel", ft.size - 2, 600)
        put(line, ft, INK, y, 0.01)
        y += int(ft.size * 1.12)
    y += int(10 * scale)
    put(sub, fs, (80, 70, 52), y)
    y += int(66 * scale)
    w = d.textlength(cta.upper(), font=fb) + fb.size * 0.15 * len(cta) + 90 * scale
    h = int(72 * scale)
    bx = x if align == "left" else x - w / 2
    d.rounded_rectangle((bx, y, bx + w, y + h), radius=h // 2, fill=INK)
    tx = bx + 45 * scale
    for ch in cta.upper():
        d.text((tx, y + (h - fb.size) / 2 - 4 * scale), ch, font=fb, fill=GOLD_L)
        tx += d.textlength(ch, font=fb) + fb.size * 0.15


ACC = {"hair": (236, 196, 128), "skin": (246, 214, 120), "bath": (240, 190, 205), "perf": (226, 206, 160), "oil": (226, 180, 110), "soap": (210, 226, 196)}
SLIDES = [
    ("slide-hair-care", "Hair Care", ["Desi Hair Care"], "Haldi + Badam · Amla Reetha · Rosemary · 7 Herbal Oils", "Shop Hair Care", "hair",
     ["haldi-badam-shampoo-100ml", "amla-reetha-shampoo-200ml", "rosemary-hair-scalp-oil-100ml", "7-herbal-oils-blend-100ml"]),
    ("slide-skin-care", "Skin Care", ["Glow, The Desi Way"], "Herbal Face Wash + Haldi · Zafarani Cream", "Shop Skin Care", "skin",
     ["zuaja-pk-herbal-face-wash-haldi-80-ml", "zafarani-cream"]),
    ("slide-bath-body", "Bath & Body", ["Fresh Every Day"], "Rose · Neem · Lavender hand & body washes", "Shop Bath & Body", "bath",
     ["rose-body-wash-100ml", "neem-handwash-bodywash-100ml", "zuaja-pk-lavender-hand-body-wash-with-lavender-extract-100-ml"]),
    ("slide-perfumes", "Fragrance", ["Zuaja Perfumes"], "White Oud · Signature · Unisex", "Shop Perfumes", "perf",
     ["premium-perfume", "zuaja-pk-premium-white-oud-perfume-50-ml", "zuaja-pk-premium-perfume-50-ml"]),
]

CATS = [
    ("cat-shampoos", "hair", ["amla-reetha-shampoo-200ml", "haldi-badam-shampoo-100ml"]),
    ("cat-hair-oils", "oil", ["7-herbal-oils-blend-100ml", "rosemary-hair-scalp-oil-100ml"]),
    ("cat-skin-care", "skin", ["zuaja-pk-herbal-face-wash-haldi-80-ml", "zafarani-cream"]),
    ("cat-bath-body", "bath", ["rose-body-wash-100ml", "neem-handwash-bodywash-100ml"]),
    ("cat-soaps", "soap", ["rose-soap", "neem-soap"]),
    ("cat-perfumes", "perf", ["zuaja-pk-premium-white-oud-perfume-50-ml", "zuaja-pk-premium-perfume-50-ml"]),
]


def main():
    for name, kicker, title, sub, cta, ak, keys in SLIDES:
        W, H = 1920, 760
        c = bg(W, H, accent=ACC[ak])
        group(c, keys, W * 0.70, H * 0.88, H * 0.74, W * 0.44)
        text_block(c, int(W * 0.07), int(H * 0.24), kicker, title, sub, cta, 1.0, max_w=W * 0.42)
        c.convert("RGB").save(OUT / f"zuaja-{name}-desktop.jpg", quality=88, optimize=True, progressive=True)
        W, H = 1080, 1350
        c = bg(W, H, 0.5, 0.62, accent=ACC[ak])
        group(c, keys, W / 2, H * 0.93, H * 0.46, W * 0.86)
        text_block(c, W // 2, int(H * 0.07), kicker, title, sub, cta, 1.05, align="center", max_w=W * 0.9)
        c.convert("RGB").save(OUT / f"zuaja-{name}-mobile.jpg", quality=88, optimize=True, progressive=True)
    for name, ak, keys in CATS:
        S = 800
        c = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        m = Image.new("L", (S, S), 0)
        ImageDraw.Draw(m).ellipse((0, 0, S - 1, S - 1), fill=255)
        circ = bg(S, S, 0.5, 0.55, accent=ACC[ak])
        c.paste(circ, (0, 0), m)
        ImageDraw.Draw(c).ellipse((6, 6, S - 7, S - 7), outline=GOLD_L + (255,), width=6)
        inner = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        group_img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        tmp = bg(S, S)
        tmp.putalpha(0)
        soapy = ak == "soap"
        group(group_img, keys, S / 2, S * (0.66 if soapy else 0.80), S * (0.42 if soapy else 0.58), S * 0.70)
        c.alpha_composite(group_img)
        out = Image.new("RGBA", (S, S), (255, 255, 255, 0))
        out.paste(c, (0, 0), m)
        out.save(OUT / f"zuaja-{name}.png", optimize=True)
    print("ok")


if __name__ == "__main__":
    main()
