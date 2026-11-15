"""Zuaja PK organic social pack (Instagram + Facebook), evergreen, no sale wording.

posts/       13 product hero posts 4:5 (1080x1350), "colour-block editorial" look:
             product-tinted gradient, giant faded word, reflection, gold frame
carousels/   4 carousels (4:5 slides): shampoo finder, champi ritual, desi ingredients, scent finder
engage/      engagement posts 4:5: This-or-That, comment prompts, tag-a-friend, brand intro
stories/     story templates 9:16 with space for poll/quiz stickers
Run from repo root: python3 -I marketing/social-pack/make_social.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "marketing/meta-ads-nov"))
from make_statics import GOLD, GOLD_L, INK, bg, fit, font, load_cutout, money, wrap  # noqa: E402

HERE = Path(__file__).resolve().parent
LOGO = ROOT / "brand/zuaja-logo-horizontal-1600.png"
CREAM = (247, 236, 214)
GOLD_D = (128, 88, 16)  # deep gold for text on light backgrounds
P = {p["key"]: p for p in json.loads((ROOT / "marketing/meta-ads-nov/products.json").read_text())}

LOOK = {  # key: (top colour, bottom colour, light text?, giant word, headline, trio)
    "rosemary-oil": ((214, 140, 40), (110, 56, 10), True, "ROSEMARY", "Roots deserve a ritual.", "Nourish · Massage · Overnight"),
    "7-herbal-oil": ((160, 88, 28), (58, 28, 8), True, "HERBAL", "Seven oils. One ritual.", "Kalonji · Amla · Badam"),
    "amla-reetha-shampoo": ((70, 118, 64), (20, 50, 28), True, "AMLA", "The desi deep clean.", "Cleanse · Refresh · Soften"),
    "haldi-badam-shampoo": ((250, 214, 120), (226, 150, 40), False, "HALDI", "Golden care for dry hair.", "Haldi · Badam · Shine"),
    "face-wash": ((253, 218, 130), (238, 150, 45), False, "GLOW", "Fresh face, every day.", "Cleanse · Refresh · Glow"),
    "zafarani-cream": ((126, 62, 126), (48, 18, 54), True, "ZAFRAN", "The saffron glow.", "Saffron · Soft · Radiant"),
    "neem-wash": ((104, 176, 84), (30, 96, 44), True, "NEEM", "Neem fresh, all day.", "Gentle · Fresh · Clean"),
    "rose-wash": ((240, 140, 172), (176, 40, 92), True, "ROSE", "Wake up to roses.", "Soft · Smooth · Fragrant"),
    "lavender-wash": ((180, 152, 222), (92, 62, 150), True, "LAVENDER", "Calm in every wash.", "Gentle · Calm · Soft"),
    "neem-soap": ((96, 172, 84), (28, 86, 40), True, "NEEM", "The green herbal bar.", "Herbal · Fresh · Daily"),
    "rose-soap": ((242, 132, 168), (170, 30, 84), True, "ROSE", "A rose bath, every day.", "Floral · Soft · Fresh"),
    "white-oud": ((46, 44, 42), (8, 8, 8), True, "OUD", "Scent of a royal majlis.", "Rich · Lasting · Bold"),
    "signature-perfume": ((248, 239, 220), (224, 200, 152), False, "SIGNATURE", "Your signature, bottled.", "Elegant · Gift · Classic"),
    "unisex-perfume": ((236, 238, 242), (168, 174, 186), False, "UNISEX", "One scent for everyone.", "Fresh · Travel · Daily"),
}


def logo_img(width, light):
    lg = Image.open(LOGO).convert("RGBA"); lg = lg.crop(lg.getbbox())
    lg = lg.resize((width, round(lg.height * width / lg.width)), Image.LANCZOS)
    if light:
        a = np.asarray(lg).astype(np.float32)
        lum = a[..., :3] @ np.array([.299, .587, .114])
        dark = (lum < 140)[..., None]
        a[..., :3] = np.where(dark, np.array(CREAM, np.float32), a[..., :3])
        lg = Image.fromarray(a.astype(np.uint8))
    return lg


def gradient(w, h, top, bot, glow_y=0.5):
    y = np.linspace(0, 1, h)[:, None, None]
    base = np.array(top, np.float32) * (1 - y) + np.array(bot, np.float32) * y
    base = np.repeat(base, w, axis=1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot((xx - w / 2) / w, (yy - h * glow_y) / h) * 2.2
    lift = np.clip(1 - d, 0, 1)[..., None] ** 2 * 0.35
    base = base + (255 - base) * lift
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")


def frame(c, light, inset=26):
    d = ImageDraw.Draw(c)
    col = GOLD_L if light else GOLD
    d.rectangle((inset, inset, c.width - inset, c.height - inset), outline=col + (200,), width=3)


def giant_word(c, word, light, y):
    layer = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    size = 300
    while size > 80:
        f = font("Cinzel", size, "Bold")
        if d.textlength(word, font=f) < c.width * 0.94: break
        size -= 10
    col = (255, 255, 255, 46) if light else (255, 255, 255, 120)
    d.text((c.width // 2, y), word, font=f, fill=col, anchor="mm")
    c.alpha_composite(layer)


def product_with_reflection(c, cut, cx, base, maxw, maxh):
    p = fit(load_cutout(cut), maxw, maxh)
    # contact shadow
    s = Image.new("L", c.size, 0)
    ImageDraw.Draw(s).ellipse((cx - p.width * 0.52, base - 14, cx + p.width * 0.52, base + 18), fill=120)
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); sh.putalpha(s.filter(ImageFilter.GaussianBlur(16))); c.alpha_composite(sh)
    # reflection
    r = p.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, p.width, int(p.height * 0.32)))
    g = np.linspace(0.28, 0, r.height)[:, None]
    ra = (np.asarray(r.getchannel("A")).astype(np.float32) * g).astype(np.uint8)
    r.putalpha(Image.fromarray(ra))
    c.alpha_composite(r, (int(cx - p.width / 2), int(base + 4)))
    c.alpha_composite(p, (int(cx - p.width / 2), int(base - p.height)))
    return p


def tc(light):
    return CREAM if light else INK


def hero_post(key):
    p = P[key]; top, bot, light, word, head, trio = LOOK[key]
    W, H = 1080, 1350
    c = gradient(W, H, top, bot, 0.55)
    giant_word(c, word, light, 690)
    lg = logo_img(230, light); c.alpha_composite(lg, (W // 2 - lg.width // 2, 64))
    d = ImageDraw.Draw(c)
    d.text((W // 2, 64 + lg.height + 34), p["cat"].upper(), font=font("Jost", 26, "SemiBold"), fill=GOLD_L if light else GOLD_D, anchor="ma")
    hf = font("CormorantGaramond", 78, "Bold"); y = 64 + lg.height + 76
    for ln in wrap(d, head, hf, W - 160):
        d.text((W // 2, y), ln, font=hf, fill=tc(light), anchor="ma"); y += 80
    product_with_reflection(c, p["cutout"], W // 2, 1080, 640, 1080 - y - 40)
    d = ImageDraw.Draw(c)
    name = p["name"] + (f"  ·  {p['size']}" if p["size"] else "")
    d.text((W // 2, 1150), name.upper(), font=font("Jost", 28, "SemiBold"), fill=tc(light), anchor="ma")
    d.text((W // 2, 1196), trio.upper(), font=font("Jost", 24, "SemiBold"), fill=GOLD_L if light else GOLD_D, anchor="ma")
    # price + site pill
    pill = f"{money(p['price'])}   ·   zuaja.pk"
    pf = font("Jost", 30, "Bold"); pw = d.textlength(pill, font=pf) + 70
    fill = CREAM if light else INK; txt = INK if light else CREAM
    d.rounded_rectangle((W / 2 - pw / 2, 1240, W / 2 + pw / 2, 1300), radius=30, fill=fill)
    d.text((W // 2, 1270), pill, font=pf, fill=txt, anchor="mm")
    frame(c, light)
    return c.convert("RGB")


# ---------- carousels (ivory brand look) ----------
def slide(n, total, title, body=None, items=(), kicker="", cover=False, cta=False, big=None):
    W, H = 1080, 1350
    c = bg(W, H); d = ImageDraw.Draw(c)
    lg = logo_img(200, False); c.alpha_composite(lg, (70, 64))
    d.text((W - 70, 80), f"{n:02d} / {total:02d}", font=font("Jost", 26, "SemiBold"), fill=GOLD, anchor="ra")
    y = 230 if not cover else 300
    if kicker:
        d.text((W // 2, y), kicker.upper(), font=font("Jost", 28, "SemiBold"), fill=GOLD, anchor="ma"); y += 52
    tf = font("CormorantGaramond", 96 if cover else 76, "Bold")
    for ln in wrap(d, title, tf, W - 160):
        d.text((W // 2, y), ln, font=tf, fill=INK, anchor="ma"); y += (98 if cover else 80)
    if big:
        d.text((W // 2, y + 10), big, font=font("Jost", 34, "Medium"), fill=(90, 80, 66), anchor="ma"); y += 60
    y += 20
    if body:
        bf = font("Jost", 36, "Regular")
        for ln in wrap(d, body, bf, W - 200):
            d.text((W // 2, y), ln, font=bf, fill=(60, 55, 48), anchor="ma"); y += 50
        y += 20
    if items:
        area_top, base = y + 10, 1150
        cuts = [load_cutout(P[k]["cutout"]) for k in items]
        hh = base - area_top
        ps = [q.resize((max(1, round(q.width * hh * (1 if len(cuts) == 1 else .9) / q.height)), round(hh * (1 if len(cuts) == 1 else .9))), Image.LANCZOS) for q in cuts]
        tot = sum(q.width for q in ps) + 30 * (len(ps) - 1)
        if tot > W - 160:
            k = (W - 160) / tot; ps = [q.resize((round(q.width * k), round(q.height * k)), Image.LANCZOS) for q in ps]; tot = sum(q.width for q in ps) + 30 * (len(ps) - 1)
        x = (W - tot) / 2
        s = Image.new("L", c.size, 0); ImageDraw.Draw(s).ellipse((W / 2 - tot * .55, base - 14, W / 2 + tot * .55, base + 18), fill=100)
        sh = Image.new("RGBA", c.size, (60, 40, 10, 0)); sh.putalpha(s.filter(ImageFilter.GaussianBlur(16))); c.alpha_composite(sh)
        for q in ps:
            c.alpha_composite(q, (int(x), base - q.height)); x += q.width + 30
    d = ImageDraw.Draw(c)
    if cover:
        d.text((W // 2, 1236), "SWIPE  →", font=font("Jost", 30, "Bold"), fill=GOLD, anchor="ma")
    elif cta:
        d.rounded_rectangle((W / 2 - 300, 1200, W / 2 + 300, 1290), radius=45, fill=INK)
        d.text((W // 2, 1245), "SAVE THIS  ·  SHOP AT ZUAJA.PK", font=font("Jost", 30, "Bold"), fill=GOLD_L, anchor="mm")
    else:
        d.line((W / 2 - 60, 1250, W / 2 + 60, 1250), fill=GOLD, width=3)
    frame(c, False)
    return c.convert("RGB")


CAROUSELS = {
    "shampoo-finder": [
        dict(title="Which Zuaja shampoo is right for you?", kicker="Hair guide", cover=True, items=["amla-reetha-shampoo", "haldi-badam-shampoo"]),
        dict(title="Oily scalp by evening?", kicker="Pick: Amla Reetha", body="Amla, reetha, bhringraj and aloe vera deep-clean the scalp so hair feels light and fresh.", items=["amla-reetha-shampoo"], big="200 ml · Rs 750"),
        dict(title="Dry, frizzy ends?", kicker="Pick: Haldi + Badam", body="Haldi purifies the scalp, badam nourishes and adds natural shine.", items=["haldi-badam-shampoo"], big="100 ml · Rs 450"),
        dict(title="Want stronger-looking roots?", kicker="Add: Rosemary Oil", body="Massage a few drops into the scalp, leave overnight, then wash with your Zuaja shampoo.", items=["rosemary-oil"], big="100 ml · Rs 950"),
        dict(title="Save this for wash day", kicker="Zuaja PK", cta=True, items=["amla-reetha-shampoo", "rosemary-oil", "haldi-badam-shampoo"]),
    ],
    "champi-ritual": [
        dict(title="The 10-minute champi ritual", kicker="Hair oil guide", cover=True, items=["rosemary-oil", "7-herbal-oil"]),
        dict(title="Step 1 · Warm it", body="Rub a few drops of Rosemary or 7 Herbal oil between your palms.", items=["7-herbal-oil"]),
        dict(title="Step 2 · Massage", body="Part the hair and massage into the scalp with your fingertips for 5–10 minutes.", items=["rosemary-oil"]),
        dict(title="Step 3 · Leave it", body="Leave it overnight, or at least one hour, so the oils can do their work."),
        dict(title="Step 4 · Wash", body="Wash with Amla Reetha (oily scalp) or Haldi + Badam (dry hair).", items=["amla-reetha-shampoo", "haldi-badam-shampoo"]),
        dict(title="Champi night, every week", kicker="Zuaja PK", cta=True, items=["rosemary-oil", "7-herbal-oil"]),
    ],
    "desi-ingredients": [
        dict(title="Know your desi ingredients", kicker="What's inside Zuaja", cover=True, items=["haldi-badam-shampoo", "zafarani-cream", "neem-wash"]),
        dict(title="Haldi", kicker="Turmeric", body="A kitchen classic used for generations to purify and brighten. In our Haldi + Badam Shampoo and Herbal Face Wash.", items=["face-wash"]),
        dict(title="Badam", kicker="Almond", body="Rich and nourishing, for softer hair with natural shine. In our Haldi + Badam Shampoo and 7 Herbal Oils.", items=["haldi-badam-shampoo"]),
        dict(title="Amla & Reetha", kicker="Indian gooseberry & soapnut", body="The original desi hair wash, deep cleaning without the heavy feel. In our Amla Reetha Shampoo.", items=["amla-reetha-shampoo"]),
        dict(title="Rosemary & Kalonji", kicker="Herbal oils", body="Used in champi oils for the scalp and roots. In our Rosemary Oil and 7 Herbal Oils Blend.", items=["rosemary-oil", "7-herbal-oil"]),
        dict(title="Zafran & Neem", kicker="Saffron & neem", body="Zafran for the glow, neem for freshness. In Zafarani Cream, Neem Wash and Neem Soap.", items=["zafarani-cream", "neem-wash"]),
        dict(title="Desi care, made modern", kicker="Zuaja PK", cta=True, items=["amla-reetha-shampoo", "rosemary-oil", "zafarani-cream", "face-wash"]),
    ],
    "scent-finder": [
        dict(title="Find your Zuaja scent", kicker="Fragrance guide", cover=True, items=["signature-perfume", "white-oud", "unisex-perfume"]),
        dict(title="Rich & royal?", kicker="Premium White Oud", body="Deep, long-lasting oud for weddings, Jummah and evenings.", items=["white-oud"], big="50 ml · Rs 1,999"),
        dict(title="Elegant & classic?", kicker="Signature Perfume", body="A graceful everyday luxury in a crystal-cut bottle. A perfect gift.", items=["signature-perfume"], big="50 ml · Rs 2,200"),
        dict(title="Easy & everyday?", kicker="Unisex Perfume", body="One fresh scent for him and her, in a travel-friendly 30 ml.", items=["unisex-perfume"], big="30 ml · Rs 1,500"),
        dict(title="Not sure yet? Try the White Oud Tester for Rs 250", kicker="Zuaja PK", cta=True, items=["white-oud"]),
    ],
}


def split_post(left, right, title, prompt, n1="1", n2="2"):
    W, H = 1080, 1350
    c = Image.new("RGBA", (W, H))
    for i, k in enumerate((left, right)):
        top, bot, *_ = LOOK[k]
        c.alpha_composite(gradient(W // 2, H, top, bot, 0.55), (i * W // 2, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, W, 300), fill=(251, 246, 236))
    lg = logo_img(200, False); c.alpha_composite(lg, (W // 2 - lg.width // 2, 50))
    d.text((W // 2, 140), title, font=font("CormorantGaramond", 84, "Bold"), fill=INK, anchor="ma")
    for i, k in enumerate((left, right)):
        cx = W // 4 + i * W // 2; light = LOOK[k][2]
        product_with_reflection(c, P[k]["cutout"], cx, 1060, 400, 560)
        d = ImageDraw.Draw(c)
        d.ellipse((cx - 52, 318, cx + 52, 422), fill=(251, 246, 236), outline=GOLD, width=4)
        d.text((cx, 372), (n1, n2)[i], font=font("Cinzel", 64, "Bold"), fill=INK, anchor="mm")
        d.text((cx, 1110), P[k]["name"].upper(), font=font("Jost", 26, "SemiBold"), fill=tc(light), anchor="ma")
    d.rectangle((0, H - 140, W, H), fill=INK)
    d.text((W // 2, H - 70), prompt, font=font("Jost", 40, "Bold"), fill=GOLD_L, anchor="mm")
    d.line((W // 2, 300, W // 2, H - 140), fill=GOLD_L, width=3)
    return c.convert("RGB")


def prompt_post(key, title, prompt, sub=""):
    top, bot, light, word, *_ = LOOK[key]
    W, H = 1080, 1350
    c = gradient(W, H, top, bot, 0.6); giant_word(c, word, light, 760)
    lg = logo_img(220, light); c.alpha_composite(lg, (W // 2 - lg.width // 2, 64))
    d = ImageDraw.Draw(c); y = 200
    for ln in wrap(d, title, font("CormorantGaramond", 92, "Bold"), W - 160):
        d.text((W // 2, y), ln, font=font("CormorantGaramond", 92, "Bold"), fill=tc(light), anchor="ma"); y += 94
    if sub:
        d.text((W // 2, y + 10), sub, font=font("Jost", 32, "Medium"), fill=GOLD_L if light else GOLD, anchor="ma"); y += 60
    product_with_reflection(c, P[key]["cutout"], W // 2, 1110, 560, 1110 - y - 50)
    d = ImageDraw.Draw(c)
    fill = CREAM if light else INK; txt = INK if light else CREAM
    pf = font("Jost", 34, "Bold"); pw = d.textlength(prompt, font=pf) + 80
    d.rounded_rectangle((W / 2 - pw / 2, 1200, W / 2 + pw / 2, 1276), radius=38, fill=fill)
    d.text((W // 2, 1238), prompt, font=pf, fill=txt, anchor="mm")
    frame(c, light)
    return c.convert("RGB")


def lineup_post(keys, title, sub):
    W, H = 1080, 1350
    c = bg(W, H); d = ImageDraw.Draw(c)
    lg = logo_img(300, False); c.alpha_composite(lg, (W // 2 - lg.width // 2, 80))
    d.text((W // 2, 250), title, font=font("CormorantGaramond", 88, "Bold"), fill=INK, anchor="ma")
    d.text((W // 2, 355), sub, font=font("Jost", 32, "Medium"), fill=GOLD, anchor="ma")
    base = 1110; cuts = [load_cutout(P[k]["cutout"]) for k in keys]
    hh = 620
    ps = [q.resize((max(1, round(q.width * hh * (1 if i == len(cuts) // 2 else .82) / q.height)), round(hh * (1 if i == len(cuts) // 2 else .82))), Image.LANCZOS) for i, q in enumerate(cuts)]
    tot = sum(q.width for q in ps) - 20 * (len(ps) - 1)
    if tot > W - 120:
        k = (W - 120) / tot; ps = [q.resize((round(q.width * k), round(q.height * k)), Image.LANCZOS) for q in ps]; tot = sum(q.width for q in ps) - 20 * (len(ps) - 1)
    x = (W - tot) / 2; xs = []
    for q in ps: xs.append(x); x += q.width - 20
    mid = len(ps) // 2
    for i in [j for j in range(len(ps)) if j != mid] + [mid]:
        c.alpha_composite(ps[i], (int(xs[i]), base - ps[i].height))
    d = ImageDraw.Draw(c)
    d.text((W // 2, 1160), "Shampoos · Hair Oils · Face Wash · Cream · Body Wash · Soap · Perfume", font=font("Jost", 26, "Medium"), fill=INK, anchor="ma")
    d.text((W // 2, 1230), "zuaja.pk  ·  WhatsApp 0316 1121130", font=font("Jost", 30, "Bold"), fill=GOLD, anchor="ma")
    frame(c, False)
    return c.convert("RGB")


def story(key, question, a, b):
    top, bot, light, word, *_ = LOOK[key]
    W, H = 1080, 1920
    c = gradient(W, H, top, bot, 0.45); giant_word(c, word, light, 780)
    lg = logo_img(260, light); c.alpha_composite(lg, (W // 2 - lg.width // 2, 230))
    d = ImageDraw.Draw(c); y = 380
    for ln in wrap(d, question, font("CormorantGaramond", 96, "Bold"), W - 160):
        d.text((W // 2, y), ln, font=font("CormorantGaramond", 96, "Bold"), fill=tc(light), anchor="ma"); y += 98
    product_with_reflection(c, P[key]["cutout"], W // 2, 1180, 560, 1180 - y - 40)
    d = ImageDraw.Draw(c)
    # the poll sticker goes in the empty band y 1290-1520; small hint text under it
    d.text((W // 2, 1560), f"{a}   or   {b}?", font=font("Jost", 34, "SemiBold"), fill=GOLD_L if light else GOLD, anchor="ma")
    return c.convert("RGB")


def save(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=90, optimize=True, progressive=True)


def main():
    for k in LOOK:
        save(hero_post(k), HERE / "posts" / f"{k}_post-4x5.jpg"); print("post", k, flush=True)
    for name, slides in CAROUSELS.items():
        for i, s in enumerate(slides, 1):
            save(slide(i, len(slides), **s), HERE / "carousels" / name / f"{i:02d}.jpg")
        print("carousel", name, flush=True)
    E = HERE / "engage"
    save(split_post("white-oud", "signature-perfume", "This or that?", "COMMENT 1 OR 2"), E / "this-or-that-perfume.jpg")
    save(split_post("amla-reetha-shampoo", "haldi-badam-shampoo", "Team oily or team dry?", "COMMENT 1 OR 2"), E / "this-or-that-shampoo.jpg")
    save(prompt_post("rosemary-oil", "Tag someone who needs a champi tonight", "TAG THEM IN THE COMMENTS", "Rosemary Oil · Rs 950"), E / "tag-a-friend-rosemary.jpg")
    save(prompt_post("lavender-wash", "Which scent is in your bathroom?", "NEEM · ROSE · LAVENDER, COMMENT BELOW"), E / "comment-bath-scent.jpg")
    save(prompt_post("zafarani-cream", "Your nani's glow secret?", "COMMENT 'ZAFRAN' FOR DETAILS", "Zafarani Cream · Rs 350"), E / "comment-zafran.jpg")
    save(lineup_post(["amla-reetha-shampoo", "rosemary-oil", "white-oud", "zafarani-cream", "face-wash"], "Meet Zuaja PK", "Desi care for hair, skin & body"), E / "brand-intro.jpg")
    S = HERE / "stories"
    save(story("amla-reetha-shampoo", "Oily scalp or dry ends?", "Oily", "Dry"), S / "poll-hair-type.jpg")
    save(story("white-oud", "Oud or floral?", "Oud", "Floral"), S / "poll-scent.jpg")
    save(story("rosemary-oil", "Do you oil your hair every week?", "Yes", "Not yet"), S / "poll-champi.jpg")
    save(story("face-wash", "Morning face wash: yes or no?", "Yes", "No"), S / "poll-face-wash.jpg")
    print("engage + stories done")


if __name__ == "__main__":
    main()
