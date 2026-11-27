"""Haldi + Badam UGC ad re-cut to the owner's own voiceover (no music).

The owner's caption-free 21 s reel supplies the voice; the visuals are re-cut from the
clean raw clips so each shot matches what is being said. show-bottle is a mirrored
selfie clip, so it is flipped to make the label read correctly.
Inputs (gitignored): media/raw/haldi-ugc/{owner-nocap,bottle-hand,show-bottle,hair-touch}.mov
Outputs (media/haldi-ugc/):
  haldi-badam-vo-cut_9x16.mp4 / _4x5.mp4   captions + end card (ad version)
  haldi-badam-vo-cut_9x16_clean.mp4        same cut, no captions
  owner-original-nocap.mp4                 owner's own reel, kept as delivered
Usage: python3 -I tools/make_haldi_vo_cut.py
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_ugc_reels as mu  # noqa: E402
from make_haldi_ugc import GRADE, OUT, RAW, W, H, FPS, hook_png, run  # noqa: E402
from fix_owner_haldi import CAPS  # noqa: E402
from make_statics import font, wrap  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

VO = RAW / "owner-nocap.mov"
LEN, END = 21.0, 3.5
SHOTS = [  # (clip, src_start, global_start) - cut points sit on the voice's pauses
    ("show-bottle", 0.4, 0.0),    # hook: bottle pushed to camera
    ("bottle-hand", 0.5, 3.8),    # "Zuaja PK ka Haldi + Badam Shampoo"
    ("hair-touch", 5.3, 7.9),     # winter, dry scalp - hand in hair
    ("bottle-hand", 6.0, 10.4),   # "socha try karun"
    ("hair-touch", 10.0, 13.0),   # scalp clean - hands through hair
    ("hair-touch", 13.0, 15.3),   # soft and fresh - styled hair
    ("hair-touch", 0.5, 17.4),    # "kaafi achhe lag rahe"
    ("hair-touch", 16.2, 18.5),   # price line - thumbs up + smile
]
TEXT = [(0.25, 2.0, "Haldi sirf chehre ke liye nahi...", False)] + [c for c in CAPS if c[0] >= 2.0]


def cap_png(text, yellow, path, y=1480):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    f = font("Jost", 68, "ExtraBold"); lines = wrap(d, text, f, W - 150); yy = y - 41 * (len(lines) - 1)
    for ln in lines:
        mu.outlined(d, (W // 2, yy), ln, f, mu.YELLOW if yellow else (255, 255, 255), 8); yy += 82
    c.save(path)


def shot(i, clip, ss, dur, tmp):
    k = f"if(lt(t,0.25),1.10-0.10*t/0.25,1+0.035*(t-0.25)/{dur:.2f})"
    flip = "hflip," if clip == "show-bottle" else ""
    vf = (f"{flip}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE},"
          f"scale=w='trunc({W}*{k}/2)*2':h='trunc({H}*{k}/2)*2':eval=frame,crop={W}:{H},format=yuv420p")
    out = tmp / f"s{i}.mp4"
    run(["-ss", f"{ss}", "-t", f"{dur + 0.2:.2f}", "-i", str(RAW / f"{clip}.mov"), "-vf", vf, "-t", f"{dur:.4f}",
         "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(out)])
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        ends = [s[2] for s in SHOTS[1:]] + [LEN]
        files = [shot(i, c, ss, e - g, tmp) for i, ((c, ss, g), e) in enumerate(zip(SHOTS, ends))]
        (tmp / "l.txt").write_text("".join(f"file '{f}'\n" for f in files))
        run(["-f", "concat", "-safe", "0", "-i", str(tmp / "l.txt"), "-c", "copy", str(tmp / "cut.mp4")])
        # end card from a clean smiling frame
        run(["-ss", "18.5", "-i", str(RAW / "hair-touch.mov"), "-frames:v", "1", "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", str(tmp / "last.png")])
        mu.end_card(tmp / "last.png", "Haldi + Badam Shampoo · 100 ml", "Rs 450", tmp / "end.png")
        run(["-loop", "1", "-i", str(tmp / "end.png"), "-vf", "fade=t=in:st=0:d=0.25,format=yuv420p", "-t", f"{END}",
             "-r", str(FPS), "-c:v", "libx264", "-crf", "16", str(tmp / "end.mp4")])
        # captions + hook over the cut
        ins, chain, last, n = ["-i", str(tmp / "cut.mp4")], [], "0:v", 1
        ovs = [(lambda p: hook_png("Kya aap jaante hain?", p), 0.0, 3.8)]
        ovs += [((lambda p, t=t, y=y: cap_png(t, y, p)), a, b) for a, b, t, y in TEXT]
        for j, (fn, a, b) in enumerate(ovs):
            p = tmp / f"c{j}.png"; fn(p)
            ins += ["-loop", "1", "-t", f"{LEN}", "-i", str(p)]
            chain.append(f"[{n}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.15:alpha=1[p{n}]")
            chain.append(f"[{last}][p{n}]overlay=0:0:enable='between(t,{a:.2f},{b - 0.01:.2f})'[v{n}]")
            last, n = f"v{n}", n + 1
        chain.append(f"[{last}]format=yuv420p[out]")
        run(ins + ["-filter_complex", ";".join(chain), "-map", "[out]", "-t", f"{LEN}", "-c:v", "libx264", "-crf", "16",
                   "-preset", "medium", str(tmp / "cap.mp4")])
        voice = (f"[1:a]highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
                 f"loudnorm=I=-14:TP=-1.5,aresample=48000,atrim=0:{LEN},apad=whole_dur={{tot}}[a]")
        for tag, body, tail in (("9x16", "cap.mp4", True), ("9x16_clean", "cut.mp4", False)):
            src = tmp / body
            if tail:
                (tmp / "f.txt").write_text(f"file '{src}'\nfile '{tmp / 'end.mp4'}'\n")
                run(["-f", "concat", "-safe", "0", "-i", str(tmp / "f.txt"), "-c", "copy", str(tmp / "full.mp4")]); src = tmp / "full.mp4"
            tot = LEN + (END if tail else 0)
            run(["-i", str(src), "-i", str(VO), "-filter_complex", voice.format(tot=tot), "-map", "0:v", "-map", "[a]",
                 "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-t", f"{tot}",
                 "-movflags", "+faststart", str(OUT / f"haldi-badam-vo-cut_{tag}.mp4")])
        run(["-i", str(OUT / "haldi-badam-vo-cut_9x16.mp4"), "-vf", "crop=1080:1350:0:285", "-c:v", "libx264", "-crf", "19",
             "-c:a", "copy", "-movflags", "+faststart", str(OUT / "haldi-badam-vo-cut_4x5.mp4")])
        run(["-i", str(VO), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac",
             "-b:a", "192k", "-movflags", "+faststart", str(OUT / "owner-original-nocap.mp4")])
    print("ok")


if __name__ == "__main__":
    main()
