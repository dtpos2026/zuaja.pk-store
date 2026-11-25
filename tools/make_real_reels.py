"""Reels from the client's real footage + real photos, cut to the Zuaja jingle (96 BPM, 24 beats = 15 s;
beats 20-24 are always the end card on the 'Zu-a-ja P-K' motif).

Each reel = list of segments (source, beats, caption, sub-caption). Sources:
  ("clip", path, start_s, speed)   video clip: graded, 1080x1920, 30 fps (slow-mo via motion interpolation)
  ("photo", name)                  graded photo, Ken Burns push-in
  ("card", text)                   ink title card
Outputs media/reels/<name>_9x16.mp4 and _4x5.mp4 (centre crop; all text sits in y 300-1620).
Usage: python3 -I tools/make_real_reels.py [name ...]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "marketing/meta-ads-nov"))
sys.path.insert(0, str(ROOT / "marketing/social-pack"))
from grade_photo import crop_to, logo, mask  # noqa: E402
from make_social_reels import end_card  # noqa: E402
from make_statics import GOLD_L, INK, font, wrap  # noqa: E402

W, H, FPS = 1080, 1920, 30
BEAT = 60 / 96
RAW = ROOT / "media/raw"
OUT = ROOT / "media/reels"
MUSIC = ROOT / "marketing/social-pack/music/aura/zuaja-aura-15s.wav"  # v4 aura trailer: owner wants an action/trailer feel on videos
GRADE = "eq=contrast=1.06:saturation=1.14:brightness=0.012,colorbalance=rs=0.03:gs=0.0:bs=-0.03,unsharp=5:5:0.55"

REELS = {
    "signature-unboxing": [
        (("clip", RAW / "perfume-unboxing-C080.mov", 0.0, 0.7), 20, "Unboxing luxury", "Zuaja Signature Perfume · 50 ml · Rs 2,200"),
    ],
    "washes": [
        (("clip", RAW / "washes-pan-C075.mov", 0.2, 1.2), 8, "Pick your shower mood", "Neem · Lavender · Rose"),
        (("clip", RAW / "washes-trio-C076.mov", 0.5, 1.0), 12, "Gentle, fresh, everyday", "Hand & Body Wash · 100 ml · from Rs 300"),
    ],
    "real-zuaja": [
        (("card", "Just arrived. The real Zuaja."), 2, None, None),
        (("photo", "rosemary-hand"), 2, "Real rosemary inside", "Rosemary Hair Oil · Rs 950"),
        (("photo", "amla-hand"), 2, "For oily scalps", "Amla Reetha Shampoo · Rs 750"),
        (("photo", "haldi-hand"), 2, "For dry, frizzy hair", "Haldi + Badam Shampoo · Rs 450"),
        (("photo", "hair-trio-a"), 2, "Your desi hair routine", "from Rs 450"),
        (("clip", RAW / "washes-trio-C076.mov", 1.0, 1.0), 4, "Neem · Lavender · Rose", "Hand & Body Wash · from Rs 300"),
        (("clip", RAW / "perfume-unboxing-C080.mov", 1.0, 0.8), 4, "Gift-box luxury", "Signature Perfume · Rs 2,200"),
        (("card", "Desi care, made modern."), 2, None, None),
    ],
}


def caption_png(title, sub, path):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if title:
        shade = Image.new("L", (W, H), 0); d = ImageDraw.Draw(shade)
        for i in range(420):
            d.line((0, 260 + i, W, 260 + i), fill=int(150 * max(0, 1 - abs(i - 170) / 230)))
        layer = Image.new("RGBA", (W, H), (8, 6, 4, 0)); layer.putalpha(shade); c.alpha_composite(layer)
        lg = logo(240); c.alpha_composite(lg, (W // 2 - lg.width // 2, 300))
        tf = font("CormorantGaramond", 92, "Bold"); d = ImageDraw.Draw(c); y = 300 + lg.height + 30
        for ln in wrap(d, title, tf, W - 120):
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((W // 2, y), ln, font=tf, fill=(0, 0, 0, 190), anchor="ma")
            c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7))); ImageDraw.Draw(c).text((W // 2, y), ln, font=tf, fill=(255, 250, 240), anchor="ma"); y += 96
    if sub:
        d = ImageDraw.Draw(c); f = font("Jost", 34, "SemiBold")
        w = d.textlength(sub.upper(), font=f) + 80
        d.rounded_rectangle((W / 2 - w / 2, 1470, W / 2 + w / 2, 1546), radius=38, fill=(16, 14, 12, 215), outline=GOLD_L + (255,), width=2)
        d.text((W // 2, 1508), sub.upper(), font=f, fill=GOLD_L, anchor="mm")
    c.save(path)


def card_png(text, path):
    c = Image.new("RGB", (W, H), INK).convert("RGBA")
    lg = logo(380); c.alpha_composite(lg, (W // 2 - lg.width // 2, 640))
    d = ImageDraw.Draw(c); tf = font("CormorantGaramond", 100, "Bold"); y = 640 + lg.height + 70
    for ln in wrap(d, text, tf, W - 140):
        d.text((W // 2, y), ln, font=tf, fill=(255, 250, 240), anchor="ma"); y += 104
    d.line((W / 2 - 120, y + 30, W / 2 + 120, y + 30), fill=GOLD_L, width=4)
    c.convert("RGB").save(path)


def run(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args, check=True)


def segment(src, beats, cap, sub, tmp, i):
    dur = beats * BEAT; out = tmp / f"seg{i:02d}.mp4"; cap_png = tmp / f"cap{i:02d}.png"
    caption_png(cap, sub, cap_png)
    fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    ov = f"[0:v]{{base}}[b];[b][1:v]overlay=0:0:enable='gte(t,0.12)',format=yuv420p"
    if src[0] == "clip":
        _, path, start, speed = src
        need = dur * speed + 0.3
        base = f"setpts=PTS/{speed},{fit},{GRADE}," + (f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1" if speed < 1 else f"fps={FPS}")
        run(["-ss", str(start), "-t", f"{need:.3f}", "-i", str(path), "-loop", "1", "-i", str(cap_png),
             "-filter_complex", ov.format(base=base), "-t", f"{dur:.3f}", "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)])
    elif src[0] == "photo":
        g = Image.open(ROOT / f"media/photos/{src[1]}_graded.jpg").convert("RGB")
        crop_to(g, mask(g), W / H).resize((W * 2, H * 2), Image.LANCZOS).save(tmp / f"ph{i:02d}.jpg", quality=94)
        n = int(round(dur * FPS))
        base = f"zoompan=z='1+0.07*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS}"
        run(["-i", str(tmp / f"ph{i:02d}.jpg"), "-loop", "1", "-i", str(cap_png), "-filter_complex", ov.format(base=base),
             "-t", f"{dur:.3f}", "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(out)])
    else:
        card_png(src[1], tmp / f"card{i:02d}.png")
        run(["-loop", "1", "-i", str(tmp / f"card{i:02d}.png"), "-vf", f"fade=t=in:st=0:d=0.25,format=yuv420p", "-t", f"{dur:.3f}", "-r", str(FPS),
             "-c:v", "libx264", "-crf", "18", str(out)])
    return out


def render(name, segs):
    assert sum(s[1] for s in segs) == 20, name
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = [segment(src, b, cap, sub, tmp, i) for i, (src, b, cap, sub) in enumerate(segs)]
        end_card().convert("RGB").save(tmp / "end.png")
        files.append(tmp / "end.mp4")
        run(["-loop", "1", "-i", str(tmp / "end.png"), "-vf", "fade=t=in:st=0:d=0.3,format=yuv420p", "-t", f"{4 * BEAT:.3f}", "-r", str(FPS), "-c:v", "libx264", "-crf", "18", str(files[-1])])
        lst = tmp / "list.txt"; lst.write_text("".join(f"file '{f}'\n" for f in files))
        v916 = OUT / f"{name}_9x16.mp4"
        run(["-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(MUSIC), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20",
             "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(v916)])
        run(["-i", str(v916), "-vf", "crop=1080:1350:0:285", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "copy",
             "-movflags", "+faststart", str(OUT / f"{name}_4x5.mp4")])
    print(name, "ok", flush=True)


if __name__ == "__main__":
    want = set(sys.argv[1:])
    for n, s in REELS.items():
        if not want or n in want:
            render(n, s)
