"""Haldi + Badam UGC testimonial ad (30 s) from the owner's own clips.

Timeline (matches VOICEOVER-SCRIPT in marketing/haldi-ugc/):
 A 0.0-5.6   show-bottle  hook      ends with the push-into-lens whip (natural transition)
 B 5.6-11.6  bottle-hand  product close-up
 C 11.6-17.6 hair-touch   result
 D 17.6-22.1 hair-touch   price
 E 22.1-26.1 hair-touch   smile / CTA lead-in
 F 26.1-30.0 end card     price + ORDER NOW + zuaja.store + COD
Every cut opens with a 0.3 s zoom punch, then a slow push-in; captions pop in (alpha fade).
Outputs (media/haldi-ugc/): *_9x16_voiceover-bed.mp4 (music low, for adding VO),
*_9x16_music.mp4 (full music), *_4x5 versions, captions .srt.
Usage: python3 -I tools/make_haldi_ugc.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_ugc_reels as mu  # noqa: E402
from make_statics import font, wrap  # noqa: E402

W, H, FPS = 1080, 1920, 30
RAW = ROOT / "media/raw/haldi-ugc"
OUT = ROOT / "media/haldi-ugc"
MUSIC = ROOT / "marketing/social-pack/music/commercial/zuaja-commercial-30s.wav"
GRADE = "hqdn3d=2:1.5:3:3,eq=contrast=1.06:saturation=1.12:brightness=0.015,colorbalance=rs=0.025:bs=-0.025,unsharp=5:5:0.6"
SEGS = [  # (clip, start, dur, hook, [(t0, t1, caption)])
    ("show-bottle", 0.0, 5.6, "Kya aap jaante hain?", [(0.3, 2.8, "Haldi sirf chehre ke liye nahi..."), (2.8, 5.5, "baalon ki care mein bhi kamaal hai!")]),
    ("bottle-hand", 1.0, 6.0, None, [(0.0, 3.0, "Zuaja PK Haldi + Badam Shampoo"), (3.0, 6.0, "Sardiyon mein meri scalp par khushki...")]),
    ("hair-touch", 0.3, 6.0, None, [(0.0, 3.0, "Maine khud try kiya"), (3.0, 6.0, "Scalp saaf, baal soft aur fresh")]),
    ("hair-touch", 6.5, 4.5, None, [(0.0, 4.5, "Qeemat? Sirf Rs 450")]),
    ("hair-touch", 14.6, 4.0, None, [(0.0, 4.0, "Aap bhi apni routine mein try karein")]),
]
END = 3.9


def cap_png(text, path, y=1230):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    f = font("Jost", 70, "ExtraBold"); lines = wrap(d, text, f, W - 150); yy = y - 42 * (len(lines) - 1)
    for ln in lines:
        mu.outlined(d, (W // 2, yy), ln, f, (255, 255, 255), 8); yy += 84
    c.save(path)


def hook_png(text, path):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    f = font("Jost", 68, "ExtraBold"); tw = d.textlength(text, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 40, 290, W / 2 + tw / 2 + 40, 400), radius=28, fill=(10, 10, 10, 225))
    d.text((W // 2, 345), text, font=f, fill=mu.YELLOW, anchor="mm")
    c.save(path)


def run(a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + a, check=True)


def segment(i, clip, start, dur, hook, caps, tmp):
    k = f"if(lt(t,0.3),1.12-0.12*t/0.3,1+0.04*(t-0.3)/{dur:.2f})"
    base = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE},"
            f"scale=w='trunc({W}*{k}/2)*2':h='trunc({H}*{k}/2)*2':eval=frame,crop={W}:{H}[v0]")
    ins = ["-ss", str(start), "-t", f"{dur + 0.2:.2f}", "-i", str(RAW / f"{clip}.mov")]
    chain, last, n = [base], "v0", 1
    overlays = [(hook_png, hook, 0.0, dur)] if hook else []
    overlays += [(cap_png, t, a, b) for a, b, t in caps]
    for j, (fn, text, a, b) in enumerate(overlays):
        p = tmp / f"o{i}_{j}.png"; fn(text, p)
        ins += ["-loop", "1", "-t", f"{dur:.2f}", "-i", str(p)]
        chain.append(f"[{n}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.18:alpha=1[p{n}]")
        chain.append(f"[{last}][p{n}]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[v{n}]")
        last, n = f"v{n}", n + 1
    chain.append(f"[{last}]format=yuv420p[out]")
    out = tmp / f"s{i}.mp4"
    run(ins + ["-filter_complex", ";".join(chain), "-map", "[out]", "-t", f"{dur:.3f}", "-r", str(FPS), "-an",
               "-c:v", "libx264", "-crf", "17", "-preset", "medium", str(out)])
    return out


def srt():
    t, rows = 0.0, []
    for _, _, dur, hook, caps in SEGS:
        for a, b, text in caps:
            rows.append((t + a, t + b, text))
        t += dur
    rows.append((t, t + END, "Order now: zuaja.store · WhatsApp 0316 1121130 · Cash on Delivery"))
    ts = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round(s % 1 * 1000)):03d}"  # noqa: E731
    return "".join(f"{i}\n{ts(a)} --> {ts(b)}\n{x}\n\n" for i, (a, b, x) in enumerate(rows, 1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files = [segment(i, *s, tmp) for i, s in enumerate(SEGS)]
        run(["-sseof", "-0.1", "-i", str(files[-1]), "-frames:v", "1", str(tmp / "last.png")])
        mu.end_card(tmp / "last.png", "Haldi + Badam Shampoo · 100 ml", "Rs 450", tmp / "end.png")
        files.append(tmp / "end.mp4")
        run(["-loop", "1", "-i", str(tmp / "end.png"), "-vf", "fade=t=in:st=0:d=0.25,format=yuv420p", "-t", f"{END}", "-r", str(FPS),
             "-c:v", "libx264", "-crf", "17", str(files[-1])])
        (tmp / "l.txt").write_text("".join(f"file '{f}'\n" for f in files))
        run(["-f", "concat", "-safe", "0", "-i", str(tmp / "l.txt"), "-c", "copy", str(tmp / "v.mp4")])
        for tag, vol in (("voiceover-bed", 0.28), ("music", 1.0)):
            v = OUT / f"haldi-badam-ugc_9x16_{tag}.mp4"
            run(["-i", str(tmp / "v.mp4"), "-i", str(MUSIC), "-filter_complex", f"[1:a]volume={vol},afade=t=out:st=29:d=1[a]",
                 "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
                 "-shortest", "-movflags", "+faststart", str(v)])
            run(["-i", str(v), "-vf", "crop=1080:1350:0:285", "-c:v", "libx264", "-crf", "19", "-c:a", "copy", "-movflags", "+faststart",
                 str(OUT / f"haldi-badam-ugc_4x5_{tag}.mp4")])
        run(["-i", str(tmp / "v.mp4"), "-c", "copy", "-movflags", "+faststart", str(OUT / "haldi-badam-ugc_9x16_silent.mp4")])
    (OUT / "haldi-badam-ugc_captions.srt").write_text(srt())
    print("ok")


if __name__ == "__main__":
    main()
