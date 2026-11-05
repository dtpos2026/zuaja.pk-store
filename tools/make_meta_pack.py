"""Zuaja PK Meta Ads Pack (same structure as the Anjum Mart pack, Zuaja branding).

Usage: python3 -I make_meta_pack.py <cutouts_dir> <logo_lockup_png> <fonts_dir> <out_dir>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

CUT, LOGO, FONTS, OUT = (Path(p) for p in sys.argv[1:5])
PACK = OUT / "Zuaja-PK-Meta-Ads-Pack"
PACK.mkdir(parents=True, exist_ok=True)

GOLD = (214, 176, 98)
GOLD_L = (236, 205, 130)
CREAM = (243, 234, 215)
MUTED = (205, 196, 178)
INK = (14, 13, 11)
WA = "923161121130"
SITE = "https://zuaja.pk"
rng = np.random.default_rng(11)
LOGO_DARK = Path(sys.argv[5]) if len(sys.argv) > 5 else LOGO


def font(name, size, weight=None):
    f = ImageFont.truetype(str(FONTS / f"{name}.ttf"), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def spaced(draw, cx, y, text, f, fill, tracking=0.0):
    widths = [draw.textlength(ch, font=f) for ch in text]
    extra = f.size * tracking
    total = sum(widths) + extra * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += w + extra
    return total


def fit(draw, text, name, size, weight, max_w, tracking=0.0):
    while size > 18:
        f = font(name, size, weight)
        w = sum(draw.textlength(ch, font=f) for ch in text) + f.size * tracking * (len(text) - 1)
        if w <= max_w:
            return f
        size -= 2
    return font(name, size, weight)


def logo(color, width):
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    solid = Image.new("RGBA", lg.size, color + (255,))
    solid.putalpha(lg.getchannel("A"))
    return solid.resize((width, round(lg.height * width / lg.width)), Image.LANCZOS)


def backdrop(W, H, cy):
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    d = np.sqrt(((x - 0.5) * W / H) ** 2 + (y - cy) ** 2)
    glow = np.clip(1 - d / 0.55, 0, 1) ** 1.8
    base = np.array(INK, dtype=np.float32)
    warm = np.array([92, 66, 22], dtype=np.float32)
    img = base + (warm - base) * glow[..., None] * 0.85
    vig = np.clip(np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2) - 0.35, 0, 1)
    img = img * (1 - vig[..., None] * 0.6)
    c = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bok)
    for _ in range(9):
        side = rng.choice([0, 1])
        bx = rng.uniform(0.04, 0.2) if side == 0 else rng.uniform(0.8, 0.96)
        by = rng.uniform(0.25, 0.8)
        r = rng.uniform(10, 26) * W / 1080
        bd.ellipse((bx * W - r, by * H - r, bx * W + r, by * H + r), fill=GOLD_L + (int(rng.uniform(60, 120)),))
    c.alpha_composite(bok.filter(ImageFilter.GaussianBlur(7 * W / 1080)))
    fr = ImageDraw.Draw(c)
    m = int(16 * W / 1080)
    fr.rectangle((m, m, W - m, H - m), outline=(120, 96, 52), width=2)
    return c


def place_products(c, keys, cx, base, max_h, max_w):
    ims = []
    for k in keys:
        p = Image.open(CUT / f"{k}.png").convert("RGBA")
        p = p.crop(p.getbbox())
        ims.append(p)
    rel = [1.0 if len(keys) == 1 else REL.get(k, 0.85) for k in keys]
    ims = [p.resize((max(1, round(p.width * max_h * r / p.height)), round(max_h * r)), Image.LANCZOS) for p, r in zip(ims, rel)]
    gap = max_w * 0.03
    total = sum(p.width for p in ims) + gap * (len(ims) - 1)
    if total > max_w:
        k = max_w / total
        ims = [p.resize((max(1, round(p.width * k)), max(1, round(p.height * k))), Image.LANCZOS) for p in ims]
        gap *= k
        total = max_w
    W, H = c.size
    # warm backlight so dark bottles separate from the background
    halo = Image.new("L", (W, H), 0)
    tall = max(p.height for p in ims)
    ImageDraw.Draw(halo).ellipse((cx - total * 0.62, base - tall * 1.05, cx + total * 0.62, base + tall * 0.05), fill=110)
    c.paste(Image.new("RGBA", (W, H), (150, 112, 46, 255)), (0, 0), halo.filter(ImageFilter.GaussianBlur(W * 0.08)))
    x = cx - total / 2
    for p in ims:
        sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).ellipse((x - 8, base - 12, x + p.width + 8, base + 16), fill=200)
        c.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
        refl = p.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, p.width, int(p.height * 0.18)))
        g = Image.linear_gradient("L").resize(refl.size).point(lambda v: int((255 - v) * 0.16))
        refl.putalpha(ImageChops.multiply(refl.getchannel("A"), g))
        c.alpha_composite(refl, (int(x), int(base + 2)))
        c.alpha_composite(p, (int(x), int(base - p.height)))
        x += p.width + gap


def wa_icon(size, color):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = max(3, s // 11)
    d.ellipse((w, w, s - w, s - w), outline=color, width=w)
    d.polygon([(s * 0.14, s * 0.70), (s * 0.06, s * 0.96), (s * 0.34, s * 0.88)], fill=color)
    d.rounded_rectangle((s * 0.33, s * 0.30, s * 0.47, s * 0.46), radius=s * 0.05, fill=color)
    d.rounded_rectangle((s * 0.53, s * 0.54, s * 0.69, s * 0.68), radius=s * 0.05, fill=color)
    d.line((s * 0.40, s * 0.44, s * 0.58, s * 0.62), fill=color, width=int(w * 1.4))
    return im.resize((size, size), Image.LANCZOS)


def button(c, cx, y, label, scale):
    d = ImageDraw.Draw(c)
    f = font("Jost", int(30 * scale), 600)
    tw = sum(d.textlength(ch, font=f) for ch in label) + f.size * 0.12 * (len(label) - 1)
    icon = int(34 * scale)
    pad = int(40 * scale)
    w = tw + icon + int(14 * scale) + pad * 2
    h = int(70 * scale)
    x0 = int(cx - w / 2)
    grad = Image.linear_gradient("L").rotate(90).resize((int(w), h))
    pill = Image.composite(Image.new("RGBA", (int(w), h), (226, 186, 92, 255)), Image.new("RGBA", (int(w), h), (240, 210, 130, 255)), grad)
    m = Image.new("L", (int(w), h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, int(w) - 1, h - 1), radius=h // 2, fill=255)
    c.paste(pill, (x0, y), m)
    ic = wa_icon(icon, (20, 18, 14, 255))
    c.alpha_composite(ic, (x0 + pad, y + (h - icon) // 2))
    tx = x0 + pad + icon + int(14 * scale)
    for ch in label:
        d.text((tx, y + (h - f.size) // 2 - int(4 * scale)), ch, font=f, fill=(20, 18, 14))
        tx += d.textlength(ch, font=f) + f.size * 0.12


def creative(W, H, item):
    story = H > 1500
    scale = W / 1080
    cy_glow = 0.50
    c = backdrop(W, H, cy_glow)
    d = ImageDraw.Draw(c)
    top = int((150 if story else 46) * scale)
    lg = Image.open(LOGO_DARK).convert("RGBA")
    lw = int(270 * scale)
    lg = lg.resize((lw, round(lg.height * lw / lg.width)), Image.LANCZOS)
    c.alpha_composite(lg, ((W - lg.width) // 2, top))
    y = top + lg.height + int(30 * scale)
    fk = font("Jost", int(24 * scale), 500)
    spaced(d, W / 2, y, item["kicker"].upper(), fk, GOLD, 0.22)
    y += int(44 * scale)
    ft = fit(d, item["title"], "CormorantGaramond", int(78 * scale), 600, W * 0.86, 0.01)
    spaced(d, W / 2, y, item["title"], ft, CREAM, 0.01)
    y += int(ft.size * 1.15)
    fs = fit(d, item["sub"], "Jost", int(28 * scale), 400, W * 0.84)
    spaced(d, W / 2, y, item["sub"], fs, MUTED, 0.0)
    y += int(fs.size * 1.6)
    bottom_block = int((330 if story else 300) * scale)
    base = H - bottom_block - int((260 if story else 60) * scale)
    place_products(c, item["keys"], W / 2, base, base - y - int(30 * scale), W * 0.80)
    d = ImageDraw.Draw(c)
    py = base + int(40 * scale)
    fp = font("CormorantGaramond", int(92 * scale), 600)
    spaced(d, W / 2, py, item["price"], fp, GOLD_L, 0.01)
    py += int(fp.size * 1.12)
    fl = font("Jost", int(26 * scale), 400)
    spaced(d, W / 2, py, "Delivery All Over Pakistan  ·  Cash on Delivery", fl, CREAM, 0.02)
    button(c, W / 2, py + int(54 * scale), "ORDER ON WHATSAPP", scale)
    return c.convert("RGB")


REL = {"amla-reetha-shampoo-200ml": 1.0, "haldi-badam-shampoo-100ml": 0.92, "rosemary-hair-scalp-oil-100ml": 0.88,
       "7-herbal-oils-blend-100ml": 0.88, "zuaja-pk-herbal-face-wash-haldi-80-ml": 0.78, "zafarani-cream": 0.46,
       "neem-handwash-bodywash-100ml": 0.9, "zuaja-pk-lavender-hand-body-wash-with-lavender-extract-100-ml": 0.9,
       "rose-body-wash-100ml": 0.9, "rose-soap": 0.4, "neem-soap": 0.42,
       "zuaja-pk-premium-white-oud-perfume-50-ml": 0.7, "zuaja-pk-premium-perfume-50-ml": 0.72, "premium-perfume": 0.68,
       "zuaja-pk-premium-white-oud-perfume-tester": 0.5}

GROUPS = [
    ("01-HAIR-CARE", "Hair Care", [
        dict(code="H1", slug="haldi-badam-shampoo", keys=["haldi-badam-shampoo-100ml"], kicker="Hair Care · Shampoo", title="Haldi + Badam Shampoo",
             sub="100 ml · For hair that feels dry or rough", price="Rs. 450", n=450,
             desc="A daily shampoo with turmeric (haldi) and almond (badam), the desi duo our elders trusted.",
             roman="Haldi aur badam wala daily shampoo, khushk aur rough baalon ke liye.", url="/products/haldi-badam-shampoo-100ml",
             tags="#HaldiBadam #Shampoo #DryHair #HairCare"),
        dict(code="H2", slug="amla-reetha-shampoo", keys=["amla-reetha-shampoo-200ml"], kicker="Hair Care · Shampoo", title="Amla Reetha Shampoo",
             sub="200 ml · For oily scalps and oiled hair", price="Rs. 750", n=750,
             desc="Reetha is the soapnut our grandmothers used to wash hair, paired with amla in a 200 ml pump bottle.",
             roman="Amla aur reetha wala shampoo, oily scalp aur tel lage baalon ke liye. 200 ml pump bottle.", url="/products/amla-reetha-shampoo-200ml",
             tags="#AmlaReetha #Shampoo #OilyScalp #HairCare"),
        dict(code="H3", slug="rosemary-oil", keys=["rosemary-hair-scalp-oil-100ml"], kicker="Hair Care · Hair Oil", title="Rosemary Oil",
             sub="100 ml dropper · Massage into the scalp before washing", price="Rs. 950", n=950,
             desc="Rosemary herbal hair oil in a dropper bottle, so it goes on your scalp, not all over your hands.",
             roman="Rosemary herbal hair oil, dropper ke saath. Nahane se pehle scalp par massage karein.", url="/products/rosemary-hair-scalp-oil-100ml",
             tags="#RosemaryOil #HairOil #Champi #ScalpCare"),
        dict(code="H4", slug="7-herbal-oils-blend", keys=["7-herbal-oils-blend-100ml"], kicker="Hair Care · Hair Oil", title="7 Herbal Oils Blend",
             sub="100 ml · Seven oils for hair, scalp and body", price="Rs. 1,200", n=1200,
             desc="A multi-purpose blend of seven herbal oils for hair, scalp and body massage.",
             roman="7 herbal oils ek bottle mein: baal, scalp aur body massage ke liye.", url="/products/7-herbal-oils-blend-100ml",
             tags="#HerbalOil #HairOil #BodyMassage #Champi"),
        dict(code="H5", slug="hair-care-collection", keys=["haldi-badam-shampoo-100ml", "amla-reetha-shampoo-200ml", "rosemary-hair-scalp-oil-100ml", "7-herbal-oils-blend-100ml"],
             kicker="Hair Care · Zuaja PK", title="Desi Hair Care", sub="Haldi + Badam · Amla Reetha · Rosemary · 7 Herbal Oils", price="From Rs. 450", n=450,
             desc="Shampoos and herbal hair oils made with ingredients Pakistani homes already trust.",
             roman="Shampoo aur herbal hair oils: haldi, badam, amla, reetha aur rosemary.", url="/collections/hair-care",
             tags="#HairCare #Shampoo #HairOil #DesiCare"),
    ]),
    ("02-SKIN-CARE", "Skin Care", [
        dict(code="S1", slug="herbal-face-wash-haldi", keys=["zuaja-pk-herbal-face-wash-haldi-80-ml"], kicker="Skin Care · Face Wash", title="Herbal Face Wash + Haldi",
             sub="80 ml tube · Daily wash for dirt and oil", price="Rs. 320", n=320,
             desc="A herbal face wash with haldi for washing off everyday dirt and oil. Handbag-friendly 80 ml tube.",
             roman="Haldi wala herbal face wash, roz ki mitti aur oil saaf karne ke liye. 80 ml tube.", url="/products/zuaja-pk-herbal-face-wash-haldi-80-ml",
             tags="#FaceWash #Haldi #Turmeric #SkinCare"),
        dict(code="S2", slug="zafarani-cream", keys=["zafarani-cream"], kicker="Skin Care · Cream", title="Zafarani Cream",
             sub="Rich cream for your daily skincare", price="Rs. 350", n=350,
             desc="A rich zafarani (saffron) cream for your morning or evening routine. Patch test before first use.",
             roman="Zafarani cream, subah ya raat ki skincare ke liye. Pehli dafa patch test zaroor karein.", url="/products/zafarani-cream",
             tags="#ZafaraniCream #Saffron #SkinCare #Glow"),
        dict(code="S3", slug="skin-care-collection", keys=["zuaja-pk-herbal-face-wash-haldi-80-ml", "zafarani-cream"],
             kicker="Skin Care · Zuaja PK", title="Your Daily Skincare", sub="Herbal Face Wash + Haldi · Zafarani Cream", price="From Rs. 320", n=320,
             desc="Wash with haldi, care with zafarani: a simple two-step daily routine.",
             roman="Haldi face wash aur zafarani cream: roz ki do-step skincare.", url="/collections/skin-care",
             tags="#SkinCare #FaceWash #Zafarani #DesiCare"),
    ]),
    ("03-BATH-BODY", "Bath & Body", [
        dict(code="B1", slug="neem-handwash-bodywash", keys=["neem-handwash-bodywash-100ml"], kicker="Bath & Body · 2-in-1 Wash", title="Neem Handwash + Bodywash",
             sub="100 ml · One wash for sink and shower", price="Rs. 330", n=330,
             desc="A two-in-one neem wash for everyday hand and body washing.",
             roman="Neem wala 2-in-1 wash: haath aur jism dono ke liye.", url="/products/neem-handwash-bodywash-100ml",
             tags="#Neem #Handwash #Bodywash #FreshSkin"),
        dict(code="B2", slug="lavender-hand-body-wash", keys=["zuaja-pk-lavender-hand-body-wash-with-lavender-extract-100-ml"], kicker="Bath & Body · Hand & Body Wash", title="Lavender Hand & Body Wash",
             sub="100 ml · With lavender extract", price="Rs. 350", n=350,
             desc="Hand and body wash with lavender extract and a soft floral scent.",
             roman="Lavender extract wala hand & body wash, halki phoolon wali khushbu.", url="/products/zuaja-pk-lavender-hand-body-wash-with-lavender-extract-100-ml",
             tags="#Lavender #Bodywash #Handwash #SelfCare"),
        dict(code="B3", slug="rose-hand-body-wash", keys=["rose-body-wash-100ml"], kicker="Bath & Body · Hand & Body Wash", title="Rose Hand & Body Wash",
             sub="100 ml · Soft floral scent", price="Rs. 300", n=300,
             desc="Rose hand and body wash with a soft floral scent for every day.",
             roman="Rose hand & body wash, gulab ki halki khushbu ke saath.", url="/products/rose-body-wash-100ml",
             tags="#Rose #Bodywash #Handwash #SelfCare"),
        dict(code="B4", slug="rose-soap", keys=["rose-soap"], kicker="Bath & Body · Soap", title="Rose Soap",
             sub="Bathing bar with a soft floral scent", price="Rs. 220", n=220,
             desc="A rose bathing bar with a soft floral scent. Comes in its own carton.",
             roman="Gulab ki khushbu wala nahane ka sabun, apne carton mein.", url="/products/rose-soap",
             tags="#RoseSoap #Soap #BathTime"),
        dict(code="B5", slug="neem-soap", keys=["neem-soap"], kicker="Bath & Body · Soap", title="Neem Soap",
             sub="Green neem bar for hands and body", price="Rs. 180", n=180,
             desc="A green neem bathing bar for everyday hand and body washing.",
             roman="Neem ka hara sabun, roz haath aur jism dhone ke liye.", url="/products/neem-soap",
             tags="#NeemSoap #Neem #Soap #BathTime"),
        dict(code="B6", slug="bath-body-collection", keys=["rose-body-wash-100ml", "neem-handwash-bodywash-100ml", "zuaja-pk-lavender-hand-body-wash-with-lavender-extract-100-ml"],
             kicker="Bath & Body · Zuaja PK", title="Hand & Body Washes", sub="Rose · Neem · Lavender · 100 ml each", price="From Rs. 300", n=300,
             desc="Three everyday hand and body washes: rose, neem and lavender.",
             roman="Teen hand & body wash: rose, neem aur lavender.", url="/collections/bath-body",
             tags="#Bodywash #Handwash #Rose #Neem #Lavender"),
    ]),
    ("04-FRAGRANCE", "Fragrance", [
        dict(code="F1", slug="white-oud-perfume", keys=["zuaja-pk-premium-white-oud-perfume-50-ml"], kicker="Fragrance · Eau de Parfum", title="Premium White Oud",
             sub="50 ml · Oud-inspired, dark glass and gold", price="Rs. 1,999", n=1999,
             desc="Premium White Oud perfume in a dark glass bottle with gold detailing. A tester is available too.",
             roman="Premium White Oud, 50 ml. Pehle try karna ho to tester bhi mojood hai.", url="/products/zuaja-pk-premium-white-oud-perfume-50-ml",
             tags="#WhiteOud #Oud #Perfume #Fragrance"),
        dict(code="F2", slug="signature-perfume", keys=["zuaja-pk-premium-perfume-50-ml"], kicker="Fragrance · Eau de Parfum", title="Zuaja Signature Perfume",
             sub="50 ml · Faceted glass, golden detailing", price="Rs. 2,200", n=2200,
             desc="Our signature perfume in a faceted glass bottle with a golden cap. A gift that looks as good as it smells.",
             roman="Zuaja Signature Perfume, 50 ml, crystal jaisi bottle. Tohfe ke liye behtareen.", url="/products/zuaja-pk-premium-perfume-50-ml",
             tags="#Perfume #SignatureScent #GiftIdeas #Fragrance"),
        dict(code="F3", slug="unisex-perfume", keys=["premium-perfume"], kicker="Fragrance · Unisex", title="Unisex Perfume",
             sub="30 ml spray · For him and her", price="Rs. 1,500", n=1500,
             desc="A unisex everyday perfume in a compact 30 ml spray, small enough for your bag.",
             roman="Unisex perfume, 30 ml spray: mard aur aurat dono ke liye.", url="/products/premium-perfume",
             tags="#UnisexPerfume #Perfume #EverydayScent"),
        dict(code="F4", slug="white-oud-tester", keys=["zuaja-pk-premium-white-oud-perfume-tester"], kicker="Fragrance · Tester", title="White Oud Tester",
             sub="Try it before the full bottle", price="Rs. 250", n=250,
             desc="A small spray tester of White Oud, so you can try it before buying the full bottle.",
             roman="White Oud ka chhota tester: poori bottle lene se pehle try karein.", url="/products/zuaja-pk-premium-white-oud-perfume-tester",
             tags="#PerfumeTester #WhiteOud #TryItFirst"),
        dict(code="F5", slug="perfumes-collection", keys=["premium-perfume", "zuaja-pk-premium-white-oud-perfume-50-ml", "zuaja-pk-premium-perfume-50-ml"],
             kicker="Fragrance · Zuaja PK", title="Zuaja Perfumes", sub="White Oud · Signature · Unisex", price="From Rs. 1,500", n=1500,
             desc="Three Zuaja perfumes: Premium White Oud, Signature and Unisex.",
             roman="Teen Zuaja perfumes: White Oud, Signature aur Unisex.", url="/collections/perfumes",
             tags="#Perfume #Oud #Fragrance #GiftIdeas"),
    ]),
]
COMMON = "#ZuajaPK #Zuaja #OnlineShoppingPakistan #CashOnDelivery #MadeInPakistan #DesiCare"


def caption_block(it):
    head = it["title"]
    return f"""==================================================
{it['code']}-{it['slug']}
==================================================
CAPTION FOR THE POST (English)
{head} ✨
{it['desc']}
{it['price']} · Delivery all over Pakistan · Cash on Delivery.
Tap the WhatsApp button to order or ask us anything.

CAPTION FOR THE POST (Roman Urdu)
{head} ✨
{it['roman']}
Qeemat {it['price']}. Poore Pakistan mein delivery aur Cash on Delivery.
Order ya sawaal ke liye WhatsApp button dabayein.

HASHTAGS (paste under the caption)
{it['tags']} {COMMON}

META ADS FIELDS (Click to WhatsApp ad)
Primary text : {head} · {it['price']}. Delivery all over Pakistan, Cash on Delivery. Message us on WhatsApp to order.
Headline     : {head} · {it['price']}
Description  : Delivery all over Pakistan · Cash on Delivery
Call to action: WhatsApp message (Send WhatsApp message)
Customer's pre-filled WhatsApp message: Assalamualaikum! I like the {head} ({it['price']}). Please share the details.
Product page (for your replies): {SITE}{it['url']}

"""


def main():
    for folder, label, items in GROUPS:
        g = PACK / folder
        (g / "Feed-4x5").mkdir(parents=True, exist_ok=True)
        (g / "Story-Reels-9x16").mkdir(parents=True, exist_ok=True)
        txt = [f"ZUAJA PK: CAPTIONS AND AD TEXTS, {label}\nEach block matches the picture with the same code (feed and story).\n\n"]
        for it in items:
            creative(1080, 1350, it).save(g / "Feed-4x5" / f"{it['code']}-{it['slug']}-feed-1080x1350.jpg", quality=92, optimize=True)
            creative(1080, 1920, it).save(g / "Story-Reels-9x16" / f"{it['code']}-{it['slug']}-story-1080x1920.jpg", quality=92, optimize=True)
            txt.append(caption_block(it))
            print(it["code"])
        (g / f"CAPTIONS-{folder[3:]}.txt").write_text("".join(txt), encoding="utf-8")
    links = ["ZUAJA PK: PRODUCT AND COLLECTION LINKS (send these to customers on WhatsApp)\n\nCOLLECTIONS"]
    for path, name in [("/collections/hair-care", "Hair care (shampoos and oils)"), ("/collections/shampoos", "Shampoos"), ("/collections/hair-oils", "Hair oils"),
                       ("/collections/skin-care", "Skin care"), ("/collections/bath-body", "Bath & body"), ("/collections/soaps", "Soaps"),
                       ("/collections/perfumes", "Perfumes"), ("/collections/all", "Everything")]:
        links.append(f"{name:<34}{SITE}{path}")
    for folder, label, items in GROUPS:
        links.append(f"\n{label.upper()}")
        for it in items:
            if "/products/" in it["url"]:
                links.append(f"{it['title']} ({it['price']})\n  {SITE}{it['url']}")
    (PACK / "Product-Links.txt").write_text("\n".join(links) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
