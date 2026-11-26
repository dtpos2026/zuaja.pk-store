"""Professional posts from the client's REAL photos, without cutting anything out (owner preference):
the whole graded photo sits as a rounded card with a soft drop shadow and gold hairline on a
product-tinted gradient, with logo + headline above and product line + price below.
4:5 feed (1080x1350) and 9:16 story (1080x1920, text inside the safe zone).
Usage: python3 -I tools/make_real_posts.py   -> media/real-posts/
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "marketing/social-pack"))
sys.path.insert(0, str(ROOT / "marketing/meta-ads-nov"))
sys.path.insert(0, str(ROOT / "tools"))
from grade_photo import crop_to, mask  # noqa: E402
from make_social import CREAM, GOLD_D, frame, gradient, logo_img, tc  # noqa: E402
from make_statics import GOLD, GOLD_L, INK, font, wrap  # noqa: E402

OUT = ROOT / "media/real-posts"
POSTS = {  # photo: (top, bottom, light text?, kicker, headline, line, price)
    "signature-box-a": ((248, 239, 220), (214, 186, 132), False, "Signature Perfume · 50 ml", "Gift-ready luxury.", "Crystal bottle · satin gift box", "Rs 2,200"),
    "signature-box-hand": ((46, 44, 42), (10, 10, 10), True, "Signature Perfume", "The gift they'll remember.", "Long-lasting · gift box", "Rs 2,200"),
    "whiteoud-box": ((46, 44, 42), (8, 8, 8), True, "Premium White Oud · 50 ml", "Scent of a royal majlis.", "Rich · long-lasting · bold", "Rs 1,999"),
    "washes-trio-2": ((236, 170, 210), (120, 70, 160), True, "Hand & Body Wash · 100 ml", "Pick your shower mood.", "Neem · Lavender · Rose", "from Rs 300"),
    "hair-trio-b": ((196, 138, 52), (40, 66, 34), True, "Hair care", "Your desi hair routine.", "Amla Reetha · Haldi + Badam · Rosemary", "from Rs 450"),
    "rosemary-hand": ((214, 140, 40), (110, 56, 10), True, "Rosemary Hair Oil · 100 ml", "Real rosemary inside.", "Nourish · massage · overnight", "Rs 950"),
    "amla-hand": ((70, 118, 64), (20, 50, 28), True, "Amla Reetha Shampoo · 200 ml", "The desi deep clean.", "For oily scalps", "Rs 750"),
    "haldi-hand": ((250, 214, 120), (226, 150, 40), False, "Haldi + Badam Shampoo · 100 ml", "Golden care for dry hair.", "Haldi · Badam · shine", "Rs 450"),
}


def card(photo, w, h, radius=30):
    g = Image.open(ROOT / f"media/photos/{photo}_graded.jpg").convert("RGB")
    im = crop_to(g, mask(g), w / h).resize((w, h), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    im.putalpha(m)
    return im, m


def place_card(c, im, m, x, y, light):
    sh = Image.new("L", c.size, 0); sh.paste(m, (x + 10, y + 26))
    shadow = Image.new("RGBA", c.size, (0, 0, 0, 0)); shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55)))
    c.alpha_composite(shadow); c.alpha_composite(im, (x, y))
    ImageDraw.Draw(c).rounded_rectangle((x, y, x + im.width - 1, y + im.height - 1), radius=30, outline=(GOLD_L if light else GOLD) + (230,), width=3)


def pill(d, cx, y, text, light, size=30, h=62):
    f = font("Jost", size, "Bold"); w = d.textlength(text, font=f) + 80
    d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + h), radius=h // 2, fill=CREAM if light else INK)
    d.text((cx, y + h // 2), text, font=f, fill=INK if light else CREAM, anchor="mm")


def feed(key):
    top, bot, light, kicker, head, line, price = POSTS[key]
    W, H = 1080, 1350
    c = gradient(W, H, top, bot, 0.5)
    lg = logo_img(200, light); c.alpha_composite(lg, (W // 2 - lg.width // 2, 40))
    d = ImageDraw.Draw(c)
    d.text((W // 2, 40 + lg.height + 22), kicker.upper(), font=font("Jost", 24, "SemiBold"), fill=GOLD_L if light else GOLD_D, anchor="ma")
    hf = font("CormorantGaramond", 64, "Bold")
    d.text((W // 2, 40 + lg.height + 58), head, font=hf, fill=tc(light), anchor="ma")
    cw, ch = 700, 935
    im, m = card(key, cw, ch); place_card(c, im, m, (W - cw) // 2, 232, light)
    d = ImageDraw.Draw(c)
    d.text((W // 2, 232 + ch + 26), line.upper(), font=font("Jost", 24, "SemiBold"), fill=tc(light), anchor="ma")
    pill(d, W // 2, 232 + ch + 66, f"{price}  ·  zuaja.store", light, 28, 56)
    frame(c, light)
    return c.convert("RGB")


def story(key):
    top, bot, light, kicker, head, line, price = POSTS[key]
    W, H = 1080, 1920
    c = gradient(W, H, top, bot, 0.5)
    lg = logo_img(260, light); c.alpha_composite(lg, (W // 2 - lg.width // 2, 240))
    d = ImageDraw.Draw(c); y = 240 + lg.height + 24
    d.text((W // 2, y), kicker.upper(), font=font("Jost", 28, "SemiBold"), fill=GOLD_L if light else GOLD_D, anchor="ma"); y += 44
    hf = font("CormorantGaramond", 80, "Bold")
    for ln in wrap(d, head, hf, W - 140):
        d.text((W // 2, y), ln, font=hf, fill=tc(light), anchor="ma"); y += 84
    pill(d, W // 2, y + 10, f"{price}  ·  ORDER AT ZUAJA.STORE", light, 30, 66)
    y += 110
    cw = 860; ch = min(1210, H - y - 60)
    im, m = card(key, cw, ch); place_card(c, im, m, (W - cw) // 2, y, light)
    return c.convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.jpg"):
        old.unlink()   # drop the earlier cut-out versions (owner didn't like the cut edges)
    for k in POSTS:
        feed(k).save(OUT / f"{k}_post-4x5.jpg", quality=90, optimize=True, progressive=True)
        story(k).save(OUT / f"{k}_story-9x16.jpg", quality=90, optimize=True, progressive=True)
        print(k, flush=True)


if __name__ == "__main__":
    main()
