"""Prepare Eyescan Batch.

Extracts unreviewed adapted rows into a CSV for human review.
"""
import csv
import json
import logging
import sys
from pathlib import Path

from _paths import SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prepare_eyescan")

def main():
    raw_file = SEED_DIR / "seed_v3_adapted_raw.jsonl"
    out_csv = SEED_DIR / "eyescan_batch.csv"
    
    if not raw_file.exists():
        logger.error(f"Not found: {raw_file}")
        sys.exit(1)

    rows = []
    with raw_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(BharatCRICRow(**json.loads(line)))

    # Filter unreviewed adapted rows
    unreviewed = [r for r in rows if r.validation_status == "llm_adapted_unreviewed"]
    
    # We want ~150 Hindi and ~100 Bhojpuri, ~50 Maithili
    batch = []
    hin_count = 0
    bho_count = 0
    mai_count = 0
    
    for r in unreviewed:
        if r.language == "hin" and hin_count < 150:
            batch.append(r)
            hin_count += 1
        elif r.language == "bho" and bho_count < 100:
            batch.append(r)
            bho_count += 1
        elif r.language == "mai" and mai_count < 50:
            batch.append(r)
            mai_count += 1

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row_id", "language", "instruction", "completion", "english_gloss", "verdict", "notes"])
        for r in batch:
            writer.writerow([r.row_id, r.language, r.instruction, r.completion, r.english_gloss or "", "", ""])

    logger.info(f"Prepared eyescan batch with {len(batch)} rows (Hin: {hin_count}, Bho: {bho_count}, Mai: {mai_count}) -> {out_csv.name}")

if __name__ == "__main__":
    main()
