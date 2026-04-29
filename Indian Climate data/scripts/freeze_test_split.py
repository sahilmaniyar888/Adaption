"""Freeze Test Split (Day 4).

Samples 200 rows, writes to test_gold.jsonl, and creates SHA256.
Removes these rows from the train pool.
"""
import hashlib
import json
import logging
import random
import sys
from collections import defaultdict
from pathlib import Path

from _paths import DATA_DIR, SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("freeze_test")

def main():
    in_file = SEED_DIR / "seed_v4_with_pairs.jsonl"
    test_out = DATA_DIR / "final" / "test_gold.jsonl"
    hash_out = DATA_DIR / "final" / "test_gold.sha256"
    train_pool_out = SEED_DIR / "seed_v4_train_pool.jsonl"
    
    if not in_file.exists():
        logger.error("No seed_v4_with_pairs found.")
        sys.exit(1)

    rows = []
    with in_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(BharatCRICRow(**json.loads(line)))

    # We need 200 rows total: eng=50, hin=60, bho=30, mai=25, sat=20
    # Including 15 scam pairs (30 rows). We'll get 5 pairs eng, 5 pairs hin, 5 pairs bho.
    
    # Valid candidates for test split: source_authentic or eyescan_passed
    valid_rows = [r for r in rows if r.validation_status in ["source_authentic", "llm_adapted_eyescan_reviewed"]]
    
    # Group scam pairs
    scam_pairs_by_lang = defaultdict(list)
    pair_ids = {r.pair_id for r in valid_rows if r.variant_type == "heat_scam"}
    
    for pid in pair_ids:
        pair_rows = [r for r in valid_rows if r.pair_id == pid]
        if len(pair_rows) == 2:
            scam_pairs_by_lang[pair_rows[0].language].append(pair_rows)
            
    # Select 15 pairs
    selected_pairs = []
    for lang in ["eng", "hin", "bho"]:
        selected_pairs.extend(scam_pairs_by_lang[lang][:5])
        
    test_rows = []
    for pair in selected_pairs:
        test_rows.extend(pair)
        
    # Subtract pairs count from target quotas
    quotas = {"eng": 65, "hin": 65, "bho": 30, "mai": 20, "sat": 20}
    for r in test_rows:
        quotas[r.language] -= 1
        
    # Fill remaining quotas with genuine/standard rows
    # Exclude already selected pairs
    used_ids = {r.row_id for r in test_rows}
    remaining_rows = [r for r in valid_rows if r.row_id not in used_ids and not r.variant_type]
    
    random.seed(42)
    random.shuffle(remaining_rows)
    
    for r in remaining_rows:
        if quotas.get(r.language, 0) > 0:
            test_rows.append(r)
            quotas[r.language] -= 1
            used_ids.add(r.row_id)
            
    # Fill any remaining shortfall up to 200
    if len(test_rows) < 200:
        shortfall = 200 - len(test_rows)
        fallback_rows = [r for r in valid_rows if r.row_id not in used_ids and not r.variant_type]
        random.shuffle(fallback_rows)
        for r in fallback_rows[:shortfall]:
            test_rows.append(r)
            used_ids.add(r.row_id)
            
    # Verify count
    logger.info(f"Test split size: {len(test_rows)} (Target: 200)")
    
    # Save test split
    with test_out.open("w", encoding="utf-8") as fh:
        for r in test_rows:
            fh.write(r.model_dump_json() + "\n")
            
    # Hash
    with test_out.open("rb") as fh:
        sha256 = hashlib.sha256(fh.read()).hexdigest()
        
    with hash_out.open("w", encoding="utf-8") as fh:
        fh.write(f"{sha256}  test_gold.jsonl\n")
        
    logger.info(f"Frozen test split SHA256: {sha256}")
    
    # Save train pool
    train_pool = [r for r in rows if r.row_id not in used_ids]
    with train_pool_out.open("w", encoding="utf-8") as fh:
        for r in train_pool:
            fh.write(r.model_dump_json() + "\n")
            
    logger.info(f"Saved train pool: {len(train_pool)} rows.")

if __name__ == "__main__":
    main()
