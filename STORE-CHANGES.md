# Zuaja.pk store changes — 5 Nov 2026

## Store analysis
- 14 active products (shampoo, hair oil, face wash, cream, soap, hand & body wash, perfume).
- Inventory is not tracked, so every product can be bought (stock numbers show 0 or negative but this does not block orders).
- Live theme: "Zuaja PK — Tab Logo". Store has about 18 old unpublished theme copies that can be cleaned up.
- Problems found: footer legal links (Shipping, Terms, Privacy, FAQs, Order tracking) all pointed to "#"; no Facebook link anywhere; only a Privacy policy existed.

## Changes made directly in the store (already live)
- New collection **11.11 Sale** (`/collections/11-11-sale`): automatically includes every product with a sale price.
- New pages: **Terms of service** (`/pages/terms-of-service`) and **Refund policy** (`/pages/refund-policy`).

## Official price list applied (live)
Amla Reetha 750 · Haldi + Badam (Almond + Turmeric) 450 · Lavender wash 350 · Neem wash 330 · Zafarani Cream 350 · Face Wash 320 · 7 Herbal Oils 1,200 · Rosemary 950 · Signature (Zuaja) Perfume 50 ml 2,200 · White Oud 1,999 · Unisex Perfume 30 ml (renamed from "Premium Perfume") 1,500 · White Oud Tester 250 · Rose Soap 220 · Neem Soap 180.
- "temporary-price" tag removed from all products. Old compare-at (cut) prices kept.
- New product **Rose Body Wash, 100 ml** (Rs. 300) created as DRAFT: needs a photo before it goes live.

## Changes in the new theme "Zuaja PK — 11.11 Sale & Facebook" (needs Publish)
- Announcement bar: 11.11 SALE IS LIVE — SAVE ON EVERY CATEGORY, delivery all over Pakistan, WhatsApp order number, Shop the 11.11 Sale link.
- Header menu: "11.11 Sale 🔥" and "Skin Care" added. Mobile menu lists the 11.11 Sale first.
- Footer: Facebook icon (facebook.com/zuaja.pk) next to Instagram, TikTok and WhatsApp; legal links fixed; Refund policy and 11.11 Sale links added.
- Mobile menu: Facebook link added.
- Floating "Order on WhatsApp" button on every page except the cart.

## 11.11 Sale — 11% off (5 Nov – 15 Nov 2026)
- Automatic discount "11.11 Sale — 11% off everything" is ACTIVE from 5 Nov until 15 Nov 2026, 11:59 pm PKT. It applies to all products and all customers at checkout, with no code needed. It does not combine with other product or order discounts.
- The theme "Zuaja PK — 11.11 Sale & Facebook" was published by the owner.
- New theme "Zuaja PK — 11.11 Popup, Tags & Logo" (needs Publish) adds `snippets/zuaja-2026-sale-1111.liquid` (copy in `theme/snippets/`):
  - an animated 11.11 popup with a countdown, shown once per visit;
  - a "11.11 SALE · 11% OFF" tag on every product card and product photo;
  - an "11.11 price" box under the price on product pages;
  - a countdown strip above the footer.
  - All of it disappears automatically after 15 Nov.
  - Homepage copy rewritten to be customer friendly:
    - Hero: "11.11 SALE · EXTRA 11% OFF" and "Desi care for hair, skin & body", with the main button going to the sale.
    - Trust strip: delivery all over Pakistan, 11% off till 15 Nov, WhatsApp help 10am–10pm, damaged item support.
    - Shampoo guide: oily scalp → Amla Reetha, dry hair → Haldi + Badam.
    - Products are grouped by category.
    - Brand note gives the WhatsApp number.
    - Unused (disabled) homepage sections were removed from this copy.

## Original logo (from owner)
- Made from the owner's original logo: a horizontal version (icon + ZUAJA.PK / POWERED BY SK) with a transparent background. Files are in `brand/`.
- The theme "Zuaja PK — 11.11 Popup, Tags & Logo" uses it in the header and the 11.11 popup: it replaces `assets/zuaja-pk-logo-complete-4k.webp`.
- New browser-tab icon `assets/zuaja-favicon-48.png`, made from the logo's Z/J mark.

## SEO and creative pack
- SEO title and meta description written for 14 products and 8 collections. They are live and show in Google search results.
- `marketing/11-11-pack/` holds the creative pack:
  - store packshots: product centred on a white background, plus transparent PNGs;
  - 4 social/ad sizes and 1 evergreen post per product;
  - the 11.11 lineup campaign in all sizes;
  - captions with hashtags, and `ads-copy.csv` (headline, primary text, description).
- Not done: uploading product photos to Shopify. Sending files to Shopify's staged upload service was blocked in this session, so the owner must upload `store/white` (Content → Files) or allow the upload.
- Not done: the "Brand Polish" theme copy. Shopify's limit of 20 themes is reached, so old theme copies must be deleted first.

## Product photos and final brand design (live / ready)
- All 14 active products now have this gallery, live: (1) white-background packshot, (2) brand banner, (3) the earlier studio image, (4) the enhanced original photo, (5) the ingredients label or another angle where a photo exists. Images were added from the public GitHub repo URLs.
- The theme "Zuaja PK — FINAL Brand Design (publish this)" (the old "11.11 Sale & Facebook" copy) has been brought in line with the live theme and adds `snippets/zuaja-2026-brand-polish.liquid`:
  - Cinzel serif headings with a gold rule under them;
  - gold hairline borders and lift-on-hover on product cards;
  - a framed product gallery;
  - a trust row under the product buttons;
  - scroll-reveal animation (switched off for reduced motion);
  - a header shadow on scroll and a gold line on top of the footer.
- Theme sources are in `theme/`.

## To do by the owner
- Publish the theme: Shopify admin → Online Store → Themes → "Zuaja PK — 11.11 Sale & Facebook" → Publish.
- Add official policies in Settings → Policies (this connection has no permission to write them). The Terms and Refund pages can be copied there.
- Confirm the refund window (written as 3 days after delivery) and the unopened-only return rule.
- Decide the extra 11.11 discount (percentage, start and end dates) if one is wanted.
