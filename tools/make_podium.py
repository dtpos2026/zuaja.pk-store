"""Luxury studio packshots: real product cut-out on a rendered ivory-marble podium with a gold rim.

Every product gets the identical set (same light, podium, bokeh) so the store looks like one shoot.
Label pixels come only from the real photo; nothing on the product is generated.
Usage: python3 -I make_podium.py <out_dir> <logo_png> <key>=<cutout.png>[:raw] ...
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

OUT, LOGO = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
S = 1500
rng = np.random.default_rng(7)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def backdrop():
    y = np.linspace(0, 1, S)[:, None]
    x = np.linspace(0, 1, S)[None, :]
    top, bottom = np.array([252, 247, 236]), np.array([241, 228, 202])
    base = top + (bottom - top) * (y ** 1.2)[..., None]
    # key light from the upper left
    d = np.sqrt((x - 0.25) ** 2 + (y - 0.12) ** 2)
    light = np.clip(1 - d / 0.9, 0, 1) ** 2 * 18
    img = np.clip(base + light[..., None], 0, 255)
    c = Image.fromarray(img.astype(np.uint8)).convert("RGBA")
    # soft diagonal light beams
    beams = Image.new("L", (S, S), 0)
    bd = ImageDraw.Draw(beams)
    for off, w in ((0.05, 90), (0.2, 60), (0.33, 40)):
        x0 = int(S * off)
        bd.polygon([(x0, 0), (x0 + w, 0), (x0 + w + 700, S), (x0 + 700, S)], fill=40)
    c.paste(Image.new("RGBA", (S, S), (255, 252, 240, 255)), (0, 0), beams.filter(ImageFilter.GaussianBlur(60)))
    # gold bokeh in the far background
    bok = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bk = ImageDraw.Draw(bok)
    for _ in range(26):
        side = rng.choice([0, 1])
        cx = rng.uniform(0.0, 0.2) if side == 0 else rng.uniform(0.8, 1.0)
        cy = rng.uniform(0.15, 0.6)
        r = rng.uniform(14, 46)
        a = int(rng.uniform(70, 150))
        bk.ellipse((cx * S - r, cy * S - r, cx * S + r, cy * S + r), fill=(238, 205, 130, a))
    c.alpha_composite(bok.filter(ImageFilter.GaussianBlur(10)))
    return c


def marble(w, h):
    n = rng.normal(0, 1, (h // 8 + 2, w // 8 + 2))
    n = Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    n = n.filter(ImageFilter.GaussianBlur(6))
    arr = np.asarray(n).astype(np.float32) / 255
    veins = np.abs(np.sin((np.linspace(0, 1, w)[None, :] * 9 + arr * 5) * np.pi))
    veins = (veins < 0.06).astype(np.float32) * 0.5
    col = np.array([245, 238, 226]) - (arr[..., None] * 14) - (veins[..., None] * np.array([40, 34, 20]))
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))


def podium(c):
    cx, top_y = S // 2, int(S * 0.78)
    rx, ry, h = int(S * 0.34), int(S * 0.055), int(S * 0.10)
    # floor shadow
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse((cx - rx * 1.15, top_y + h - ry * 0.6, cx + rx * 1.15, top_y + h + ry * 1.5), fill=120)
    c.paste(Image.new("RGBA", (S, S), (120, 98, 60, 255)), (0, 0), m.filter(ImageFilter.GaussianBlur(40)))
    # cylinder side: marble with left-to-right shading
    side = marble(2 * rx, h + ry).convert("RGBA")
    shade = np.linspace(0.92, 1.04, 2 * rx)[None, :, None] * np.ones((h + ry, 1, 1))
    sa = np.clip(np.asarray(side.convert("RGB")).astype(np.float32) * shade, 0, 255).astype(np.uint8)
    side = Image.fromarray(sa).convert("RGBA")
    mask = Image.new("L", side.size, 0)
    md = ImageDraw.Draw(mask)
    md.rectangle((0, ry, 2 * rx, h), fill=255)
    md.ellipse((0, h - ry, 2 * rx, h + ry), fill=255)
    c.paste(side, (cx - rx, top_y), mask)
    # gold rim band
    d = ImageDraw.Draw(c)
    for i, col in enumerate([(176, 128, 40), (229, 194, 113), (196, 147, 47)]):
        d.arc((cx - rx, top_y - ry + 6 + i * 2, cx + rx, top_y + ry + 6 + i * 2), 0, 180, fill=col, width=3)
    # top face
    topf = marble(2 * rx, 2 * ry)
    tm = Image.new("L", topf.size, 0)
    ImageDraw.Draw(tm).ellipse((0, 0, 2 * rx - 1, 2 * ry - 1), fill=255)
    topf = ImageEnhance.Brightness(topf).enhance(1.04)
    c.paste(topf, (cx - rx, top_y - ry), tm)
    d.ellipse((cx - rx, top_y - ry, cx + rx, top_y + ry), outline=(205, 160, 70), width=4)
    return cx, top_y


def retouch(p, gloss=True):
    """Studio retouch from the real photo: balance, S-curve, clarity, vibrance, then a soft
    vertical studio-light gloss on the left third (screen blend inside the product only)."""
    rgb = p.convert("RGB")
    a = np.asarray(p.getchannel("A")) > 200
    arr = np.asarray(rgb).astype(np.float32)
    if a.sum() > 500:
        px = arr[a]
        lo, hi = np.percentile(px, 0.5, axis=0), np.percentile(px, 99.5, axis=0)
        arr = np.clip((arr - lo) / np.maximum(hi - lo, 1) * 255, 0, 255)
        m = arr[a].mean(0)
        arr = np.clip(arr * (m.mean() / m) ** 0.6, 0, 255)
    x = arr / 255.0
    x = x + 0.3 * (x - x ** 2) * (2 * x - 1)  # gentle S-curve
    x = np.clip(0.5 + (x - 0.5) * 1.08, 0, 1)
    arr = x * 255
    rgb = Image.fromarray(arr.astype(np.uint8))
    clar = rgb.filter(ImageFilter.UnsharpMask(radius=24, percent=35, threshold=0))
    rgb = clar.filter(ImageFilter.UnsharpMask(radius=1.6, percent=(40 if os.environ.get("ZUAJA_SR") else 110), threshold=2))
    rgb = ImageEnhance.Color(rgb).enhance(1.16)
    out = rgb.convert("RGBA")
    if gloss:
        w, h = out.size
        g = Image.new("L", (w, h), 0)
        gd = ImageDraw.Draw(g)
        gd.rectangle((int(w * 0.22), int(h * 0.04), int(w * 0.30), int(h * 0.96)), fill=95)
        gd.rectangle((int(w * 0.72), int(h * 0.08), int(w * 0.75), int(h * 0.92)), fill=45)
        g = g.filter(ImageFilter.GaussianBlur(max(4, w * 0.025)))
        g = ImageChops.multiply(g, p.getchannel("A"))
        white = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        out = Image.composite(Image.blend(out, ImageChops.screen(out, white), 1.0), out, g)
    out.putalpha(p.getchannel("A"))
    return out


def drop_stand(p):
    """Soap photos stand on a light block; cut where the dark bar ends and the block begins."""
    arr = np.asarray(p.convert("RGBA")).astype(np.float32)
    al = arr[..., 3] > 128
    mean = arr[..., :3].mean(axis=2)
    med = np.array([np.median(mean[y][al[y]]) if al[y].any() else 0 for y in range(p.height)])
    bar = np.median(med[int(p.height * 0.2):int(p.height * 0.5)])
    thr = max(90, bar * 2.2)
    for y in range(int(p.height * 0.35), p.height):
        if med[y] > thr:
            return p.crop((0, 0, p.width, max(1, y - 4)))
    return p


def feather(p):
    a = p.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    p = p.copy()
    p.putalpha(a)
    return p


def watermark(c):
    lg = Image.open(LOGO).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    w = int(S * 0.22)
    lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.55)))
    m = int(S * 0.035)
    c.alpha_composite(lg, (S - w - m, S - lg.height - m))


BASE = None


def sweep():
    y = np.linspace(0, 1, S)[:, None] * np.ones((1, S))
    x = np.ones((S, 1)) * np.linspace(0, 1, S)[None, :]
    wall_t, wall_b = np.array([250, 244, 230]), np.array([244, 233, 210])
    floor_t, floor_b = np.array([238, 226, 200]), np.array([250, 245, 234])
    hz = 0.72
    wall = wall_t + (wall_b - wall_t) * (y / hz)[..., None]
    fl = floor_t + (floor_b - floor_t) * ((y - hz) / (1 - hz)).clip(0, 1)[..., None]
    blend = np.clip((y - hz + 0.04) / 0.08, 0, 1)[..., None]
    img = wall * (1 - blend) + fl * blend
    d = np.sqrt((x - 0.5) ** 2 + ((y - 0.42) * 1.1) ** 2)
    img = img + (np.clip(1 - d / 0.45, 0, 1) ** 2 * 14)[..., None]
    vig = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
    img = img - (np.clip(vig - 0.45, 0, 1) * 40)[..., None]
    c = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    r = S * 0.33
    ImageDraw.Draw(ring).ellipse((S / 2 - r, S * 0.42 - r, S / 2 + r, S * 0.42 + r), outline=(205, 160, 70, 150), width=4)
    c.alpha_composite(ring.filter(ImageFilter.GaussianBlur(0.6)))
    return c


def straighten(p):
    """Rotate an upright bottle so its main axis is vertical (fixes hand-held tilt)."""
    a = np.asarray(p.getchannel("A")) > 128
    ys, xs = np.nonzero(a)
    if len(xs) < 1000:
        return p
    xy = np.stack([xs - xs.mean(), ys - ys.mean()])
    w, v = np.linalg.eigh(np.cov(xy))
    vx, vy = v[:, np.argmax(w)]
    ang = np.degrees(np.arctan2(vx, vy))
    if ang > 90:
        ang -= 180
    if ang < -90:
        ang += 180
    if 0.4 < abs(ang) < 9:
        p = p.rotate(-ang, resample=Image.BICUBIC, expand=True)
    return p


import os
STYLE = os.environ.get("ZUAJA_STYLE", "studio")


def scene(p, upright=True):
    global BASE
    if BASE is None:
        BASE = Image.new("RGBA", (S, S), (255, 255, 255, 255)) if STYLE == "white" else sweep()
    c = BASE.copy()
    if upright:
        p = straighten(p)
    p = p.crop(p.getbbox())
    if STYLE == "cutout":
        return p
    if STYLE == "white":
        r = min(S * 0.80 / p.height, S * 0.62 / p.width)
    else:
        r = min(S * 0.60 / p.height, S * 0.40 / p.width)
    p = p.resize((round(p.width * r), round(p.height * r)), Image.LANCZOS)
    cx, base = S // 2, int(S * (0.90 if STYLE == "white" else 0.80))
    x, y = cx - p.width // 2, base - p.height
    if STYLE != "white":
        refl = p.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, p.width, int(p.height * 0.28)))
        g = Image.linear_gradient("L").resize(refl.size).point(lambda v: int((255 - v) * 0.22))
        refl.putalpha(ImageChops.multiply(refl.getchannel("A"), g))
        c.alpha_composite(refl.filter(ImageFilter.GaussianBlur(1.2)), (x, base + 1))
    for spread, blur, alpha in (((0.9, 26, 45), (1.0, 8, 90)) if STYLE == "white" else ((0.8, 30, 70), (1.0, 9, 140))):
        m = Image.new("L", (S, S), 0)
        w = p.width * spread
        ImageDraw.Draw(m).ellipse((cx - w / 2 - 10, base - 10, cx + w / 2 + 10, base + 12), fill=alpha)
        c.paste(Image.new("RGBA", (S, S), (70, 55, 30, 255)), (0, 0), m.filter(ImageFilter.GaussianBlur(blur)))
    c.alpha_composite(p, (x, y))
    watermark(c)
    return c.convert("RGB")


for arg in sys.argv[3:]:
    key, src = arg.split("=", 1)
    soap = src.endswith(":soap")
    src = src[:-5] if soap else src
    flat = src.endswith(":flat")
    src = src[:-5] if flat else src
    raw = src.endswith(":raw")
    src = src[:-4] if raw else src
    p = Image.open(src).convert("RGBA")
    if soap:
        p = drop_stand(p)
        flat = True
    p = feather(p if raw else retouch(p, gloss=not flat))
    res = scene(p, upright=not flat)
    if STYLE == "cutout":
        res.save(OUT / f"{key}.png", optimize=True)
    else:
        res.save(OUT / f"{key}.jpg", quality=90, optimize=True, progressive=True)
    print(key)
