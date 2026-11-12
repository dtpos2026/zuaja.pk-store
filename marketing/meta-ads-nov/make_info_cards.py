"""Product-page gallery info cards (1600x1600): studio render left, name, 3 benefits,
what's inside and how to use on the right, in the store's ivory/ink/gold branding.
Usage (repo root): python3 -I marketing/meta-ads-nov/make_info_cards.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_statics import GOLD, GOLD_L, INK, bg, fit, font, glow_disc, load_cutout, logo, shadow, wrap  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = Path(__file__).resolve().parents[2] / "brand/info-cards"
EXTRA = [
    {"key": "rose-soap", "handle": "rose-soap", "name": "Rose Soap", "size": "", "cat": "Bath & Body",
     "cutout": "brand/cutouts-sr/rose-soap.png",
     "benefits": ["Soft floral rose scent", "Daily bathing bar", "Leaves skin fresh"],
     "ingredients": "Rose fragrance · Soap base", "use": "Lather on wet skin, rinse."},
    {"key": "white-oud-tester", "handle": "zuaja-pk-premium-white-oud-perfume-tester", "name": "White Oud Tester", "size": "", "cat": "Fragrance",
     "cutout": "brand/cutouts-sr/zuaja-pk-premium-white-oud-perfume-tester.png",
     "benefits": ["Try White Oud first", "Pocket-size spray", "Rich, long-lasting oud"],
     "ingredients": "White oud · Warm woods · Musk", "use": "Spray on pulse points: neck and wrists."},
]


def card(p):
    S = 1600
    c = bg(S, S); d = ImageDraw.Draw(c)
    # left: product
    glow_disc(c, 470, 820, 430)
    prod = fit(load_cutout(p["cutout"]), 640, 1060)
    shadow(c, 470, 1330, prod.width)
    c.alpha_composite(prod, (470 - prod.width // 2, 1330 - prod.height))
    # right column
    x = 900; y = 170; maxw = S - x - 90
    logo_h = logo(c, x + 170, y, 340); y += logo_h + 50
    d = ImageDraw.Draw(c)
    d.text((x, y), p["cat"].upper(), font=font("Jost", 34, "SemiBold"), fill=GOLD); y += 56
    nf = font("CormorantGaramond", 76, "Bold")
    for ln in wrap(d, p["name"], nf, maxw):
        d.text((x, y), ln, font=nf, fill=INK); y += 80
    if p.get("size"):
        d.text((x, y + 6), p["size"], font=font("Jost", 36, "Medium"), fill=(110, 100, 85)); y += 56
    y += 24
    d.line((x, y, x + 160, y), fill=GOLD, width=4); y += 44
    bf = font("Jost", 38, "Medium")
    for b in p["benefits"]:
        d.ellipse((x, y + 2, x + 44, y + 46), fill=GOLD)
        d.line((x + 11, y + 25, x + 19, y + 33), fill="white", width=5); d.line((x + 19, y + 33, x + 33, y + 14), fill="white", width=5)
        lines = wrap(d, b, bf, maxw - 64)
        for ln in lines:
            d.text((x + 64, y), ln, font=bf, fill=INK); y += 50
        y += 18
    y += 20
    for title, body in (("WHAT'S INSIDE", p["ingredients"]), ("HOW TO USE", p["use"])):
        d.text((x, y), title, font=font("Jost", 30, "Bold"), fill=GOLD); y += 46
        f = font("Jost", 32, "Regular")
        for ln in wrap(d, body, f, maxw):
            d.text((x, y), ln, font=f, fill=(60, 55, 48)); y += 44
        y += 26
    # bottom strip
    d.rectangle((0, S - 96, S, S), fill=INK); d.line((0, S - 96, S, S - 96), fill=GOLD, width=4)
    d.text((S // 2, S - 48), "zuaja.pk  ·  WhatsApp 0316 1121130  ·  Delivery all over Pakistan",
           font=font("Jost", 34, "Medium"), fill=(245, 236, 217), anchor="mm")
    return c.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prods = json.loads((HERE / "products.json").read_text()) + EXTRA
    for p in prods:
        card(p).save(OUT / f"{p['handle']}-info.jpg", quality=88, optimize=True, progressive=True)
        print(p["handle"], flush=True)


if __name__ == "__main__":
    main()
