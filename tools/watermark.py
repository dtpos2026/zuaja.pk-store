"""Add a Zuaja logo watermark to the bottom-right corner of product images.

Usage: python3 -I watermark.py <logo_png> <out_dir> <image> [<image> ...]
"""
import sys
from pathlib import Path

from PIL import Image

logo_path, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
logo = Image.open(logo_path).convert("RGBA")
logo = logo.crop(logo.getbbox())

for src in map(Path, sys.argv[3:]):
    im = Image.open(src).convert("RGBA")
    w = int(im.width * 0.22)
    lg = logo.resize((w, round(logo.height * w / logo.width)), Image.LANCZOS)
    a = lg.getchannel("A").point(lambda v: int(v * 0.55))
    lg.putalpha(a)
    m = int(im.width * 0.035)
    im.alpha_composite(lg, (im.width - lg.width - m, im.height - lg.height - m))
    dst = out / src.name
    if src.suffix.lower() == ".png":
        im.convert("RGB").save(dst, optimize=True)
    else:
        im.convert("RGB").save(dst, quality=88, optimize=True, progressive=True)
    print(dst.name)
