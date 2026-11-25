"""UGC-style ad creatives from the graded real photos: natural photo, bold hook on top,
product + price + CTA bar at the bottom. 4:5 (feed) and 9:16 (stories/reels, safe zones).
Usage: python3 -I tools/make_ugc_ads.py   (reads media/photos/*_graded.jpg, writes media/ugc-ads/)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "marketing/meta-ads-nov"))
from grade_photo import crop_to, logo, mask  # noqa: E402
from make_statics import GOLD, GOLD_L, INK, font, wrap  # noqa: E402

PH = ROOT / "media/photos"
OUT = ROOT / "media/ugc-ads"
CREAM = (247, 236, 214)
ADS = {
    "rosemary-hand": ("Real rosemary inside. You can see it.", "Rosemary Hair Oil · 100 ml", "Rs 950", "Rs 1,500"),
    "hair-trio-a": ("Your full desi hair routine, in 3 bottles", "Amla Reetha · Haldi + Badam · Rosemary", "from Rs 450", None),
    "hair-trio-b": ("Oily scalp? Dry hair? We've got both.", "Amla Reetha · Haldi + Badam · Rosemary Oil", "from Rs 450", None),
    "amla-hand": ("Oily scalp by evening? Meet Amla Reetha.", "Amla Reetha Shampoo · 200 ml", "Rs 750", None),
    "haldi-hand": ("Dry, frizzy hair? Haldi + Badam it.", "Haldi + Badam Shampoo · 100 ml", "Rs 450", "Rs 880"),
    "washes-trio": ("Neem, Lavender or Rose: pick your shower mood", "Hand & Body Washes · 100 ml", "from Rs 300", None),
}


def shade(c, top, bottom):
    """Dark gradients behind the text so it reads on any photo."""
    w, h = c.size
    a = np.zeros((h, w), np.float32)
    y = np.arange(h)[:, None]
    a = np.maximum(a, np.clip(1 - y / top, 0, 1) * 0.72)
    a = np.maximum(a, np.clip((y - (h - bottom)) / bottom, 0, 1) * 0.82)
    layer = Image.new("RGBA", c.size, (10, 8, 6, 0)); layer.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    c.alpha_composite(layer)


def text_shadow(c, xy, s, f, fill, anchor="ma"):
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text(xy, s, font=f, fill=(0, 0, 0, 170), anchor=anchor)
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(c).text(xy, s, font=f, fill=fill, anchor=anchor)


def pill(d, cx, y, text, f, fill, txt, padx=46, h=84):
    w = d.textlength(text, font=f) + padx * 2
    d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + h), radius=h // 2, fill=fill)
    d.text((cx, y + h // 2), text, font=f, fill=txt, anchor="mm")


def price_text(price, old):
    return price + (f"  (was {old})" if old else "")


def make_feed(name):
    """4:5: whole photo visible (3:4 at full height) on its own blurred extension; hook over the dark sky;
    solid ink band at the bottom with product, price and CTA, so nothing covers the label."""
    hook, prod, price, old = ADS[name]
    W, H, band = 1080, 1350, 230
    g = Image.open(PH / f"{name}_graded.jpg").convert("RGB")
    ph = H - band
    fg = g.resize((round(g.width * ph / g.height), ph), Image.LANCZOS)
    bgi = g.resize((W, ph)).filter(ImageFilter.GaussianBlur(36)).point(lambda v: int(v * 0.5))
    c = Image.new("RGB", (W, H), INK); c.paste(bgi, (0, 0)); c.paste(fg, ((W - fg.width) // 2, 0))
    c = c.convert("RGBA"); shade(c, 360, 1)
    d = ImageDraw.Draw(c)
    hf = font("CormorantGaramond", 66, "Bold"); y = 34
    for ln in wrap(d, hook, hf, W - 100):
        text_shadow(c, (W // 2, y), ln, hf, (255, 250, 240)); y += 70
    d = ImageDraw.Draw(c)
    d.rectangle((0, H - band, W, H), fill=INK); d.line((0, H - band, W, H - band), fill=GOLD, width=4)
    lg = logo(190); c.alpha_composite(lg, (52, H - band + 34))
    d.text((52, H - band + 112), prod, font=font("Jost", 28, "Medium"), fill=CREAM)
    d.text((52, H - band + 150), price_text(price, old), font=font("Jost", 44, "Bold"), fill=GOLD_L)
    pill(d, W - 240, H - band + 70, "ORDER NOW", font("Jost", 34, "Bold"), CREAM, INK, 50, 90)
    d.text((W - 240, H - band + 180), "zuaja.pk  ·  0316 1121130", font=font("Jost", 22, "Medium"), fill=(200, 190, 170), anchor="ma")
    return c.convert("RGB")


def make_story(name):
    """9:16: ink top block (logo, hook, price pill) inside the safe zone; full-width photo below."""
    hook, prod, price, old = ADS[name]
    W, H, top = 1080, 1920, 700
    g = Image.open(PH / f"{name}_graded.jpg").convert("RGB")
    fg = g.resize((W, round(g.height * W / g.width)), Image.LANCZOS)
    fg = fg.crop((0, fg.height - (H - top), W, fg.height))          # keep the bottom (products), drop sky
    c = Image.new("RGBA", (W, H), INK + (255,)); c.paste(fg, (0, top))
    fade = Image.new("RGBA", (W, 160), INK + (0,)); fa = np.linspace(255, 0, 160).astype(np.uint8)[:, None].repeat(W, 1)
    fade.putalpha(Image.fromarray(fa)); c.alpha_composite(fade, (0, top))
    d = ImageDraw.Draw(c)
    lg = logo(300); c.alpha_composite(lg, (W // 2 - lg.width // 2, 250))
    hf = font("CormorantGaramond", 80, "Bold"); y = 250 + lg.height + 36
    for ln in wrap(d, hook, hf, W - 120):
        d.text((W // 2, y), ln, font=hf, fill=(255, 250, 240), anchor="ma"); y += 84
    d.text((W // 2, y + 14), prod.upper(), font=font("Jost", 28, "SemiBold"), fill=GOLD_L, anchor="ma")
    pill(d, W // 2, y + 64, f"{price_text(price, old)}  ·  ORDER AT ZUAJA.PK", font("Jost", 32, "Bold"), CREAM, INK, 40, 78)
    return c.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for n in ADS:
        make_feed(n).save(OUT / f"{n}_ugc-4x5.jpg", quality=90, optimize=True, progressive=True)
        make_story(n).save(OUT / f"{n}_ugc-9x16.jpg", quality=90, optimize=True, progressive=True)
        print(n, flush=True)


if __name__ == "__main__":
    main()
