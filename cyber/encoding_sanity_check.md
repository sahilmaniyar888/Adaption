# Encoding Sanity Check

Generated: 2026-04-28

File checked: `dataset_v0.csv`

BOM check: UTF-8 BOM not present. First three bytes are `22 72 6F`, the opening quote and `ro` from the CSV header.

Method:

- Re-read file from disk with UTF-8 decoding.
- Read raw bytes from disk.
- For each sample substring, computed expected UTF-8 bytes and searched for the exact byte sequence in the file.

## Results

| sample | expected UTF-8 bytes | text found | byte sequence found |
|---|---|---:|---:|
| भैया | `E0 A4 AD E0 A5 88 E0 A4 AF E0 A4 BE` | true | true |
| तुमची shipment | `E0 A4 A4 E0 A5 81 E0 A4 AE E0 A4 9A E0 A5 80 20 73 68 69 70 6D 65 6E 74` | true | true |
| म्हणतो address | `E0 A4 AE E0 A5 8D E0 A4 B9 E0 A4 A3 E0 A4 A4 E0 A5 8B 20 61 64 64 72 65 73 73` | true | true |
| कोई CBI वाला | `E0 A4 95 E0 A5 8B E0 A4 88 20 43 42 49 20 E0 A4 B5 E0 A4 BE E0 A4 B2 E0 A4 BE` | true | true |
| kyc-boi-secure[.]xyz | `6B 79 63 2D 62 6F 69 2D 73 65 63 75 72 65 5B 2E 5D 78 79 7A` | true | true |

## 120-Row Checkpoint

After scaling to 120 rows:

- UTF-8 BOM: not present
- CSV row count: 120
- Hindi/Marathi rows: 60
- Hindi/Marathi rows containing non-ASCII text: 60
- Replacement-sequence check: 0 rows contain `??`
- Inert-link rows: 13 rows contain `[.]`
- Rows marked `contains_link=true` without `[.]`: 0

Conclusion: Hindi, Marathi, mixed Latin+Devanagari, and inert-link text are present after scaling without visible replacement-character drift.
