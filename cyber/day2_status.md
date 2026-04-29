# Day 2 Status

Generated: 2026-04-28

## Genuine Anchors

- Total anchors: 67
- Real-SMS-register paraphrased anchors added: 31
- Coverage now includes transaction debit/credit SMS, UPI AutoPay mandate SMS, loan installment notice, Hindi/Marathi KYC notices, CKYC/eKYC OTP and success messages, courier tracking, delivery-code, and LPG invoice/delivery SMS.
- All user-supplied private data was anonymized with fake names, fake account endings, fake RRNs, fake OTPs/DACs, fake order IDs, fake AWBs, and fake tracking tokens.

## Pattern Library

- Total patterns: 32
- Distribution:
  - `digital_arrest`: 8
  - `upi_collect_request`: 8
  - `fake_courier_parcel`: 8
  - `fake_kyc`: 8
- No scam type is thin.
- No `representative_excerpt` or `pressure_tactic` gaps found.
- No 404s found in source URL check; 5 official/bank URLs need manual browser confirmation because PowerShell timed out.

## Dataset V0

- Current rows: 120
- Current status: scaled checkpoint generated after pilot review
- Coverage: all 48 cells have at least 2 rows.
- Balance: 30 rows per language, 30 rows per scam type, 40 rows per variant type.
- Next step is human spot-check of the 15 random rows in `spot_check_sample.md`; do not run the Adaption smoke test before that review.

## Adaption Smoke Test

- Not run yet.
- Blockers:
  - Human spot-check of the 120-row checkpoint is pending.
  - API key is available from the user message, but must not be written to disk.
- SDK import check passed.

## Recipes

- `adaption_recipes.md` has four production recipes plus a smoke-test blueprint.
- Important pending decision: if Adaption standardizes scam-register text, skip refinement for scam rows and keep those as `hand_built` / `needs_human_review`.

## Risks

- Biggest risk: Hindi/Marathi/Hinglish register quality in seed rows.
- Second risk: Adaption may over-clean scam-register abbreviations.
- Third risk: CSV encoding drift once Devanagari rows are written repeatedly.

## Next Human Gate

Pick 10 patterns for seed triplets and review the first 12 rows before expanding:

- 3 digital arrest
- 3 fake courier/parcel
- 2 fake KYC
- 2 UPI collect request
