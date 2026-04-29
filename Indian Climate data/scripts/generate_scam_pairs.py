"""Generate Scam Pairs (Day 4).

Takes genuine rows, spawns scam variants, sets variant_type for the genuine,
and appends to a new dataset seed_v4_with_pairs.jsonl.
"""
import json
import logging
import random
import sys
import uuid
from pathlib import Path

from _paths import SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow
from bharat_cric.adversarial.pair_generator import generate_scam_variant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate_scams")

def main():
    base_file = SEED_DIR / "seed_v3_adapted.jsonl"
    out_file = SEED_DIR / "seed_v4_with_pairs.jsonl"
    
    if not base_file.exists():
        logger.error(f"Not found: {base_file}")
        sys.exit(1)

    rows = []
    with base_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(BharatCRICRow(**json.loads(line)))

    # We want ~100 pairs (200 rows)
    # Select high quality rows from english, hindi, bhojpuri
    candidates = [r for r in rows if r.language in ["eng", "hin", "bho"] and r.surface_format in ["sms", "whatsapp"] and r.validation_status == "source_authentic"]
    
    random.seed(42)
    random.shuffle(candidates)
    selected = candidates[:100]
    
    new_rows = []
    pair_count = 0
    
    for gen_row in selected:
        gen_row.variant_type = "genuine_advisory"
        if not gen_row.pair_id:
            gen_row.pair_id = str(uuid.uuid4())
            
        scam_row = generate_scam_variant(gen_row)
        
        new_rows.append(scam_row)
        pair_count += 1
        
    final_rows = rows + new_rows
    
    with out_file.open("w", encoding="utf-8") as fh:
        for r in final_rows:
            fh.write(r.model_dump_json() + "\n")
            
    logger.info(f"Generated {pair_count} scam pairs. Total rows: {len(final_rows)}")

if __name__ == "__main__":
    main()
