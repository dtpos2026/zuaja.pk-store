"""Enhance compressed phone/WhatsApp clips for ads: 2-pass stabilise (vidstab, light smoothing so it
still feels hand-held), upscale to 1080x1920 (lanczos), denoise (hqdn3d), sharpen, 30 fps.
Colour grading is applied later by the reel builder.
Usage: python3 -I tools/enhance_clips.py   (media/raw/wa/*.mp4 -> media/raw/wa-hd/*.mp4)
"""
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "media/raw/wa", ROOT / "media/raw/wa-hd"


def run(a):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + a, check=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for v in sorted(SRC.glob("*.mp4")):
        with tempfile.TemporaryDirectory() as td:
            trf = Path(td) / "t.trf"
            run(["-i", str(v), "-vf", f"vidstabdetect=shakiness=6:accuracy=15:result={trf}", "-f", "null", "-"])
            vf = (f"vidstabtransform=input={trf}:smoothing=14:optzoom=1:zoomspeed=0.2:interpol=bicubic,"
                  "hqdn3d=2.5:2:4:3,scale=1080:1920:flags=lanczos,unsharp=5:5:0.8:3:3:0.3,fps=30,format=yuv420p")
            run(["-i", str(v), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "15", "-preset", "medium", str(OUT / v.name)])
        print(v.name, flush=True)


if __name__ == "__main__":
    main()
