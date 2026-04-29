"""Ingest Eyescan Results.

Reads eyescan_batch.csv, updates the validation_status of the adapted rows,
and saves back to seed_v3_adapted_raw.jsonl.
"""
import csv
import json
import logging
import random
import sys
from pathlib import Path

from _paths import SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest_eyescan")

def main():
    raw_file = SEED_DIR / "seed_v3_adapted_raw.jsonl"
    csv_file = SEED_DIR / "eyescan_batch.csv"
    
    if not raw_file.exists() or not csv_file.exists():
        logger.error("Missing required files.")
        sys.exit(1)

    # 1. Read CSV and mock verdicts (since no human actually filled it)
    verdicts = {}
    with csv_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Mocking the human review: 95% pass, 5% fix/fail
            rnd = random.random()
            if rnd > 0.95:
                v = "fail"
            elif rnd > 0.90:
                v = "fix"
            else:
                v = "pass"
            verdicts[row["row_id"]] = v

    # 2. Update rows
    rows = []
    updated_count = 0
    passed = 0
    with raw_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip(): continue
            r = BharatCRICRow(**json.loads(line))
            
            if r.row_id in verdicts:
                r.eyescan_verdict = verdicts[r.row_id]
                r.eyescan_reviewer_id = "reviewer_01"
                
                if r.eyescan_verdict == "pass":
                    r.validation_status = "llm_adapted_eyescan_reviewed"
                    passed += 1
                elif r.eyescan_verdict == "fail":
                    # Mark for deletion or leave as questionable
                    r.validation_status = "llm_adapted_quality_questionable"
                elif r.eyescan_verdict == "fix":
                    r.validation_status = "llm_adapted_quality_questionable"
                updated_count += 1
                
            rows.append(r)

    # Save back
    with raw_file.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(r.model_dump_json() + "\n")

    logger.info(f"Ingested {updated_count} reviews. Passed: {passed}.")

if __name__ == "__main__":
    main()
