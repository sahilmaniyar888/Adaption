# Adaption Smoke Test Log

Status: not run yet.

Reason: `dataset_v0.csv` now has a balanced 120-row checkpoint, but the current gate says to stop for the 15-row human spot-check before running the Adaption smoke test.

Local SDK check:

- `adaption` import: ok
- `ADAPTION_API_KEY`: not set in this shell
- Existing helper: `isl_dataset/upload.py` has a `push_to_adaption` helper, but it is scoped to the ISL medical JSONL workflow rather than this CSV dataset.

Next smoke-test steps after 5 seed rows exist:

1. Select five rows covering English and Hindi, plus both `genuine` and `scam`.
2. Submit with blueprint: "preserve language and code-mixing as-is; correct only obvious typos and unnatural register; do not rewrite content."
3. Check Devanagari preservation.
4. Check English loanwords such as OTP, CBI, UPI, parcel.
5. Check metadata columns remain unchanged.
6. Record grade and failures.

Pass condition: at least 4 of 5 rows pass without script corruption or metadata drift.
