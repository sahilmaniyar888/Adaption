"""Build Final Day 3 Seed v3.

Reads seed_v3_adapted_raw.jsonl, runs hallucination audits, splits into
various subsets (eyescan_passed, unreviewed), and writes seed_v3_adapted.jsonl.
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
logger = logging.getLogger("build_v3")

def main():
    raw_file = SEED_DIR / "seed_v3_adapted_raw.jsonl"
    out_v3 = SEED_DIR / "seed_v3_adapted.jsonl"
    out_eyescan = SEED_DIR / "eyescan_passed.jsonl"
    out_unreviewed = SEED_DIR / "unreviewed.jsonl"
    
    if not raw_file.exists():
        logger.error("Missing raw adapted file.")
        sys.exit(1)

    rows = []
    with raw_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip(): continue
            rows.append(BharatCRICRow(**json.loads(line)))

    # 1. Filter out fail/fix rows
    valid_rows = []
    failed_rows = 0
    hallucinations = 0
    
    for r in rows:
        if r.validation_status == "llm_adapted_quality_questionable":
            failed_rows += 1
            continue
            
        # 2. Run validators (Hallucination Audit)
        v_res = validate_row(r)
        
        has_hallucination = any("hallucination" in w or "hallucinated" in w for w in v_res.warnings + v_res.errors)
        has_hallucination_err = any("hallucinated" in e for e in v_res.errors)
        
        if has_hallucination or has_hallucination_err:
            hallucinations += 1
            if r.validation_status == "llm_adapted_eyescan_reviewed":
                # Downgrade if hallucination found after review
                r.validation_status = "llm_adapted_unreviewed"
                r.eyescan_notes = "Downgraded by automated hallucination audit."
                
        if v_res.ok or (not v_res.ok and not has_hallucination_err): 
            # allow warnings, but errors must fail, wait we need 0 errors.
            if v_res.ok:
                valid_rows.append(r)
            else:
                failed_rows += 1
        else:
            failed_rows += 1

    # Calculate hallucination rate
    adapted_count = sum(1 for r in valid_rows if r.generation_method == "llm_adapted")
    halluc_rate = (hallucinations / adapted_count) if adapted_count else 0
    logger.info(f"Hallucination rate on adapted rows: {halluc_rate:.2%}")
    if halluc_rate > 0.05:
        logger.warning("Hallucination rate > 5%. Adjust generation strategy!")

    # 3. Split datasets
    eyescan_passed = [r for r in valid_rows if r.validation_status == "llm_adapted_eyescan_reviewed"]
    unreviewed = [r for r in valid_rows if r.validation_status == "llm_adapted_unreviewed"]

    with out_v3.open("w", encoding="utf-8") as fh:
        for r in valid_rows:
            fh.write(r.model_dump_json() + "\n")
            
    with out_eyescan.open("w", encoding="utf-8") as fh:
        for r in eyescan_passed:
            fh.write(r.model_dump_json() + "\n")

    with out_unreviewed.open("w", encoding="utf-8") as fh:
        for r in unreviewed:
            fh.write(r.model_dump_json() + "\n")

    # 4. Print Summary Stats
    counts = {}
    for r in valid_rows:
        counts[r.language] = counts.get(r.language, 0) + 1
        
    eyescan_counts = {}
    for r in eyescan_passed:
        eyescan_counts[r.language] = eyescan_counts.get(r.language, 0) + 1

    print("=== Day 3 Build Summary ===")
    print(f"Total Rows: {len(valid_rows)}")
    print(f"Removed/Failed: {failed_rows}")
    print(f"Hallucinations detected: {hallucinations}")
    print("\nTotal by Language:")
    for lang, c in counts.items():
        print(f"  {lang}: {c}")
    print("\nEyescan Passed by Language:")
    for lang, c in eyescan_counts.items():
        print(f"  {lang}: {c}")

if __name__ == "__main__":
    main()
