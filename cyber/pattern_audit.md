# Pattern Audit

Generated: 2026-04-28

## Summary

- Total patterns: 32
- Minimum target: 30+
- Per-scam-type minimum target: 6
- Current distribution: balanced at 8 patterns per scam type

| scam_type | count | thinness_flag |
|---|---:|---|
| digital_arrest | 8 | no |
| upi_collect_request | 8 | no |
| fake_courier_parcel | 8 | no |
| fake_kyc | 8 | no |

## Missing Field Audit

No rows are missing `representative_excerpt`.

No rows are missing `pressure_tactic`.

## Source URL Audit

PowerShell URL check result:

- 21 unique URLs returned HTTP 200.
- 0 unique URLs returned HTTP 404.
- 5 unique URLs timed out or closed the connection in PowerShell; these are not marked as dead because they are official/bank pages and were reachable through browser/search context.

Timed-out or connection-closed URLs to manually re-open before final citation:

- https://www.icicibank.com/personal-banking/products/online-safe-banking/Phishing
- https://www.npci.org.in/what-we-do/bhim/faq/
- https://www.npci.org.in/what-we-do/ipo/faqs
- https://www.npci.org.in/what-we-do/upi/circular
- https://www.npci.org.in/what-we-do/upi/product-overview/

## Expansion Done

Added 8 new patterns:

- `PAT-DA-007`: fake affidavit / oath of secrecy
- `PAT-DA-008`: fake Supreme Court / ministry letters
- `PAT-UPI-007`: debit-reversal collect request
- `PAT-UPI-008`: unknown UPI request warning counterpattern
- `PAT-FC-007`: fake courier customer-care number
- `PAT-FC-008`: delivery USSD call-forwarding scam
- `PAT-KYC-007`: URN/payee-registration vishing
- `PAT-KYC-008`: APK/KYC security update

## Notes

The pattern library is dense enough for Day 2 seed generation. The next quality risk is not pattern count; it is whether the generated rows preserve real SMS register and natural Hindi/Marathi/Hinglish tone.
