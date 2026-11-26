"""UGC ads from the owner's hand-held product videos (one per product + 2 combos).
Clips come from media/raw/wa-hd (see enhance_clips.py); rendering reuses make_ugc_reels
(hook box, outlined captions, push-in, grade, price end card, commercial music + aura alternate).
Captions sit high (CAP_Y) so the bottle label in the hand stays clear.
Usage: python3 -I tools/make_hand_ads.py [name ...]   -> media/hand-ads/
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_ugc_reels as mu  # noqa: E402

HD = ROOT / "media/raw/wa-hd"
V = lambda n, s, sp=1.0: ("clip", HD / f"{n}.mp4", s, sp)  # noqa: E731
P = mu.P
COD = "Cash on Delivery · Order now"
ADS = {
    "rosemary-oil": ([
        (V("rosemary-hand", 0.3), 4, "Real rosemary INSIDE the bottle", None),
        (V("rosemary-hand", 3.6), 3, None, "See it? Real rosemary sprigs"),
        (V("rosemary-hand", 8.8), 3, None, "Rosemary + onion + castor + amla"),
        (P("rosemary-hand"), 3, None, "Massage into roots, leave overnight"),
        (V("rosemary-hand", 11.2), 3, None, "For stronger-looking, shiny hair"),
        (V("rosemary-hand", 13.6), 4, None, "Only Rs 950 · " + COD),
    ], ("Rosemary Hair Oil · 100 ml", "Rs 950")),
    "amla-reetha": ([
        (V("amla-hand", 0.5), 4, "Oily scalp by evening?", None),
        (V("amla-hand", 4.5), 3, None, "Meet Amla Reetha Shampoo"),
        (V("amla-hand", 8.0), 3, None, "Amla + Reetha + Bhringraj"),
        (V("amla-hand", 11.5), 3, None, "Deep clean. Light, fresh hair."),
        (P("amla-hand"), 3, None, "200 ml · Only Rs 750"),
        (V("amla-hand", 17.5), 4, None, COD),
    ], ("Amla Reetha Shampoo · 200 ml", "Rs 750")),
    "haldi-badam": ([
        (V("haldi-hand", 0.2), 4, "Dry, frizzy hair?", None),
        (V("haldi-hand", 2.8), 3, None, "Try Haldi + Badam Shampoo"),
        (V("haldi-back", 0.6), 3, None, "Haldi cleanses. Badam nourishes."),
        (V("haldi-back", 5.8), 3, None, "Soft, shiny, manageable hair"),
        (P("haldi-hand"), 3, None, "Only Rs 450 (was Rs 880)"),
        (P("hair-trio-b"), 4, None, COD),
    ], ("Haldi + Badam Shampoo · 100 ml", "Rs 450")),
    "neem-wash": ([
        (V("neem-hand", 0.5), 4, "Sticky, tired skin after a long day?", None),
        (V("neem-hand", 4.5), 3, None, "Neem Hand & Body Wash"),
        (V("neem-hand", 8.5), 3, None, "Neem: the desi skin cleanser"),
        (V("neem-hand", 12.5), 3, None, "Fresh, clean feel every wash"),
        (V("neem-hand", 16.0), 3, None, "100 ml · Only Rs 300"),
        (V("neem-hand", 19.5), 4, None, COD),
    ], ("Neem Hand & Body Wash · 100 ml", "Rs 300")),
    "rose-wash": ([
        (V("rose-hand", 0.3), 4, "Want skin that smells like roses?", None),
        (V("rose-hand", 2.9), 3, None, "Rose Hand & Body Wash"),
        (V("rose-hand", 5.0), 3, None, "Gentle cleansing, soft skin"),
        (V("rose-hand", 7.2), 3, None, "Fresh rose fragrance"),
        (V("rose-hand", 9.3), 3, None, "100 ml · Only Rs 300"),
        (V("rose-hand", 11.3), 4, None, COD),
    ], ("Rose Hand & Body Wash · 100 ml", "Rs 300")),
    "lavender-wash": ([
        (V("lavender-hand", 0.3), 4, "Stressful day? Lavender shower.", None),
        (V("lavender-hand", 2.8), 3, None, "Lavender Hand & Body Wash"),
        (V("lavender-hand", 4.9), 3, None, "Calming lavender scent"),
        (V("lavender-hand", 7.5), 3, None, "Gentle on skin, every day"),
        (V("lavender-hand", 9.8), 3, None, "100 ml · Only Rs 300"),
        (V("lavender-hand", 12.0), 4, None, COD),
    ], ("Lavender Hand & Body Wash · 100 ml", "Rs 300")),
    "wash-moods": ([
        (V("washes-trio", 0.3), 3, "Which shower mood are you?", None),
        (V("neem-hand", 4.5), 3, None, "Neem = fresh"),
        (V("lavender-hand", 2.8), 3, None, "Lavender = calm"),
        (V("rose-hand", 2.9), 3, None, "Rose = soft skin"),
        (V("washes-pan", 0.5), 4, None, "All 3 · 100 ml each"),
        (V("washes-trio", 5.0), 4, None, "Rs 300 each · Cash on Delivery"),
    ], ("Neem · Lavender · Rose · 100 ml", "Rs 300 each")),
    "signature-perfume": ([
        (V("signature-box", 0.2), 4, "Gift-ready luxury. Look at this.", None),
        (V("signature-box", 2.7), 3, None, "Crystal bottle. Satin box."),
        (P("signature-box-hand"), 3, None, "Smells expensive. Lasts all day."),
        (V("signature-box", 4.6), 3, None, "Perfect gift for Eid & weddings"),
        (P("signature-box-a"), 3, None, "Signature Perfume · 50 ml"),
        (V("signature-box", 6.2), 4, None, "Rs 2,200 · Cash on Delivery"),
    ], ("Signature Perfume · 50 ml", "Rs 2,200")),
    "white-oud": ([
        (V("whiteoud-open", 0.0), 4, "POV: you open the White Oud box", None),
        (V("whiteoud-open", 2.5), 4, None, "Royal oud, gift-boxed"),
        (V("whiteoud-open", 5.0), 4, None, "Rich. Bold. Long-lasting."),
        (P("whiteoud-box"), 4, None, "Premium White Oud · 50 ml"),
        (V("whiteoud-open", 5.3, 0.8), 4, None, "Rs 1,999 · Cash on Delivery"),
    ], ("Premium White Oud · 50 ml", "Rs 1,999")),
    "hair-routine": ([
        (V("amla-hand", 0.5), 3, "Your full desi hair routine", None),
        (V("amla-hand", 4.5), 3, None, "1. Amla Reetha: oily scalp"),
        (V("haldi-hand", 0.2), 3, None, "2. Haldi + Badam: dry hair"),
        (V("rosemary-hand", 0.3), 3, None, "3. Rosemary Oil: roots"),
        (V("rosemary-hand", 3.6), 3, None, "Real rosemary inside"),
        (P("hair-trio-a"), 5, None, "From Rs 450 · Cash on Delivery"),
    ], ("Amla Reetha · Haldi + Badam · Rosemary", "from Rs 450")),
}

if __name__ == "__main__":
    mu.REELS = ADS
    mu.OUT = ROOT / "media/hand-ads"
    mu.CAP_Y = 400
    want = set(sys.argv[1:])
    for n in ADS:
        if not want or n in want:
            mu.render(n)
