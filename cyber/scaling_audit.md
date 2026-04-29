# Scaling Audit

Generated: 2026-04-28

## Summary

- Total rows: 120
- Pilot rows preserved: 12
- New generated rows: 108
- New triplets: 36 (28 base generation + 8 cross-language variants)
- No Adaption job has been run.

### Language

| value | count |
|---|---:|
| English | 30 |
| Hindi | 30 |
| Hinglish | 30 |
| Marathi | 30 |

### Scam Type

| value | count |
|---|---:|
| digital_arrest | 30 |
| fake_courier_parcel | 30 |
| fake_kyc | 30 |
| upi_collect_request | 30 |

### Variant Type

| value | count |
|---|---:|
| genuine | 40 |
| help_seeking | 40 |
| scam | 40 |

### Surface Format

| value | count |
|---|---:|
| SMS | 58 |
| WhatsApp | 26 |
| app_notification | 6 |
| awareness_notice | 1 |
| courier_sms | 1 |
| help_message | 4 |
| phone_call_summary | 14 |
| video_call_summary | 10 |

### Validation Status

| value | count |
|---|---:|
| corrected_after_review | 3 |
| machine_generated | 54 |
| needs_human_review | 63 |

## 4 x 4 x 3 Cell Counts

| scam_type | language | genuine | scam | help_seeking | flag |
|---|---|---:|---:|---:|---|
| digital_arrest | English | 2 | 2 | 2 | ok |
| digital_arrest | Hindi | 4 | 4 | 4 | ok |
| digital_arrest | Marathi | 2 | 2 | 2 | ok |
| digital_arrest | Hinglish | 2 | 2 | 2 | ok |
| upi_collect_request | English | 2 | 2 | 2 | ok |
| upi_collect_request | Hindi | 2 | 2 | 2 | ok |
| upi_collect_request | Marathi | 2 | 2 | 2 | ok |
| upi_collect_request | Hinglish | 4 | 4 | 4 | ok |
| fake_courier_parcel | English | 2 | 2 | 2 | ok |
| fake_courier_parcel | Hindi | 2 | 2 | 2 | ok |
| fake_courier_parcel | Marathi | 4 | 4 | 4 | ok |
| fake_courier_parcel | Hinglish | 2 | 2 | 2 | ok |
| fake_kyc | English | 4 | 4 | 4 | ok |
| fake_kyc | Hindi | 2 | 2 | 2 | ok |
| fake_kyc | Marathi | 2 | 2 | 2 | ok |
| fake_kyc | Hinglish | 2 | 2 | 2 | ok |

## Random Spot-Check Row IDs

Use these 15 row IDs for human register review:

- `CYB-SCALE-036`
- `CYB-SCALE-054`
- `CYB-SCALE-016`
- `CYB-SCALE-106`
- `CYB-SCALE-071`
- `CYB-SCALE-049`
- `CYB-SCALE-066`
- `CYB-SCALE-073`
- `CYB-SCALE-063`
- `CYB-PILOT-011`
- `CYB-SCALE-032`
- `CYB-SCALE-078`
- `CYB-SCALE-018`
- `CYB-PILOT-007`
- `CYB-SCALE-105`

## Notes

- English and Hinglish generated rows are marked `machine_generated`.
- Hindi and Marathi generated rows are marked `needs_human_review`.
- Reviewed pilot corrections remain marked `corrected_after_review`.
- Scam links, where present, use inert `[.]` notation.
