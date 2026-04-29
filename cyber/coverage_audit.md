# Coverage Audit

Generated: 2026-04-28

## Summary

- `dataset_v0.csv` rows: 120
- Status: 120-row checkpoint generated; pilot rows preserved
- Coverage target for Day 2 seed set: every cell has at least 2 rows
- Current coverage: all 48 cells have at least 2 rows

## Cell Counts

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

## UTF-8 / Script Check

`dataset_v0.csv` now contains 60 Hindi/Marathi rows with non-ASCII text. PowerShell `Import-Csv` parses the file successfully. A Python read confirmed 0 `??` replacement sequences, 60/60 Hindi-Marathi rows containing non-ASCII text, 13 inert-link rows containing `[.]`, and no UTF-8 BOM.

## Required Next Fill

Minimum additional rows needed to satisfy Day 2 seed coverage:

- 0. The 120-row checkpoint satisfies the 2-row-per-cell seed coverage target.

Recommended Day 2 seed shape:

- 10 selected patterns
- 3 variants per pattern
- English, Hindi, Marathi hand-reviewed
- Hinglish derived only after Hindi/Marathi are reviewed
