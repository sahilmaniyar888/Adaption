"""Prepare Test Split Eyescan Batch.

Exports the 200 frozen test rows as a CSV for real human review.
"""
import csv
import json
import logging
import sys
from pathlib import Path

from _paths import DATA_DIR, SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_eyescan")

def main():
    test_file = DATA_DIR / "final" / "test_gold.jsonl"
    out_csv = DATA_DIR / "final" / "test_eyescan_batch.csv"
    
    if not test_file.exists():
        logger.error(f"Not found: {test_file}")
        sys.exit(1)

    rows = []
    with test_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(BharatCRICRow(**json.loads(line)))

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row_id", "language", "variant_type", "scam_category", "instruction", "completion", "english_gloss", "verdict", "notes"])
        for r in rows:
            writer.writerow([r.row_id, r.language, r.variant_type or "", r.scam_category or "", r.instruction, r.completion, r.english_gloss or "", "", ""])

    logger.info(f"Prepared test split eyescan batch with {len(rows)} rows -> {out_csv.name}")

if __name__ == "__main__":
    main()
