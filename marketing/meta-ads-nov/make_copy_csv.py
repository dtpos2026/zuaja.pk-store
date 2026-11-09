"""Writes ads-copy.csv: one row per ad in the launch plan (ad set, ad name, files, copy, URL with UTMs)."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = {p["key"]: p for p in json.loads((HERE / "products.json").read_text())}
UTM = "utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.name}}&utm_content={{ad.name}}"
DESC = "Delivery all over Pakistan · WhatsApp 0316 1121130"
LINEUPS = {
    "lineup-hair": ("Your desi hair ritual", "Shampoos and hair oils made with amla, reetha, haldi, badam, rosemary and kalonji 🌿 Find the right one for your hair: oily scalp → Amla Reetha, dry hair → Haldi + Badam, roots → Rosemary Oil. From Rs 450.", "/collections/hair-care"),
    "lineup-fragrance": ("Scents people remember", "Three Zuaja PK fragrances, three moods ✨ Signature (crystal bottle), Premium White Oud and the travel-friendly Unisex 30 ml. From Rs 1,500. Want to try first? White Oud Tester, Rs 250.", "/collections/perfumes"),
    "lineup-skin-bath": ("Fresh skin, every day", "Haldi face wash, Zafarani cream and rose & lavender body washes: everyday desi care for fresh, soft skin 🌼 From Rs 300.", "/collections/skin-care"),
    "lineup-all": ("Desi care for hair, skin & body", "Zuaja PK: shampoos, herbal hair oils, face wash, cream, body washes and perfumes made with ingredients Pakistani homes trust 🌿 Haldi, badam, amla, reetha, neem, rosemary. From Rs 180.", "/collections/all"),
}
PLAN = [
    ("AS1 Hair Care", ["rosemary-oil:reel", "rosemary-oil:static", "7-herbal-oil:reel", "haldi-badam-shampoo:reel", "amla-reetha-shampoo:static", "lineup-hair:static"]),
    ("AS2 Skin & Bath", ["face-wash:reel", "zafarani-cream:reel", "zafarani-cream:static", "face-wash:static", "lineup-skin-bath:static"]),
    ("AS3 Fragrance", ["white-oud:reel", "white-oud:static", "signature-perfume:reel", "unisex-perfume:static", "lineup-fragrance:static"]),
    ("AS4 Broad Advantage+", ["lineup-all:static", "haldi-badam-shampoo:static", "rosemary-oil:reel", "white-oud:reel"]),
]
rows = []
for adset, ads in PLAN:
    for a in ads:
        key, kind = a.split(":")
        for tag in ("sale", "evergreen"):
            if key in LINEUPS:
                head, prim, path = LINEUPS[key]
            else:
                p = P[key]; head, prim, path = p["headline"], p["primary"], f"/products/{p['handle']}"
            if tag == "sale":
                prim = prim + " 🔥 11.11 Sale: extra 11% off at checkout until 15 Nov."
            if kind == "reel":
                files = f"reels/{key}_reel-9x16_{tag}.mp4  (+ feed: statics/{key}_feed-4x5_{tag}.jpg)"
            else:
                files = f"statics/{key}_feed-4x5_{tag}.jpg  +  statics/{key}_story-9x16_{tag}.jpg"
            rows.append({
                "variant": tag, "ad_set": adset, "ad_name": f"{key}_{kind}_{tag}",
                "files": files, "primary_text": prim, "headline": head, "description": DESC,
                "cta": "Shop now", "url": f"https://zuaja.pk{path}?{UTM}",
            })
with open(HERE / "ads-copy.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
