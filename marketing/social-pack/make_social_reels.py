"""5 organic reels (1080x1920, 15 s) cut on the beat of Zuaja's own jingle (96 BPM, 24 beats).
The last 4 beats are always the end card, timed with the 'Zu-a-ja P-K' motif + bell.
Key content stays inside the Reels safe zone (y 230-1540).
Run from repo root: python3 -I marketing/social-pack/make_social_reels.py [name ...]
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_social import CREAM, GOLD_D, LOOK, P, giant_word, gradient, logo_img, tc  # noqa: E402
from make_statics import GOLD, GOLD_L, INK, bg, fit, font, load_cutout, money, wrap  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "reels"
MUSIC = HERE / "music/zuaja-jingle-15s.wav"
W, H, FPS = 1080, 1920, 30
BEAT = 60 / 96

REELS = {
    "brand": [("intro", "Desi care, made modern", 2)]
    + [("prod", k, "", 1) for k in ["amla-reetha-shampoo", "haldi-badam-shampoo", "rosemary-oil", "7-herbal-oil", "face-wash",
                                    "zafarani-cream", "neem-wash", "rose-wash", "lavender-wash", "neem-soap", "white-oud",
                                    "signature-perfume", "unisex-perfume"]]
    + [("text", "Hair · Skin · Body · Fragrance", 3), ("text", "From Gujranwala, Pakistan", 2)],
    "hair-ritual": [("intro", "Your weekly hair ritual", 2),
                    ("prod", "amla-reetha-shampoo", "Oily scalp? Amla Reetha", 4),
                    ("prod", "haldi-badam-shampoo", "Dry ends? Haldi + Badam", 4),
                    ("prod", "rosemary-oil", "Champi night: Rosemary Oil", 4),
                    ("prod", "7-herbal-oil", "7 desi oils, 1 bottle", 4),
                    ("text", "Save it. Share it. Try it.", 2)],
    "fragrance": [("intro", "Find your scent", 2),
                  ("prod", "white-oud", "Rich & royal", 5),
                  ("prod", "signature-perfume", "Elegant & classic", 5),
                  ("prod", "unisex-perfume", "Fresh, for everyone", 5),
                  ("text", "Try the White Oud Tester for Rs 250", 3)],
    "glow": [("intro", "Glow, the desi way", 2),
             ("prod", "face-wash", "Morning: Haldi Face Wash", 5),
             ("prod", "zafarani-cream", "Night: Zafarani Cream", 5),
             ("text", "Fresh by day, glowing by night", 3),
             ("prod", "rose-wash", "Shower: Rose Body Wash", 5)],
    "bath": [("intro", "Your shower, upgraded", 2),
             ("prod", "neem-wash", "Neem: fresh & clean", 4),
             ("prod", "rose-wash", "Rose: soft & fragrant", 4),
             ("prod", "lavender-wash", "Lavender: calm & gentle", 4),
             ("prod", "neem-soap", "Neem Soap: the herbal bar", 4),
             ("text", "Which one is yours?", 2)],
}


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def text_layer(lines, f, fill, lh):
    im = Image.new("RGBA", (W, lh * len(lines) + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((W // 2, 10 + i * lh), l, font=f, fill=fill, anchor="ma")
    return im


def place(c, im, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0: return
    if scale != 1.0:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.BILINEAR)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


class Scene:
    def __init__(self, spec, accent_key):
        kind = spec[0]; self.kind = kind; self.beats = spec[-1]
        tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        if kind == "prod":
            key, cap = spec[1], spec[2]; p = P[key]; top, bot, light, word, head, _ = LOOK[key]
            self.bg = gradient(W, H, top, bot, 0.5); giant_word(self.bg, word, light, 900)
            lg = logo_img(260, light); self.bg.alpha_composite(lg, (W // 2 - lg.width // 2, 250))
            self.prod = fit(load_cutout(p["cutout"]), 800, 820)
            cap = cap or p["name"]
            size = 92  # one line only, so the caption never runs into the product
            while size > 64 and tmp.textlength(cap, font=font("CormorantGaramond", size, "Bold")) > W - 120:
                size -= 4
            hf = font("CormorantGaramond", size, "Bold")
            self.head = text_layer(wrap(tmp, cap, hf, W - 100)[:2], hf, tc(light), size + 4)
            sub = f"{p['name']}{'  ·  ' + p['size'] if p['size'] else ''}   |   {money(p['price'])}"
            self.sub = text_layer([sub.upper()], font("Jost", 32, "SemiBold"), GOLD_L if light else GOLD_D, 40)
        else:
            k = accent_key; top, bot, light, word, *_ = LOOK[k]
            if kind == "intro":
                self.bg = bg(W, H); light = False
            else:
                self.bg = gradient(W, H, top, bot, 0.5)
            lg = logo_img(340 if kind == "intro" else 260, light)
            self.bg.alpha_composite(lg, (W // 2 - lg.width // 2, 300 if kind == "intro" else 250))
            hf = font("CormorantGaramond", 110 if kind == "intro" else 96, "Bold")
            self.head = text_layer(wrap(tmp, spec[1], hf, W - 140), hf, tc(light), 112 if kind == "intro" else 100)
            self.prod = None; self.sub = None
            self.line = GOLD if not light else GOLD_L

    def frame(self, t):
        c = self.bg.copy()
        if self.kind == "prod":
            k = ease(t / 0.3)
            place(c, self.prod, W // 2, 1000 + (1 - k) * 120, min(1, k * 1.4), (0.86 + 0.14 * k) * (1 + 0.03 * t))
            place(c, self.head, W // 2, 520 - (1 - ease((t - 0.05) / 0.25)) * 40, ease((t - 0.05) / 0.2))
            place(c, self.sub, W // 2, 1500, ease((t - 0.12) / 0.2))
        else:
            k = ease(t / 0.35)
            place(c, self.head, W // 2, 820 + (1 - k) * 60, k, 0.94 + 0.06 * k)
            d = ImageDraw.Draw(c); w = int(200 * ease((t - 0.15) / 0.4))
            if w > 0: d.line((W / 2 - w, 980, W / 2 + w, 980), fill=self.line, width=4)
        return c


def end_card():
    c = bg(W, H); d = ImageDraw.Draw(c)
    lg = logo_img(520, False); c.alpha_composite(lg, (W // 2 - lg.width // 2, 520))
    d.text((W // 2, 760), "Desi care for hair, skin & body", font=font("CormorantGaramond", 64, "Bold"), fill=INK, anchor="ma")
    d.rounded_rectangle((W / 2 - 330, 900, W / 2 + 330, 1010), radius=55, fill=INK)
    d.text((W // 2, 955), "SHOP AT ZUAJA.PK", font=font("Jost", 46, "Bold"), fill=GOLD_L, anchor="mm")
    d.text((W // 2, 1080), "WhatsApp 0316 1121130  ·  Delivery all over Pakistan", font=font("Jost", 32, "Medium"), fill=GOLD_D, anchor="ma")
    return c


def render(name, specs):
    accent = next((s[1] for s in specs if s[0] == "prod"), "white-oud")
    scenes = [Scene(s, accent) for s in specs]
    assert sum(s.beats for s in scenes) == 20, name
    end = end_card()
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"zuaja-reel-{name}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(MUSIC), "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(24 * BEAT * FPS) + 1
    starts = np.cumsum([0] + [s.beats for s in scenes]) * BEAT
    for f in range(total):
        t = f / FPS
        if t >= 20 * BEAT:
            te = t - 20 * BEAT
            c = end.copy()
            k = ease(te / 0.4)
            if k < 1:  # end card slides in
                c = Image.blend(scenes[-1].frame(t - starts[-2]).convert("RGB").convert("RGBA"), c, k)
        else:
            i = int(np.searchsorted(starts, t, side="right") - 1)
            c = scenes[i].frame(t - starts[i])
            since = t - starts[i]
            if i > 0 and since < 0.07:  # quick flash on the cut, lands on the beat
                c = Image.blend(c, Image.new("RGBA", c.size, (255, 250, 240, 255)), 0.35 * (1 - since / 0.07))
        ff.stdin.write(c.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    print(out.name, out.stat().st_size // 1024, "KB", flush=True)


if __name__ == "__main__":
    want = set(sys.argv[1:])
    for n, s in REELS.items():
        if not want or n in want:
            render(n, s)
