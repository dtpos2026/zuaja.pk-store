# Zuaja PK: Meta Ads launch plan (Nov 2026)

**Goal:** sales on zuaja.pk. The 11.11 Sale (extra 11% off at checkout) runs until **15 Nov, 11:59 pm**. From **16 Nov** switch to the evergreen creatives.
**Budget used below:** **Rs 5,000 / day** (scale tiers at the end).
Short version in Roman Urdu: aik campaign, 4 ad sets, 20 ads aaj raat. Har ad set mein reels aur static dono. 15 Nov tak "sale" wale creatives, 16 Nov se "evergreen" wale.

---

## 0. Before you launch (10 minutes)
1. **Pixel / Facebook channel:** Shopify admin → Sales channels → *Facebook & Instagram* must be connected with the Meta **Pixel + Conversions API** set to *Maximum*. Then check in Events Manager that **Purchase** and **AddToCart** events are arriving.
   *If the pixel is NOT connected yet:* run the same structure with objective **Traffic → Landing page views** for 2–3 days while it collects data, or use **Engagement → Messages (WhatsApp 0316 1121130)**.
2. **Page and Instagram:** facebook.com/zuaja.pk and IG @zuaja.pk1 linked in Business Settings.
3. **Domain:** verify zuaja.pk in Business Settings → Brand safety → Domains.
4. **Payment method** added in the ad account. Ad account currency PKR, time zone Asia/Karachi.

---

## 1. Campaign structure

| | Setting |
|---|---|
| **Campaign** | `ZUAJA | Sales | 11.11 Launch | Nov26` |
| Objective | **Sales**, conversion location **Website**, event **Purchase** |
| Budget | **Ad set budgets (ABO)** for the first 4 days, so each category gets a fair test. After day 4, move winners into a CBO campaign. |
| Attribution | 7-day click, 1-day view |
| Placements | **Advantage+ placements** (Feed, Reels, Stories, Explore). Upload both 4:5 and 9:16 for every ad. |
| Location | Pakistan (all). Optional later: exclude areas you can't deliver to. |
| Language | leave empty (Urdu and English speakers) |

### Ad sets (4) and daily budgets

| Ad set | Budget/day | Audience | Ads |
|---|---|---|---|
| **AS1 Hair Care** | **Rs 1,800** | Age 18–45, all genders (Advantage+ audience ON with these suggestions): *Hair care, Hair oil, Shampoo, Herbal medicine, Ayurveda, Organic food, Beauty* | 6 |
| **AS2 Skin & Bath** | **Rs 1,000** | Women 18–40 (suggestion), interests: *Skin care, Cosmetics, Facial care, Beauty salons, Natural skin care* | 5 |
| **AS3 Fragrance** | **Rs 1,200** | Age 20–45, all genders, interests: *Perfume, Fragrance, Oud, Attar, Luxury goods, Gifts, Weddings* | 5 |
| **AS4 Broad Advantage+** | **Rs 1,000** | Age 18–50, Pakistan, **no interests** (let Meta find buyers) | 4 |
| **Total** | **Rs 5,000** | | **20 ads** |

Ad set naming: `AS1 Hair Care | PK 18-45 | ABO 1800`.

### Ads per ad set (each ad = 4:5 feed + 9:16 story/reel in the same ad)

**AS1 Hair Care (6)**
1. `rosemary-oil_reel`: reel *(main bet)*
2. `rosemary-oil_static`
3. `7-herbal-oil_reel`
4. `haldi-badam-shampoo_reel`: cheapest entry, Rs 450
5. `amla-reetha-shampoo_static`
6. `lineup-hair_static`: all 4 hair products

**AS2 Skin & Bath (5)**
1. `face-wash_reel`
2. `zafarani-cream_reel`: 65% off, strong hook
3. `zafarani-cream_static`
4. `face-wash_static`
5. `lineup-skin-bath_static`

**AS3 Fragrance (5)**
1. `white-oud_reel` *(main bet)*
2. `white-oud_static`
3. `signature-perfume_reel`
4. `unisex-perfume_static`
5. `lineup-fragrance_static`

**AS4 Broad Advantage+ (4)**
1. `lineup-all_static`
2. `haldi-badam-shampoo_static`
3. `rosemary-oil_reel`
4. `white-oud_reel`

**Reserve creatives** (already made, for week 2 or for fatigue): Neem wash, Rose wash, Lavender wash and Neem Soap (feed, story and reel each), plus the second format of every product above.

All text, headlines and links for these 20 ads (sale and evergreen) are in **`ads-copy.csv`**. The URLs already have UTM tags.

---

## 2. Ad copy rules (already applied in the CSV)
- English copy; prices in Rs; no delivery-charge mention. Description line: *Delivery all over Pakistan · WhatsApp 0316 1121130*.
- Sale version ends with: *🔥 11.11 Sale: extra 11% off at checkout until 15 Nov.*
- CTA button: **Shop now**. Links go to the product page (lineups go to the collection).
- Claims are kept soft ("helps", "stronger-looking") so ads pass Meta review. Never write "stops hair fall 100%" or "guaranteed results".
- **Multiple text options:** in each ad, add the product's primary text as option 1. Add the matching lineup text as option 2, so Meta can test both.

---

## 3. Creatives delivered

| Folder | What | Count |
|---|---|---|
| `statics/` | Feed 4:5 (1080×1350) + Story 9:16 (1080×1920), **sale** and **evergreen** for 13 products + 4 lineups | 68 images |
| `reels/` | 12 s reels 9:16 with original background music, sale and evergreen for 13 products | 26 videos |
| `VOICEOVER-SCRIPTS.md` | Urdu (Roman) voice-over for every reel | 13 scripts |

**Reel storyboard (all products):** 0–2.5 s question hook + product rises → 2.5–7.5 s product name + 3 benefits → 7.5–9.5 s *What's inside* → 9.5–12 s price card + 11.11 pill + *Order now · zuaja.pk*.
**Voice-over:** online Urdu text-to-speech was blocked in this session, so the reels ship with music only. Most people watch muted, and captions carry the message. To add the Urdu voice: CapCut → open reel → *Text-to-speech → Urdu*, or record it yourself from `VOICEOVER-SCRIPTS.md`. Keep the music at about 20%.

---

## 4. First 7 days: what to do

| Day | Action |
|---|---|
| **Day 0 (tonight)** | Launch all 4 ad sets. Don't edit anything for **48 hours**, because edits reset learning. |
| **Day 2** | Pause any ad with **> Rs 600 spent and link CTR < 0.8%** or **CPC > Rs 35**. Keep the rest. |
| **Day 3–4** | Look at **cost per purchase** (target **≤ Rs 450**; break-even depends on margin, around 40% of order value). Pause ad sets with **2× target spent and 0 purchases**. |
| **Day 4** | Move the **top 3–5 ads** into a new **CBO campaign** `ZUAJA | Sales | Winners`. Start at Rs 4,000/day and raise it **20% every 48 h** while cost per purchase holds. |
| **Day 4+** | Add **AS5 Retargeting**: website visitors 14 days + IG/FB engagers 30 days, excluding purchasers 30 days. Rs 700/day. Use the **sale** creatives until 15 Nov, then evergreen. |
| **16 Nov** | Sale over: duplicate each live ad, swap in the `_evergreen` files and copy, then pause the `_sale` ads. The 11.11 popup and tags on the store switch off automatically. |
| **Weekly** | Rotate in the reserve creatives when an ad's **frequency is above 3** or its CTR drops 30%. |

### KPIs to watch (Ads Manager → Columns → Performance and clicks)
Link CTR ≥ 1% · CPC ≤ Rs 30 · Landing page view rate ≥ 70% of clicks · Add to cart rate ≥ 5% of LPV · Cost per purchase ≤ Rs 450 · ROAS ≥ 2.

### Budget tiers
| Daily | Split (AS1/AS2/AS3/AS4) |
|---|---|
| Rs 3,000 | 1,200 / 600 / 700 / 500 |
| **Rs 5,000** | **1,800 / 1,000 / 1,200 / 1,000** |
| Rs 10,000 | 3,500 / 2,000 / 2,500 / 2,000 (+ retargeting 1,000 from day 4) |

---

## 5. Organic posting (same creatives)
- **Instagram and Facebook feed:** 1 post a day from `statics/*_feed-4x5_*`. Captions = the primary text + hashtags `#ZuajaPK #DesiCare #HerbalHairOil #RosemaryOil #NaturalHairCare #PakistaniSkincare #Oud #PerfumePakistan`.
- **Reels:** 1 a day from `reels/`, with the Urdu voice-over added in CapCut. Pin the White Oud and Rosemary reels.
- **Stories:** 2–3 a day from `statics/*_story-9x16_*` with a *Link* sticker to the product.
