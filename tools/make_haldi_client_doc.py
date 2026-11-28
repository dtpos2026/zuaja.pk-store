"""Client caption sheet (DOCX) for the Haldi + Badam UGC videos + a zip with videos.
Usage: python3 -I tools/make_haldi_client_doc.py
"""
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "marketing/haldi-ugc"
VID = ROOT / "media/haldi-ugc"
LINK = "https://zuaja.store"
WA = "0316 1121130"
TAGS = "#ZuajaPK #HaldiBadam #HaldiShampoo #HairCare #DesiHairCare #HairCarePakistan #DryScalp #WinterHairCare #RealReview #CashOnDelivery"

CAPS = [
    ("Caption 1: Real review (Roman Urdu)", False,
     f"Haldi sirf chehre ke liye nahi, baalon ke liye bhi! 🌿\n"
     f"Maine khud Zuaja PK ka Haldi + Badam Shampoo try kiya: scalp saaf, baal soft aur fresh. ✨\n\n"
     f"💰 Sirf Rs 450 (100 ml)\n✅ Cash on Delivery\n🚚 Poore Pakistan mein delivery\n\n"
     f"🛒 Order karein: {LINK}\n📲 WhatsApp: {WA}\n\n{TAGS}"),
    ("Caption 2: Sardiyon ki khushki (Roman Urdu)", False,
     f"Sardiyon mein scalp par khushki? ❄️\n"
     f"Zuaja PK Haldi + Badam Shampoo: haldi aur badam ki desi care, baal saaf, soft aur fresh. 🌿\n\n"
     f"💰 Qeemat sirf Rs 450\n✅ Cash on Delivery · 🚚 All Pakistan delivery\n\n"
     f"🛒 {LINK}\n📲 WhatsApp: {WA}\n\n{TAGS}"),
    ("Caption 3: Short (Reels / Stories / TikTok)", False,
     f"Haldi + Badam Shampoo 🌿 baal soft, scalp fresh. Sirf Rs 450, Cash on Delivery! 🛒 {LINK}\n\n"
     "#ZuajaPK #HaldiBadam #HairCare #DesiHairCare #Rs450"),
    ("کیپشن 4: اردو", True,
     f"ہلدی صرف چہرے کے لیے نہیں، بالوں کے لیے بھی! 🌿\n"
     f"میں نے خود زواجا پی کے کا ہلدی + بادام شیمپو استعمال کیا: اسکیلپ صاف، بال سوفٹ اور فریش۔ ✨\n\n"
     f"💰 صرف 450 روپے (100 ml)\n✅ کیش آن ڈیلیوری\n🚚 پورے پاکستان میں ڈیلیوری\n\n"
     f"🛒 آرڈر کریں: {LINK}\n📲 واٹس ایپ: {WA}\n\n{TAGS}"),
    ("Caption 5: English", False,
     f"Turmeric isn't just for your face, your hair loves it too! 🌿\n"
     f"I tried Zuaja PK's Haldi + Badam (Turmeric & Almond) Shampoo: clean scalp, soft and fresh hair. ✨\n\n"
     f"💰 Only Rs 450 (100 ml)\n✅ Cash on Delivery\n🚚 Delivery all over Pakistan\n\n"
     f"🛒 Order now: {LINK}\n📲 WhatsApp: {WA}\n\n{TAGS}"),
]


def rtl(p):
    pPr = p._p.get_or_add_pPr()
    b = pPr.makeelement(qn("w:bidi"), {})
    pPr.append(b)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in p.runs:
        r.font.rtl = True
        r.font.name = "Jameel Noori Nastaleeq"
        r._element.rPr.rFonts.set(qn("w:cs"), "Jameel Noori Nastaleeq")
        r.font.size = Pt(14)


def main():
    d = Document()
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    h = d.add_heading("Zuaja PK · Haldi + Badam Shampoo: Video Captions", 0)
    d.add_paragraph(f"Website: {LINK}   ·   WhatsApp: {WA}   ·   Price: Rs 450 (100 ml)   ·   Cash on Delivery")
    d.add_heading("Videos (attached)", 1)
    for name, use in [("haldi-badam-vo-cut_9x16.mp4", "Reels / Stories / TikTok / Status. Captions + end card included"),
                      ("haldi-badam-vo-cut_4x5.mp4", "Facebook / Instagram feed post"),
                      ("haldi-badam-vo-cut_9x16_clean.mp4", "Same video without captions (add your own text)"),
                      ("owner-original-nocap.mp4", "Original vlog-style reel, as recorded")]:
        d.add_paragraph(f"{name}: {use}", style="List Bullet")
    d.add_heading("Captions (copy and paste; any one per post)", 1)
    for title, is_rtl, body in CAPS:
        d.add_heading(title, 2)
        for line in body.split("\n"):
            p = d.add_paragraph(line)
            if is_rtl and line.strip():
                rtl(p)
    d.add_heading("Posting tips", 1)
    for t in ["Pin the video on the profile; reply to every comment with the WhatsApp number.",
              "Best time to post: 8 PM to 11 PM.",
              "In TikTok / Reels, keep the first line of the caption short; the hook is in the video.",
              f"Always keep the link {LINK} in the bio as well."]:
        d.add_paragraph(t, style="List Bullet")
    doc = OUT / "Zuaja-Haldi-Captions.docx"
    d.save(doc)
    z = ROOT / "Zuaja-Haldi-Client-Pack.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:
        zf.write(doc, doc.name)
        for v in ["haldi-badam-vo-cut_9x16.mp4", "haldi-badam-vo-cut_4x5.mp4", "haldi-badam-vo-cut_9x16_clean.mp4", "owner-original-nocap.mp4"]:
            zf.write(VID / v, v)
    print(doc, z, z.stat().st_size // 1_000_000, "MB")


if __name__ == "__main__":
    main()
