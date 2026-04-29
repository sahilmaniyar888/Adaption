# Adaption Recipes

Generated: 2026-04-28

Do not run these at full scale until the smoke test passes on real seed rows.

## Shared Hard Constraints

Preserve all metadata columns exactly:

- `row_id`
- `triplet_id`
- `variant_type`
- `scam_type`
- `language`
- `script`
- `genuine_anchor_id`
- `pattern_id`
- `source_type`
- `source_url`
- `source_date`
- `pressure_tactic`
- `ask`
- `red_flags`
- `validation_status`

Never introduce real bank account numbers, real phone numbers beyond official public reporting helplines already present in sources, working phishing URLs, real OTPs, real UPI IDs, real QR payloads, real USSD strings, or realistic mule-account details.

## Job 1: Genuine-Variant Naturalness Pass

Blueprint:

> Make `message_text` read like an actual Indian bank, UPI, or courier SMS in 2026. Preserve the input language, script, length, abbreviation pattern, sender-tag format, punctuation quirks, and compact SMS register. Do not add a greeting if one is not present. Do not lengthen the text. Do not turn the SMS into awareness advice. Preserve masked account endings, fake RRNs, fake AWBs, fake order IDs, and fake OTP/DAC style numbers. Keep all metadata columns untouched.

Run on:

- `variant_type = genuine`

Expected output:

- More natural genuine SMS register
- No formal advisory paragraphs
- No metadata changes

## Job 2: Help-Seeking Variant Naturalization

Blueprint:

> Make `message_text` sound like a worried Indian person asking a trusted contact or helpline for help. Preserve language, script, and code-mixing exactly. Preserve regional-language quirks and English loanwords like OTP, CBI, KYC, UPI, Aadhaar, parcel, debit, RRN. Do not formalize the tone. Keep it short, anxious, and question-like. Do not add scammer instructions. Keep all metadata columns untouched.

Run on:

- `variant_type = help_seeking`

Expected output:

- Family-WhatsApp or helpline-call register
- Natural anxiety without polished prose
- No new operational scam details

## Job 3: Contrastive Consistency Check

Blueprint:

> For each `triplet_id`, compare the genuine, scam, and help-seeking rows. Verify that the scam variant retains structural similarity to the genuine variant where appropriate, such as sender format, length, opening style, account masking, notification shape, or courier tracking shape, while introducing the malicious ask documented in `red_flags`. Verify that help-seeking rows refer to the same underlying situation. If divergence is too large, set `validation_status` to `needs_human_review` and add a short note in a review field if available. Do not rewrite content unless explicitly needed for consistency. Keep all metadata columns untouched.

Run on:

- Complete triplets after seed rows exist

Expected output:

- Triplet-level consistency flags
- Minimal rewriting

## Job 4: Safety / Red-Team Filter

Blueprint:

> Review each row for operational misuse risk. Flag rows where the scam template could be lifted directly to defraud someone with no modification, including working phishing URLs, real bank account numbers, real UPI IDs, real phone numbers other than official public helplines, real OTPs, real USSD call-forwarding strings, or exact step-by-step fraud mechanics. Mark `safety_review_needed: true` if available, otherwise set `validation_status` to `needs_human_review`. Do not redact unless a field requires it. Keep all metadata columns untouched.

Run on:

- All rows before final export

Expected output:

- Safety flags
- No silent redaction

## Smoke-Test Blueprint

Use this before any production job:

> Preserve language, script, and code-mixing exactly as input. Do not rewrite content. Do not formalize register. Preserve scam-register weirdness in scam rows, including urgency punctuation, abbreviations, broken grammar, and short-message shape. Correct only obvious typos and impossible orthography. Keep all metadata columns (`triplet_id`, `pattern_id`, `red_flags`, `validation_status`) untouched. Preserve row order and `row_id`.

Pass condition:

- At least 8 of 10 rows pass without destructive rewriting, transliteration, metadata drift, or safety rejection.
