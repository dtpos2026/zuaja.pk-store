"""Build the two client deliverables:
Zuaja-Ad-Package.zip   (ugc-ads, ugc-reels, video-ads, AD-PLAN.md, ads-copy-real.csv, music mp3)
Zuaja-Feed-Package.zip (real-posts, photos _clean, ugc-reels + video-ads 9x16, FEED-CAPTIONS.md)
Usage: python3 -I tools/make_packages.py
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M, PK, MU = ROOT / "media", ROOT / "marketing/real-product-pack", ROOT / "marketing/social-pack/music"


def build(name, items):
    z = ROOT / name
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as f:   # media is already compressed
        for arc, src in items:
            f.write(src, arc)
    print(name, len(items), "files", round(z.stat().st_size / 1e6, 1), "MB")


ad = [(f"ugc-ads/{p.name}", p) for p in sorted((M / "ugc-ads").glob("*.jpg"))]
ad += [(f"ugc-reels/{p.name}", p) for p in sorted((M / "ugc-reels").glob("*.mp4"))]
ad += [(f"video-ads/{p.name}", p) for p in sorted((M / "reels").glob("*.mp4"))]
ad += [(p.name, p) for p in (PK / "CAMPAIGN-PLAN-DEC.md", PK / "AD-PLAN.md", PK / "ads-copy-real.csv")]
ad += [(f"music/{d}/{p.name}", p) for d in ("commercial", "aura") for p in sorted((MU / d).glob("*.mp3"))]
build("Zuaja-Ad-Package.zip", ad)

feed = [(f"real-posts/{p.name}", p) for p in sorted((M / "real-posts").glob("*.jpg"))]
feed += [(f"photos/{p.name}", p) for p in sorted((M / "photos").glob("*_clean-*.jpg"))]
feed += [(f"ugc-reels/{p.name}", p) for p in sorted((M / "ugc-reels").glob("*_9x16.mp4"))]
feed += [(f"video-ads/{p.name}", p) for p in sorted((M / "reels").glob("*_9x16.mp4"))]
feed += [("FEED-CAPTIONS.md", PK / "FEED-CAPTIONS.md")]
build("Zuaja-Feed-Package.zip", feed)
