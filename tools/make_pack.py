"""Zuaja PK: e-commerce packshots + social/ad creative pack + copy.

Usage: python3 -I make_pack.py <cut_dir> <logo_dir> <out_dir>
"""
import csv
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

CUT, LOGO, OUT = (Path(p) for p in sys.argv[1:4])

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
IVORY = (251, 244, 228)
IVORY_2 = (243, 231, 203)
INK = (23, 23, 23)
GOLD = (196, 147, 47)
GOLD_L = (229, 194, 113)
CREAM_TXT = (240, 230, 205)

# key, handle, name, category, size, price, tagline, hook (caption opener), body, tags
P = [
    ("haldi", "haldi-badam-shampoo-100ml", "Haldi + Badam Shampoo", "HAIR CARE", "100 ml", 450,
     "For hair that feels dry or rough",
     "Dry, rough hair? Haldi + badam to the rescue.",
     "A daily shampoo with turmeric (haldi) and almond (badam), the desi duo our elders trusted. Gentle enough for regular washes.",
     "#haldi #badam #shampoo #dryhair #haircare"),
    ("amla", "amla-reetha-shampoo-200ml", "Amla Reetha Shampoo", "HAIR CARE", "200 ml", 750,
     "For oily scalps and oiled hair",
     "Oiled your hair last night? Amla Reetha washes it out clean.",
     "Reetha is the soapnut our grandmothers soaked to wash hair. Paired with amla in a 200 ml pump bottle for everyday use.",
     "#amla #reetha #amlareetha #shampoo #oilyscalp"),
    ("rosemary", "rosemary-hair-scalp-oil-100ml", "Rosemary Oil", "HAIR OIL", "100 ml", 950,
     "Massage into the scalp before washing",
     "Your weekly champi, upgraded.",
     "Rosemary herbal hair oil in a dropper bottle, so it goes on your scalp, not all over your hands. Massage in before you wash.",
     "#rosemaryoil #hairoil #champi #scalpcare #herbaloil"),
    ("herbal7", "7-herbal-oils-blend-100ml", "7 Herbal Oils Blend", "HAIR OIL", "100 ml", 1200,
     "Seven oils for hair, scalp and body",
     "Seven oils. One bottle.",
     "A multi-purpose herbal oil blend for hair, scalp and body massage. Warm a little in your palms and massage in.",
     "#herbaloil #hairoil #bodymassage #champi #7oils"),
    ("neemwash", "neem-handwash-bodywash-100ml", "Neem Handwash + Bodywash", "BATH & BODY", "100 ml", 330,
     "One neem wash for sink and shower",
     "One bottle for the sink and the shower.",
     "A two-in-one neem wash for everyday hand and body washing. Fresh and clean, in an easy pump bottle.",
     "#neem #handwash #bodywash #neemwash #freshskin"),
    ("lavender", "zuaja-pk-lavender-hand-body-wash-with-lavender-extract-100-ml", "Lavender Hand & Body Wash", "BATH & BODY", "100 ml", 350,
     "Floral everyday cleansing",
     "A little lavender in your everyday routine.",
     "Hand and body wash with lavender extract and a soft floral scent. Keep it by the sink or in the shower.",
     "#lavender #bodywash #handwash #selfcare #floral"),
    ("zafarani", "zafarani-cream", "Zafarani Cream", "SKIN CARE", "", 350,
     "Rich cream for your daily skincare",
     "Saffron-inspired care, morning and night.",
     "A rich zafarani cream for your daily skincare routine. Apply a small amount to clean skin. Patch test before first use.",
     "#zafarani #zafranicream #skincare #saffron #glow"),
    ("facewash", "zuaja-pk-herbal-face-wash-haldi-80-ml", "Herbal Face Wash + Haldi", "SKIN CARE", "80 ml", 320,
     "Daily wash for dirt and oil",
     "Haldi in your daily face wash.",
     "A herbal face wash with haldi for washing off everyday dirt and oil. Handbag-friendly 80 ml tube.",
     "#facewash #haldi #turmeric #skincare #herbalfacewash"),
    ("rosesoap", "rose-soap", "Rose Soap", "SOAP", "", 220,
     "Bathing bar with a soft floral scent",
     "Rose-scented bath time.",
     "A rose bathing bar with a soft floral scent. Comes in its own carton, so it makes a sweet little gift too.",
     "#rosesoap #soap #handmadesoap #rose #bathtime"),
    ("neemsoap", "neem-soap", "Neem Soap", "SOAP", "", 180,
     "Green neem bar for hands and body",
     "The classic neem bar, done right.",
     "A green neem bathing bar for everyday hand and body washing. Lather with water and rinse clean.",
     "#neemsoap #neem #soap #herbalsoap #bathtime"),
    ("whiteoud", "zuaja-pk-premium-white-oud-perfume-50-ml", "White Oud Perfume", "FRAGRANCE", "50 ml", 1999,
     "Oud-inspired, dark glass and gold",
     "White Oud. Made to be noticed.",
     "Premium White Oud eau de parfum in a dark glass bottle with gold detailing. Want to try first? Ask for the tester.",
     "#whiteoud #oud #perfume #attar #fragrance"),
    ("signature", "zuaja-pk-premium-perfume-50-ml", "Zuaja Signature Perfume", "FRAGRANCE", "50 ml", 2200,
     "Faceted glass, golden detailing",
     "Our signature scent, in crystal-cut glass.",
     "The Zuaja Signature perfume in a faceted glass bottle with a golden cap. A gift that looks as good as it smells.",
     "#perfume #signaturescent #giftideas #fragrance #luxuryperfume"),
    ("unisex", "premium-perfume", "Unisex Perfume", "FRAGRANCE", "30 ml", 1500,
     "Everyday fragrance, compact spray",
     "One scent, for him and her.",
     "A unisex everyday perfume in a compact 30 ml spray. Small enough for your bag, ready for the whole day.",
     "#unisexperfume #perfume #everydayscent #fragrance #pocketperfume"),
    ("tester", "zuaja-pk-premium-white-oud-perfume-tester", "White Oud Tester", "FRAGRANCE", "", 250,
     "Try it before the full bottle",
     "Not sure yet? Try White Oud for Rs. 250.",
     "A small spray tester of White Oud, so you can try it before you buy the full bottle. Easy to carry in your bag.",
     "#perfumetester #whiteoud #tryitfirst #oud #fragrance"),
]
COMMON_TAGS = "#zuajapk #zuaja #pakistan #desicare #madeinpakistan #1111sale #11dot11 #onlineshoppingpakistan"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, path, start, max_w, min_size=18):
    s = start
    while s > min_size and draw.textlength(text, font=font(path, s)) > max_w:
        s -= 2
    return font(path, s)


def center(draw, cx, y, text, f, fill):
    draw.text((cx - draw.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


def logo(color, width):
    lg = Image.open(LOGO / "lockup.png").convert("RGBA")
    lg = lg.crop(lg.getbbox())
    solid = Image.new("RGBA", lg.size, color + (255,))
    solid.putalpha(lg.getchannel("A"))
    return solid.resize((width, round(lg.height * width / lg.width)), Image.LANCZOS)


def product(key, max_w, max_h):
    p = Image.open(CUT / f"{key}.png").convert("RGBA")
    p = p.crop(p.getbbox())
    r = min(max_w / p.width, max_h / p.height)
    return p.resize((round(p.width * r), round(p.height * r)), Image.LANCZOS)


def place(canvas, p, cx, base_y, shadow=True):
    """Place product with its bottom at base_y, centred on cx, with a soft contact shadow."""
    x, y = int(cx - p.width / 2), int(base_y - p.height)
    if shadow:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        w = p.width * 0.95
        ImageDraw.Draw(sh).ellipse((cx - w / 2, base_y - 16, cx + w / 2, base_y + 22), fill=(40, 28, 10, 110))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    canvas.alpha_composite(p, (x, y))


def backdrop(W, H, glow_center, glow_r):
    c = Image.new("RGBA", (W, H), IVORY + (255,))
    grad = Image.linear_gradient("L").resize((W, H))
    c = Image.composite(Image.new("RGBA", (W, H), IVORY_2 + (255,)), c, grad)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy = glow_center
    ImageDraw.Draw(g).ellipse((cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r), fill=GOLD_L + (150,))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(glow_r * 0.25)))
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    r2 = glow_r * 1.08
    ImageDraw.Draw(ring).ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=GOLD + (170,), width=3)
    c.alpha_composite(ring)
    return c


def offer_badge(draw, cx, cy, r):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK, outline=GOLD, width=4)
    center(draw, cx, cy - r * 0.62, "11.11", font(SERIF_B, int(r * 0.48)), GOLD_L)
    center(draw, cx, cy - r * 0.08, "EXTRA", font(SANS_B, int(r * 0.2)), CREAM_TXT)
    center(draw, cx, cy + r * 0.16, "11% OFF", font(SANS_B, int(r * 0.3)), GOLD_L)


def price_line(n):
    return f"Rs. {n:,}"


# ---------- e-commerce packshots ----------
def packshots(d):
    key, handle = d[0], d[1]
    p = Image.open(CUT / f"{key}.png").convert("RGBA")
    p = p.crop(p.getbbox())
    if max(p.size) > 1600:
        p.thumbnail((1600, 1600), Image.LANCZOS)
    p.save(OUT / "store" / "transparent" / f"{handle}.png", optimize=True)
    W = 1500
    c = Image.new("RGBA", (W, W), (255, 255, 255, 255))
    pr = product(key, W * 0.62, W * 0.78)
    place(c, pr, W / 2, W * 0.5 + pr.height / 2)
    c.convert("RGB").save(OUT / "store" / "white" / f"{handle}.png", optimize=True)


# ---------- social creatives ----------
def creative(d, W, H, offer=True):
    key, _, name, cat, size, price, tagline = d[:7]
    portrait = H > W * 1.1
    wide = W > H * 1.4
    if wide:
        c = backdrop(W, H, (int(W * 0.30), int(H * 0.52)), int(H * 0.42))
        dr = ImageDraw.Draw(c)
        pr = product(key, W * 0.34, H * 0.78)
        place(c, pr, W * 0.30, H * 0.90)
        lg = logo(INK, 230)
        c.alpha_composite(lg, (int(W * 0.58), 40))
        tx = int(W * 0.58)
        dr.text((tx, 120), cat, font=font(SANS_B, 20), fill=GOLD)
        f = fit(dr, name.upper(), SERIF_B, 50, W * 0.40)
        dr.text((tx, 152), name.upper(), font=f, fill=INK)
        dr.text((tx, 222), tagline, font=fit(dr, tagline, SERIF_I, 30, W * 0.40), fill=(70, 60, 40))
        dr.text((tx, 280), price_line(price) + (f"  ·  {size}" if size else ""), font=font(SANS_B, 34), fill=INK)
        if offer:
            dr.rounded_rectangle((tx, 342, tx + 440, 402), 30, fill=INK)
            dr.text((tx + 24, 356), "11.11  EXTRA 11% OFF", font=font(SANS_B, 26), fill=GOLD_L)
        dr.text((tx, 440 if offer else 360), "Order: zuaja.pk  ·  WhatsApp 0316 1121130", font=font(SANS, 22), fill=(60, 50, 35))
        dr.rectangle((0, H - 10, W, H), fill=GOLD)
        return c.convert("RGB")

    c = backdrop(W, H, (W // 2, int(H * (0.47 if portrait else 0.48))), int(W * 0.36))
    dr = ImageDraw.Draw(c)
    lg = logo(INK, int(W * 0.34))
    top = int(H * 0.035) + (60 if H > 1800 else 0)
    c.alpha_composite(lg, ((W - lg.width) // 2, top))
    center(dr, W / 2, top + lg.height + 18, cat, font(SANS_B, 22), GOLD)
    band_h = int(H * (0.25 if portrait else 0.27))
    band_y = H - band_h - (150 if H > 1800 else 0)
    area_top = top + lg.height + 60
    pr = product(key, W * 0.56, band_y - area_top - 40)
    place(c, pr, W / 2, band_y - 26)
    if offer:
        offer_badge(dr, W - int(W * 0.15), int(area_top + W * 0.13), int(W * 0.105))
    dr.rectangle((0, band_y, W, H if H < 1800 else band_y + band_h), fill=INK)
    dr.line((0, band_y, W, band_y), fill=GOLD, width=6)
    f = fit(dr, name.upper(), SERIF_B, 62, W * 0.9)
    center(dr, W / 2, band_y + band_h * 0.12, name.upper(), f, GOLD_L)
    center(dr, W / 2, band_y + band_h * 0.40, tagline, fit(dr, tagline, SERIF_I, 36, W * 0.9), CREAM_TXT)
    pl = price_line(price) + (f"  ·  {size}" if size else "")
    if offer:
        pl += "  ·  extra 11% off at checkout"
    center(dr, W / 2, band_y + band_h * 0.62, pl, fit(dr, pl, SANS_B, 30, W * 0.9), (255, 255, 255))
    center(dr, W / 2, band_y + band_h * 0.82, "zuaja.pk  ·  WhatsApp 0316 1121130  ·  Delivery all over Pakistan",
           font(SANS, 22), (200, 190, 165))
    if H > 1800:  # story/reel: keep bottom 250px clear for UI, add swipe cue in gold
        center(dr, W / 2, H - 120, "TAP TO SHOP  ↑", font(SANS_B, 30), GOLD)
    return c.convert("RGB")


def lineup(W, H):
    keys = ["amla", "haldi", "rosemary", "herbal7", "facewash", "zafarani", "lavender", "neemwash", "whiteoud", "signature"]
    c = backdrop(W, H, (W // 2, int(H * 0.52)), int(min(W, H) * 0.42))
    dr = ImageDraw.Draw(c)
    lg = logo(INK, int(min(W, H) * 0.36))
    top = 40 if H < 800 else int(H * 0.04) + (60 if H > 1800 else 0)
    c.alpha_composite(lg, ((W - lg.width) // 2, top))
    title_y = top + lg.height + 14
    center(dr, W / 2, title_y, "11.11 SALE", font(SERIF_B, int(min(W, H) * 0.09)), INK)
    sub = "EXTRA 11% OFF ON EVERYTHING · TILL 15 NOV"
    center(dr, W / 2, title_y + int(min(W, H) * 0.11), sub, fit(dr, sub, SANS_B, 32, W * 0.9), GOLD)
    base = H - (int(H * 0.16) if H > 1800 else int(H * 0.14))
    row_h = base - (title_y + int(min(W, H) * 0.18))
    rel = {"amla": 1.0, "haldi": 0.95, "rosemary": 0.92, "herbal7": 0.92, "facewash": 0.7, "zafarani": 0.42,
           "lavender": 0.88, "neemwash": 0.88, "whiteoud": 0.62, "signature": 0.62}
    imgs = []
    for k in keys:
        p = Image.open(CUT / f"{k}.png").convert("RGBA")
        p = p.crop(p.getbbox())
        th = row_h * rel[k]
        imgs.append(p.resize((round(p.width * th / p.height), round(th)), Image.LANCZOS))
    gap = W * 0.012
    total = sum(i.width for i in imgs) + gap * (len(imgs) - 1)
    k = min(1.0, (W * 0.94) / total)
    imgs = [i.resize((max(1, round(i.width * k)), max(1, round(i.height * k))), Image.LANCZOS) for i in imgs]
    total = sum(i.width for i in imgs) + gap * k * (len(imgs) - 1)
    x = (W - total) / 2
    for im in imgs:
        place(c, im, x + im.width / 2, base, shadow=True)
        x += im.width + gap * k
    dr.rectangle((0, H - 10, W, H), fill=GOLD)
    msg = "Shop now: zuaja.pk  ·  WhatsApp 0316 1121130"
    center(dr, W / 2, H - (90 if H > 1800 else 56), msg, fit(dr, msg, SANS, 26, W * 0.9), INK)
    return c.convert("RGB")


SIZES = {
    "instagram-post-1080x1080": (1080, 1080),
    "instagram-portrait-1080x1350": (1080, 1350),
    "story-reel-1080x1920": (1080, 1920),
    "facebook-ad-1200x628": (1200, 628),
}


def main():
    for sub in ["store/transparent", "store/white", "social", "campaign"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    rows = []
    captions = ["# Zuaja PK — Instagram & Facebook captions\n"]
    for d in P:
        key, handle, name, cat, size, price, tagline, hook, body, tags = d
        packshots(d)
        folder = OUT / "social" / handle
        folder.mkdir(exist_ok=True)
        for label, (w, h) in SIZES.items():
            creative(d, w, h, offer=True).save(folder / f"{handle}-11-11-{label}.jpg", quality=90, optimize=True)
        creative(d, 1080, 1350, offer=False).save(folder / f"{handle}-evergreen-1080x1350.jpg", quality=90, optimize=True)
        sale_price = round(price * 0.89)
        caption = (f"{hook}\n\n{body}\n\n"
                   f"✨ {name}{' (' + size + ')' if size else ''}: {price_line(price)}\n"
                   f"\U0001F525 11.11 Sale: extra 11% off at checkout (about {price_line(sale_price)}) till 15 November\n"
                   f"\U0001F69A Delivery all over Pakistan\n"
                   f"\U0001F4F2 Order at zuaja.pk or WhatsApp 0316 1121130\n\n"
                   f"{tags} {COMMON_TAGS}")
        (folder / "caption.txt").write_text(caption + "\n", encoding="utf-8")
        captions.append(f"## {name}\n\n{caption}\n")
        rows.append({
            "product": name,
            "image_files": "; ".join(f"{handle}-11-11-{k}.jpg" for k in SIZES),
            "headline": f"{name} · 11% Off"[:40],
            "primary_text": f"{hook} {body} 11.11 Sale: extra 11% off everything till 15 Nov. Delivery all over Pakistan.",
            "description": f"{price_line(price)} + 11% off"[:30],
            "call_to_action": "Shop now",
            "website_url": f"https://zuaja.pk/products/{handle}",
        })
    for label, (w, h) in SIZES.items():
        lineup(w, h).save(OUT / "campaign" / f"zuaja-11-11-lineup-{label}.jpg", quality=90, optimize=True)
    rows.append({
        "product": "Whole store (11.11 lineup)",
        "image_files": "; ".join(f"zuaja-11-11-lineup-{k}.jpg" for k in SIZES),
        "headline": "11.11 Sale · Extra 11% Off",
        "primary_text": "Desi care for hair, skin and body: haldi, badam, amla, reetha, neem and rosemary from Zuaja PK, plus our perfumes. 11.11 Sale: extra 11% off everything till 15 November. Delivery all over Pakistan. Order at zuaja.pk or WhatsApp 0316 1121130.",
        "description": "Ends 15 November",
        "call_to_action": "Shop now",
        "website_url": "https://zuaja.pk/collections/11-11-sale",
    })
    with open(OUT / "ads-copy.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    camp = ("## 11.11 lineup (whole store)\n\n11.11 SALE IS LIVE \U0001F525\n\n"
            "Desi care for hair, skin and body from Zuaja PK: Haldi + Badam and Amla Reetha shampoos, Rosemary and 7 Herbal oils, "
            "Herbal Face Wash, Zafarani Cream, neem and lavender washes, soaps and our perfumes.\n\n"
            "Extra 11% off on everything at checkout, till 15 November.\n"
            "\U0001F69A Delivery all over Pakistan\n\U0001F4F2 zuaja.pk · WhatsApp 0316 1121130\n\n" + COMMON_TAGS + " #haircare #skincare #perfume\n")
    captions.append(camp)
    (OUT / "campaign" / "caption.txt").write_text(camp, encoding="utf-8")
    (OUT / "captions.md").write_text("\n".join(captions), encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
