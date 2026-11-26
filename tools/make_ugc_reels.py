"""UGC-style sales reels (TikTok / Reels ad look) from the client's real footage and photos.

Style: hook in the first second (white text on a dark box, top), big bold captions with a black
outline in the lower-middle, fast beat cuts, slight push-in on every shot, real footage first,
minimal branding, CTA end card (blurred last shot + price + ORDER NOW). 15 s on the 96 BPM grid:
content = 20 beats, end card = beats 20-24. Music: commercial track (aura alternate also exported).
Usage: python3 -I tools/make_ugc_reels.py [name ...]   -> media/ugc-reels/
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "marketing/meta-ads-nov"))
from grade_photo import crop_to, logo, mask  # noqa: E402
from make_statics import INK, font, wrap  # noqa: E402

W, H, FPS = 1080, 1920, 30
BEAT = 60 / 96
RAW = ROOT / "media/raw"
OUT = ROOT / "media/ugc-reels"
MUSIC = ROOT / "marketing/social-pack/music/commercial/zuaja-commercial-15s.wav"
MUSIC_ALT = ROOT / "marketing/social-pack/music/aura/zuaja-aura-15s.wav"
GRADE = "eq=contrast=1.06:saturation=1.14:brightness=0.012,colorbalance=rs=0.03:bs=-0.03,unsharp=5:5:0.55"
YELLOW = (255, 214, 64)

C = lambda f, s, sp=1.0: ("clip", RAW / f, s, sp)  # noqa: E731
P = lambda n: ("photo", n)  # noqa: E731
REELS = {  # name: (segments [(src, beats, hook, caption)], end-card price line)
    "pov-parcel": ([
        (C("perfume-unboxing-C080.mov", 0.0, 0.8), 3, "POV: your Zuaja parcel just arrived", None),
        (P("signature-box-hand"), 2, None, "Look at this packaging"),
        (C("C078.mov", 4.2, 0.9), 3, None, "Satin gift box. Crystal bottle."),
        (P("signature-box-a"), 2, None, "Smells expensive. Lasts all day."),
        (C("perfume-unboxing-C080.mov", 4.0, 0.8), 4, None, "Perfect gift for Eid, weddings, birthdays"),
        (P("signature-box-wide"), 2, None, "Only Rs 2,200"),
        (P("signature-opening"), 4, None, "Order now at zuaja.pk"),
    ], ("Signature Perfume · 50 ml", "Rs 2,200")),
    "oily-dry-scalp": ([
        (P("amla-hand"), 3, "Stop scrolling if you have an oily scalp", None),
        (P("hair-trio-a"), 2, None, "Amla Reetha = deep clean"),
        (P("haldi-hand"), 3, None, "Dry, frizzy hair? Haldi + Badam"),
        (P("rosemary-hand"), 3, None, "Weak-looking roots? Rosemary oil"),
        (P("rosemary-hand"), 2, None, "You can SEE the real rosemary inside"),
        (P("hair-trio-b"), 3, None, "Full routine from Rs 450"),
        (P("hair-trio-a"), 4, None, "Order now at zuaja.pk"),
    ], ("Amla Reetha · Haldi + Badam · Rosemary", "from Rs 450")),
    "shower-mood": ([
        (C("washes-pan-C075.mov", 0.2), 3, "Which one are you?", None),
        (C("washes-pan-C075.mov", 2.2), 2, None, "Neem = fresh"),
        (C("washes-pan-C075.mov", 3.4), 2, None, "Lavender = calm"),
        (C("washes-pan-C075.mov", 4.6), 2, None, "Rose = soft skin"),
        (C("washes-trio-C076.mov", 0.5), 5, None, "Gentle cleansing, every day"),
        (P("washes-trio-2"), 2, None, "Only Rs 300 each"),
        (P("washes-trio"), 4, None, "Order now at zuaja.pk"),
    ], ("Neem · Lavender · Rose · 100 ml", "from Rs 300")),
    "real-not-ads": ([
        (P("rosemary-hand"), 2, "These are REAL photos, not ads", None),
        (P("amla-hand"), 2, None, "No studio. Real bottles."),
        (P("haldi-hand"), 2, None, "Real desi ingredients"),
        (C("washes-trio-C076.mov", 1.0), 3, None, "Real body washes"),
        (P("signature-box-hand"), 2, None, "Real gift box"),
        (C("perfume-unboxing-C080.mov", 2.0, 0.8), 3, None, "Real luxury"),
        (P("hair-trio-a"), 2, None, "Made in Pakistan"),
        (P("washes-trio-2"), 4, None, "Order at zuaja.pk"),
    ], ("Hair · Skin · Body · Perfume", "from Rs 300")),
}


def outlined(d, xy, text, f, fill=(255, 255, 255), stroke=8):
    d.text(xy, text, font=f, fill=fill, anchor="ma", stroke_width=stroke, stroke_fill=(0, 0, 0))


def overlay_png(hook, cap, path):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    if hook:
        f = font("Jost", 66, "ExtraBold"); lines = wrap(d, hook, f, W - 160)
        bh = 40 + 80 * len(lines); y0 = 300
        d.rounded_rectangle((60, y0, W - 60, y0 + bh), radius=26, fill=(10, 10, 10, 225))
        for i, ln in enumerate(lines):
            d.text((W // 2, y0 + 22 + i * 80), ln, font=f, fill=YELLOW if i == 0 else (255, 255, 255), anchor="ma")
    if cap:
        f = font("Jost", 74, "ExtraBold"); lines = wrap(d, cap, f, W - 140); y = 1170 - 44 * (len(lines) - 1)
        for ln in lines:
            outlined(d, (W // 2, y), ln, f); y += 88
    c.save(path)


def run(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args, check=True)


def segment(src, beats, hook, cap, tmp, i):
    dur = beats * BEAT; out = tmp / f"s{i:02d}.mp4"; ov = tmp / f"o{i:02d}.png"
    overlay_png(hook, cap, ov)
    k = f"(1+0.05*t/{dur:.3f})"  # slow push-in over the shot
    push = f"scale=w='trunc({W}*{k}/2)*2':h='trunc({H}*{k}/2)*2':eval=frame,crop={W}:{H}"
    fc = "[0:v]{base}[b];[b][1:v]overlay=0:0,format=yuv420p"
    if src[0] == "clip":
        _, path, start, sp = src
        base = (f"setpts=PTS/{sp},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{GRADE},"
                + (f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1," if sp < 1 else f"fps={FPS},") + push)
        run(["-ss", str(start), "-t", f"{dur * sp + 0.3:.3f}", "-i", str(path), "-loop", "1", "-i", str(ov),
             "-filter_complex", fc.format(base=base), "-t", f"{dur:.3f}", "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)])
    else:
        g = Image.open(ROOT / f"media/photos/{src[1]}_graded.jpg").convert("RGB")
        crop_to(g, mask(g), W / H).resize((W, H), Image.LANCZOS).save(tmp / f"p{i:02d}.jpg", quality=94)
        run(["-loop", "1", "-framerate", str(FPS), "-i", str(tmp / f"p{i:02d}.jpg"), "-loop", "1", "-i", str(ov),
             "-filter_complex", fc.format(base=push), "-t", f"{dur:.3f}", "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)])
    return out


def end_card(last_png, line, price, path):
    bgi = Image.open(last_png).convert("RGB").filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.45)).convert("RGBA")
    d = ImageDraw.Draw(bgi)
    lg = logo(360); bgi.alpha_composite(lg, (W // 2 - lg.width // 2, 520))
    d.text((W // 2, 760), line.upper(), font=font("Jost", 34, "SemiBold"), fill=(255, 255, 255), anchor="ma")
    outlined(d, (W // 2, 830), price, font("Jost", 120, "ExtraBold"), YELLOW, 10)
    d.rounded_rectangle((W / 2 - 340, 1030, W / 2 + 340, 1150), radius=60, fill=(255, 255, 255))
    d.text((W // 2, 1090), "ORDER NOW", font=font("Jost", 60, "ExtraBold"), fill=INK, anchor="mm")
    d.text((W // 2, 1200), "zuaja.pk  ·  WhatsApp 0316 1121130", font=font("Jost", 34, "Medium"), fill=(255, 255, 255), anchor="ma")
    d.text((W // 2, 1256), "Delivery all over Pakistan", font=font("Jost", 30, "Medium"), fill=(220, 220, 220), anchor="ma")
    bgi.convert("RGB").save(path)


def render(name):
    segs, (line, price) = REELS[name]
    assert sum(s[1] for s in segs) == 20, name
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = [segment(src, b, hk, cp, tmp, i) for i, (src, b, hk, cp) in enumerate(segs)]
        run(["-sseof", "-0.1", "-i", str(files[-1]), "-frames:v", "1", str(tmp / "last.png")])
        end_card(tmp / "last.png", line, price, tmp / "end.png")
        files.append(tmp / "end.mp4")
        run(["-loop", "1", "-i", str(tmp / "end.png"), "-vf", "fade=t=in:st=0:d=0.2,format=yuv420p", "-t", f"{4 * BEAT:.3f}", "-r", str(FPS),
             "-c:v", "libx264", "-crf", "18", str(files[-1])])
        (tmp / "l.txt").write_text("".join(f"file '{f}'\n" for f in files))
        v = OUT / f"{name}_9x16.mp4"
        run(["-f", "concat", "-safe", "0", "-i", str(tmp / "l.txt"), "-i", str(MUSIC), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20",
             "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(v)])
        run(["-i", str(v), "-vf", "crop=1080:1350:0:285", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", str(OUT / f"{name}_4x5.mp4")])
        run(["-i", str(v), "-i", str(MUSIC_ALT), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
             "-movflags", "+faststart", str(OUT / f"{name}_9x16_aura.mp4")])
    print(name, "ok", flush=True)


if __name__ == "__main__":
    want = set(sys.argv[1:])
    for n in REELS:
        if not want or n in want:
            render(n)
