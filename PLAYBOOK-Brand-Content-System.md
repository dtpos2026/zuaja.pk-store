# Brand Content System: Playbook

**How the Zuaja PK package was built, and how to reuse it for any brand**

> Roman Urdu summary: yeh file poore system ka nuskha hai. Background hatana, white store tasveerein, ads, social posts, reels, apni music, 28 din ka posting plan aur page launch kit sab ismein hai. Naye brand ke liye **section 10** ki checklist follow karein: logo, rang, products.json aur music ki dhun badlein, phir commands chalayein.

Everything below is scripted (Python + ffmpeg + FluidSynth + Chromium). Nothing needs Photoshop or a paid tool. All scripts live in this repo:

| Step | Script(s) | Output |
|---|---|---|
| 1. Background removal | `tools/cut_isnet.py`, `tools/fix_cuts.py` | transparent PNG cut-outs (`brand/cutouts/`) |
| 2. Store images | `tools/make_studio_white.py`, `marketing/meta-ads-nov/make_info_cards.py`, `tools/make_category_tiles.py`, `tools/make_category_banners_v4.py` | white first images, info cards, round category tiles, category banners |
| 3. Ad creatives | `marketing/meta-ads-nov/make_statics.py`, `make_reels.py`, `make_copy_csv.py` | feed/story ads, 12 s ad reels, ad copy CSV |
| 4. Social pack | `marketing/social-pack/make_social.py`, `make_social_reels.py` | colour-block posts, carousels, engagement posts, poll stories, 15 s reels |
| 5. Brand music | `marketing/social-pack/make_music_v3.py` (v1 synth / v2 desi kept as alternatives) | jingle 15 s, sonic logo 4 s, bed 30 s (+ `.mid`) |
| 6. Posting plan | `marketing/social-pack/make_plan_pdf.py` | 28-day PDF schedule with captions, hashtags, alt text |
| 7. Launch kit | `marketing/social-pack/make_launch_kit.py` | first 6 posts, profile picture, FB cover, highlight covers, grid preview PDF |

---

## 0. Setup (once per machine)

```bash
pip install pillow numpy scipy onnxruntime mido
```
```bash
apt-get install -y ffmpeg fluidsynth fluid-soundfont-gm poppler-utils
```
- **Background model:** `isnet-general-use.onnx` (from the `rembg` project). The scripts expect it at `/root/.rembg/models/isnet-general-use/isnet-general-use.onnx`; change `M=` in `tools/cut_isnet.py` if yours is elsewhere.
- **Chromium + Playwright** (Node `require('playwright')`) renders the PDFs and text-heavy designs.
- **Fonts** (in `marketing/meta-ads-nov/fonts/`): Cinzel (luxury headings / giant words), Cormorant Garamond (serif headlines), Jost (UI text, prices, labels). Variable fonts; weights are chosen with `set_variation_by_name("Bold")`.
- **Soundfont:** `/usr/share/sounds/sf2/FluidR3_GM.sf2` (free General MIDI instruments, OK for commercial use).

---

## 1. Inputs to collect from the client

| Input | Notes |
|---|---|
| **Logo** (PNG, transparent, high-res) | A horizontal version (mark + wordmark) is used everywhere. The mark alone is auto-cropped for the profile picture. |
| **Product photos or renders** | Best: studio renders on plain white or black. Real photos also work; give the client the **photo guide** (`marketing/photo-guide/`): white paper, window light (no direct sun), **Photo mode 2x (no Portrait mode)**, label facing the camera, send as **WhatsApp Document**. |
| **Price list** | Price and compare-at price per product. Used for badges like "-37%". |
| **Social links, WhatsApp, email** | Used in footers, captions and the end card. |
| **Brand colours** | Default system: ivory `#FBF6EC`, ink `#171717`, gold `#C4932F` / light gold `#E5C271`. |

**Check every label before using a render.** In this project the client's renders had typos ("POWERD", "CLEANYSES") and one render showed a wrong tagline. Always flag these to the client.

---

## 2. Background removal (BG remove)

### 2.1 Basic cut-out: `tools/cut_isnet.py`
```bash
python3 -I tools/cut_isnet.py brand/cutouts  haldi=photos/haldi.jpg  oud=renders/oud.png:black
```
How it works:
1. Resize the image to **1024×1024** and normalise `(x/255 − 0.5)`.
2. Run **IS-Net** (ONNX, CPU) to get a soft mask, then min-max normalise it.
3. Firm up the edges: `alpha = clip((mask − 0.15) / 0.7)`. This removes halos but keeps glass and pump edges soft.
4. Add **`:black`** after the path for renders on black: edge pixels are **un-premultiplied against black** (`rgb / alpha`), so glass bottles do not keep a dark fringe.

### 2.2 Clean-up recipes: `tools/fix_cuts.py`, plus the inline variants used in this project
| Problem | Fix |
|---|---|
| **Blue/grey wall colour** reflected on white bottles (phone photos) | Pull blue-dominant pixels to grey (`w = clip((B − max(R, G)) / 25)`), then white-balance on bright neutral pixels. |
| **White bottle looks grey** | Lift highlights: `x += (250 − x) · 0.55 · smoothstep(lum, 120, 210)`, skipping saturated (label) pixels. |
| **White box on a black background cut too thin** (soap boxes) | "Solidify": `alpha = max(model_alpha, clip((lum − 14) / 22))` near the object, then `binary_fill_holes`. |
| **Glass label interior becomes transparent** (dark perfume labels) | `binary_fill_holes(binary_closing(alpha > 60))`, eroded 2 px, merged into alpha. |
| **Stand or plinth remnants under the product** | Find rows with cyan/white pixels near the bottom 15 % and cut them off. Remove small detached blobs (keep components ≥ 8 % of the largest). |
| **Product looks off-centre** | Faint alpha noise expands the bounding box, so always crop on `alpha > 24`, never on `getbbox()` alone. |

### 2.3 Optional upscale
`tools/esrgan_onnx.py` runs Real-ESRGAN x4 (`realesr-general-x4v3`) without PyTorch, using a weights-only `.pth` reader and onnxruntime. Use it for small or soft photos before cutting.

---

## 3. Store images (white e-commerce look)

**Rule:** the store uses **white backgrounds** (marketplace standard: trustworthy, consistent, fast, liked by Google Shopping and the Meta catalog). **Colour backgrounds are for social only.**

### 3.1 First image: `tools/make_studio_white.py`
```bash
FILL=0.92 VIVID=1 python3 -I tools/make_studio_white.py brand/hero-vivid brand/logo.png  product-handle=brand/cutouts/x.png
```
| Setting | Value |
|---|---|
| Canvas | **1600×1600** white, JPEG q88 (≈110–290 KB). Shopify's CDN serves smaller sizes automatically. |
| Size | product fills `FILL` of the height (0.92 for bottles, **0.80 for wide items** like soap boxes and jars) and `FILL − 0.04` of the width |
| Shadow | soft contact ellipse under the product, blur 22 |
| Watermark | logo at 20 % of the width, 55 % opacity, bottom-right, 3.5 % margin |
| `VIVID=1` (photos) | S-curve `x + 0.35·x(1−x)(2x−1)`, highlight lift 0.18, colour ×1.22, unsharp (1.4/35/3) + clarity (6/22/2) |
| `VIVID=0` (renders) | keeps the client's render colours untouched |

### 3.2 Gallery info card: `make_info_cards.py` (1600×1600)
The studio render sits left on an ivory disc. On the right are the category, name, size, **3 benefits** (gold ticks), **What's inside**, **How to use**, and an ink footer with the website, WhatsApp and delivery line.
**Gallery order on every product:** 1. studio image, 2. info card, 3+. real photos and label shots (only good ones).

### 3.3 Category tiles and banners
- **Round tiles** (`make_category_tiles.py`, 800×800 PNG): ivory disc, gold double ring, 1–3 products, with wide items centred vertically.
- **Wide banners** (`make_category_banners_v4.py`, 2172×724): calm ivory on the left (the theme writes the title there), products on a gold-edged plinth on the right, sized by a relative-height table (`REL`).

### 3.4 Uploading to Shopify (Admin GraphQL)
1. Push the images to a public repo and use `raw.githubusercontent.com/...` URLs as `originalSource`.
2. `productUpdate(media: [...])` adds the image; `productReorderMedia` moves it to position 0 or 1.
3. `fileUpdate(referencesToRemove: [product])` detaches old images (the file stays in Files, so it is reversible).
4. **To replace a theme image without editing the theme**, use `fileUpdate(id, originalSource: newURL)`. It keeps the same filename and URL, so the live theme updates immediately.
5. **Theme edits:** duplicate the live theme, edit the copy (`themeFilesUpsert`), and the owner clicks **Publish**.

---

## 4. Ad creatives (Meta Ads)

### 4.1 Data: `products.json` (one object per product)
```json
{ "key": "rosemary-oil", "handle": "rosemary-hair-scalp-oil-100ml", "name": "Rosemary Hair Oil", "size": "100 ml",
  "cat": "Hair Care", "cutout": "brand/cutouts/rosemary-render.webp", "price": 950, "compare": 1500,
  "hook": "Weak, thin-looking hair?", "hook_ur": "Baal kamzor aur patle lagte hain?",
  "benefits": ["…", "…", "…"], "ingredients": "…", "use": "…",
  "headline": "…", "primary": "…ad primary text…", "vo": "…Roman Urdu voice-over…" }
```
**Claims rule:** use soft wording ("helps", "stronger-looking"), never "100 % stops hair fall". This passes Meta review.

### 4.2 Statics: `make_statics.py`
- **Feed 4:5 (1080×1350):** logo, category kicker, **hook question** headline, product on a glow disc with a gold ring, name, 3 benefit chips, price (old price struck, **-X %** badge), Shop Now button, ink footer.
- **Story 9:16 (1080×1920):** same content inside the **safe zone**. Keep the top ~250 px and bottom ~340 px free (Instagram's UI covers them).
- Every creative has two versions: **`_sale`** (offer pill or ribbon) and **`_evergreen`**. Switch to evergreen the day the offer ends.
- **Line-ups:** 3–5 products of a category, with the middle one 15 % taller.

### 4.3 Ad reels: `make_reels.py` (12 s, 1080×1920, 30 fps, H.264 + AAC)
| Time | Scene |
|---|---|
| 0–2.5 s | hook question pops in; product rises into frame |
| 2.5–7.5 s | name + 3 benefit chips slide in one by one; slow zoom |
| 7.5–9.5 s | "What's inside" ingredients card |
| 9.5–12 s | price card + offer pill + "ORDER NOW · site" |
Frames are drawn with Pillow and piped as raw RGB into ffmpeg. Use `-movflags +faststart`.

### 4.4 Campaign template: `CAMPAIGN-PLAN.md` and `ads-copy.csv`
- **1 campaign**: Sales → Website → Purchase (or Traffic/Messages while the pixel is new).
- **4 ad sets (ABO for 4 days)**: by category (Hair / Skin & Bath / Fragrance) plus **Broad Advantage+**, around 5 ads each, with budget split about 36/20/24/20 %.
- **Rules**: no edits for 48 h. On day 2, pause any ad with more than Rs 600 spent and a link CTR below 0.8 % or a CPC above Rs 35. On days 3–4, pause ad sets that have spent 2× the target cost per purchase with no sale. Move winners to CBO on day 4 and scale +20 % every 48 h. Add retargeting from day 4.
- `make_copy_csv.py` writes one row per ad: primary text, headline, description, CTA and a **UTM** URL (`utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.name}}&utm_content={{ad.name}}`).

---

## 5. Social pack (organic Instagram + Facebook)

### 5.1 Product hero posts: "colour-block editorial" (`make_social.py`)
Each product gets a **LOOK** entry: top colour, bottom colour, light/dark text, **giant word**, headline, and a 3-word trio.
```python
"rosemary-oil": ((214,140,40), (110,56,10), True, "ROSEMARY", "Roots deserve a ritual.", "Nourish · Massage · Overnight"),
```
Layout (1080×1350):
1. Vertical gradient, with a radial lift behind the product.
2. Giant faded word (Cinzel, auto-fitted to 94 % of the width).
3. Logo, recoloured to cream on dark backgrounds.
4. Category and headline.
5. Product with a **reflection** (flipped, 32 % height, alpha 0.28 → 0) and a contact shadow.
6. Name, gold trio, and a price + site pill.
7. Gold inner frame.

Pick the colour from the product itself (oil amber, neem green, lavender purple, oud black, rose pink).

### 5.2 Other formats
| Format | Purpose | Rules |
|---|---|---|
| **Carousels** (5–7 slides, ivory) | saves and shares, which push posts into Explore | slide 1 = question title + products + "SWIPE →"; middle slides = one idea each; last slide = "SAVE THIS · SHOP AT …"; slide counter top-right |
| **Engagement posts** | comments | "This or That" split (1 vs 2), tag-a-friend, "comment KEYWORD for details", brand intro line-up |
| **Poll stories** (9:16) | daily reach to followers | question + product; leave the band at y ≈ 1290–1520 empty for the Poll sticker |

### 5.3 Social reels: `make_social_reels.py` (15 s, cut on the music beat)
- Music at **96 BPM**: 1 beat = 0.625 s, 24 beats = 15 s.
- A reel is a list of scenes `(type, content, beats)`. **The scenes must add up to exactly 20 beats**; beats 20–24 are always the **end card** (logo, "SHOP AT …", WhatsApp), timed to the sonic logo.
- Every cut lands on a beat with a 2-frame warm flash. Product scenes ease in (scale 0.86 → 1, rise 120 px); captions fit on one line.
- Scene types: `intro` (ivory title), `prod` (colour-block product + one-line caption + "name · size | price"), `text` (statement on the brand colour).
- 5 themes used: Brand (all products, 1 beat each), Hair ritual, Fragrance, Glow, Bath.
- To change the music later: `ffmpeg -i reel.mp4 -i new.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest out.mp4`.

---

## 6. Brand music (sonic identity)

### 6.1 Final version (v3): international beauty-brand sound (`make_music_v3.py`)
| Element | Choice |
|---|---|
| Style | modern, elegant R&B-pop (luxury cosmetics ad feel), **96 BPM**, F major |
| Chords | **Fmaj7 – Am7 – Dm7 – B♭maj7** (open piano voicings), Fmaj9 on the logo |
| Instruments (General MIDI) | Grand Piano 0, Celesta 8, Music Box 10, Voice Oohs 53, Warm Pad 89, Slow Strings 49, Synth Bass 38, Tubular Bells 14 (logo bell), Reverse Cymbal 119 (swells), drums on channel 10 (kick, snap and clap on 2 & 4, 16th hats, open hat, rim, shaker) |
| Hook | celesta melody doubled an octave down on soft piano |
| **Sonic logo** | 5 notes on scale degrees **5–6–8–6–8** (here C–D–F–D–F), rhythm ½ ½ 1 ½ 1½ beats, on piano + celesta + crystal bell, with a reverse-cymbal swell into it. **Always starts on beat 20.** |
| Mastering | `highpass 32 Hz → bass −2 dB @100 Hz → treble +5 dB @7 kHz → compressor (−20 dB, 2.2:1) → stereo widen ×1.25 → loudnorm −14 LUFS, TP −1.2 → 0.7 s fade` |
| Files | `jingle-15s` (intro bar, 4-bar groove, logo), `sonic-logo-4s`, `bed-30s` (intro, A section, B section with "ooh" line, breakdown, logo), plus `.mid` files |

**QA without listening:** check integrated loudness with `ffmpeg -af ebur128`, look at a spectrogram (`showspectrumpic`), and compare band energy. Aim for **mids ≥ lows**: phone speakers lose bass and the melody must lead.

### 6.2 Alternatives kept
- **v1** (`make_music.py`): fully synthesised desi sound (Karplus-Strong "sitar", synthesised tabla, tanpura drone). Copyright-free, but sounds like a computer.
- **v2** (`make_music_v2.py`): desi-pop with real samples (sitar, congas). The client found it too "village" for a cosmetics brand.

**Lesson:** for beauty and cosmetics brands, clients expect an **international, luxury** sound (piano, celesta, airy vocals, R&B groove), even for desi ingredients. Keep the desi flavour in the visuals and words, not in the music.

### 6.3 New brand = new motif
Keep the structure. Change the key, the chords (any four-chord loop with maj7/m7 colour), and the 5-note motif (e.g. 1–3–5–3–5 or 5–6–8–6–8). Stay at 96 BPM, or change `BEAT` in the reel script to match.

---

## 7. 28-day posting plan (PDF): `make_plan_pdf.py`

### 7.1 Rhythm
- **1 feed post every day** + **3 reels a week (Mon / Wed / Fri)** + **2–3 stories every day**.
- Times alternate between **1:30 PM** and **9:00 PM** (Pakistan). Stay online for 30–60 minutes after posting and reply to everything.

### 7.2 Weekly themes (customer journey)
1. **Awareness**: brand intro, hero products, first carousel, first reels.
2. **Education**: guides, ingredients, "which one for me".
3. **Category focus**: bath, fragrance, more engagement.
4. **Conversion**: routines, gifting, range posts (with price and Shop Now).

### 7.3 Content mix (28 feed slots)
14 product posts · 4 carousels · 6 engagement posts · 4 range or line-up posts. Reels: the 5 social reels + 7 product ad reels reused as organic reels.
Stories rotate: poll stories (Mon/Wed/Thu/Sun), the product story with a **Link sticker** on product days, and a **Question sticker** on other days.

### 7.4 Caption formula (Instagram SEO)
```
<SEO first line = what people search, e.g. "Rosemary oil for hair in Pakistan"> ✨

<benefit paragraph with ingredients + price>

<one Roman Urdu line>                       ← warmth / local search
📍 Delivery all over Pakistan · Order at site or WhatsApp
💬 <engagement question or CTA: comment / tag / save>

#Brand #Product #Category #Niche #CountryTag  ← exactly 5 (Instagram limit)
```
- **Alt text** (Advanced settings → Accessibility): "Brand + product + size + photo type + the keyword".
- **Location** on every post. Name field = "Brand | Keyword Keyword" (it is searchable). Bio = tagline · categories · delivery · link.
- **Pin 3**: brand intro, best carousel, best reel. Rename the reel audio to "<Brand> Signature Sound".
- Be honest with the client: nobody can guarantee trending. Consistency, saves, shares and comments in the first hour are what move reach.

### 7.5 PDF build
HTML (A4, brand fonts, base64 thumbnails, reel thumbnail = frame at 4 s) rendered with **Chromium `page.pdf()`** with a page-number footer. Sections: cover, strategy, how-to, reply templates, overview table, **one card per day** (feed + reel + story, with file path, time, caption, hashtags and alt text), weekly KPI tracker.

---

## 8. Page launch kit (empty page → professional in one evening): `make_launch_kit.py`
- **6 posts = 2 full grid rows** (Instagram shows 3 per row; a half row looks unfinished). Post them **20–30 minutes apart** with "Share to Facebook" on.
- **Order (oldest → newest):** brand intro → hero product 1 → hero product 2 (contrasting colour) → guide carousel → hero product 3 → brand reel with a custom cover. The grid then alternates ivory and colour blocks.
- **Profile set**:
  - profile picture: the logo mark only, in an ivory circle with a gold ring (1080²)
  - Facebook cover: 1640×624, key content in the centre band
  - 5 highlight covers: 1080×1920, with the product in a gold-ring circle
- **Grid mock-up:** a phone-style preview of how the profile will look, so the client can approve it.
- After launch, continue the 28-day plan from **Day 7**.

---

## 9. QA checklist (do this every time)
- [ ] Contact sheet of every batch (`PIL` grid) checked for clipped products, overlapping text and halos.
- [ ] Labels and spellings checked on every render; problems flagged to the client.
- [ ] Story/reel text inside the safe zones; captions on one line in reels.
- [ ] Image sizes: store 1600² ≈ 100–300 KB; posts 1080×1350; stories and reels 1080×1920.
- [ ] Music: loudness −14 LUFS, true peak ≤ −1 dB, mids ≥ lows, logo on beat 20.
- [ ] After a Shopify upload: re-query the media order (`media(first:2)`) before detaching old images.
- [ ] Sale creatives switched to evergreen when the offer ends; store popups and tags removed too.

---

## 10. New-brand checklist (copy, change, run)
1. **Copy** `tools/`, `marketing/meta-ads-nov/`, `marketing/social-pack/` (scripts + fonts) into the new repo.
2. **Brand constants**:
   - logo path (`LOGO`), colours (`INK`, `GOLD`, `GOLD_L`, `CREAM`, ivory in `bg()`), fonts
   - website / WhatsApp / footer text in `make_statics.py` (`footer`, `cta`), `make_social_reels.py` (`end_card`) and `make_plan_pdf.py` (`CTA`)
3. **Cut-outs**: `cut_isnet.py` (+ fixes) → `brand/cutouts/`.
4. **`products.json`**: one entry per product (section 4.1).
5. **Social looks**: `LOOK` in `make_social.py`; `CAROUSELS`, engagement texts and story questions.
6. **Reels**: `REELS` scene lists (beats add up to 20) in `make_social_reels.py`.
7. **Music**: key, chords, `HOOK`, `MOTIF` in `make_music_v3.py` (or the v2 style for a desi-pop brand).
8. **Plan**: `KW` (SEO first lines), `TAGS` (5 hashtags), `ASK` (questions), `EXTRA`/`REEL` captions, the `PLAN` week table and `START` date in `make_plan_pdf.py`.
9. **Run, in order:**
```bash
python3 -I tools/make_studio_white.py brand/hero-vivid brand/logo.png key=brand/cutouts/key.png
```
```bash
python3 -I marketing/meta-ads-nov/make_info_cards.py
```
```bash
python3 -I marketing/meta-ads-nov/make_statics.py
```
```bash
python3 -I marketing/meta-ads-nov/make_reels.py
```
```bash
python3 -I marketing/meta-ads-nov/make_copy_csv.py
```
```bash
python3 -I marketing/social-pack/make_music_v3.py
```
```bash
python3 -I marketing/social-pack/make_social.py
```
```bash
python3 -I marketing/social-pack/make_social_reels.py
```
```bash
python3 -I marketing/social-pack/make_plan_pdf.py
```
```bash
python3 -I marketing/social-pack/make_launch_kit.py
```
10. **Upload** the store images (section 3.4), then send three zips: Store Images, Meta Ads, Social Pack (+ Launch Kit and plan PDF).

---

## 11. Lessons from the Zuaja project
- Clients judge by **look first**: white for the store, rich colour blocks for social, ivory + gold for ads. Dark "black luxury" ads and the ivory podium style were rejected.
- **Never let AI invent labels.** Use the client's real renders or real photos; AI-generated packshots had the wrong logo.
- Show a **contact sheet before publishing**, then take **one approval** and publish everything together.
- When a product photo is bad (dark soap bar), hide the product (Draft) until a proper render arrives, instead of showing a weak image.
- Remove all traces of a sale on the day it ends: discount, theme popup, tags, menu, ads.
- Shopify connector limits: live theme files and publishing may need the owner's click, so plan for one "Publish" step.
