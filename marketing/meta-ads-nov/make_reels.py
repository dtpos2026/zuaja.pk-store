"""12-second 9:16 reels for Meta ads (1080x1920, 30 fps, H.264 + AAC) in the Zuaja branding.

Storyboard per product (all key content inside the Reels safe zone, y 230-1540):
  0.0-2.5s  hook question pops in, product rises into frame
  2.5-7.5s  product name + 3 benefit chips slide in one by one, slow zoom
  7.5-9.5s  "What's inside" ingredients card
  9.5-12s   price card (old price struck, % badge), 11.11 pill (sale variant), CTA "Order now · zuaja.pk"
Background music is generated here (soft original pad + pluck), so there are no copyright issues.
Usage (repo root):  python3 -I marketing/meta-ads-nov/make_reels.py [key ...]
"""
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_statics import (CREAM, GOLD, GOLD_L, INK, RED, ROOT, bg, fit, font,  # noqa: E402
                          load_cutout, money, wrap)

HERE = Path(__file__).resolve().parent
OUT = HERE / "reels"
W, H, FPS, DUR = 1080, 1920, 30, 12.0
N = int(FPS * DUR)
LOGO = ROOT / "brand/zuaja-logo-horizontal-1600.png"


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def win(f, a, b, fade=8):
    """0..1 visibility for frame f inside [a, b) with fades."""
    if f < a or f >= b:
        return 0.0
    return min(1.0, (f - a) / fade, (b - f) / fade)


def music(path, dur=DUR, sr=44100):
    t = np.arange(int(sr * dur)) / sr
    y = np.zeros_like(t)
    chords = [[261.63, 329.63, 392.0, 493.88], [220.0, 261.63, 329.63, 392.0],
              [174.61, 220.0, 261.63, 329.63], [196.0, 246.94, 293.66, 392.0]]
    seg = dur / 4
    for i, ch in enumerate(chords):
        m = (t >= i * seg) & (t < (i + 1) * seg + 0.6)
        tt = t[m] - i * seg
        env = np.minimum(1, tt / 0.5) * np.exp(-np.maximum(0, tt - seg) * 4)
        for fq in ch:
            y[m] += 0.05 * env * (np.sin(2 * np.pi * fq / 2 * tt) + 0.35 * np.sin(2 * np.pi * fq * tt))
    beat = 60 / 96 / 2
    k = 0
    while k * beat < dur - 0.3:
        ch = chords[min(3, int(k * beat // seg))]
        fq = ch[[0, 2, 1, 3, 2, 1][k % 6]] * 2
        s = int(k * beat * sr); n = int(0.9 * sr)
        tt = np.arange(min(n, len(t) - s)) / sr
        y[s:s + len(tt)] += 0.06 * np.exp(-tt * 5) * (np.sin(2 * np.pi * fq * tt) + 0.2 * np.sin(4 * np.pi * fq * tt))
        k += 1
    # simple echo for space
    d = int(0.28 * sr); y[d:] += 0.35 * y[:-d]
    y *= np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.8)
    y = (y / max(1e-6, np.abs(y).max()) * 0.6 * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(y.tobytes())


def rays():
    r = Image.new("L", (W * 2, W * 2), 0); d = ImageDraw.Draw(r)
    cx = cy = W
    for i in range(18):
        a0 = i * 20; a1 = a0 + 7
        d.pieslice((0, 0, W * 2, W * 2), a0, a1, fill=30)
    return r.filter(ImageFilter.GaussianBlur(40))


def chip_img(text, f):
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tw = tmp.textlength(text, font=f); w = int(tw + 110); h = 84
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(255, 255, 255, 240), outline=GOLD_L + (255,), width=3)
    d.ellipse((16, 16, 68, 68), fill=GOLD)
    d.line((29, 43, 39, 53), fill="white", width=5); d.line((39, 53, 55, 31), fill="white", width=5)
    d.text((84, h // 2), text, font=f, fill=INK, anchor="lm")
    return im


def text_img(lines, f, fill, spacing=12, maxw=W - 120):
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    hs = [f.getbbox(l)[3] - f.getbbox(l)[1] for l in lines]
    lh = max(hs) + spacing
    im = Image.new("RGBA", (maxw, lh * len(lines) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((maxw // 2, 10 + i * lh), l, font=f, fill=fill, anchor="ma")
    return im


def place(c, im, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0: return
    if scale != 1.0:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.BILINEAR)
    if alpha < 1:
        im = im.copy(); a = im.getchannel("A").point(lambda v: int(v * alpha)); im.putalpha(a)
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def price_card(p, sale):
    w, h = 900, 400 if sale else 330
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=40, fill=(255, 255, 255, 245), outline=GOLD + (255,), width=4)
    fp = font("Jost", 104, "Bold"); fo = font("Jost", 46, "Medium")
    price = money(p["price"]); tw = d.textlength(price, font=fp)
    old = money(p["compare"]) if p.get("compare") else None
    ow = d.textlength(old, font=fo) if old else 0
    total = tw + (ow + 26 if old else 0)
    x0 = (w - total) / 2; y = 140
    d.text((x0, y), price, font=fp, fill=INK, anchor="ls")
    if old:
        ox = x0 + tw + 26
        d.text((ox, y - 10), old, font=fo, fill=(140, 130, 115), anchor="ls")
        d.line((ox, y - 26, ox + ow, y - 26), fill=RED, width=4)
        pct = round((p["compare"] - p["price"]) * 100 / p["compare"])
        d.rounded_rectangle((w - 170, 18, w - 22, 78), radius=30, fill=RED)
        d.text((w - 96, 48), f"-{pct}%", font=font("Jost", 36, "Bold"), fill="white", anchor="mm")
    yy = 170
    if sale:
        d.rounded_rectangle((90, yy, w - 90, yy + 64), radius=32, fill=GOLD)
        d.text((w // 2, yy + 32), "11.11 · EXTRA 11% OFF · TILL 15 NOV", font=font("Jost", 32, "Bold"), fill=INK, anchor="mm")
        yy += 84
    d.rounded_rectangle((120, yy, w - 120, yy + 100), radius=50, fill=INK)
    d.text((w // 2, yy + 50), "ORDER NOW  ·  zuaja.pk", font=font("Jost", 40, "Bold"), fill=GOLD_L, anchor="mm")
    return im


def render(p, sale, music_path):
    tag = "sale" if sale else "evergreen"
    out = OUT / f"{p['key']}_reel-9x16_{tag}.mp4"
    base = bg(W, H)
    ray = rays()
    lg = Image.open(LOGO).convert("RGBA"); lg = lg.crop(lg.getbbox()); lg = lg.resize((300, round(lg.height * 300 / lg.width)), Image.LANCZOS)
    prod = fit(load_cutout(p["cutout"]), 820, 760)
    ga = Image.new("L", (1000, 1000), 0); ImageDraw.Draw(ga).ellipse((70, 70, 930, 930), fill=255)
    glow = Image.new("RGBA", (1000, 1000), (255, 255, 255, 0)); glow.putalpha(ga.filter(ImageFilter.GaussianBlur(60)))
    ring = Image.new("RGBA", (1000, 1000), GOLD_L + (0,)); ra = Image.new("L", (1000, 1000), 0)
    ImageDraw.Draw(ra).ellipse((80, 80, 920, 920), outline=200, width=5); ring.putalpha(ra)
    hook_lines = wrap(ImageDraw.Draw(base), p["hook"], font("CormorantGaramond", 96, "Bold"), W - 140)
    hook = text_img(hook_lines, font("CormorantGaramond", 96, "Bold"), INK, 14)
    name = text_img([p["name"] + (f" · {p['size']}" if p["size"] else "")], font("Jost", 50, "SemiBold"), INK)
    kick = text_img([p["cat"].upper()], font("Jost", 34, "SemiBold"), GOLD)
    chips = [chip_img(b, font("Jost", 36, "Medium")) for b in p["benefits"]]
    inside_t = text_img(["WHAT'S INSIDE"], font("Jost", 36, "Bold"), GOLD)
    ing_lines = wrap(ImageDraw.Draw(base), p["ingredients"], font("Jost", 44, "Medium"), W - 220)
    ing = text_img(ing_lines, font("Jost", 44, "Medium"), INK, 16, W - 160)
    card = price_card(p, sale)
    sa = Image.new("L", (prod.width + 300, 120), 0)
    ImageDraw.Draw(sa).ellipse((150 - prod.width * 0.05, 30, 150 + prod.width * 1.05, 90), fill=120)
    sh = Image.new("RGBA", sa.size, (70, 45, 10, 0)); sh.putalpha(sa.filter(ImageFilter.GaussianBlur(18)))

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", str(music_path), "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    PCY = 900  # product centre
    shc = Image.new("RGBA", (prod.width + 300, 120), (70, 45, 10, 0))
    for f in range(N):
        c = base.copy()
        # slow rotating light rays behind the product
        r = ray.rotate(f * 0.25, resample=Image.BILINEAR)
        layer = Image.new("RGBA", (W, H), GOLD_L + (0,))
        a = Image.new("L", (W, H), 0); a.paste(r, (-W // 2, PCY - W))
        layer.putalpha(a); c.alpha_composite(layer)
        # logo always on top (below the IG header area)
        place(c, lg, W // 2, 290, ease(f / 12))
        # glow + ring
        gin = ease(f / 20)
        place(c, glow, W // 2, PCY, gin, 0.9 + 0.1 * gin)
        place(c, ring, W // 2, PCY, gin, 0.96 + 0.04 * gin)
        # product: rise in, then slow zoom; shrinks a bit for the price card
        rise = ease((f - 4) / 26)
        zoom = 1.0 + 0.06 * min(1, max(0, (f - 75) / 210))
        endk = ease((f - 285) / 18)
        sc = (0.86 + 0.14 * rise) * zoom * (1 - 0.22 * endk)
        cy = PCY + (1 - rise) * 600 - endk * 120
        place(c, sh, W // 2, cy + prod.height * sc / 2 - 8, rise, sc)
        place(c, prod, W // 2, cy, min(1, rise * 1.5), sc)
        # scene 1: hook
        hv = win(f, 6, 80, 10)
        place(c, hook, W // 2, 470 - (1 - ease((f - 6) / 14)) * -40, hv, 0.92 + 0.08 * ease((f - 6) / 14))
        # scene 2: kicker + name + chips
        nv = win(f, 75, 285, 10)
        place(c, kick, W // 2, 410, nv); place(c, name, W // 2, 480, nv)
        for i, ch in enumerate(chips):
            st = 85 + i * 40
            v = win(f, st, 225, 10)
            dx = (1 - ease((f - st) / 14)) * -500
            place(c, ch, W // 2 + dx, 1350 + i * 96, v)
        # scene 3: ingredients
        iv = win(f, 225, 290, 10)
        place(c, inside_t, W // 2, 1360, iv); place(c, ing, W // 2, 1400 + ing.height / 2, iv)
        # scene 4: price card
        pv = ease((f - 285) / 14)
        if pv > 0:
            place(c, card, W // 2, 1330 + (1 - pv) * 200, pv)
        ff.stdin.write(c.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    print(out.name, out.stat().st_size // 1024, "KB", flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mp = OUT / "zuaja-bed-12s.wav"
    music(mp)
    prods = json.loads((HERE / "products.json").read_text())
    want = set(sys.argv[1:])
    variants = [True, False]
    if want & {"--sale-only"}:
        variants = [True]; want -= {"--sale-only"}
    for p in prods:
        if want and p["key"] not in want:
            continue
        for sale in variants:
            render(p, sale, mp)


if __name__ == "__main__":
    main()
