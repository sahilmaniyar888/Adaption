"""Prepare seeds for Day 3 Adaption.

Applies seed_score, actionability_score, quality_flag, santali_policy, 
linguistic_purity, and extracts top 100 rows + high quality pairs.
"""
import json
import logging
import re
import sys
from pathlib import Path

from _paths import SEED_DIR, ensure_on_path
ensure_on_path()
from bharat_cric.schema import BharatCRICRow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prepare_day3")

HINDI_STOPWORDS = {"है", "कि", "में", "को", "का", "से", "और", "के", "लिए", "पर", "भी"}

def _calc_linguistic_purity(text: str) -> str:
    words = re.findall(r"\w+", text)
    if not words:
        return "neutral"
    stop_count = sum(1 for w in words if w in HINDI_STOPWORDS)
    if stop_count / len(words) > 0.4:  # conservative 40% threshold for leakage
        return "suspect"
    return "pass"

def main():
    seed_file = SEED_DIR / "seed_v2_multilingual.jsonl"
    out_file = SEED_DIR / "seed_v2_multilingual.jsonl"
    
    if not seed_file.exists():
        logger.error(f"Not found: {seed_file}")
        sys.exit(1)

    rows = []
    with seed_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip(): continue
            data = json.loads(line)
            row = BharatCRICRow(**data)
            
            if not row.metadata_json:
                row.metadata_json = {}
            
            # 1. Backfill instruction_type for English (Day 1)
            if not row.instruction_type:
                instr_lower = row.instruction.lower()
                if "translate" in instr_lower:
                    row.instruction_type = "translation"
                elif "classify" in instr_lower or "true/false" in instr_lower or "yes/no" in instr_lower:
                    row.instruction_type = "classification"
                elif "?" in instr_lower and any(w in instr_lower for w in ["what", "how", "why", "when"]):
                    row.instruction_type = "qa"
                elif "extract" in instr_lower or "list" in instr_lower:
                    row.instruction_type = "extraction"
                else:
                    row.instruction_type = "summarization"
            
            # 2. Quality Flag
            corpus = (row.source_corpus or "").lower()
            ref = (row.source_reference or "").lower()
            if "wikipedia" in corpus or "wikipedia" in ref:
                row.quality_flag = "medium"
            elif row.source_quality == "high" or "curated" in corpus or "ndma" in ref or "imd" in ref:
                row.quality_flag = "high_confidence"
            else:
                row.quality_flag = "medium"
                
            # 3. Actionability Score
            action_score = 0.0
            comp_lower = row.completion.lower()
            if any(v in comp_lower for v in ["drink", "avoid", "call", "stay", "wear", "पिएं", "बचें", "करें", "पहनें"]):
                action_score += 0.4
            if any(t in comp_lower for t in ["am", "pm", "baje", "बजे", "morning", "evening", "सुबह", "शाम", "hospital", "shade", "छाया"]):
                action_score += 0.3
            if row.helplines_mentioned or any(kw in comp_lower for kw in ["emergency", "आपातकाल", "police", "ambulance", "doctor", "डॉक्टर"]):
                action_score += 0.3
            row.actionability_score = round(min(1.0, action_score), 2)

            # 4. Seed Score
            score = 0.0
            if row.quality_flag == "high_confidence":
                score += 0.30
            if row.helplines_mentioned:
                score += 0.25
            if row.instruction_type != "translation":
                score += 0.25
            if row.surface_format in ["official_bulletin", "radio_script"]:
                score += 0.10
            elif row.surface_format == "community_post":
                score += 0.05
            # Instruction complexity proxy: length of instruction > 10 words
            if len(row.instruction.split()) > 10:
                score += 0.10
            row.seed_score = round(score, 2)
            
            # 5. Santali Policy
            if row.language == "sat":
                row.metadata_json["santali_policy"] = "seed_only_no_expansion"
                
            # 6. Linguistic Purity for Bho/Mai
            if row.language in ["bho", "mai"]:
                row.metadata_json["linguistic_purity"] = _calc_linguistic_purity(row.completion)

            rows.append(row)

    # Save back
    with out_file.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(row.model_dump_json() + "\n")
            
    logger.info(f"Updated {len(rows)} rows with scores and flags.")

    # Top 100 for Adaption (exclude synthetic relabels)
    valid_top = [r for r in rows if r.metadata_json.get("format_origin") != "synthetic_relabel" and r.metadata_json.get("santali_policy") != "seed_only_no_expansion"]
    top_100 = sorted(valid_top, key=lambda r: r.seed_score or 0.0, reverse=True)[:100]
    top_100_path = SEED_DIR / "adaption_seed_top100.jsonl"
    with top_100_path.open("w", encoding="utf-8") as fh:
        for row in top_100:
            fh.write(row.model_dump_json() + "\n")
    logger.info(f"Saved {len(top_100)} top rows to {top_100_path.name}")
    
    # Filter Parallel Pairs
    pairs_path = SEED_DIR / "parallel_pairs.jsonl"
    hq_pairs_path = SEED_DIR / "high_quality_pairs.jsonl"
    
    if pairs_path.exists():
        row_dict = {r.row_id: r for r in rows}
        hq_pairs = []
        with pairs_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip(): continue
                pair = json.loads(line)
                ra = row_dict.get(pair["row_id_a"])
                rb = row_dict.get(pair["row_id_b"])
                
                if ra and rb:
                    a_has_helpline = bool(ra.helplines_mentioned)
                    b_has_helpline = bool(rb.helplines_mentioned)
                    a_actionable = ra.intent_label in ["warn_imminent_risk", "first_aid_instruction", "worker_safety_protocol"]
                    b_actionable = rb.intent_label in ["warn_imminent_risk", "first_aid_instruction", "worker_safety_protocol"]
                    
                    if (a_has_helpline or a_actionable) and (b_has_helpline or b_actionable):
                        # Add semantic tags
                        if _calc_linguistic_purity(rb.completion) == "pass":
                            pair["pair_alignment"] = "exact" if pair["score"] > 0.4 else "approximate"
                        else:
                            pair["pair_alignment"] = "approximate"
                        pair["alignment_confidence"] = pair["score"]
                        hq_pairs.append(pair)
                        
        # Take top 25 by score
        hq_pairs = sorted(hq_pairs, key=lambda x: x["score"], reverse=True)[:25]
        with hq_pairs_path.open("w", encoding="utf-8") as fh:
            for p in hq_pairs:
                fh.write(json.dumps(p) + "\n")
        logger.info(f"Saved {len(hq_pairs)} high-quality pairs to {hq_pairs_path.name}")

if __name__ == "__main__":
    main()
