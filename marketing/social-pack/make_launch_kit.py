"""Launch kit for an empty Instagram/Facebook page: the first 6 posts (2 full grid rows),
profile picture, Facebook cover, 5 Instagram highlight covers, a profile mock-up and a PDF guide.
Run from repo root: python3 -I marketing/social-pack/make_launch_kit.py
"""
import base64
import html
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "marketing/social-pack"))
from make_plan_pdf import EXTRA, P, REEL, product_caption, esc  # noqa: E402
from make_social import CREAM, LOOK, gradient, logo_img  # noqa: E402
from make_statics import GOLD, GOLD_L, INK, bg, fit, font, load_cutout  # noqa: E402

SP = ROOT / "marketing/social-pack"
OUT = SP / "launch-kit"
FONTS = ROOT / "marketing/meta-ads-nov/fonts"
LOGO = ROOT / "brand/zuaja-logo-horizontal-1600.png"

# posting order: oldest first. Instagram shows the newest at the top-left.
LAUNCH = [
    ("engage", "brand-intro", SP / "engage/brand-intro.jpg"),
    ("post", "rosemary-oil", SP / "posts/rosemary-oil_post-4x5.jpg"),
    ("post", "white-oud", SP / "posts/white-oud_post-4x5.jpg"),
    ("car", "shampoo-finder", SP / "carousels/shampoo-finder/01.jpg"),
    ("post", "zafarani-cream", SP / "posts/zafarani-cream_post-4x5.jpg"),
    ("reel", "brand", SP / "reels/zuaja-reel-brand.mp4"),
]


def mark():
    lg = Image.open(LOGO).convert("RGBA"); lg = lg.crop(lg.getbbox())
    m = lg.crop((0, 0, 345, lg.height)); return m.crop(m.getbbox())


def profile_pic():
    S = 1080; c = bg(S, S); d = ImageDraw.Draw(c)
    d.ellipse((60, 60, S - 60, S - 60), outline=GOLD, width=10)
    m = fit(mark(), 560, 560); c.alpha_composite(m, (S // 2 - m.width // 2, S // 2 - m.height // 2 - 10))
    return c.convert("RGB")


def fb_cover():
    W, H = 1640, 624
    c = bg(W, H); d = ImageDraw.Draw(c)
    lg = logo_img(520, False); c.alpha_composite(lg, (250, 170))
    d.text((250, 330), "Desi care, made modern", font=font("CormorantGaramond", 58, "Bold"), fill=INK)
    d.text((252, 410), "HAIR · SKIN · BODY · FRAGRANCE", font=font("Jost", 26, "SemiBold"), fill=GOLD)
    d.text((252, 452), "zuaja.store  ·  WhatsApp 0316 1121130", font=font("Jost", 26, "Medium"), fill=(90, 80, 66))
    keys = ["amla-reetha-shampoo", "rosemary-oil", "white-oud", "zafarani-cream", "face-wash"]
    ps = [load_cutout(P[k]["cutout"]) for k in keys]
    hh = 400; ps = [q.resize((max(1, round(q.width * hh * (1 if i == 2 else .82) / q.height)), round(hh * (1 if i == 2 else .82))), Image.LANCZOS) for i, q in enumerate(ps)]
    tot = sum(q.width for q in ps) - 18 * 4; x0 = 1390 - tot // 2; base = 540
    s = Image.new("L", c.size, 0); ImageDraw.Draw(s).ellipse((x0 - 10, base - 12, x0 + tot + 10, base + 16), fill=100)
    sh = Image.new("RGBA", c.size, (60, 40, 10, 0)); sh.putalpha(s.filter(ImageFilter.GaussianBlur(14))); c.alpha_composite(sh)
    xs = []; x = x0
    for q in ps: xs.append(x); x += q.width - 18
    for i in [0, 1, 3, 4, 2]:
        c.alpha_composite(ps[i], (int(xs[i]), base - ps[i].height))
    return c.convert("RGB")


def highlight(label, key=None):
    W, H = 1080, 1920
    c = bg(W, H); d = ImageDraw.Draw(c)
    cx, cy, r = W // 2, H // 2, 420
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 251, 242), outline=GOLD, width=14)
    if key:
        q = fit(load_cutout(P[key]["cutout"]), 470, 520)
        c.alpha_composite(q, (cx - q.width // 2, cy - q.height // 2 - 40))
    else:
        m = fit(mark(), 420, 420); c.alpha_composite(m, (cx - m.width // 2, cy - m.height // 2 - 40))
    d = ImageDraw.Draw(c)
    d.text((cx, cy + 300), label.upper(), font=font("Jost", 54, "Bold"), fill=GOLD, anchor="mm")
    return c.convert("RGB")


def thumb_img(path):
    path = Path(path)
    if path.suffix == ".mp4":
        tmp = OUT / "_f.jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "4", "-i", str(path), "-frames:v", "1", str(tmp)], check=True)
        im = Image.open(tmp).convert("RGB"); tmp.unlink(); return im
    return Image.open(path).convert("RGB")


def grid_mock(profile):
    """Phone-style mock of the profile after the 6 launch posts (newest first)."""
    W = 1080; cell = W // 3; top = 520
    c = Image.new("RGB", (W, top + cell * 4 // 3 * 2 + 6), "white"); d = ImageDraw.Draw(c)
    pp = profile.resize((210, 210)); m = Image.new("L", (210, 210), 0); ImageDraw.Draw(m).ellipse((0, 0, 209, 209), fill=255)
    c.paste(pp, (50, 50), m)
    for i, (n, l) in enumerate((("6", "posts"), ("—", "followers"), ("—", "following"))):
        d.text((420 + i * 220, 120), n, font=font("Jost", 44, "Bold"), fill=INK, anchor="mm")
        d.text((420 + i * 220, 175), l, font=font("Jost", 28, "Regular"), fill=(90, 90, 90), anchor="mm")
    d.text((50, 290), "Zuaja PK | Herbal Hair & Skin Care", font=font("Jost", 32, "Bold"), fill=INK)
    for i, ln in enumerate(["Desi care, made modern 🌿".replace("🌿", ""), "Shampoos · Hair Oils · Face Wash · Perfumes", "Delivery all over Pakistan · zuaja.store"]):
        d.text((50, 340 + i * 40), ln, font=font("Jost", 28, "Regular"), fill=(40, 40, 40) if i < 2 else (30, 80, 160))
    hl = [("Hair", "rosemary-oil"), ("Skin", "zafarani-cream"), ("Bath", "neem-wash"), ("Scents", "white-oud"), ("Order", None)]
    hl_y = 470 - 10
    # newest first in the grid
    items = [Image.open(OUT / "reel-cover-brand.jpg").convert("RGB") if str(p).endswith(".mp4") else thumb_img(p) for _, _, p in reversed(LAUNCH)]
    h = cell * 4 // 3
    for i, im in enumerate(items):
        x, y = (i % 3) * cell, top + (i // 3) * (h + 3)
        im = im.resize((cell - 3, int((cell - 3) * im.height / im.width)))
        im = im.crop((0, (im.height - h) // 2, im.width, (im.height - h) // 2 + h)) if im.height > h else im
        c.paste(im, (x, y))
    return c


def b64(im, w=None):
    if w: im = im.copy(); im.thumbnail((w, w * 3))
    b = io.BytesIO(); im.save(b, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def caption_for(kind, key):
    if kind == "post":
        return product_caption(key)
    if kind == "engage":
        return EXTRA[key]
    if kind == "car":
        return EXTRA["car-" + key]
    cap, tags = REEL[key]
    return (cap + "\n📍 Delivery all over Pakistan · Order at zuaja.store or WhatsApp 0316 1121130", tags, "")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pp = profile_pic(); pp.save(OUT / "profile-picture.jpg", quality=92)
    fc = fb_cover(); fc.save(OUT / "facebook-cover.jpg", quality=92)
    HL = [("Hair", "rosemary-oil"), ("Skin", "zafarani-cream"), ("Bath", "neem-wash"), ("Scents", "white-oud"), ("Order", None)]
    hls = []
    for lab, k in HL:
        im = highlight(lab, k); im.save(OUT / f"highlight-{lab.lower()}.jpg", quality=90); hls.append(im)
    mock = grid_mock(pp); mock.save(OUT / "profile-preview.jpg", quality=88)
    names = {"engage": "Engagement post", "post": "Product post", "car": "Carousel (upload all 5 slides in order)", "reel": "Reel (music inside)"}
    files = {"engage": "Social-Pack / engage/brand-intro.jpg", "car": "Social-Pack / carousels/shampoo-finder/01–05.jpg", "reel": "Social-Pack / reels/zuaja-reel-brand.mp4 · cover: launch-kit/reel-cover-brand.jpg (Edit cover → Add from camera roll)"}
    steps = []
    for i, (kind, key, path) in enumerate(LAUNCH, 1):
        cap, tags, alt = caption_for(kind, key)
        f = files.get(kind, f"Social-Pack / posts/{key}_post-4x5.jpg")
        title = names[kind] + ("" if kind not in ("post",) else f": {P[key]['name']}")
        pin = " · 📌 PIN THIS" if (kind, key) in (("engage", "brand-intro"), ("car", "shampoo-finder"), ("reel", "brand")) else ""
        img = Image.open(OUT / "reel-cover-brand.jpg").convert("RGB") if kind == "reel" else thumb_img(path)
        steps.append(f'''<div class="post"><div class="n">{i}</div><img src="{b64(img, 300)}"><div class="b">
<div class="t">{html.escape(title)}{pin}</div><div class="f">{html.escape(f)}</div>
<div class="cap">{esc(cap)}</div><div class="tags">{html.escape(tags)}</div>{('<div class="alt"><b>Alt text:</b> ' + html.escape(alt) + '</div>') if alt else ''}</div></div>''')
    hl_html = "".join(f'<div class="hl"><img src="{b64(im.crop((0, 420, 1080, 1500)), 200)}"><span>{lab}</span></div>' for (lab, _), im in zip(HL, hls))
    page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Jost;src:url("file://{FONTS}/Jost.ttf")}}@font-face{{font-family:Corm;src:url("file://{FONTS}/CormorantGaramond.ttf")}}
@page{{size:A4;margin:12mm}}*{{box-sizing:border-box}}body{{font-family:Jost;color:#1b1b1b;font-size:10.5pt;line-height:1.42;margin:0}}
h1,h2{{font-family:Corm;margin:0}}h2{{font-size:22pt;margin:0 0 4mm}}.pb{{page-break-before:always}}
.cover{{height:268mm;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;background:radial-gradient(circle at 50% 40%,#fffaf0,#f1e3c2);border:3px solid #c4932f}}
.cover h1{{font-size:38pt;margin-top:8mm}}.cover p{{font-size:13pt;color:#6b5a3a;margin:2mm}}
.box{{background:#fbf6ec;border:1px solid #ead9b3;border-radius:3mm;padding:4mm 5mm;margin:3mm 0}}
.two{{display:flex;gap:6mm;align-items:flex-start}}.two img{{width:78mm;border:1px solid #ddd;border-radius:3mm}}
ol li,ul li{{margin:1mm 0}}.post{{display:flex;gap:4mm;page-break-inside:avoid;border:1px solid #ead9b3;border-radius:3mm;padding:3mm;margin-bottom:4mm;background:#fffdf8}}
.post img{{width:36mm;border-radius:2mm;align-self:flex-start}}.n{{font-family:Corm;font-size:30pt;font-weight:700;color:#c4932f;width:10mm}}
.b{{flex:1}}.t{{font-weight:700;font-size:11.5pt}}.f{{font-size:8.5pt;color:#777;margin-bottom:1.5mm}}
.cap{{background:#fff;border-left:3px solid #c4932f;padding:2mm 3mm;font-size:9.5pt}}.tags{{color:#1d5fa8;font-weight:600;margin-top:1.5mm;font-size:9.5pt}}.alt{{font-size:8.5pt;color:#555;margin-top:1mm}}
.hls{{display:flex;gap:4mm;margin:3mm 0}}.hl{{text-align:center;font-weight:600}}.hl img{{width:30mm;height:30mm;object-fit:cover;border-radius:50%;border:2px solid #c4932f;display:block;margin-bottom:1mm}}
</style></head><body>
<div class="cover"><img src="file://{LOGO}" style="width:90mm"><h1>Page Launch Kit</h1><p>Your first 6 posts + profile set-up</p><p style="color:#a77a1f">Instagram &amp; Facebook · post today</p></div>

<div class="pb"><h2>1 · What your page will look like</h2><div class="two"><img src="{b64(mock, 700)}"><div>
<div class="box"><b>Why 6 posts?</b> Instagram shows 3 posts per row. Six posts make two full rows, so the page looks complete and trustworthy from day one.</div>
<b>Post them in this order (1 → 6), 20–30 minutes apart, today.</b> Instagram puts the newest post at the top-left, so the brand reel and Zafarani will be on top and the brand intro bottom-right.
<ul><li>Best start: 1st post at <b>8:00 PM</b>, last around <b>10:30 PM</b>.</li><li>Tick <b>Share to Facebook</b> on every post so both pages fill up together.</li>
<li>After posting, <b>pin</b> 3 posts (… → Pin to profile): Brand intro, Shampoo finder and the Brand reel.</li>
<li>Then follow the 28-day plan PDF from <b>Day 7</b> (Day 1–6 posts are already done here).</li></ul></div></div></div>

<div class="pb"><h2>2 · Set up the profile first (10 minutes)</h2>
<div class="two"><img src="{b64(pp, 400)}" style="width:45mm"><div><ol>
<li><b>Profile picture:</b> <i>launch-kit/profile-picture.jpg</i> (same on Instagram and Facebook).</li>
<li><b>Name field</b> (it is searchable): <b>Zuaja PK | Herbal Hair &amp; Skin Care</b></li>
<li><b>Username:</b> keep @zuaja.pk1 on Instagram and /zuaja.pk on Facebook.</li>
<li><b>Bio:</b><br>Desi care, made modern 🌿<br>Shampoos · Hair Oils · Face Wash · Perfumes<br>🚚 Delivery all over Pakistan · WhatsApp 0316 1121130</li>
<li><b>Link:</b> https://zuaja.store · <b>Category:</b> Health/Beauty · <b>Contact buttons:</b> WhatsApp + email zuaja.official@gmail.com</li></ol></div></div>
<h3 style="font-family:Corm;font-size:15pt">Facebook cover photo</h3><img src="{b64(fc, 900)}" style="width:100%;border:1px solid #ddd;border-radius:2mm">
<p style="font-size:9pt;color:#666">File: <i>launch-kit/facebook-cover.jpg</i> (1640×624, safe for both mobile and desktop)</p>
<h3 style="font-family:Corm;font-size:15pt">Instagram Highlights (covers)</h3><div class="hls">{hl_html}</div>
<p style="font-size:9.5pt">Post one story to each highlight first (e.g. the matching product story from the Meta-Ads pack). Then Edit highlight → Edit cover → choose <i>launch-kit/highlight-*.jpg</i>.</p></div>

<div class="pb"><h2>3 · The 6 launch posts (captions ready to copy)</h2>{"".join(steps)}</div>
</body></html>'''
    hp = OUT / "_kit.html"; hp.write_text(page, encoding="utf-8")
    js = OUT / "_pdf.js"
    js.write_text(f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{hp}',{{waitUntil:'networkidle'}});await p.pdf({{path:'{SP}/Zuaja-PK-Page-Launch-Kit.pdf',format:'A4',printBackground:true,margin:{{top:'12mm',bottom:'12mm',left:'12mm',right:'12mm'}}}});await b.close();}})();""")
    subprocess.run(["node", str(js)], check=True); js.unlink(); hp.unlink()
    print("launch kit ok")


if __name__ == "__main__":
    main()
