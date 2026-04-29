"""Build Train/Val Splits.

Reads seed_v4_train_pool.jsonl and creates train.jsonl and val.jsonl.
Validation set excludes unreviewed adapted rows.
"""
import json
import logging
import random
import sys
from pathlib import Path

from _paths import DATA_DIR, SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("build_train_val")

def main():
    pool_file = SEED_DIR / "seed_v4_train_pool.jsonl"
    train_out = DATA_DIR / "final" / "train.jsonl"
    val_out = DATA_DIR / "final" / "val.jsonl"
    
    if not pool_file.exists():
        logger.error("No train pool found.")
        sys.exit(1)

    rows = []
    with pool_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(BharatCRICRow(**json.loads(line)))

    # Separate eligible val rows
    val_eligible = [r for r in rows if r.validation_status != "llm_adapted_unreviewed"]
    
    # We want 10% of total in val
    total_len = len(rows)
    val_size = total_len // 10
    
    random.seed(42)
    random.shuffle(val_eligible)
    
    # Take val_size keeping pairs together? Scam pairs can just be split wherever, but usually better to keep pair in same split. 
    # To keep it simple, just take by row. If pair gets split between train/val it's actually bad for leakage!
    # Let's group by pair_id
    grouped = {}
    for r in rows:
        pid = r.pair_id if r.pair_id else r.row_id
        if pid not in grouped:
            grouped[pid] = []
        grouped[pid].append(r)
        
    group_keys = list(grouped.keys())
    random.shuffle(group_keys)
    
    train_rows = []
    val_rows = []
    
    for pid in group_keys:
        group = grouped[pid]
        # Check if group is eligible for val
        if all(r.validation_status != "llm_adapted_unreviewed" for r in group) and len(val_rows) < val_size:
            val_rows.extend(group)
        else:
            train_rows.extend(group)

    with train_out.open("w", encoding="utf-8") as fh:
        for r in train_rows:
            fh.write(r.model_dump_json() + "\n")
            
    with val_out.open("w", encoding="utf-8") as fh:
        for r in val_rows:
            fh.write(r.model_dump_json() + "\n")
            
    logger.info(f"Train set: {len(train_rows)} rows")
    logger.info(f"Val set: {len(val_rows)} rows")

if __name__ == "__main__":
    main()
