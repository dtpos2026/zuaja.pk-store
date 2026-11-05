"""Build Zuaja product images: brand banner, enhanced original, optional back label.

Usage: python3 -I make_images.py <scratchpad_dir> <logo_dir> <out_dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

S, LOGO, OUT = (Path(p) for p in sys.argv[1:4])
OUT.mkdir(parents=True, exist_ok=True)
FILES = json.load(open(S / "index.json"))

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

IVORY = (251, 244, 228)
INK = (23, 23, 23)
GOLD = (196, 147, 47)
GOLD_LIGHT = (229, 194, 113)

# handle: (name, tagline, front index, back/alt index or None)
PRODUCTS = {
    "haldi-badam-shampoo-100ml": ("Haldi + Badam Shampoo", "For hair that feels dry or rough", 29, 28),
    "amla-reetha-shampoo-200ml": ("Amla Reetha Shampoo", "For oily scalps and oiled hair", 44, 38),
    "rosemary-hair-scalp-oil-100ml": ("Rosemary Oil", "Massage into the scalp before washing", 12, 32),
    "7-herbal-oils-blend-100ml": ("7 Herbal Oils Blend", "Seven oils for hair, scalp and body", 15, 17),
    "neem-handwash-bodywash-100ml": ("Neem Handwash + Bodywash", "One neem wash for sink and shower", 41, 35),
    "zuaja-pk-lavender-hand-body-wash-with-lavender-extract-100-ml": ("Lavender Hand & Body Wash", "Floral everyday cleansing", 34, 33),
    "zafarani-cream": ("Zafarani Cream", "Rich cream for your daily skincare", 22, 20),
    "zuaja-pk-herbal-face-wash-haldi-80-ml": ("Herbal Face Wash + Haldi", "Daily wash for dirt and oil", 1, 4),
    "rose-soap": ("Rose Soap", "Bathing bar with a soft floral scent", 18, None),
    "neem-soap": ("Neem Soap", "Green neem bar for hands and body", 21, None),
    "zuaja-pk-premium-white-oud-perfume-50-ml": ("White Oud Perfume", "Oud-inspired, dark glass and gold", 24, 27),
    "zuaja-pk-premium-perfume-50-ml": ("Zuaja Signature Perfume", "Faceted glass, golden detailing", 19, 30),
    "premium-perfume": ("Unisex Perfume", "Everyday fragrance, compact spray", 42, None),
    "zuaja-pk-premium-white-oud-perfume-tester": ("White Oud Tester", "Try it before the full bottle", 11, None),
    "rose-body-wash-100ml": ("Rose Body Wash", "Soft floral scent for the shower", 10, 7),
}


def enhance(img):
    """Gray-world white balance, gentle auto-contrast, warmth, brightness and sharpening."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    g = np.asarray(img.convert("L"))
    rows = np.where(g.mean(1) > 30)[0]
    cols = np.where(g.mean(0) > 30)[0]
    img = img.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))
    # screen captures also carry a phone toolbar at the bottom; drop the last 8% when the image was letterboxed
    if rows[0] > 20:
        img = img.crop((0, 0, img.width, int(img.height * 0.92)))
    a = np.asarray(img).astype(np.float32)
    means = a.reshape(-1, 3).mean(0)
    a *= means.mean() / means
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    img = ImageOps.autocontrast(img, cutoff=(0.5, 0.5))
    img = ImageEnhance.Brightness(img).enhance(1.06)
    img = ImageEnhance.Color(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    return img.filter(ImageFilter.UnsharpMask(radius=2, percent=90, threshold=3))


def square(img, size=1200):
    """Fit the photo into a square over a soft blurred copy of itself."""
    bg = ImageOps.fit(img, (size, size)).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(1.08)
    fg = img.copy()
    fg.thumbnail((size, size), Image.LANCZOS)
    bg.paste(fg, ((size - fg.width) // 2, (size - fg.height) // 2))
    return bg


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *img.size), radius, fill=255)
    out = Image.new("RGBA", img.size)
    out.paste(img, (0, 0), mask)
    return out


def tinted_logo(color, width):
    logo = Image.open(LOGO / "lockup.png").convert("RGBA")
    logo = logo.crop(logo.getbbox())
    alpha = logo.getchannel("A")
    solid = Image.new("RGBA", logo.size, color + (255,))
    solid.putalpha(alpha)
    h = round(solid.height * width / solid.width)
    return solid.resize((width, h), Image.LANCZOS)


def text_center(draw, y, text, font, fill, width=1200):
    w = draw.textlength(text, font=font)
    draw.text(((width - w) / 2, y), text, font=font, fill=fill)


def fit_font(draw, text, path, start, max_w):
    size = start
    while size > 20:
        f = ImageFont.truetype(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(path, size)


def banner(photo, name, tagline):
    W = H = 1200
    c = Image.new("RGBA", (W, H), IVORY + (255,))
    d = ImageDraw.Draw(c)
    # soft gold arc behind the product
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((220, 170, 980, 930), fill=GOLD_LIGHT + (120,))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    # header logo
    logo = tinted_logo(INK, 330)
    c.alpha_composite(logo, ((W - logo.width) // 2, 48))
    # product photo card
    card_w, card_h = 620, 700
    ph = ImageOps.fit(photo, (card_w, card_h), centering=(0.5, 0.45))
    shadow = Image.new("RGBA", (card_w + 80, card_h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((40, 48, card_w + 40, card_h + 48), 36, fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    x, y = (W - card_w) // 2, 170
    c.alpha_composite(shadow, (x - 40, y - 40))
    c.alpha_composite(rounded(ph.convert("RGB"), 36), (x, y))
    d.rounded_rectangle((x - 2, y - 2, x + card_w + 2, y + card_h + 2), 38, outline=GOLD, width=3)
    # bottom panel
    d.rectangle((0, 900, W, H), fill=INK)
    d.line((0, 900, W, 900), fill=GOLD, width=6)
    title = fit_font(d, name.upper(), SERIF_B, 64, 1080)
    text_center(d, 935, name.upper(), title, GOLD_LIGHT)
    tag = fit_font(d, tagline, SERIF_I, 40, 1080)
    text_center(d, 1020, tagline, tag, IVORY)
    small = ImageFont.truetype(SANS, 24)
    text_center(d, 1110, "ZUAJA.PK  ·  WhatsApp 0316 1121130  ·  Delivery all over Pakistan", small, (210, 200, 180))
    return c.convert("RGB")


def main():
    report = {}
    for handle, (name, tagline, front, back) in PRODUCTS.items():
        f = enhance(Image.open(FILES[front]))
        files = []
        p = OUT / f"{handle}-1-banner.jpg"
        banner(f, name, tagline).save(p, quality=86, optimize=True, progressive=True)
        files.append(p.name)
        p = OUT / f"{handle}-3-original.jpg"
        square(f).save(p, quality=86, optimize=True, progressive=True)
        files.append(p.name)
        if back is not None:
            p = OUT / f"{handle}-4-detail.jpg"
            square(enhance(Image.open(FILES[back]))).save(p, quality=86, optimize=True, progressive=True)
            files.append(p.name)
        report[handle] = files
    json.dump(report, open(OUT / "manifest.json", "w"), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
