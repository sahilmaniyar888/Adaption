"""Balance surface formats to inject radio_script and official_bulletin."""
import json
import logging
import random
import sys
from pathlib import Path

from _paths import SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("balance_formats")

def main():
    seed_file = SEED_DIR / "seed_v2_multilingual.jsonl"
    
    if not seed_file.exists():
        logger.error(f"Not found: {seed_file}")
        sys.exit(1)

    rows = []
    
    with seed_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip(): continue
            rows.append(BharatCRICRow(**json.loads(line)))

    # Count current
    counts = {r.surface_format: 0 for r in rows}
    for r in rows:
        counts[r.surface_format] += 1
        
    logger.info(f"Before balance: {counts}")
    
    # We want ~30 radio_script and ~30 official_bulletin
    needed_radio = max(0, 30 - counts.get("radio_script", 0))
    needed_bulletin = max(0, 30 - counts.get("official_bulletin", 0))
    
    # Take from sms/whatsapp
    candidates = [r for r in rows if r.surface_format in ["sms", "whatsapp"]]
    random.seed(42) # Deterministic
    random.shuffle(candidates)
    
    for r in candidates[:needed_radio]:
        object.__setattr__(r, "surface_format", "radio_script")
        if not r.metadata_json: r.metadata_json = {}
        r.metadata_json["format_origin"] = "synthetic_relabel"
        
    for r in candidates[needed_radio:needed_radio+needed_bulletin]:
        object.__setattr__(r, "surface_format", "official_bulletin")
        if not r.metadata_json: r.metadata_json = {}
        r.metadata_json["format_origin"] = "synthetic_relabel"
        
    # Re-save
    with seed_file.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(row.model_dump_json() + "\n")
            
    # Count after
    counts_after = {r.surface_format: 0 for r in rows}
    for r in rows:
        counts_after[r.surface_format] += 1
    logger.info(f"After balance: {counts_after}")

if __name__ == "__main__":
    main()
