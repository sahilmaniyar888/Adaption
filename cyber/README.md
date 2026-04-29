# Cyber Fraud Contrastive Dataset V0

This folder is the focused Day 1 workspace for a 500-row Indian cyber-fraud awareness dataset.

Scope for v0:

- Scam types: `digital_arrest`, `upi_collect_request`, `fake_courier_parcel`, `fake_kyc`
- Languages: `English`, `Hindi`, `Marathi`, `Hinglish`
- Variant types: `genuine`, `scam`, `help_seeking`
- Target matrix: 4 scam types x 4 languages x 3 variants, about 10 rows per cell

## Files

- `verified_sources.md`: provenance notes, confirmed sources, and claims not verified.
- `pattern_library.csv`: paraphrased scam patterns extracted from official/reputable sources.
- `genuine_anchors.csv`: genuine/public-guidance anchors for contrastive rows.
- `dataset_v0.csv`: pilot dataset scaffold and seed rows pending review.
- `adaption_smoke_test_log.md`: smoke-test status and blockers.

## Locked 21-Column Schema

1. `row_id`: unique row id, for example `CYB-EN-0001`.
2. `triplet_id`: groups genuine/scam/help-seeking variants, for example `TRIP-DIGARR-001`.
3. `variant_type`: one of `genuine`, `scam`, `help_seeking`.
4. `scam_type`: one of `digital_arrest`, `upi_collect_request`, `fake_courier_parcel`, `fake_kyc`.
5. `language`: one of `English`, `Hindi`, `Marathi`, `Hinglish`.
6. `script`: expected script, for example `Latin`, `Devanagari`, or `Mixed`.
7. `surface_format`: SMS, WhatsApp, phone_call_summary, video_call_summary, app_notification, awareness_notice.
8. `message_text`: the actual dataset text. For v0, never copy victim text verbatim from news.
9. `text_en_gloss`: short English gloss for non-English/code-mixed rows. May be blank if it slows hand-building.
10. `genuine_anchor_id`: anchor id from `genuine_anchors.csv`; for genuine rows this may point to itself or a source anchor.
11. `pattern_id`: pattern id from `pattern_library.csv`; required for scam/help rows.
12. `source_type`: `official`, `bank`, `news_paraphrase`, `synthetic_from_verified_pattern`, `hand_built`, or `needs_review`.
13. `source_url`: source URL for the anchor or pattern.
14. `source_date`: ISO date where known, otherwise `unknown` or a checked date.
15. `pressure_tactic`: short label such as `account_freeze_threat`, `fake_arrest`, `refund_lure`.
16. `ask`: what the text asks the user to do, such as `share_otp`, `approve_collect_request`, `report_1930`.
17. `red_flags`: pipe-separated red flags, for example `urgent|unknown_link|asks_otp`.
18. `mentioned_institutions`: pipe-separated real institution names or public services mentioned in the row, for example `BOI|Bank of India|1930`.
19. `contains_link`: boolean, `true` if `message_text` contains a URL-like string, otherwise `false`.
20. `link_pattern`: one of `none`, `official_reporting`, `shortened`, `lookalike_govt`, `lookalike_bank`, `apk_drop`, `courier_tracking`, or another documented pattern if needed.
21. `validation_status`: `hand_built`, `machine_generated`, `validator_approved`, `validator_rejected`, or `needs_human_review`.

## Row Contract

- Scam rows must be paraphrased and anchored to a pattern id.
- Scam variants should not state the malicious mechanism too explicitly in `message_text`. Real scams often obscure the dangerous step; use generic action verbs such as `approve`, `process complete`, `verification complete`, or `continue`, while documenting the true mechanism in `ask` and `red_flags`.
- Scam SMS/notification variants should match the brevity of real Indian scam messages: typically 2-3 short clauses, not 3 full sentences. Never use stand-alone phrases like `process complete hoga` or `verification complete hogi`; bury the action inside the request.
- Genuine rows must not contain scammer instructions. They should model realistic safe guidance, transaction alerts, or official reporting paths.
- Help-seeking rows should sound like a citizen asking whether a message/call is real.
- Real institution names are allowed because impersonation of real institutions is part of the documented fraud pattern. No institution is implicated as the source of any scam row.
- In scam rows, account numbers, phone numbers, URLs, OTPs, RRNs, AWBs, customer-care numbers, UPI IDs, and operational payment details must be fake, masked, inert, or omitted.
- All scam URLs must use `[.]` notation, for example `bit[.]ly/kyc482` or `kyc-bharat-secure[.]xyz`, so they remain inert in markdown/HTML rendering.
- `contains_link` and `link_pattern` preserve the structural signal of link-based fraud without creating clickable phishing content.
- Do not cite `Sahyog` as a victim-reporting portal in v0.
- Do not cite a Trust Wallet April 27, 2026 advisory unless it is manually verified from an official source.
- Keep deliberate scam-register weirdness only in scam rows, and label it in `red_flags`.

## Institution Disclaimer

Institution names appear because they are essential to the documented fraud patterns. No institution is implicated as the source of any scam; impersonation is the documented modus operandi in official and reputable public sources including I4C/MHA, PIB, RBI, NPCI, and bank safety advisories.
