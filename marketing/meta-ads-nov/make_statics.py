"""Static Meta ad creatives in the Zuaja store branding (ivory, ink, gold).

For every product in products.json: feed 4:5 (1080x1350) and story/reel 9:16 (1080x1920),
each in a "sale" variant (11.11 ribbon, ends 15 Nov) and an "evergreen" variant.
Plus line-up creatives per category. Run from the repo root:
    python3 -I marketing/meta-ads-nov/make_statics.py
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "statics"
FONTS = HERE / "fonts"
LOGO = ROOT / "brand/zuaja-logo-horizontal-1600.png"

INK = (23, 23, 23)
GOLD = (196, 147, 47)
GOLD_L = (229, 194, 113)
IVORY = (251, 246, 236)
CREAM = (243, 231, 207)
RED = (176, 38, 38)


def font(name, size, var=None):
    f = ImageFont.truetype(str(FONTS / f"{name}.ttf"), size)
    if var:
        f.set_variation_by_name(var)
    return f


def money(v):
    return f"Rs {v:,}"


def bg(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot((x - w * 0.5) / w, (y - h * 0.46) / h) * 1.7
    t = np.clip(d, 0, 1)[..., None]
    a = np.array([255, 252, 245], np.float32); b = np.array(CREAM, np.float32)
    im = Image.fromarray((a * (1 - t) + b * t).astype(np.uint8)).convert("RGBA")
    return im


def load_cutout(path):
    p = Image.open(ROOT / path).convert("RGBA")
    # crop to visible pixels only (faint alpha noise would make the product look off-centre)
    return p.crop(p.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())


def fit(p, maxw, maxh):
    k = min(maxw / p.width, maxh / p.height)
    return p.resize((round(p.width * k), round(p.height * k)), Image.LANCZOS)


def glow_disc(c, cx, cy, r):
    g = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 255))
    g = g.filter(ImageFilter.GaussianBlur(r * 0.18)); c.alpha_composite(g)
    ring = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ring)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD_L + (200,), width=4)
    d.ellipse((cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18), outline=GOLD_L + (90,), width=2)
    c.alpha_composite(ring)


def shadow(c, cx, base, w):
    s = Image.new("L", c.size, 0)
    ImageDraw.Draw(s).ellipse((cx - w * 0.55, base - 16, cx + w * 0.55, base + 20), fill=110)
    s = s.filter(ImageFilter.GaussianBlur(20))
    layer = Image.new("RGBA", c.size, (60, 40, 10, 0)); layer.putalpha(s); c.alpha_composite(layer)


def text_c(d, cx, y, s, f, fill, anchor="ma"):
    d.text((cx, y), s, font=f, fill=fill, anchor=anchor)


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def logo(c, cx, y, w):
    lg = Image.open(LOGO).convert("RGBA"); lg = lg.crop(lg.getbbox())
    lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    c.alpha_composite(lg, (cx - w // 2, y))
    return lg.height


def chip(c, x, y, s, f):
    d = ImageDraw.Draw(c)
    tw = d.textlength(s, font=f); w = int(tw + 92); h = 64
    d.rounded_rectangle((x, y, x + w, y + h), radius=32, fill=(255, 255, 255, 235), outline=GOLD_L, width=2)
    d.ellipse((x + 14, y + 14, x + 50, y + 50), fill=GOLD)
    d.line((x + 23, y + 33, x + 30, y + 40), fill="white", width=4); d.line((x + 30, y + 40, x + 42, y + 24), fill="white", width=4)
    d.text((x + 62, y + h // 2), s, font=f, fill=INK, anchor="lm")
    return w, h


def sale_ribbon(c, w):
    d = ImageDraw.Draw(c)
    h = 74
    for i in range(h):  # gold gradient strip
        t = i / h
        col = tuple(int(GOLD[k] * (1 - t) + GOLD_L[k] * t) for k in range(3))
        d.line((0, i, w, i), fill=col)
    d.text((w // 2, h // 2), "11.11 SALE  ·  EXTRA 11% OFF AT CHECKOUT  ·  TILL 15 NOV", font=font("Jost", 30, "Bold"), fill=INK, anchor="mm")
    return h


def price_block(c, cx, y, p, sale, scale=1.0, left=None):
    d = ImageDraw.Draw(c)
    fp = font("Jost", int(76 * scale), "Bold"); fo = font("Jost", int(38 * scale), "Medium")
    price = money(p["price"]); tw = d.textlength(price, font=fp)
    old = money(p["compare"]) if p.get("compare") else None
    ow = d.textlength(old, font=fo) + 24 if old else 0
    total = tw + ow
    badge_w = (118 * scale + 18) if old else 0
    x0 = left if left is not None else cx - (total + badge_w) / 2
    d.text((x0, y), price, font=fp, fill=INK, anchor="ls")
    if old:
        ox = x0 + tw + 24
        d.text((ox, y - 6 * scale), old, font=fo, fill=(140, 130, 115), anchor="ls")
        ow2 = d.textlength(old, font=fo)
        d.line((ox, y - 20 * scale, ox + ow2, y - 20 * scale), fill=RED, width=max(2, int(3 * scale)))
        pct = round((p["compare"] - p["price"]) * 100 / p["compare"])
        bx, by = x0 + total + 18, y - 62 * scale
        d.rounded_rectangle((bx, by, bx + 118 * scale, by + 50 * scale), radius=25 * scale, fill=RED)
        d.text((bx + 59 * scale, by + 25 * scale), f"-{pct}%", font=font("Jost", int(30 * scale), "Bold"), fill="white", anchor="mm")


def cta(c, cx, y, label="SHOP NOW  →", w=440, h=92):
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((cx - w // 2, y, cx + w // 2, y + h), radius=h // 2, fill=INK)
    d.rounded_rectangle((cx - w // 2 + 5, y + 5, cx + w // 2 - 5, y + h - 5), radius=h // 2 - 5, outline=GOLD_L, width=2)
    d.text((cx, y + h // 2), label, font=font("Jost", 34, "Bold"), fill=GOLD_L, anchor="mm")


def footer(c, w, h, fh=86):
    d = ImageDraw.Draw(c)
    d.rectangle((0, h - fh, w, h), fill=INK)
    d.line((0, h - fh, w, h - fh), fill=GOLD, width=4)
    d.text((w // 2, h - fh // 2), "zuaja.pk  ·  WhatsApp 0316 1121130  ·  Delivery all over Pakistan",
           font=font("Jost", 28, "Medium"), fill=(245, 236, 217), anchor="mm")


def feed(p, sale):
    W, H = 1080, 1350
    c = bg(W, H); d = ImageDraw.Draw(c)
    top = sale_ribbon(c, W) if sale else 0
    lh = logo(c, W // 2, top + 34, 250)
    y = top + 34 + lh + 22
    text_c(d, W // 2, y, p["cat"].upper(), font("Jost", 26, "SemiBold"), GOLD); y += 40
    hf = font("CormorantGaramond", 66, "Bold")
    for ln in wrap(d, p["hook"], hf, W - 140):
        text_c(d, W // 2, y, ln, hf, INK); y += 70
    # product
    area_top, area_bot = y + 6, 1030
    glow_disc(c, W // 2, (area_top + area_bot) // 2 + 10, (area_bot - area_top) // 2 - 4)
    prod = fit(load_cutout(p["cutout"]), 600, area_bot - area_top - 30)
    shadow(c, W // 2, area_bot - 12, prod.width)
    c.alpha_composite(prod, (W // 2 - prod.width // 2, area_bot - 12 - prod.height))
    # name + chips + price
    d = ImageDraw.Draw(c)
    name = p["name"] + (f"  ·  {p['size']}" if p["size"] else "")
    text_c(d, W // 2, 1046, name, font("Jost", 36, "SemiBold"), INK)
    for fs in (25, 24, 23, 22, 21, 20):
        fchip = font("Jost", fs, "Medium")
        if sum(d.textlength(b, font=fchip) + 92 for b in p["benefits"]) + 18 * 2 <= W - 50: break
    rows = [p["benefits"]]
    cy = 1100
    for row in rows:
        rw = sum(d.textlength(b, font=fchip) + 92 for b in row) + 18 * (len(row) - 1)
        x = (W - rw) / 2
        for b in row:
            w_, _ = chip(c, int(x), cy, b, fchip); x += w_ + 18
        cy += 76
    footer(c, W, H, 70)
    # price + CTA side by side above footer
    py = H - 70 - 34
    price_block(c, 0, py, p, sale, 0.86, left=56)
    cta(c, 852, py - 82, w=340, h=84)
    return c.convert("RGB")


def story(p, sale):
    W, H = 1080, 1920
    c = bg(W, H); d = ImageDraw.Draw(c)
    # keep the top ~250 px and bottom ~340 px free of key text (Meta UI overlays)
    y = 150
    if sale:
        d.rounded_rectangle((W // 2 - 360, y, W // 2 + 360, y + 70), radius=35, fill=GOLD)
        text_c(d, W // 2, y + 35, "11.11 SALE · EXTRA 11% OFF · TILL 15 NOV", font("Jost", 30, "Bold"), INK, "mm")
        y += 100
    lh = logo(c, W // 2, y, 300); y += lh + 30
    text_c(d, W // 2, y, p["cat"].upper(), font("Jost", 30, "SemiBold"), GOLD); y += 48
    hf = font("CormorantGaramond", 84, "Bold")
    for ln in wrap(d, p["hook"], hf, W - 140):
        text_c(d, W // 2, y, ln, hf, INK); y += 88
    area_top, area_bot = y + 10, 1200
    glow_disc(c, W // 2, (area_top + area_bot) // 2, min(430, (area_bot - area_top) // 2))
    prod = fit(load_cutout(p["cutout"]), 760, area_bot - area_top - 20)
    shadow(c, W // 2, area_bot, prod.width)
    c.alpha_composite(prod, (W // 2 - prod.width // 2, area_bot - prod.height))
    d = ImageDraw.Draw(c)
    name = p["name"] + (f"  ·  {p['size']}" if p["size"] else "")
    text_c(d, W // 2, 1220, name, font("Jost", 44, "SemiBold"), INK)
    fchip = font("Jost", 30, "Medium")
    cy = 1288
    for b in p["benefits"]:
        w_ = d.textlength(b, font=fchip) + 92
        chip(c, int((W - w_) / 2), cy, b, fchip); cy += 72
    price_block(c, W // 2, cy + 78, p, sale, 1.0)
    cta(c, W // 2, cy + 104, w=480)
    return c.convert("RGB")


def lineup(title, kicker, items, size, sale, name):
    W, H = size
    c = bg(W, H); d = ImageDraw.Draw(c)
    top = sale_ribbon(c, W) if (sale and H < 1600) else 0
    y = (top + 34) if H < 1600 else 170
    if sale and H >= 1600:
        d.rounded_rectangle((W // 2 - 360, y, W // 2 + 360, y + 70), radius=35, fill=GOLD)
        text_c(d, W // 2, y + 35, "11.11 SALE · EXTRA 11% OFF · TILL 15 NOV", font("Jost", 30, "Bold"), INK, "mm"); y += 100
    lh = logo(c, W // 2, y, 270 if H < 1600 else 300); y += lh + 26
    text_c(d, W // 2, y, kicker.upper(), font("Jost", 28, "SemiBold"), GOLD); y += 44
    hf = font("CormorantGaramond", 72 if H < 1600 else 88, "Bold")
    for ln in wrap(d, title, hf, W - 120):
        text_c(d, W // 2, y, ln, hf, INK); y += (76 if H < 1600 else 92)
    base = 1080 if H < 1600 else 1360
    ph = base - y - 40
    ps = []
    for i, it in enumerate(items):
        q = load_cutout(it["cutout"]); hh = ph * (1.0 if i == len(items) // 2 else 0.86)
        ps.append(q.resize((max(1, round(q.width * hh / q.height)), round(hh)), Image.LANCZOS))
    gap = -18
    total = sum(p.width for p in ps) + gap * (len(ps) - 1)
    if total > W - 120:
        k = (W - 120) / total; ps = [p.resize((round(p.width * k), round(p.height * k)), Image.LANCZOS) for p in ps]
        total = sum(p.width for p in ps) + gap * (len(ps) - 1)
    glow_disc(c, W // 2, base - ph // 2, min(W // 2 - 40, ph // 2 + 40))
    shadow(c, W // 2, base, total)
    x = (W - total) // 2; xs = []
    for p in ps: xs.append(x); x += p.width + gap
    mid = len(ps) // 2
    order = [i for i in range(len(ps)) if i != mid] + [mid]
    for i in order:
        c.alpha_composite(ps[i], (int(xs[i]), base - ps[i].height))
    d = ImageDraw.Draw(c)
    fr = font("Jost", 30 if H < 1600 else 34, "Medium")
    lo = min(it["price"] for it in items)
    text_c(d, W // 2, base + 34, f"From {money(lo)}  ·  Natural desi care", fr, INK)
    cta(c, W // 2, base + (96 if H < 1600 else 110), w=460)
    if H < 1600: footer(c, W, H, 70)
    c.convert("RGB").save(OUT / f"{name}.jpg", quality=90, optimize=True, progressive=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prods = json.loads((HERE / "products.json").read_text())
    for p in prods:
        for sale in (True, False):
            tag = "sale" if sale else "evergreen"
            feed(p, sale).save(OUT / f"{p['key']}_feed-4x5_{tag}.jpg", quality=90, optimize=True, progressive=True)
            story(p, sale).save(OUT / f"{p['key']}_story-9x16_{tag}.jpg", quality=90, optimize=True, progressive=True)
        print(p["key"], flush=True)
    by = {p["key"]: p for p in prods}
    sets = {
        "lineup-hair": ("Your desi hair ritual", "Shampoos & Hair Oils", ["amla-reetha-shampoo", "rosemary-oil", "7-herbal-oil", "haldi-badam-shampoo"]),
        "lineup-fragrance": ("Scents people remember", "Zuaja Fragrance", ["signature-perfume", "white-oud", "unisex-perfume"]),
        "lineup-skin-bath": ("Fresh skin, every day", "Skin, Bath & Body", ["face-wash", "zafarani-cream", "rose-wash", "lavender-wash"]),
        "lineup-all": ("Desi care for hair, skin & body", "Zuaja PK", ["amla-reetha-shampoo", "rosemary-oil", "white-oud", "zafarani-cream", "face-wash"]),
    }
    for name, (title, kicker, keys) in sets.items():
        items = [by[k] for k in keys]
        for sale in (True, False):
            tag = "sale" if sale else "evergreen"
            lineup(title, kicker, items, (1080, 1350), sale, f"{name}_feed-4x5_{tag}")
            lineup(title, kicker, items, (1080, 1920), sale, f"{name}_story-9x16_{tag}")
        print(name, flush=True)


if __name__ == "__main__":
    main()
