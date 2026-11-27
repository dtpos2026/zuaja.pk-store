"""Polish the owner's own 21 s Haldi + Badam edit (their voiceover kept).

Fixes: the phone's auto English captions were mistranslated ("Hair loss after use",
"Zodrat Pake", "&amp;"), so that band is blurred and replaced with Roman Urdu captions
timed to the voice; adds a hook badge, a soft music bed under the voice, and a 4 s
end card (Rs 450, ORDER NOW, zuaja.store, WhatsApp, COD).
Input: media/raw/haldi-ugc/owner-edit.mov (gitignored).
Outputs: media/haldi-ugc/haldi-badam-owner-vo_9x16.mp4 and _4x5.mp4
Usage: python3 -I tools/fix_owner_haldi.py
"""
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_ugc_reels as mu  # noqa: E402
from make_haldi_ugc import MUSIC, OUT, W, H, FPS, hook_png, run  # noqa: E402
from make_statics import font, wrap  # noqa: E402

SRC = ROOT / "media/raw/haldi-ugc/owner-edit.mov"
LEN, END = 21.0, 4.0
BAND_Y, BAND_H = 1370, 230          # where the phone's captions sit
CAPS = [  # (t0, t1, text, yellow?) timed to the voice phrases
    (0.0, 1.0, "Kya aap jaante hain?", False),
    (1.0, 2.0, "Haldi sirf chehre ke liye nahi...", False),
    (2.0, 3.8, "baalon ki care mein bhi kaam aati hai!", False),
    (3.8, 7.0, "Zuaja PK ka Haldi + Badam Shampoo", True),
    (7.0, 8.2, "Sardiyon mein maine try kiya", False),
    (8.2, 10.4, "baalon mein khushki ka masla tha", False),
    (10.4, 13.0, "Socha kyun na isay try karun?", False),
    (13.0, 15.3, "Is shampoo se baal aur scalp saaf", False),
    (15.3, 17.4, "Istemal ke baad baal soft aur fresh", False),
    (17.4, 18.3, "Kaafi achhe lag rahe hain", False),
    (18.3, 19.6, "Aur sab se achhi baat?", False),
    (19.6, LEN, "Qeemat sirf Rs 450!", True),
]


def cap_png(text, yellow, path):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    f = font("Jost", 66, "ExtraBold"); lines = wrap(d, text, f, W - 140)
    yy = BAND_Y + BAND_H // 2 - 40 * len(lines)
    for ln in lines:
        mu.outlined(d, (W // 2, yy), ln, f, mu.YELLOW if yellow else (255, 255, 255), 8); yy += 80
    c.save(path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        ins = ["-i", str(SRC)]
        chain = [f"[0:v]fps={FPS},scale={W}:{H},split[a][b]",
                 f"[b]crop={W}:{BAND_H}:0:{BAND_Y},boxblur=22:3,eq=brightness=-0.12[band]",
                 f"[a][band]overlay=0:{BAND_Y}[v0]"]
        last, n = "v0", 1
        ovs = [(lambda p: hook_png("Real review · Haldi + Badam", p), 0.0, 3.8)]
        ovs += [((lambda p, t=t, y=y: cap_png(t, y, p)), a, b) for a, b, t, y in CAPS]
        for j, (fn, a, b) in enumerate(ovs):
            p = tmp / f"c{j}.png"; fn(p)
            ins += ["-loop", "1", "-t", f"{LEN}", "-i", str(p)]
            chain.append(f"[{n}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.15:alpha=1[p{n}]")
            chain.append(f"[{last}][p{n}]overlay=0:0:enable='between(t,{a:.2f},{b - 0.01:.2f})'[v{n}]")
            last, n = f"v{n}", n + 1
        chain.append(f"[{last}]format=yuv420p[out]")
        main_v = tmp / "main.mp4"
        run(ins + ["-filter_complex", ";".join(chain), "-map", "[out]", "-t", f"{LEN}", "-an",
                   "-c:v", "libx264", "-crf", "17", "-preset", "medium", str(main_v)])
        run(["-sseof", "-0.1", "-i", str(SRC), "-frames:v", "1", "-vf", f"scale={W}:{H},split[a][b];[b]crop={W}:{BAND_H}:0:{BAND_Y},"
             f"boxblur=40:4[band];[a][band]overlay=0:{BAND_Y}", str(tmp / "last.png")])  # caption-free frame for the end card
        mu.end_card(tmp / "last.png", "Haldi + Badam Shampoo · 100 ml", "Rs 450", tmp / "end.png")
        run(["-loop", "1", "-i", str(tmp / "end.png"), "-vf", "fade=t=in:st=0:d=0.25,format=yuv420p", "-t", f"{END}",
             "-r", str(FPS), "-c:v", "libx264", "-crf", "17", str(tmp / "end.mp4")])
        (tmp / "l.txt").write_text(f"file '{main_v}'\nfile '{tmp / 'end.mp4'}'\n")
        run(["-f", "concat", "-safe", "0", "-i", str(tmp / "l.txt"), "-c", "copy", str(tmp / "v.mp4")])
        tot = LEN + END
        v = OUT / "haldi-badam-owner-vo_9x16.mp4"
        aud = (f"[1:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5,"
               f"aresample=48000,apad=whole_dur={tot}[vo];"
               f"[2:a]aresample=48000,volume='if(lt(t,{LEN}),0.14,0.55)':eval=frame,afade=t=out:st={tot - 1}:d=1,atrim=0:{tot}[m];"
               f"[vo][m]amix=inputs=2:duration=first:normalize=0[a]")
        run(["-i", str(tmp / "v.mp4"), "-i", str(SRC), "-i", str(MUSIC), "-filter_complex", aud,
             "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "19", "-preset", "medium",
             "-c:a", "aac", "-b:a", "192k", "-t", f"{tot}", "-movflags", "+faststart", str(v)])
        run(["-i", str(v), "-vf", "crop=1080:1350:0:285", "-c:v", "libx264", "-crf", "19", "-c:a", "copy",
             "-movflags", "+faststart", str(OUT / "haldi-badam-owner-vo_4x5.mp4")])
    print("ok")


if __name__ == "__main__":
    main()
