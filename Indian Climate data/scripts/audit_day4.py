"""Day 4 Audit.

Runs the hardened validators against the dataset and reports hits.
"""
import json
import logging
import sys
from pathlib import Path

from _paths import SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow
from bharat_cric.validators import validate_row

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_day4")

def main():
    in_file = SEED_DIR / "seed_v4_with_pairs.jsonl"
    if not in_file.exists():
        logger.error("No seed found.")
        sys.exit(1)

    url_hits = 0
    amt_hits = 0
    temp_hits = 0
    total = 0
    
    with in_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                row = BharatCRICRow(**json.loads(line))
                res = validate_row(row)
                total += 1
                
                msgs = "".join(res.warnings + res.errors)
                if "url-hallucination" in msgs: url_hits += 1
                if "amount-hallucination" in msgs: amt_hits += 1
                if "temporal-hallucination" in msgs: temp_hits += 1

    print("=== Day 4 Audit Hit Rate ===")
    print(f"Total Rows Checked: {total}")
    print(f"URL Hallucination hits: {url_hits} ({url_hits/total:.2%})")
    print(f"Amount Hallucination hits: {amt_hits} ({amt_hits/total:.2%})")
    print(f"Temporal Hallucination hits: {temp_hits} ({temp_hits/total:.2%})")
    print(f"Total Combined Rate: {(url_hits + amt_hits + temp_hits)/total:.2%}")

if __name__ == "__main__":
    main()
