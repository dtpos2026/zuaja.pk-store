"""28-day Instagram + Facebook posting plan as a designed PDF (A4), with thumbnails,
SEO-first captions, 5 hashtags per post (Instagram's limit), alt text, story plan,
strategy, how-to, reply templates and a KPI tracker.
Run from repo root: python3 -I marketing/social-pack/make_plan_pdf.py
Output: marketing/social-pack/Zuaja-PK-Posting-Plan.pdf
"""
import base64
import datetime as dt
import html
import io
import json
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SP = ROOT / "marketing/social-pack"
AD = ROOT / "marketing/meta-ads-nov"
FONTS = AD / "fonts"
P = {p["key"]: p for p in json.loads((AD / "products.json").read_text())}
START = dt.date(2026, 11, 16)

KW = {  # SEO first line (what people type in Instagram / Google search)
    "rosemary-oil": "Rosemary oil for hair in Pakistan", "7-herbal-oil": "Herbal hair oil with kalonji, amla & badam",
    "amla-reetha-shampoo": "Amla reetha shampoo for oily scalp", "haldi-badam-shampoo": "Haldi badam shampoo for dry, frizzy hair",
    "face-wash": "Haldi face wash for fresh, glowing skin", "zafarani-cream": "Zafrani cream with real saffron",
    "neem-wash": "Neem hand & body wash", "rose-wash": "Rose body wash for soft skin", "lavender-wash": "Lavender body wash for a calm shower",
    "neem-soap": "Neem soap: herbal bathing bar", "rose-soap": "Rose soap with a soft floral scent",
    "white-oud": "White oud perfume in Pakistan", "signature-perfume": "Long-lasting perfume for gifting",
    "unisex-perfume": "Unisex perfume for everyday wear",
}
TAGS = {
    "rosemary-oil": "#ZuajaPK #RosemaryOil #HairOilPakistan #HairCareRoutine #DesiNuskhe",
    "7-herbal-oil": "#ZuajaPK #HerbalHairOil #Kalonji #HairCarePakistan #DesiNuskhe",
    "amla-reetha-shampoo": "#ZuajaPK #AmlaReetha #HerbalShampoo #OilyScalp #HairCarePakistan",
    "haldi-badam-shampoo": "#ZuajaPK #HaldiBadam #DryHair #HerbalShampoo #HairCarePakistan",
    "face-wash": "#ZuajaPK #HaldiFaceWash #SkincarePakistan #GlowingSkin #FaceWash",
    "zafarani-cream": "#ZuajaPK #ZafraniCream #Saffron #GlowingSkin #SkincarePakistan",
    "neem-wash": "#ZuajaPK #NeemWash #BodyWash #SelfCare #MadeInPakistan",
    "rose-wash": "#ZuajaPK #RoseBodyWash #BodyCare #SelfCareSunday #MadeInPakistan",
    "lavender-wash": "#ZuajaPK #LavenderBodyWash #BodyCare #SelfCare #MadeInPakistan",
    "neem-soap": "#ZuajaPK #NeemSoap #HerbalSoap #NaturalSoap #MadeInPakistan",
    "rose-soap": "#ZuajaPK #RoseSoap #HerbalSoap #BathTime #MadeInPakistan",
    "white-oud": "#ZuajaPK #WhiteOud #OudPerfume #PerfumePakistan #LongLastingPerfume",
    "signature-perfume": "#ZuajaPK #SignatureScent #PerfumePakistan #GiftIdeas #LuxuryPerfume",
    "unisex-perfume": "#ZuajaPK #UnisexPerfume #PerfumePakistan #EverydayScent #TravelPerfume",
}
ASK = {
    "rosemary-oil": "How often do you oil your hair? Tell us below 👇", "7-herbal-oil": "Which desi oil did your nani swear by? 👇",
    "amla-reetha-shampoo": "Oily scalp gang, say hi 👋", "haldi-badam-shampoo": "Dry hair or oily scalp? Comment below 👇",
    "face-wash": "Morning face wash: yes or no? 👇", "zafarani-cream": "Comment 'ZAFRAN' and we'll DM you how to use it ✨",
    "neem-wash": "Neem, rose or lavender: what's in your bathroom? 👇", "rose-wash": "Rose lovers, where are you? 🌹",
    "lavender-wash": "Night shower or morning shower? 👇", "neem-soap": "Bar soap or body wash? Tell us 👇",
    "rose-soap": "Tag someone who loves roses 🌹", "white-oud": "Oud or floral? Comment your side 👇",
    "signature-perfume": "Who would you gift this to? Tag them 🎁", "unisex-perfume": "One scent for both of you? Tag your partner 💛",
}
CTA = "📍 Delivery all over Pakistan · Order at zuaja.store or WhatsApp 0316 1121130"


def product_caption(k):
    p = P[k]
    return (f"{KW[k]} ✨\n\n{p['primary']}\n\n_{p['hook_ur']}_\n{CTA}\n💬 {ASK[k]}", TAGS[k],
            f"Zuaja PK {p['name']} {p['size']} studio photo, {KW[k].lower()}")


EXTRA = {
    "brand-intro": ("Meet Zuaja PK: natural desi care for hair, skin & body, made in Pakistan 🇵🇰\n\nShampoos, herbal hair oils, haldi face wash, zafrani cream, body washes, soaps and perfumes, made with ingredients Pakistani homes already trust: haldi, badam, amla, reetha, neem, rosemary and zafran.\n\n_Desi nuskhe, modern andaaz._\n" + CTA + "\n💬 Which product should we introduce first? 👇",
                    "#ZuajaPK #MadeInPakistan #PakistaniBrand #DesiCare #HerbalCare", "Zuaja PK product range: shampoos, hair oils, face wash, cream and perfumes on ivory background"),
    "this-or-that-perfume": ("Perfume in Pakistan: White Oud (1) or Signature (2)? ✨\n\nRich, royal oud vs. elegant crystal-bottle classic. Comment 1 or 2 and we'll pick a winner by Friday!\n\n_Aap ki pasand kaunsi?_\n" + CTA,
                             "#ZuajaPK #PerfumePakistan #ThisOrThat #OudPerfume #SignatureScent", "Two Zuaja PK perfumes side by side, White Oud and Signature, numbered 1 and 2"),
    "this-or-that-shampoo": ("Herbal shampoo for your hair type: team oily (1) or team dry (2)? 💧\n\nAmla Reetha for oily scalps, Haldi + Badam for dry, frizzy hair. Comment 1 or 2!\n\n_Apne baalon ki type batayein._\n" + CTA,
                             "#ZuajaPK #HerbalShampoo #AmlaReetha #HaldiBadam #HairCarePakistan", "Amla Reetha and Haldi Badam shampoos side by side, numbered 1 and 2"),
    "tag-a-friend-rosemary": ("Champi night with rosemary oil 😄 Tag someone who needs a champi tonight!\n\nRosemary, onion, castor, amla and aloe vera in one bottle. Massage, leave overnight, wash. Rs 950.\n\n_Hafte mein aik champi zaroor!_\n" + CTA,
                              "#ZuajaPK #RosemaryOil #Champi #HairOilPakistan #TagAFriend", "Zuaja PK Rosemary Oil bottle on amber background with tag a friend text"),
    "comment-bath-scent": ("Body wash scents: Neem, Rose or Lavender? 💚🌹💜\n\nComment the one in your bathroom, or the one you want next!\n\n" + CTA,
                           "#ZuajaPK #BodyWash #SelfCare #Lavender #MadeInPakistan", "Zuaja PK Lavender hand and body wash on purple background"),
    "comment-zafran": ("Zafrani cream: your nani's glow secret ✨\n\nComment 'ZAFRAN' and we'll DM you exactly how to use Zuaja PK Zafarani Cream for that soft glow. Rs 350.\n\n" + CTA,
                       "#ZuajaPK #ZafraniCream #Saffron #GlowingSkin #SkincarePakistan", "Zuaja PK Zafarani Cream jar with saffron flowers on plum background"),
    "car-shampoo-finder": ("Best herbal shampoo for your hair type in Pakistan: swipe to find yours 👉\n\nOily scalp → Amla Reetha. Dry ends → Haldi + Badam. Stronger-looking roots → add Rosemary Oil.\n\n💾 Save this for wash day and share it with your sister!\n" + CTA,
                           "#ZuajaPK #HairCareTips #HerbalShampoo #HairCarePakistan #HairCareRoutine", "Carousel guide: which Zuaja PK shampoo is right for your hair type"),
    "car-champi-ritual": ("How to oil your hair the right way: the 10-minute champi ritual 🌿\n\nWarm it, massage 5–10 min, leave overnight, wash with the right shampoo. Swipe for the steps 👉\n\n💾 Save it, and tag your champi buddy.\n" + CTA,
                          "#ZuajaPK #HairOiling #Champi #DesiNuskhe #HairCareRoutine", "Carousel: four steps of a hair oil champi ritual with Zuaja PK oils"),
    "car-desi-ingredients": ("Desi ingredients for hair & skin: haldi, badam, amla, reetha, rosemary, kalonji, zafran, neem 🌿\n\nSwipe to see what each one does and where you'll find it in Zuaja PK. Which is your favourite? 👇\n\n" + CTA,
                             "#ZuajaPK #DesiNuskhe #NaturalIngredients #Haldi #HerbalCare", "Carousel: guide to desi ingredients used in Zuaja PK products"),
    "car-scent-finder": ("Find your perfume: rich oud, elegant classic or fresh everyday? ✨\n\nSwipe to find your Zuaja scent 👉 Not sure? Try the White Oud Tester for Rs 250.\n\n" + CTA,
                         "#ZuajaPK #PerfumePakistan #OudPerfume #GiftIdeas #SignatureScent", "Carousel: guide to choosing a Zuaja PK perfume"),
    "lineup-hair": ("Hair care routine, the desi way: shampoo by scalp type, oil once a week 🌿\n\nAmla Reetha · Haldi + Badam · Rosemary Oil · 7 Herbal Oils, from Rs 450.\n\n" + CTA,
                    "#ZuajaPK #HairCareRoutine #HerbalShampoo #HairOilPakistan #HairCarePakistan", "Zuaja PK hair care range: two shampoos and two hair oils"),
    "lineup-fragrance": ("Perfume gift ideas in Pakistan: three Zuaja scents, three moods ✨\n\nSignature, Premium White Oud and Unisex 30 ml, from Rs 1,500. Gift-ready and long-lasting.\n\n" + CTA,
                         "#ZuajaPK #PerfumePakistan #GiftIdeas #OudPerfume #LuxuryPerfume", "Zuaja PK perfume range: Signature, White Oud and Unisex bottles"),
    "lineup-skin-bath": ("Daily skin & body care: haldi face wash, zafrani cream, rose & lavender washes 🌼\n\nFresh skin every day, from Rs 300.\n\n" + CTA,
                         "#ZuajaPK #SkincarePakistan #BodyCare #SelfCare #GlowingSkin", "Zuaja PK skin and bath range: face wash, cream and body washes"),
    "lineup-all": ("Natural hair, skin & body care made in Pakistan 🇵🇰\n\nOne store for your whole routine: shampoos, oils, face wash, cream, washes, soaps and perfumes. Thank you for a lovely first month with Zuaja PK 💛\n\n" + CTA,
                   "#ZuajaPK #MadeInPakistan #PakistaniBrand #HerbalCare #SelfCare", "Full Zuaja PK product line-up on ivory background"),
}
REEL = {
    "brand": ("Desi care, made modern: meet all 14 Zuaja PK products in 15 seconds ✨ Which one are you trying first? 👇", "#ZuajaPK #PakistaniBrand #MadeInPakistan #SkincarePakistan #HairCarePakistan"),
    "hair-ritual": ("Weekly hair care routine with herbal shampoo + hair oil 🌿 Save it for your next wash day!", "#ZuajaPK #HairCareRoutine #HairOiling #HerbalShampoo #HairCarePakistan"),
    "fragrance": ("Which perfume are you: rich oud, elegant classic or fresh everyday? ✨ Comment below!", "#ZuajaPK #PerfumePakistan #OudPerfume #PerfumeTok #GiftIdeas"),
    "glow": ("Glow routine the desi way: haldi face wash AM, zafrani cream PM 🌼 Save this!", "#ZuajaPK #GlowingSkin #SkincareRoutine #SkincarePakistan #HaldiFaceWash"),
    "bath": ("Shower upgrade: neem, rose, lavender or the herbal neem soap? Which one is yours? 👇", "#ZuajaPK #ShowerRoutine #BodyCare #SelfCare #MadeInPakistan"),
}


def item(kind, key):
    if kind == "post":
        cap, tags, alt = product_caption(key)
        return dict(label=f"Product post: {P[key]['name']}", file=f"Social-Pack / posts/{key}_post-4x5.jpg", img=SP / "posts" / f"{key}_post-4x5.jpg", cap=cap, tags=tags, alt=alt)
    if kind == "engage":
        cap, tags, alt = EXTRA[key]
        return dict(label="Engagement post", file=f"Social-Pack / engage/{key}.jpg", img=SP / "engage" / f"{key}.jpg", cap=cap, tags=tags, alt=alt)
    if kind == "car":
        cap, tags, alt = EXTRA["car-" + key]
        n = len(list((SP / "carousels" / key).glob("*.jpg")))
        return dict(label=f"Carousel ({n} slides, upload all in order)", file=f"Social-Pack / carousels/{key}/01–{n:02d}.jpg", img=SP / "carousels" / key / "01.jpg", cap=cap, tags=tags, alt=alt)
    if kind == "lineup":
        cap, tags, alt = EXTRA[key]
        return dict(label="Range post", file=f"Meta-Ads / statics/{key}_feed-4x5_evergreen.jpg", img=AD / "statics" / f"{key}_feed-4x5_evergreen.jpg", cap=cap, tags=tags, alt=alt)
    if kind == "reel":
        cap, tags = REEL[key]
        return dict(label="Reel (Zuaja music inside)", file=f"Social-Pack / reels/zuaja-reel-{key}.mp4", img=SP / "reels" / f"zuaja-reel-{key}.mp4", cap=cap + "\n" + CTA, tags=tags, alt="")
    if kind == "preel":
        p = P[key]
        return dict(label=f"Product reel: {p['name']}", file=f"Meta-Ads / reels/{key}_reel-9x16_evergreen.mp4", img=AD / "reels" / f"{key}_reel-9x16_evergreen.mp4",
                    cap=f"{KW[key]} in 12 seconds ✨ {p['hook']}\n{CTA}", tags=TAGS[key], alt="")


PLAN = [  # (theme of the week, [ (feed, reel or None) x7 ])
    ("Week 1 · Hello, Zuaja PK (awareness)", [
        (("engage", "brand-intro"), ("reel", "brand")), (("post", "rosemary-oil"), None),
        (("car", "shampoo-finder"), ("reel", "hair-ritual")), (("post", "white-oud"), None),
        (("engage", "this-or-that-perfume"), ("reel", "fragrance")), (("post", "zafarani-cream"), None),
        (("car", "champi-ritual"), None)]),
    ("Week 2 · Hair & skin education", [
        (("post", "amla-reetha-shampoo"), ("preel", "rosemary-oil")), (("engage", "tag-a-friend-rosemary"), None),
        (("post", "face-wash"), ("reel", "glow")), (("car", "desi-ingredients"), None),
        (("post", "haldi-badam-shampoo"), ("preel", "haldi-badam-shampoo")), (("engage", "this-or-that-shampoo"), None),
        (("post", "7-herbal-oil"), None)]),
    ("Week 3 · Bath & fragrance", [
        (("post", "neem-wash"), ("reel", "bath")), (("engage", "comment-bath-scent"), None),
        (("post", "rose-soap"), ("preel", "white-oud")), (("car", "scent-finder"), None),
        (("post", "signature-perfume"), ("preel", "zafarani-cream")), (("post", "lavender-wash"), None),
        (("lineup", "lineup-hair"), None)]),
    ("Week 4 · Routines & gifting (sales push)", [
        (("post", "rose-wash"), ("preel", "face-wash")), (("engage", "comment-zafran"), None),
        (("post", "unisex-perfume"), ("preel", "7-herbal-oil")), (("post", "neem-soap"), None),
        (("lineup", "lineup-fragrance"), ("preel", "signature-perfume")), (("lineup", "lineup-skin-bath"), None),
        (("lineup", "lineup-all"), None)]),
]
POLLS = {0: ("poll-hair-type", "Oily / Dry"), 3: ("poll-scent", "Oud / Floral"), 6: ("poll-champi", "Yes / Not yet"), 2: ("poll-face-wash", "Yes / No")}


def thumb(path, w=260):
    path = Path(path)
    if path.suffix == ".mp4":
        tmp = SP / "_frame.jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "4", "-i", str(path), "-frames:v", "1", str(tmp)], check=True)
        im = Image.open(tmp).convert("RGB"); tmp.unlink()
    else:
        im = Image.open(path).convert("RGB")
    im.thumbnail((w, int(w * 1.8)))
    b = io.BytesIO(); im.save(b, "JPEG", quality=78)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def esc(s):
    s = html.escape(s)
    out = []
    for line in s.split("\n"):
        if line.startswith("_") and line.endswith("_") and len(line) > 2:
            line = f"<i>{line[1:-1]}</i>"
        out.append(line)
    return "<br>".join(out)


def card(it, kind_cls):
    cap = it["cap"].replace("_", "") if False else it["cap"]
    alt = f'<div class="alt"><b>Alt text:</b> {html.escape(it["alt"])}</div>' if it["alt"] else ""
    return f'''<div class="item {kind_cls}"><img src="{thumb(it["img"])}"><div class="body">
<div class="lbl">{html.escape(it["label"])}</div><div class="file">{html.escape(it["file"])}</div>
<div class="cap">{esc(cap)}</div><div class="tags">{html.escape(it["tags"])}</div>{alt}</div></div>'''


def main():
    days_html = []
    d = START
    for wi, (theme, days) in enumerate(PLAN):
        days_html.append(f'<h2 class="week">{html.escape(theme)}</h2>')
        for di, (feed, reel) in enumerate(days):
            t_feed = "1:30 PM" if (wi + di) % 2 == 0 else "9:00 PM"
            t_reel = "9:00 PM" if t_feed == "1:30 PM" else "1:30 PM"
            fi = item(*feed)
            blocks = [f'<div class="slot"><span class="time">🕐 {t_feed} · Feed</span>{card(fi, "feed")}</div>']
            if reel:
                ri = item(*reel)
                blocks.append(f'<div class="slot"><span class="time">🎬 {t_reel} · Reel</span>{card(ri, "reel")}</div>')
            if di in POLLS:
                pf, opts = POLLS[di]
                story = f"Poll story: <b>Social-Pack / stories/{pf}.jpg</b>, plus an Instagram <b>Poll sticker</b> ({opts}) in the empty space. Also share today's feed post to your story."
            elif feed[0] == "post":
                story = f"Product story: <b>Meta-Ads / statics/{feed[1]}_story-9x16_evergreen.jpg</b>, plus a <b>Link sticker</b> to zuaja.store/products/{P[feed[1]]['handle']}. Then share today's post to your story."
            else:
                story = "Share today's feed post to your story and add a <b>Question sticker</b>: <i>“Ask us anything about hair & skin care”</i>."
            days_html.append(f'''<section class="day"><div class="dhead"><div class="dnum">Day {wi * 7 + di + 1}</div>
<div class="ddate">{d.strftime("%A, %d %b %Y")}</div></div>{"".join(blocks)}
<div class="story">📱 <b>Stories (2–3 a day):</b> {story}</div></section>''')
            d += dt.timedelta(days=1)

    overview = ["<table class='ov'><tr><th>Day</th><th>Date</th><th>Feed</th><th>Reel</th></tr>"]
    d = START
    for wi, (theme, days) in enumerate(PLAN):
        for di, (feed, reel) in enumerate(days):
            fi = item(*feed); ri = item(*reel)["label"] if reel else "-"
            overview.append(f"<tr><td>{wi * 7 + di + 1}</td><td>{d.strftime('%a %d %b')}</td><td>{html.escape(fi['label'])}</td><td>{html.escape(ri)}</td></tr>")
            d += dt.timedelta(days=1)
    overview.append("</table>")

    page = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Jost;src:url("file://{FONTS}/Jost.ttf")}}
@font-face{{font-family:Corm;src:url("file://{FONTS}/CormorantGaramond.ttf")}}
@page{{size:A4;margin:14mm 12mm}}
*{{box-sizing:border-box}} body{{font-family:Jost,sans-serif;color:#1b1b1b;font-size:10.5pt;line-height:1.42;margin:0}}
h1,h2,h3{{font-family:Corm,serif;font-weight:700;margin:0}}
.cover{{height:265mm;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;
 background:radial-gradient(circle at 50% 40%,#fffaf0,#f1e3c2);border:3px solid #c4932f;page-break-after:always}}
.cover img{{width:90mm}} .cover h1{{font-size:40pt;margin-top:10mm}} .cover p{{font-size:13pt;color:#6b5a3a;margin:3mm 0}}
.gold{{color:#a77a1f}} .sec{{page-break-before:always}} h2{{font-size:22pt;margin:2mm 0 4mm;color:#1b1b1b}}
h2.week{{page-break-before:always;background:#171717;color:#e5c271;padding:5mm 6mm;border-radius:3mm;font-size:20pt}}
h3{{font-size:15pt;margin:5mm 0 2mm;color:#8a6420}} ul{{margin:1mm 0 2mm 5mm;padding-left:3mm}} li{{margin:.8mm 0}}
.box{{background:#fbf6ec;border:1px solid #ead9b3;border-radius:3mm;padding:4mm 5mm;margin:3mm 0}}
.day{{page-break-inside:avoid;border:1px solid #ead9b3;border-radius:3mm;margin:0 0 6mm;padding:4mm;background:#fffdf8}}
.dhead{{display:flex;gap:4mm;align-items:baseline;border-bottom:2px solid #c4932f;padding-bottom:1.5mm;margin-bottom:3mm}}
.dnum{{font-family:Corm;font-size:20pt;font-weight:700}} .ddate{{color:#8a6420;font-weight:600}}
.slot{{margin-bottom:3mm}} .time{{display:inline-block;background:#171717;color:#e5c271;font-weight:700;font-size:9pt;padding:1mm 3mm;border-radius:10mm;margin-bottom:1.5mm}}
.item{{display:flex;gap:4mm}} .item img{{width:34mm;height:auto;align-self:flex-start;border-radius:2mm;border:1px solid #ddd}}
.item.reel img{{width:26mm}} .body{{flex:1}} .lbl{{font-weight:700;font-size:11pt}} .file{{font-size:8.5pt;color:#777;margin-bottom:1.5mm}}
.cap{{background:#fff;border-left:3px solid #c4932f;padding:2mm 3mm;font-size:9.5pt}}
.tags{{color:#1d5fa8;font-weight:600;font-size:9.5pt;margin-top:1.5mm}} .alt{{font-size:8.5pt;color:#555;margin-top:1mm}}
.story{{background:#f4ede0;border-radius:2mm;padding:2mm 3mm;font-size:9.5pt}}
table{{border-collapse:collapse;width:100%;font-size:9.5pt}} th,td{{border:1px solid #e2d3b0;padding:1.5mm 2mm;text-align:left}}
th{{background:#171717;color:#e5c271}} tr:nth-child(even) td{{background:#fbf6ec}}
.kpi td{{height:8mm}}
</style></head><body>
<div class="cover"><img src="file://{ROOT}/brand/zuaja-logo-horizontal-1600.png">
<h1>28-Day Posting Plan</h1><p>Instagram &amp; Facebook · 16 Nov – 13 Dec 2026</p>
<p class="gold">Daily feed post · 3 reels a week · daily stories · SEO captions · 5 hashtags</p>
<p style="margin-top:12mm;font-size:10pt">All files are in <b>Zuaja-Social-Pack.zip</b> and <b>Zuaja-Meta-Ads-Nov.zip</b></p></div>

<div class="sec"><h2>1 · Strategy at a glance</h2>
<div class="box"><b>Goal:</b> grow followers and send people to <b>zuaja.store</b>. Every caption ends with the order line (website and WhatsApp).</div>
<h3>Content mix</h3><ul>
<li><b>Product posts (14):</b> one per product, colour-block design. They sell.</li>
<li><b>Carousels (4):</b> guides people <b>save and share</b>. Saves and shares push posts into Explore.</li>
<li><b>Engagement posts (6):</b> "comment 1 or 2", tag a friend. Comments boost reach.</li>
<li><b>Reels (12):</b> Mon, Wed and Fri. Reels reach non-followers the fastest.</li>
<li><b>Stories (daily):</b> polls, links and questions keep followers warm and drive clicks.</li></ul>
<h3>Best posting times (Pakistan)</h3><ul><li><b>1:30 PM</b> (lunch break) and <b>9:00 PM</b> (prime time). The plan alternates them.</li>
<li>Stay online for <b>30–60 minutes after posting</b> and reply to every comment. The first hour decides reach.</li></ul>
<h3>Instagram SEO (how your posts show up in search)</h3><ul>
<li><b>First line = keywords people search</b>, e.g. "Rosemary oil for hair in Pakistan". Every caption in this plan starts that way.</li>
<li><b>Exactly 5 hashtags</b> (Instagram's current limit): 1 brand tag (#ZuajaPK), 2 product tags and 2 niche or country tags. Put them at the end of the caption.</li>
<li><b>Alt text:</b> while posting go to Advanced settings → Accessibility → Write alt text, and paste the alt text from this plan.</li>
<li><b>Location:</b> add "Pakistan" or your city (Gujranwala) to every post.</li>
<li><b>Profile:</b> Name field <i>“Zuaja PK | Herbal Hair &amp; Skin Care”</i>. Bio: <i>“Desi care, made modern 🌿 Shampoos · Hair Oils · Face Wash · Perfumes · Delivery all over Pakistan”</i> + link zuaja.store.</li>
<li><b>Pin 3 posts</b> on your profile: Brand intro, Shampoo finder carousel, White Oud post.</li>
<li><b>Reels:</b> keep <i>Original audio</i> and rename it <i>“Zuaja PK Signature Sound”</i>. Turn on <i>“Also share to Facebook”</i>.</li></ul>
<div class="box"><b>Honest note:</b> no one can guarantee a post will trend. What helps most: posting <b>every day on time</b>, replying fast, saveable carousels and reels in the first hour. Check Insights every Sunday and post more of what worked.</div>
</div>

<div class="sec"><h2>2 · How to post (2 minutes each)</h2>
<h3>Feed post or carousel</h3><ul><li>Instagram → + → Post → choose the image (for a carousel, select all slides in order) → keep <b>4:5</b> → Next.</li>
<li>Paste the <b>caption</b>, then the <b>5 hashtags</b> on a new line → Add location → Advanced settings → <b>alt text</b> → turn on <b>Share to Facebook</b> → Share.</li></ul>
<h3>Reel</h3><ul><li>+ → Reel → choose the .mp4 (the music is already inside, so do not add other music) → Next → caption + hashtags → set a <b>cover</b> (frame with the product) → Share to Facebook → Share.</li></ul>
<h3>Story</h3><ul><li>+ → Story → choose the story image → add the sticker the plan says (Poll, Link or Question) → Share.</li>
<li>Save the best stories into <b>Highlights</b>: “Hair”, “Skin”, “Perfume”, “Order”.</li></ul>
<h3>Reply templates (copy-paste)</h3>
<div class="box"><b>Price?</b> “Assalam o Alaikum! {html.escape('<product>')} is Rs ___. Order at zuaja.store or WhatsApp 0316 1121130 💛”<br>
<b>Delivery?</b> “We deliver all over Pakistan 🚚 Just order on zuaja.store or WhatsApp us at 0316 1121130.”<br>
<b>Which one for me?</b> “Oily scalp → Amla Reetha, dry hair → Haldi + Badam, for roots add Rosemary Oil 🌿 Need help? DM us!”<br>
<b>Comment ZAFRAN:</b> DM “Apply a small amount on a clean face at night and massage gently ✨ Order: zuaja.store/products/zafarani-cream”.<br>
<b>Compliment:</b> “Thank you so much! 💛 Tag a friend who'd love this too.”</div>
</div>

<div class="sec"><h2>3 · 4-week overview</h2>{"".join(overview)}</div>
{"".join(days_html)}

<div class="sec"><h2>4 · Weekly results tracker</h2>
<p>Fill this in every Sunday from Instagram <b>Insights</b> and Shopify <b>Analytics</b>.</p>
<table class="kpi"><tr><th>Week</th><th>Followers</th><th>Reach</th><th>Best post</th><th>Saves</th><th>Shares</th><th>Link clicks</th><th>Orders</th></tr>
<tr><td>1</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>2</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td>3</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>4</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>
<div class="box" style="margin-top:6mm"><b>After 4 weeks:</b> repost the top 3 posts as reels or stories, boost the best post with a small Meta ad (Rs 500–1,000/day), and start the cycle again with new photos.</div>
</div></body></html>'''
    out_html = SP / "_plan.html"; out_html.write_text(page, encoding="utf-8")
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{out_html}',{{waitUntil:'networkidle'}});await p.pdf({{path:'{SP}/Zuaja-PK-Posting-Plan.pdf',format:'A4',printBackground:true,
displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="font-size:8px;width:100%;text-align:center;color:#999">Zuaja PK · 28-Day Posting Plan · <span class="pageNumber"></span>/<span class="totalPages"></span></div>',
margin:{{top:'14mm',bottom:'16mm',left:'12mm',right:'12mm'}}}});await b.close();}})();"""
    jsf = SP / "_pdf.js"; jsf.write_text(js)
    subprocess.run(["node", str(jsf)], check=True)
    jsf.unlink(); out_html.unlink()
    print("PDF ok")


if __name__ == "__main__":
    main()
