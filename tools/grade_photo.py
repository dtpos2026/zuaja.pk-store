"""Grade real lifestyle / UGC product photos for ads and social.

Steps: light denoise (ffmpeg hqdn3d) -> subject mask (IS-Net) -> background darker + softer
(depth), subject brighter + crisper (pop) -> warm premium grade + soft vignette.
Exports per photo:
  <name>_clean-4x5.jpg   1080x1350, small cream logo top-left (organic posts, feed ads)
  <name>_clean-9x16.jpg  1080x1920, photo on a blurred extension of itself (stories/reels covers)
  <name>_graded.jpg      full-size graded master
Usage: python3 -I tools/grade_photo.py <out_dir> name=photo.jpg [...]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
M = "/root/.rembg/models/isnet-general-use/isnet-general-use.onnx"
LOGO = ROOT / "brand/zuaja-logo-horizontal-1600.png"
CREAM = (247, 236, 214)
sess = ort.InferenceSession(M, providers=["CPUExecutionProvider"])


def denoise(src):
    tmp = Path(tempfile.mkstemp(suffix=".png")[1])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", "hqdn3d=2.5:2:3:3", str(tmp)], check=True)
    im = Image.open(tmp).convert("RGB"); tmp.unlink(); return im


def mask(im):
    x = np.asarray(im.resize((1024, 1024), Image.BILINEAR), np.float32) / 255 - 0.5
    y = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    y = (y - y.min()) / (y.max() - y.min() + 1e-6)
    m = Image.fromarray((np.clip((y - 0.2) / 0.6, 0, 1) * 255).astype(np.uint8)).resize(im.size, Image.LANCZOS)
    return m.filter(ImageFilter.GaussianBlur(max(2, im.width // 300)))


def grade(im, m):
    a = np.asarray(m).astype(np.float32)[..., None] / 255
    bgd = im.filter(ImageFilter.GaussianBlur(im.width / 260))                  # extra depth blur
    bgd = ImageEnhance.Brightness(bgd).enhance(0.82)
    sub = ImageEnhance.Brightness(im).enhance(1.08)
    sub = sub.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    sub = sub.filter(ImageFilter.UnsharpMask(radius=12, percent=18, threshold=0))  # clarity
    x = np.asarray(sub).astype(np.float32) * a + np.asarray(bgd).astype(np.float32) * (1 - a)
    x = x / 255
    x = x + 0.22 * x * (1 - x) * (2 * x - 1)                                    # gentle S-curve
    x[..., 0] *= 1.03; x[..., 2] *= 0.96                                         # warm
    x = np.clip(x, 0, 1)
    h, w = x.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = 1 - 0.28 * np.clip(np.hypot((xx - w / 2) / (w / 2), (yy - h * 0.55) / (h / 2)) - 0.45, 0, 1) ** 1.6
    x = x * v[..., None]
    out = Image.fromarray((x * 255).astype(np.uint8))
    return ImageEnhance.Color(out).enhance(1.12)


def logo(width):
    lg = Image.open(LOGO).convert("RGBA"); lg = lg.crop(lg.getbbox())
    lg = lg.resize((width, round(lg.height * width / lg.width)), Image.LANCZOS)
    a = np.asarray(lg).astype(np.float32)
    dark = (a[..., :3] @ np.array([.299, .587, .114]) < 140)[..., None]
    a[..., :3] = np.where(dark, np.array(CREAM, np.float32), a[..., :3])
    return Image.fromarray(a.astype(np.uint8))


def crop_to(im, m, ratio):
    """Crop around the subject's centre to a width/height ratio."""
    w, h = im.size
    box = m.point(lambda v: 255 if v > 100 else 0).getbbox() or (0, 0, w, h)
    cx = (box[0] + box[2]) / 2
    if w / h > ratio:
        nw = int(h * ratio); x0 = int(min(max(cx - nw / 2, 0), w - nw)); return im.crop((x0, 0, x0 + nw, h))
    nh = int(w / ratio); cy = (box[1] + box[3]) / 2; y0 = int(min(max(cy - nh / 2, 0), h - nh)); return im.crop((0, y0, w, y0 + nh))


def story(im):
    W, H = 1080, 1920
    bgi = im.resize((W, int(im.height * W / im.width))).resize((W, H)).filter(ImageFilter.GaussianBlur(40))
    bgi = ImageEnhance.Brightness(bgi).enhance(0.55)
    fg = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
    c = bgi.copy(); c.paste(fg, (0, (H - fg.height) // 2))
    return c


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for arg in sys.argv[2:]:
        name, src = arg.split("=", 1)
        im = denoise(src); m = mask(im); g = grade(im, m)
        g.save(out / f"{name}_graded.jpg", quality=92)
        f = crop_to(g, m, 4 / 5).resize((1080, 1350), Image.LANCZOS).convert("RGBA")
        lg = logo(230); f.alpha_composite(lg, (44, 44))
        f.convert("RGB").save(out / f"{name}_clean-4x5.jpg", quality=90, optimize=True, progressive=True)
        s = story(g).convert("RGBA"); lg = logo(300); s.alpha_composite(lg, (1080 // 2 - lg.width // 2, 260))
        s.convert("RGB").save(out / f"{name}_clean-9x16.jpg", quality=90, optimize=True, progressive=True)
        print(name, flush=True)


if __name__ == "__main__":
    main()
